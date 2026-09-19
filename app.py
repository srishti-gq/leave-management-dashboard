import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

st.set_page_config(page_title="Leave Management Dashboard", layout="wide")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_ID = "1Yjw5dLapgWWHrVy0zGJ1pBYmJWVu0IKkuhoYOiE5ZtY"
DRIVE_FOLDER_ID = "1MmSrGm3Ml5GNXz6W3pxIGiUANMBhcpF0" 
APPROVER_EMAIL = "gangsrishti213@gmail.com"

if not st.user.is_logged_in:
    st.login()
    st.stop()

current_user_email = st.user.email
current_user_name = st.user.name

is_approver = (current_user_email == APPROVER_EMAIL)

st.sidebar.write(f"Logged in as: {current_user_name} ({current_user_email})")
if st.sidebar.button("Log out"):
    st.logout()  


@st.cache_resource
def get_sheet():
    creds = Credentials.from_service_account_file("secrets/service_account.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).sheet1

@st.cache_resource
def get_drive_service():
    creds = Credentials.from_service_account_file("secrets/service_account.json", scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


def upload_document(uploaded_file):
    drive_service = get_drive_service()

    file_metadata = {"name": uploaded_file.name, "parents": [DRIVE_FOLDER_ID]}
    media = MediaIoBaseUpload(io.BytesIO(uploaded_file.getvalue()), mimetype=uploaded_file.type)

    uploaded = drive_service.files().create(
        body=file_metadata, media_body=media, fields="id", supportsAllDrives=True
    ).execute()
    file_id = uploaded["id"]

    drive_service.permissions().create(
        fileId=file_id, body={"type": "anyone", "role": "reader"}, supportsAllDrives=True
    ).execute()

    file_info = drive_service.files().get(fileId=file_id, fields="webViewLink", supportsAllDrives=True).execute()
    return file_info["webViewLink"]


@st.cache_data(ttl=30)
def load_leave_requests():
    sheet = get_sheet()
    return sheet.get_all_records()


def update_status(request_id, new_status):
    sheet = get_sheet()
    cell = sheet.find(request_id)
    sheet.update_cell(cell.row, 7, new_status)


# --- Sidebar navigation (now functional) ---
st.sidebar.title("📋 Leave Management")
page = st.sidebar.radio("Navigate", ["Dashboard", "Apply for Leave", "My Leave Requests", "Profile"])



if is_approver:
    st.title(f"Hello {current_user_name},")
    st.write("Here's the latest overview of team leave requests.")

    records = load_leave_requests()
    df = pd.DataFrame(records)

    pending_count = (df["Status"] == "Pending").sum()
    approved_count = (df["Status"] == "Approved").sum()
    rejected_count = (df["Status"] == "Rejected").sum()
    total_count = len(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pending", pending_count)
    col2.metric("Approved", approved_count)
    col3.metric("Rejected", rejected_count)
    col4.metric("Total Requests", total_count)

    st.subheader("All Leave Requests")
    st.dataframe(df, use_container_width=True)

    st.subheader("Pending Requests — Action Needed")
    pending_df = df[df["Status"] == "Pending"]

    if pending_df.empty:
        st.write("No pending requests. 🎉")
    else:
        for _, row in pending_df.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(
                    f"**{row['Request ID']}** — {row['Employee Name']} — {row['Leave Type']} "
                    f"({row['From']} to {row['To']}) — _{row['Reason']}_"
                )
                if c2.button("Approve", key=f"approve_{row['Request ID']}"):
                    update_status(row["Request ID"], "Approved")
                    st.cache_data.clear()
                    st.rerun()
                if c3.button("Reject", key=f"reject_{row['Request ID']}"):
                    update_status(row["Request ID"], "Rejected")
                    st.cache_data.clear()
                    st.rerun()



# --- Dashboard page ---
elif page == "Dashboard" and not is_approver:
    st.title(f"Good Morning, {current_user_name}! 👋")
    st.write("Here's a quick overview of your leave requests and status.")

    records = load_leave_requests()
    df = pd.DataFrame(records)

    pending_count = (df["Status"] == "Pending").sum()
    approved_count = (df["Status"] == "Approved").sum()
    rejected_count = (df["Status"] == "Rejected").sum()
    total_count = len(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pending", pending_count)
    col2.metric("Approved", approved_count)
    col3.metric("Rejected", rejected_count)
    col4.metric("Total Requests", total_count)

    st.subheader("My Leave Requests")
    st.dataframe(df, use_container_width=True)

# --- Apply for Leave page ---
elif page == "Apply for Leave":
    st.title("Apply for Leave")

    leave_types = ["Planned Leave", "Sick Leave", "Emergency Leave", "Personal Leave", "Other"]
    leave_type = st.selectbox("Leave Type", leave_types)

    other_description = ""
    if leave_type == "Other":
        other_description = st.text_input("Please describe this leave type (required)")

    with st.form("apply_leave_form"):
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        reason = st.text_area("Reason")
        uploaded_file = st.file_uploader(
            "Attach supporting document (optional)",
            type=["pdf", "png", "jpg", "jpeg", "docx"],
        )
        submitted = st.form_submit_button("Submit")

        if submitted:
            if leave_type == "Other" and not other_description.strip():
                st.error("Please provide a description for 'Other' leave type before submitting.")
            else:
                document_link = ""
                if uploaded_file is not None:
                    try:
                        document_link = upload_document(uploaded_file)
                    except Exception:
                        st.warning("Document upload isn't available on this test account yet (will work once we're on the real company account). Your leave request was still saved without the attachment.")

                sheet = get_sheet()
                existing_rows = sheet.get_all_records()
                new_id = f"LR{len(existing_rows) + 1:03d}"

                sheet.append_row([
                    new_id,
                    current_user_name,  # placeholder until real login is built in Milestone 5
                    leave_type,
                    str(start_date),
                    str(end_date),
                    reason,
                    "Pending",
                    other_description,
                ])

                st.success(f"Leave request {new_id} submitted successfully!")
                st.cache_data.clear()

else:
    st.title(page)
    st.write("This page isn't built yet — coming in a later milestone.")