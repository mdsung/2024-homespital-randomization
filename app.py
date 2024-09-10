import os

import numpy as np
import pandas as pd
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from icecream import ic

# Set seed for reproducibility
np.random.seed(2024)

# Constants
ARMS = ["Arm 1", "Arm 2"]
INSTITUTES = ["세브란스병원", "일산병원", "아주대학교병원"]
TRIALS = ["Trial 1 (COPD)", "Trial 2 (ILD)"]
BLOCK_SIZE = 6

# Define Google API scopes (updated to include Drive access)
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# File paths for storing credentials
TOKEN_PATH = "token.json"
CREDENTIALS_PATH = "credentials.json"

# Spreadsheet range
DEFAULT_SHEET_RANGE = "A1:E"


def authenticate_google_api():
    """Authenticate the user and return the credentials."""
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())

    return creds


def create_google_sheet(sheet_title):
    """Create a new Google Spreadsheet and return its ID and first sheet name."""
    creds = authenticate_google_api()
    try:
        service = build("sheets", "v4", credentials=creds)
        sheet_body = {"properties": {"title": sheet_title}}
        spreadsheet = (
            service.spreadsheets()
            .create(body=sheet_body, fields="spreadsheetId,sheets")
            .execute()
        )
        sheet_id = spreadsheet.get("spreadsheetId")
        first_sheet_name = spreadsheet["sheets"][0]["properties"][
            "title"
        ]  # Get the name of the first sheet
        ic(sheet_title, sheet_id, first_sheet_name)
        return sheet_id, first_sheet_name
    except HttpError as err:
        print(f"An error from create_google_sheet occurred: {err}")
        return None, None


def load_data_from_google_sheets(spreadsheet_id, sheet_name):
    """Loads data from the given Google Spreadsheet."""
    creds = authenticate_google_api()
    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!{DEFAULT_SHEET_RANGE}",
            )
            .execute()
        )
        values = result.get("values", [])

        if not values:
            return pd.DataFrame(
                columns=["Institute", "Patient Number", "Block", "Random Number", "Arm"]
            )
        else:
            return pd.DataFrame(values[1:], columns=values[0])
    except HttpError as err:
        print(f"An error from load_data_from_google_sheets occurred: {err}")
        return pd.DataFrame(
            columns=["Institute", "Patient Number", "Block", "Random Number", "Arm"]
        )


def save_data_to_google_sheets(data, spreadsheet_id, sheet_name):
    """Saves data to the given Google Spreadsheet."""
    creds = authenticate_google_api()
    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        ic(sheet)
        # Prepare the data to be written
        values = [data.columns.values.tolist()] + data.values.tolist()

        # Write new data, ensuring the range is valid
        result = (
            sheet.values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!{DEFAULT_SHEET_RANGE}",
                valueInputOption="RAW",
                body={"values": values},
            )
            .execute()
        )
    except HttpError as err:
        print(f"An error from save_data_to_google_sheets occurred: {err}")


def get_existing_spreadsheet(spreadsheet_title):
    """Search for an existing non-trashed spreadsheet by title using Google Drive API."""
    creds = authenticate_google_api()
    try:
        service = build("drive", "v3", credentials=creds)
        # Search for the spreadsheet by title and ensure it is not trashed
        results = (
            service.files()
            .list(
                q=f"name='{spreadsheet_title}' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false",
                spaces="drive",
                fields="files(id, name)",
            )
            .execute()
        )
        ic(results)
        items = results.get("files", [])
        if items:
            return items[0]["id"]  # Return the spreadsheet ID if found
        return None  # Return None if no file is found
    except HttpError as err:
        print(f"An error occurred: {err}")
        return None


# Check or create the spreadsheet for both trials
if "SPREADSHEET_ID_TRIAL_1" not in st.session_state:
    st.session_state.SPREADSHEET_ID_TRIAL_1 = get_existing_spreadsheet(
        "Enrollment Data Trial 1"
    )
    if not st.session_state.SPREADSHEET_ID_TRIAL_1:
        st.session_state.SPREADSHEET_ID_TRIAL_1, st.session_state.SHEET_NAME_TRIAL_1 = (
            create_google_sheet("Enrollment Data Trial 1")
        )
    else:
        st.session_state.SHEET_NAME_TRIAL_1 = "시트1"  # You can change this to dynamically retrieve the sheet name if needed.

