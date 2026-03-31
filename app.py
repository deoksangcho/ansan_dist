from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

from services.distance_service import DistanceLookupError, WalkingDistanceService
from services.settings_service import DEFAULT_SETTINGS, SettingsService
from services.usage_service import UsageService


BASE_DIR = Path(__file__).resolve().parent
SETTINGS_PATH = BASE_DIR / "config.json"
USAGE_PATH = BASE_DIR / "usage_log.json"
settings_service = SettingsService(SETTINGS_PATH)
usage_service = UsageService(USAGE_PATH)


def build_distance_service(settings: dict) -> WalkingDistanceService:
    return WalkingDistanceService(
        app_key=settings.get("tmap_app_key", ""),
        usage_service=usage_service,
    )


def apply_saved_defaults(columns: list[str], settings: dict) -> tuple[Optional[str], Optional[str], str]:
    start_column = settings.get("default_start_column")
    end_column = settings.get("default_end_column")
    result_column = settings.get("default_result_column", DEFAULT_SETTINGS["default_result_column"])

    selected_start = start_column if start_column in columns else None
    selected_end = end_column if end_column in columns else None

    return selected_start, selected_end, result_column


def render_usage_summary(usage: dict) -> None:
    st.caption("앱 기준 오늘 사용량입니다. 같은 App Key를 다른 프로그램에서 함께 쓰는 경우 TMAP 실제 총사용량과는 다를 수 있습니다.")
    col1, col2 = st.columns(2)
    col1.metric(
        "오늘 지오코딩",
        f"{usage['geocoding_used']} / {usage['geocoding_limit']}",
        delta=f"잔여 {max(usage['geocoding_limit'] - usage['geocoding_used'], 0)}",
    )
    col2.metric(
        "오늘 경로안내",
        f"{usage['routing_used']} / {usage['routing_limit']}",
        delta=f"잔여 {max(usage['routing_limit'] - usage['routing_used'], 0)}",
    )


def render_sidebar(settings: dict) -> None:
    with st.sidebar:
        st.header("설정")
        st.caption("자주 바꾸지 않는 설정은 사이드바에서 관리합니다.")

        st.subheader("기본 열 설정")
        st.write(
            f"출발지: `{settings['default_start_column']}`\n\n"
            f"도착지: `{settings['default_end_column']}`\n\n"
            f"결과: `{settings['default_result_column']}`"
        )

        st.subheader("TMAP API 설정")
        saved_key = settings.get("tmap_app_key", "")
        if saved_key.strip():
            masked_key = f"{saved_key[:4]}{'*' * max(len(saved_key) - 8, 0)}{saved_key[-4:]}" if len(saved_key) >= 8 else "저장됨"
            st.info(f"현재 저장된 키: {masked_key}")
        else:
            st.warning("현재 저장된 TMAP App Key가 없습니다.")

        with st.form("tmap_key_form"):
            entered_key = st.text_input(
                "TMAP App Key 변경",
                value=saved_key,
                type="password",
                help="새 키를 입력하고 저장하면 이후 호출부터 바로 반영됩니다.",
            )
            save_clicked = st.form_submit_button("TMAP 키 저장", use_container_width=True)

        if save_clicked:
            settings_service.save({"tmap_app_key": entered_key.strip()})
            st.success("TMAP App Key를 저장했습니다. 이후 호출부터 새 키를 사용합니다.")
            st.rerun()

        if st.button("저장된 키 삭제", use_container_width=True):
            settings_service.save({"tmap_app_key": ""})
            st.success("저장된 TMAP App Key를 삭제했습니다.")
            st.rerun()

        st.divider()
        st.subheader("지도 바로가기")
        st.markdown("[네이버지도 열기](https://map.naver.com/)")
        st.markdown("[카카오맵 열기](https://map.kakao.com/)")


