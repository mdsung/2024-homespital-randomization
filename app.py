from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

# Set seed for reproducibility
np.random.seed(2024)

# Constants
ARMS = ["Arm 1", "Arm 2"]
INSTITUTES = ["세브란스병원", "일산병원", "아주대학교병원"]
TRIALS = ["Trial 1 (COPD)", "Trial 2 (ILD)"]
BLOCK_SIZE = 6

# Create a data folder if it doesn't exist
DATA_FOLDER = "data"
Path(DATA_FOLDER).mkdir(parents=True, exist_ok=True)

# File paths for saving data for both trials
FILE_PATH_TRIAL_1 = Path(DATA_FOLDER, "enrollment_data_trial_1.csv")
FILE_PATH_TRIAL_2 = Path(DATA_FOLDER, "enrollment_data_trial_2.csv")


# Function to load data from CSV
def load_data(file_path):
    if Path(file_path).exists():
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame(
            columns=["Institute", "Patient Number", "Block", "Random Number", "Arm"]
        )


# Function to save data to CSV
def save_data(data, file_path):
    data.to_csv(file_path, index=False)


# Initialize enrollment data storage for both trials
if "enrollment_data_trial_1" not in st.session_state:
    st.session_state.enrollment_data_trial_1 = load_data(FILE_PATH_TRIAL_1)

if "enrollment_data_trial_2" not in st.session_state:
    st.session_state.enrollment_data_trial_2 = load_data(FILE_PATH_TRIAL_2)

# Title and instructions
st.title("Patient Enrollment and Randomization")

# Add a selectbox for trial selection
trial_choice = st.selectbox("Select Trial", TRIALS)

# Set the correct file path and session state based on the selected trial
if trial_choice == TRIALS[0]:
    file_path = FILE_PATH_TRIAL_1
    enrollment_data = "enrollment_data_trial_1"
elif trial_choice == TRIALS[1]:
    file_path = FILE_PATH_TRIAL_2
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

            # Save the updated data to the corresponding CSV file
            save_data(st.session_state[enrollment_data], file_path)

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
