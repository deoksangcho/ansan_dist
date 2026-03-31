import os
from dataclasses import dataclass
from typing import Optional

import requests
from requests import HTTPError, RequestException

from services.usage_service import UsageService


class DistanceLookupError(Exception):
    pass


@dataclass
class WalkingDistanceResult:
    distance_km: float
    duration_minutes: Optional[float] = None


class WalkingDistanceService:
    def __init__(
        self,
        app_key: Optional[str] = None,
        usage_service: Optional[UsageService] = None,
        geocode_url: str = "https://apis.openapi.sk.com/tmap/geo/fullAddrGeo",
        route_url: str = "https://apis.openapi.sk.com/tmap/routes/pedestrian",
        timeout_seconds: int = 15,
    ) -> None:
        self.app_key = app_key or os.getenv("TMAP_APP_KEY", "").strip()
        self.usage_service = usage_service
        self.geocode_url = geocode_url
        self.route_url = route_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update(
            {
                "accept": "application/json",
                "content-type": "application/json",
            }
        )

    def get_walking_distance(self, start_address: str, end_address: str) -> WalkingDistanceResult:
        if not self.app_key:
            raise DistanceLookupError("TMAP App Key가 설정되지 않았습니다.")

        start_coords = self._geocode_address(start_address)
        end_coords = self._geocode_address(end_address)
        return self._route_distance(start_coords, end_coords)

    def _geocode_address(self, address: str) -> tuple[float, float]:
        try:
            response = self.session.get(
                self.geocode_url,
                params={
                    "version": 1,
                    "format": "json",
                    "coordType": "WGS84GEO",
                    "fullAddr": address,
                },
                headers={"appKey": self.app_key},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
            self._record_usage("geocoding")
        except HTTPError as exc:
            raise self._build_http_error("주소 조회", exc) from exc
        except RequestException as exc:
            raise DistanceLookupError("주소 조회 중 네트워크 오류가 발생했습니다.") from exc

        coordinates_info = (
            payload.get("coordinateInfo")
            or payload.get("coordinateinfo")
            or {}
        )
        coordinates = coordinates_info.get("coordinate") or []

        if not coordinates:
            raise DistanceLookupError(f"주소를 찾지 못했습니다: {address}")

        first_result = coordinates[0]
        lat = first_result.get("newLat") or first_result.get("lat")
        lon = first_result.get("newLon") or first_result.get("lon")
        if lat is None or lon is None:
            raise DistanceLookupError(f"주소 좌표 변환에 실패했습니다: {address}")

        return float(lat), float(lon)

    def _route_distance(
        self,
        start_coords: tuple[float, float],
        end_coords: tuple[float, float],
    ) -> WalkingDistanceResult:
        start_lat, start_lon = start_coords
        end_lat, end_lon = end_coords

        try:
            response = self.session.post(
                self.route_url,
                params={"version": 1, "format": "json"},
                headers={"appKey": self.app_key},
                json={
                    "startX": start_lon,
                    "startY": start_lat,
                    "endX": end_lon,
                    "endY": end_lat,
                    "reqCoordType": "WGS84GEO",
                    "resCoordType": "WGS84GEO",
                    "startName": "출발지",
                    "endName": "도착지",
                    "searchOption": "0",
                    "sort": "index",
                },
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
            self._record_usage("routing")
        except HTTPError as exc:
            raise self._build_http_error("경로 계산", exc) from exc
        except RequestException as exc:
            raise DistanceLookupError("경로 계산 중 네트워크 오류가 발생했습니다.") from exc

        features = payload.get("features") or []
        if not features:
            raise DistanceLookupError("도보 경로를 찾지 못했습니다.")

        summary_properties = features[0].get("properties") or {}
        total_distance = summary_properties.get("totalDistance")
        total_time = summary_properties.get("totalTime")

        if total_distance is None:
            raise DistanceLookupError("도보 경로 응답에서 거리 값을 찾지 못했습니다.")

        distance_km = float(total_distance) / 1000
        duration_minutes = float(total_time) / 60 if total_time is not None else None

        return WalkingDistanceResult(distance_km=distance_km, duration_minutes=duration_minutes)

    def _record_usage(self, metric: str) -> None:
        if self.usage_service is not None:
            self.usage_service.increment(metric)

    def _build_http_error(self, action: str, error: HTTPError) -> DistanceLookupError:
        response = error.response
        status_code = response.status_code if response is not None else None
        response_text = ""

        if response is not None:
            try:
                response_text = response.text.strip()
            except Exception:
                response_text = ""

        if status_code == 429:
            return DistanceLookupError(
                f"{action} 실패: TMAP 호출 한도를 초과했을 가능성이 있습니다. "
                f"(HTTP 429)"
            )

        if status_code in {401, 403}:
            return DistanceLookupError(
                f"{action} 실패: TMAP App Key 권한 또는 상품 사용 신청 상태를 확인해 주세요. "
                f"(HTTP {status_code})"
            )

        if status_code is not None and 500 <= status_code < 600:
            return DistanceLookupError(
                f"{action} 실패: TMAP 서버 오류가 발생했습니다. 잠시 후 다시 시도해 주세요. "
                f"(HTTP {status_code})"
            )

        if response_text:
            shortened = response_text[:200]
            return DistanceLookupError(
                f"{action} 실패: TMAP 응답 오류가 발생했습니다. "
                f"(HTTP {status_code}, 응답: {shortened})"
            )

        if status_code is not None:
            return DistanceLookupError(f"{action} 실패: HTTP {status_code} 오류가 발생했습니다.")

        return DistanceLookupError(f"{action} 실패: 알 수 없는 HTTP 오류가 발생했습니다.")