def calculate_single_distance(start_address: str, end_address: str) -> None:
    if not start_address.strip() or not end_address.strip():
        st.warning("출발지와 도착지 주소를 모두 입력해 주세요.")
        return

    with st.spinner("도보 거리를 계산하는 중입니다..."):
        try:
            settings = settings_service.load()
            distance_service = build_distance_service(settings)
            result = distance_service.get_walking_distance(start_address, end_address)
        except DistanceLookupError as exc:
            st.error(str(exc))
            return

    col1, col2 = st.columns(2)
    col1.metric("도보 거리", f"{result.distance_km:.2f} km")
    if result.duration_minutes is not None:
        col2.metric("예상 도보 시간", f"{result.duration_minutes:.0f} 분")

    st.success("도보 거리 계산이 완료되었습니다.")
    st.caption("경로 계산 결과는 외부 지도 서비스 응답에 따라 달라질 수 있습니다.")


def build_result_dataframe(
    dataframe: pd.DataFrame,
    start_column: str,
    end_column: str,
    result_column: str,
) -> tuple[pd.DataFrame, int, int, pd.DataFrame]:
    output_df = dataframe.copy()
    success_count = 0
    failure_count = 0
    result_values: list[object] = []
    failure_records: list[dict] = []
    settings = settings_service.load()
    distance_service = build_distance_service(settings)

    progress_bar = st.progress(0.0, text="행별 도보 거리를 계산하는 중입니다...")
    total_rows = len(output_df.index)

    for index, (_, row) in enumerate(output_df.iterrows(), start=1):
        start_address = row[start_column]
        end_address = row[end_column]

        if pd.isna(start_address) or pd.isna(end_address):
            message = "주소 누락"
            result_values.append(message)
            failure_count += 1
            failure_records.append(
                {
                    "행 번호": index + 1,
                    "출발지": start_address,
                    "도착지": end_address,
                    "오류": message,
                }
            )
        else:
            try:
                result = distance_service.get_walking_distance(str(start_address), str(end_address))
                result_values.append(round(result.distance_km, 3))
                success_count += 1
            except DistanceLookupError as exc:
                message = f"실패: {exc}"
                result_values.append(message)
                failure_count += 1
                failure_records.append(
                    {
                        "행 번호": index + 1,
                        "출발지": start_address,
                        "도착지": end_address,
                        "오류": str(exc),
                    }
                )

        if total_rows > 0:
            progress_bar.progress(index / total_rows, text=f"{index}/{total_rows} 행 처리 중")

    output_df[result_column] = result_values
    progress_bar.empty()

    failure_df = pd.DataFrame(failure_records)
    return output_df, success_count, failure_count, failure_df


def render_single_lookup_tab() -> None:
    st.subheader("단건 조회")
    st.caption("주소 2개를 직접 입력하면 도보 거리와 예상 시간을 바로 계산합니다.")
    st.markdown("**1. 주소 입력**")
    start_address = st.text_input("출발지 주소", placeholder="예: 서울특별시 종로구 세종대로 110")
    end_address = st.text_input("도착지 주소", placeholder="예: 서울특별시 중구 세종대로 99")

    st.markdown("**2. 계산 실행**")
    if st.button("도보 거리 계산", type="primary", use_container_width=True):
        calculate_single_distance(start_address, end_address)


