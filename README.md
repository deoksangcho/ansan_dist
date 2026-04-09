# Walking Distance App

두 주소 사이의 도보 이동거리를 계산하는 Streamlit 앱입니다.

## 기능

- 단건 조회: 주소 두 개를 직접 입력해서 도보 거리 확인
- 엑셀 일괄 처리: `.xlsx` 업로드 후 주소 열을 선택해서 결과 열 추가
- 기본 열 설정 저장: 자주 쓰는 출발지/도착지/결과 열 이름을 `config.json`에 저장
- 상용 API 연동: TMAP Geocoding + 보행자 경로 API 사용
- 앱 기준 일일 사용량 표시: 지오코딩/경로안내 호출 수를 하단에 표시

## 실행 방법

```powershell
pip install -r requirements.txt
streamlit run app.py
```

또는 `config.example.json`을 참고해서 `config.json`을 만들고 `tmap_app_key`를 넣어도 됩니다.

## 데스크톱 앱 실행

```powershell
pip install -r requirements.txt
python walkdist.py
```

데스크톱 앱은 설정 파일을 실행 폴더가 아니라 `%LOCALAPPDATA%\walkdist\` 아래에 저장합니다.

## walkdist.exe 빌드

```powershell
pip install pyinstaller
python generate_walkdist_icon.py
.\build_walkdist.ps1
```

빌드가 완료되면 `dist\walkdist\walkdist.exe`가 생성됩니다.

## GitHub 업로드 전 체크

- `config.json`은 업로드하지 마세요. API 키가 들어갈 수 있습니다.
- `.gitignore`에 `config.json`, `usage_log.json`이 포함되어 있습니다.
- 팀 공유용으로는 `config.example.json`만 올리면 됩니다.

## 주의 사항

- 현재 구현은 TMAP 상용 API를 사용합니다.
- TMAP App Key는 환경 변수 `TMAP_APP_KEY` 또는 앱 내 설정으로 입력할 수 있습니다.
- 사용량 표시는 앱 내부 집계 기준이며, 다른 시스템에서 같은 App Key를 쓴 호출은 포함되지 않습니다.
- 무료/유료 사용량, 약관, 저장 제약은 TMAP 정책을 확인해야 합니다.
- 네트워크 연결이 필요합니다.