if "SPREADSHEET_ID_TRIAL_2" not in st.session_state:
    st.session_state.SPREADSHEET_ID_TRIAL_2 = get_existing_spreadsheet(
        "Enrollment Data Trial 2"
    )
    if not st.session_state.SPREADSHEET_ID_TRIAL_2:
        st.session_state.SPREADSHEET_ID_TRIAL_2, st.session_state.SHEET_NAME_TRIAL_2 = (
            create_google_sheet("Enrollment Data Trial 2")
        )
    else:
        st.session_state.SHEET_NAME_TRIAL_2 = "시트1"  # You can change this to dynamically retrieve the sheet name if needed.

# Load the data into the session state
if "enrollment_data_trial_1" not in st.session_state:
    st.session_state.enrollment_data_trial_1 = load_data_from_google_sheets(
        st.session_state.SPREADSHEET_ID_TRIAL_1, st.session_state.SHEET_NAME_TRIAL_1
    )

if "enrollment_data_trial_2" not in st.session_state:
    st.session_state.enrollment_data_trial_2 = load_data_from_google_sheets(
        st.session_state.SPREADSHEET_ID_TRIAL_2, st.session_state.SHEET_NAME_TRIAL_2
    )

# Title and instructions
st.title("Patient Enrollment and Randomization")

# Add a selectbox for trial selection
trial_choice = st.selectbox("Select Trial", TRIALS)

# Set the correct spreadsheet ID and session state based on the selected trial
if trial_choice == TRIALS[0]:
    spreadsheet_id = st.session_state.SPREADSHEET_ID_TRIAL_1
    sheet_name = st.session_state.SHEET_NAME_TRIAL_1
    enrollment_data = "enrollment_data_trial_1"
elif trial_choice == TRIALS[1]:
    spreadsheet_id = st.session_state.SPREADSHEET_ID_TRIAL_2
    sheet_name = st.session_state.SHEET_NAME_TRIAL_2
    enrollment_data = "enrollment_data_trial_2"

# Create two tabs: one for enrollment, one for reviewing assigned patients
tab1, tab2 = st.tabs(["Enroll Patients", "Review Assignments"])

# --- TAB 1: Enrollment ---
with tab1:
    st.write(f"Enrolling patients for **{trial_choice}**.")
    st.write(
        "Use this tab to enroll patients into clinical trial arms. Please provide the institute and the patient number."
    )

    # Form for user input
    with st.form("enrollment_form"):
        institute = st.selectbox("Select Institute", options=INSTITUTES)
        patient_number = st.text_input("Patient Number")
        submit_button = st.form_submit_button("Enroll Patient")

    # Handle form submission
    if submit_button:
        if not patient_number:
            st.error("Please enter a valid patient number.")
        else:
            # Create a new row for the new patient
            rand_num = np.random.uniform(0, 1)
            block = (len(st.session_state[enrollment_data]) // BLOCK_SIZE) + 1
            arm = ARMS[len(st.session_state[enrollment_data]) % len(ARMS)]

            new_patient = {
                "Institute": institute,
                "Patient Number": patient_number,
                "Block": block,
                "Random Number": rand_num,
                "Arm": arm,
            }

            # Add the new patient to the session state DataFrame
            st.session_state[enrollment_data] = pd.concat(
                [st.session_state[enrollment_data], pd.DataFrame([new_patient])],
                ignore_index=True,
            )

            # Save the updated data to Google Sheets
            save_data_to_google_sheets(
                st.session_state[enrollment_data], spreadsheet_id, sheet_name
            )

            st.success(
                f"Patient {patient_number} from {institute} has been enrolled in {trial_choice} and assigned to {arm}."
            )

# --- TAB 2: Review Assignments ---
with tab2:
    st.write(f"### Enrolled Patients and Their Assignments for {trial_choice}")

    if len(st.session_state[enrollment_data]) > 0:
        # Display the current list of enrolled patients for the selected trial
        st.dataframe(st.session_state[enrollment_data])

        # Option to download the enrollment data as a CSV file
        csv = st.session_state[enrollment_data].to_csv(index=False)
        st.download_button(
            label=f"Download CSV for {trial_choice}",
            data=csv,
            file_name=f"enrolled_patients_{trial_choice}.csv",
            mime="text/csv",
        )
    else:
        st.write(f"No patients have been enrolled in {trial_choice} yet.")