def render_batch_tab(settings: dict) -> None:
    st.subheader("엑셀 일괄 처리")
    st.caption("엑셀을 업로드하고 주소 열을 선택하면 결과 열을 추가한 파일을 다시 내려받을 수 있습니다.")
    st.markdown("**1. 파일 업로드**")
    uploaded_file = st.file_uploader("엑셀 파일 업로드", type=["xlsx"])

    if uploaded_file is None:
        st.info("`.xlsx` 파일을 업로드하면 주소 열을 선택해서 일괄 계산할 수 있습니다.")
        return

    dataframe = pd.read_excel(uploaded_file)
    st.success(f"파일을 불러왔습니다. 총 {len(dataframe)}행, 컬럼 {len(dataframe.columns)}개")
    st.write("업로드 미리보기")
    st.dataframe(dataframe.head(10), use_container_width=True, hide_index=True)

    columns = list(dataframe.columns.astype(str))
    if not columns:
        st.error("컬럼이 없는 파일입니다.")
        return

    default_start, default_end, default_result = apply_saved_defaults(columns, settings)

    st.markdown("**2. 주소 열과 결과 열 선택**")
    start_index = columns.index(default_start) if default_start else 0
    end_index = columns.index(default_end) if default_end else min(1, len(columns) - 1)

    selection_col1, selection_col2 = st.columns(2)
    start_column = selection_col1.selectbox("출발지 주소 열", options=columns, index=start_index)
    end_column = selection_col2.selectbox("도착지 주소 열", options=columns, index=end_index)

    if default_start == start_column or default_end == end_column:
        st.caption("저장된 기본 열 설정이 자동 반영되었습니다.")

    result_mode = st.radio(
        "결과 기록 방식",
        options=["새 열 이름 입력", "기존 열 덮어쓰기"],
        horizontal=True,
    )

    if result_mode == "새 열 이름 입력":
        result_column = st.text_input("결과 열 이름", value=default_result)
    else:
        result_column = st.selectbox("결과를 기록할 기존 열", options=columns)

    left_col, right_col = st.columns(2)
    if left_col.button("현재 선택을 기본값으로 저장", use_container_width=True):
        settings_service.save(
            {
                "default_start_column": start_column,
                "default_end_column": end_column,
                "default_result_column": result_column,
            }
        )
        st.success("기본 열 설정을 저장했습니다.")

    if right_col.button("저장된 기본값 다시 불러오기", use_container_width=True):
        st.rerun()

    st.markdown("**3. 일괄 계산 실행**")
    if st.button("일괄 계산 실행", type="primary", use_container_width=True):
        if not result_column.strip():
            st.warning("결과 열 이름을 입력해 주세요.")
            return

        with st.spinner("엑셀 데이터를 처리하는 중입니다..."):
            output_df, success_count, failure_count, failure_df = build_result_dataframe(
                dataframe=dataframe.rename(columns={col: str(col) for col in dataframe.columns}),
                start_column=start_column,
                end_column=end_column,
                result_column=result_column,
            )

        st.success("일괄 계산이 완료되었습니다.")
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        summary_col1.metric("총 처리 건수", len(output_df))
        summary_col2.metric("성공", success_count)
        summary_col3.metric("실패", failure_count)

        st.write("결과 미리보기")
        st.dataframe(output_df.head(20), use_container_width=True, hide_index=True)

        if not failure_df.empty:
            st.warning("실패한 행이 있습니다. 아래 표에서 원인을 먼저 확인해 주세요.")
            st.dataframe(failure_df, use_container_width=True, hide_index=True)
            failure_bytes = dataframe_to_excel_bytes(failure_df)
            st.download_button(
                label="실패 행만 엑셀 다운로드",
                data=failure_bytes,
                file_name="walking_distance_failures.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        output_bytes = dataframe_to_excel_bytes(output_df)
        st.markdown("**4. 결과 파일 다운로드**")
        st.download_button(
            label="결과 엑셀 다운로드",
            data=output_bytes,
            file_name="walking_distance_result.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )


def dataframe_to_excel_bytes(dataframe: pd.DataFrame) -> bytes:
    from io import BytesIO

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False)
    buffer.seek(0)
    return buffer.read()


def main() -> None:
    st.set_page_config(page_title="도보 거리 계산기", page_icon="🚶", layout="wide")
    st.title("주소 기반 도보 거리 계산기")
    st.caption("직접 입력 또는 엑셀 업로드 방식으로 두 주소 사이의 도보 이동거리(km)를 계산합니다.")

    settings = settings_service.load()
    usage = usage_service.today_usage()

    render_sidebar(settings)
    render_usage_summary(usage)
    st.divider()
    st.markdown("### 작업 모드 선택")
    selected_mode = st.radio(
        "작업 모드",
        options=["단건 조회", "엑셀 일괄 처리"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if selected_mode == "단건 조회":
        st.info("빠르게 주소 2개를 넣고 즉시 거리 결과를 확인합니다.")
        render_single_lookup_tab()
    else:
        st.info("엑셀 파일을 업로드해서 여러 건의 도보 거리를 한 번에 계산합니다.")
        render_batch_tab(settings)


if __name__ == "__main__":
    main()
