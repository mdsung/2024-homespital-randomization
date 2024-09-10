다음은 위 코드를 위한 한글 README.md 파일입니다.

---

# 환자 등록 및 무작위 배정 애플리케이션

이 애플리케이션은 임상 시험에서 환자를 등록하고 무작위로 두 그룹(Arm 1, Arm 2) 중 하나에 배정하는 기능을 제공합니다. 데이터는 Google Sheets를 사용하여 저장 및 관리됩니다.

## 주요 기능

- 환자 등록: 사용자가 소속된 병원 및 환자 번호를 입력하여 환자를 등록합니다.
- 무작위 배정: 환자는 임상 시험에서 미리 정의된 두 그룹 중 하나에 무작위로 배정됩니다.
- 데이터 관리: Google Sheets를 통해 환자 등록 데이터가 자동으로 저장되고 관리됩니다.
- CSV 다운로드: 등록된 환자 데이터를 CSV 파일로 다운로드할 수 있습니다.

## 요구 사항

- Python 3.x
- 다음 Python 패키지:
  - `numpy`
  - `pandas`
  - `streamlit`
  - `google-auth`
  - `google-auth-oauthlib`
  - `google-auth-httplib2`
  - `google-api-python-client`

## 설치

```bash
poetry install
```

## Google API 설정

Google Sheets 및 Google Drive에 접근하기 위해서는 Google API 인증이 필요합니다. 이를 위해 다음 단계를 따라 설정하세요:

1. [Google Cloud Console](https://console.cloud.google.com/)에서 새 프로젝트를 생성하고 Google Sheets 및 Google Drive API를 활성화합니다.
2. OAuth 2.0 클라이언트 ID 자격 증명을 생성하고, 이를 `credentials.json` 파일로 다운로드합니다.
3. `credentials.json` 파일을 프로젝트 디렉터리에 배치합니다.

## 실행 방법

```bash
streamlit run app.py
```

애플리케이션을 실행하면 로컬 웹 브라우저가 열리며, 여기에서 환자를 등록하고 배정할 수 있습니다.

## 주요 함수

- `authenticate_google_api()`: Google API에 대한 인증을 처리하는 함수입니다.
- `create_google_sheet(sheet_title)`: 새로운 Google 스프레드시트를 생성하는 함수입니다.
- `load_data_from_google_sheets(spreadsheet_id, sheet_name)`: Google 스프레드시트에서 데이터를 불러오는 함수입니다.
- `save_data_to_google_sheets(data, spreadsheet_id, sheet_name)`: Google 스프레드시트에 데이터를 저장하는 함수입니다.
- `get_existing_spreadsheet(spreadsheet_title)`: 주어진 제목의 스프레드시트를 검색하여 ID를 반환하는 함수입니다.

## 사용법

1. 애플리케이션 실행 후, 각 임상 시험(COPD 또는 ILD) 중 하나를 선택합니다.
2. 환자를 등록하려면 병원과 환자 번호를 입력하고 'Enroll Patient' 버튼을 클릭합니다.
3. 등록된 환자는 두 그룹 중 하나에 무작위로 배정됩니다.
4. 'Review Assignments' 탭에서 등록된 환자 목록을 확인할 수 있으며, CSV로 다운로드할 수 있습니다.

## 참고 사항

- `token.json` 파일이 존재하지 않으면 Google OAuth 인증을 처음 수행할 때 이 파일이 생성됩니다.
- 무작위 배정은 6명의 환자가 하나의 블록으로 묶여 처리됩니다. (`BLOCK_SIZE`)

## TODO

- 현재 google sheet api를 추가한지 얼마 되지 않아서 내일 다시 시행해볼 것
