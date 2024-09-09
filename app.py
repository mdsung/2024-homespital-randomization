import os

import numpy as np
import pandas as pd
import streamlit as st

np.random.seed(2024)
ARMS = ["Arm 1", "Arm 2"]
INSTITUTES = ["세브란스병원", "일산병원", "아주대학교병원"]
BLOCK_SIZE = 6

# File path for saving the data
file_path = "enrollment_data.csv"


# Function to load data from CSV
def load_data(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame(
            columns=["Institute", "Patient Number", "Block", "Random Number", "Arm"]
        )


# Function to save data to CSV
def save_data(data, file_path):
    data.to_csv(file_path, index=False)


# Initialize enrollment data storage (load from file if exists)
if "enrollment_data" not in st.session_state:
    st.session_state.enrollment_data = load_data(file_path)


# Title and instructions
st.title("Patient Enrollment and Randomization")

# Create two tabs: one for enrollment, one for reviewing assigned patients
tab1, tab2 = st.tabs(["Enroll Patients", "Review Assignments"])

# --- TAB 1: Enrollment ---
with tab1:
    st.write(
        """
    Use this tab to enroll patients into clinical trial arms. Please provide the institute and the patient number.
    """
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
            block = (len(st.session_state.enrollment_data) // BLOCK_SIZE) + 1
            arm = ARMS[len(st.session_state.enrollment_data) % len(ARMS)]

            new_patient = {
                "Institute": institute,
                "Patient Number": patient_number,
                "Block": block,
                "Random Number": rand_num,
                "Arm": arm,
            }

            # Add the new patient to the session state DataFrame
            st.session_state.enrollment_data = pd.concat(
                [st.session_state.enrollment_data, pd.DataFrame([new_patient])],
                ignore_index=True,
            )

            # Save the updated data to the CSV file
            save_data(st.session_state.enrollment_data, file_path)

            st.success(
                f"Patient {patient_number} from {institute} has been enrolled and assigned to {arm}."
            )

# --- TAB 2: Review Assignments ---
with tab2:
    st.write("### Enrolled Patients and Their Assignments")

    if len(st.session_state.enrollment_data) > 0:
        # Display the current list of enrolled patients
        st.dataframe(st.session_state.enrollment_data)

        # Option to download the enrollment data as a CSV file
        csv = st.session_state.enrollment_data.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="enrolled_patients.csv",
            mime="text/csv",
        )
    else:
        st.write("No patients have been enrolled yet.")
