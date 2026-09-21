import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import requests
from datetime import date
import altair as alt

st.set_page_config(page_title="Leave Management Dashboard", layout="wide")

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #0F1A3D;
    }
    [data-testid="stSidebar"] * {
        color: #F5F7FA !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label {
        display: block;
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 4px;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background-color: #3B7DFF;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label div:first-child {
        display: none;
    }
    [data-testid="stSidebarContent"] {
        display: flex;
        flex-direction: column;
        height: 100vh;
    }
    [data-testid="stSidebarContent"] > div:last-child {
        margin-top: auto;
    }
    [data-testid="stDataFrame"] {
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_ID = "1Yjw5dLapgWWHrVy0zGJ1pBYmJWVu0IKkuhoYOiE5ZtY"
DRIVE_FOLDER_ID = "1MmSrGm3Ml5GNXz6W3pxIGiUANMBhcpF0" 
APPROVER_EMAIL = "gangsrishti213@gmail.com"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyZya5u0JvzvzzJOeId7VXs02zDCYu5POQoZ--x-BkkwkW4etc9Ce25rS485njaeB6i/exec"
APPROVAL_TOKEN = st.secrets["general"]["approval_token"]

if not st.user.is_logged_in:
    st.login()
    st.stop()

current_user_email = st.user.email
current_user_name = st.user.name

is_approver = (current_user_email == APPROVER_EMAIL)

def render_top_bar():
    profile_picture = st.user.get("picture")
    role_label = "Approver" if is_approver else "Employee"
    left, avatar_col, name_col = st.columns([6, 1, 2])
    with avatar_col:
        if profile_picture:
            st.image(profile_picture, width=36)
    with name_col:
        st.write(f"**{current_user_name}**")
        st.caption(role_label)

render_top_bar()


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


@st.dialog("Review Leave Request")
def review_request_dialog(row):
    st.write(f"**Request ID:** {row['Request ID']}")
    st.write(f"**Employee:** {row['Employee Name']}")
    st.write(f"**Leave Type:** {row['Leave Type']}")
    st.write(f"**Dates:** {row['From']} to {row['To']}")
    st.write(f"**Reason:** {row['Reason']}")
    st.write(f"**Current Status:** {row['Status']}")

    col1, col2 = st.columns(2)
    if col1.button("Approve", use_container_width=True):
        update_status(row["Request ID"], "Approved")
        st.cache_data.clear()
        st.rerun()
    if col2.button("Reject", use_container_width=True):
        update_status(row["Request ID"], "Rejected")
        st.cache_data.clear()
        st.rerun()

@st.dialog("Request Details")
def view_request_details_dialog(row):
    st.write(f"**Request ID:** {row['Request ID']}")
    st.write(f"**Leave Type:** {row['Leave Type']}")
    if row["Leave Type"] == "Other" and row.get("Other Description"):
        st.write(f"**Description:** {row['Other Description']}")
    st.write(f"**From:** {row['From']}  **To:** {row['To']}")
    st.write(f"**Reason:** {row['Reason']}")
    st.write(f"**Status:** {row['Status']}")
    st.write(f"**Applied On:** {row['Applied On']}")

    if row.get("Document Link"):
        st.markdown(f"[View Attached Document]({row['Document Link']})")
    else:
        st.write("**Document:** None attached")

    if row["Status"] == "Pending":
        st.divider()
        if st.button("Withdraw Request", type="primary"):
            update_status(row["Request ID"], "Withdrawn")
            st.cache_data.clear()
            st.rerun()


def notify_ranjeet(request_id, employee_name, leave_type, from_date, to_date, reason):
    approve_link = f"{APPS_SCRIPT_URL}?action=approve&requestId={request_id}&token={APPROVAL_TOKEN}"
    reject_link = f"{APPS_SCRIPT_URL}?action=reject&requestId={request_id}&token={APPROVAL_TOKEN}"

    payload = {
        "requestId": request_id,
        "employeeName": employee_name,
        "leaveType": leave_type,
        "fromDate": from_date,
        "toDate": to_date,
        "reason": reason,
        "approveLink": approve_link,
        "rejectLink": reject_link,
    }
    try:
        requests.post(APPS_SCRIPT_URL, json=payload, timeout=10)
    except Exception:
        st.warning("Could not send the notification email, but your leave request was saved.")

def render_stat_card(icon, label, value, subtitle, bg_color, icon_color):
    st.markdown(
        f"""
        <div style="background:{bg_color}; border:1px solid rgba(0,0,0,0.06); border-radius:12px; padding:16px 20px; min-height:110px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:600; color:#333;">{label}</span>
                <div style="background:{icon_color}; color:white; width:32px; height:32px; min-width:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:16px; flex-shrink:0;">{icon}</div>
            </div>
            <div style="font-size:26px; font-weight:bold; margin-top:8px; color:#111;">{value}</div>
            <div style="font-size:12px; color:#777; margin-top:4px;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def style_status(val):
    colors = {
        "Pending": "background-color:#FFF3D6; color:#B7791F; font-weight:600;",
        "Approved": "background-color:#DCF5E5; color:#1E7E34; font-weight:600;",
        "Rejected": "background-color:#FDE3E3; color:#C0392B; font-weight:600;",
        "Withdrawn": "background-color:#E5E7EB; color:#4B5563; font-weight:600;",
    }
    return colors.get(val, "")


# --- Sidebar navigation (now functional) ---
st.sidebar.title("📋 Leave Management")

if is_approver:
    nav_options = ["Dashboard", "All Leave Requests", "Team Overview", "Profile"]
else:
    nav_options = ["Dashboard", "Apply for Leave", "My Leave Requests", "Profile"]

page = st.sidebar.radio("Navigate", nav_options)

st.sidebar.divider()
with st.sidebar.container():
    st.write(f"**{current_user_name}**")
    st.caption(current_user_email)
    if st.button("Log out"):
        st.logout()



if is_approver and page == "Dashboard":
    st.title(f"Hello {current_user_name},")
    st.write("Here's the latest overview of team leave requests.")

    records = load_leave_requests()
    df = pd.DataFrame(records)

    pending_count = (df["Status"] == "Pending").sum()
    approved_count = (df["Status"] == "Approved").sum()
    rejected_count = (df["Status"] == "Rejected").sum()
    total_count = len(df)


    main_col, side_col = st.columns([3, 2])

    with main_col:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_stat_card("🕐", "Pending", pending_count, "Request awaiting approval", "#FFF3D6", "#F5A623")
        with col2:
            render_stat_card("✅", "Approved", approved_count, "Successfully approved", "#DCF5E5", "#34A853")
        with col3:
            render_stat_card("❌", "Rejected", rejected_count, "No rejected requests", "#FDE3E3", "#EA4335")
        with col4:
            render_stat_card("📅", "Total Requests", total_count, "All time requests", "#DCEAFB", "#4285F4")

    with side_col:
        with st.container(border=True):
            st.write("**Leave Overview**")
            status_counts = pd.DataFrame({
                "Status": ["Approved", "Pending", "Rejected"],
                "Count": [approved_count, pending_count, rejected_count],
            })
            base = alt.Chart(status_counts).encode(theta=alt.Theta("Count", stack=True))
            arc = base.mark_arc(innerRadius=50, outerRadius=80).encode(
                color=alt.Color(
                    "Status",
                    scale=alt.Scale(domain=["Approved", "Pending", "Rejected"], range=["#2e7d32", "#f9a825", "#c62828"]),
                ),
                tooltip=["Status", "Count"],
            )
            center_text = alt.Chart(pd.DataFrame({"label": [str(total_count)]})).mark_text(size=24, fontWeight="bold", color="#111").encode(text="label")
            st.altair_chart(arc + center_text, use_container_width=True)
            st.caption(f"Total Requests: {total_count}")

    with st.container(border=True):
        st.subheader("All Leave Requests")
        st.dataframe(df.style.map(style_status, subset=["Status"]), use_container_width=True)


elif is_approver and page == "All Leave Requests":
    st.title("All Leave Requests")

    records = load_leave_requests()
    df = pd.DataFrame(records)

    col1, col2, col3 = st.columns(3)
    status_options = ["All"] + sorted(df["Status"].unique().tolist())
    status_filter = col1.selectbox("Status", status_options)

    leave_type_options = ["All"] + sorted(df["Leave Type"].unique().tolist())
    leave_type_filter = col2.selectbox("Leave Type", leave_type_options)

    employee_options = ["All"] + sorted(df["Employee Name"].unique().tolist())
    employee_filter = col3.selectbox("Employee", employee_options)

    filtered = df.copy()
    if status_filter != "All":
        filtered = filtered[filtered["Status"] == status_filter]
    if leave_type_filter != "All":
        filtered = filtered[filtered["Leave Type"] == leave_type_filter]
    if employee_filter != "All":
        filtered = filtered[filtered["Employee Name"] == employee_filter]

    st.dataframe(
    filtered[["Request ID", "Employee Name", "Leave Type", "From", "To", "Reason", "Status", "Applied On", "Document Link"]].style.map(style_status, subset=["Status"]),
    use_container_width=True,
    column_config={"Document Link": st.column_config.LinkColumn("Document", display_text="Open")},
)

    st.subheader("Manage Requests")

    if filtered.empty:
        st.write("No requests match these filters.")
    else:
        request_ids = filtered["Request ID"].tolist()
        selected_id = st.selectbox("Select a request to review", request_ids)

        if st.button("Review Selected Request"):
            selected_row = filtered[filtered["Request ID"] == selected_id].iloc[0]
            review_request_dialog(selected_row)


elif is_approver and page == "Team Overview":
    st.title("Team Overview")
    st.write("A quick look at leave activity across the team.")

    records = load_leave_requests()
    df = pd.DataFrame(records)

    summary = df.groupby("Employee Name").agg(
        total_requests=("Request ID", "count"),
        pending=("Status", lambda s: (s == "Pending").sum()),
        approved=("Status", lambda s: (s == "Approved").sum()),
        rejected=("Status", lambda s: (s == "Rejected").sum()),
    ).reset_index()

    summary = summary.rename(columns={
        "total_requests": "Total Requests",
        "pending": "Pending",
        "approved": "Approved",
        "rejected": "Rejected",
    })

    st.subheader("Requests per Employee")
    st.dataframe(summary, use_container_width=True)

    st.subheader("Total Requests by Employee")
    bar_chart = alt.Chart(summary).mark_bar().encode(
        x=alt.X("Employee Name", sort="-y"),
        y="Total Requests",
        tooltip=["Employee Name", "Total Requests"],
    )
    st.altair_chart(bar_chart, use_container_width=True)


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
    with col1:
        render_stat_card("🕐", "Pending", pending_count, "Request awaiting approval", "#FFF3D6", "#F5A623")
    with col2:
        render_stat_card("✅", "Approved", approved_count, "Successfully approved", "#DCF5E5", "#34A853")
    with col3:
        render_stat_card("❌", "Rejected", rejected_count, "No rejected requests", "#FDE3E3", "#EA4335")
    with col4:
        render_stat_card("📅", "Total Requests", total_count, "All time requests", "#DCEAFB", "#4285F4")

    st.subheader("My Leave Requests")
    st.dataframe(df.style.map(style_status, subset=["Status"]), use_container_width=True)


elif page == "My Leave Requests":
    st.title("My Leave Requests")

    records = load_leave_requests()
    df = pd.DataFrame(records)
    my_requests = df[df["Employee Name"] == current_user_name].copy()

    col1, col2, col3 = st.columns(3)
    status_options = ["All"] + sorted(my_requests["Status"].unique().tolist())
    status_filter = col1.selectbox("Status", status_options)

    leave_type_options = ["All"] + sorted(my_requests["Leave Type"].unique().tolist())
    leave_type_filter = col2.selectbox("Leave Type", leave_type_options)

    date_range = col3.date_input("Applied Date Range", value=())

    filtered = my_requests.copy()
    if status_filter != "All":
        filtered = filtered[filtered["Status"] == status_filter]
    if leave_type_filter != "All":
        filtered = filtered[filtered["Leave Type"] == leave_type_filter]
    if len(date_range) == 2:
        start_d, end_d = date_range
        filtered = filtered[
            (pd.to_datetime(filtered["Applied On"]) >= pd.to_datetime(start_d))
            & (pd.to_datetime(filtered["Applied On"]) <= pd.to_datetime(end_d))
        ]

    st.dataframe(
    filtered[["Request ID", "Employee Name", "Leave Type", "From", "To", "Reason", "Status", "Applied On", "Document Link"]].style.map(style_status, subset=["Status"]),
    use_container_width=True,
    column_config={"Document Link": st.column_config.LinkColumn("Document", display_text="Open")},
)

    if filtered.empty:
        st.write("No requests match these filters.")
    else:
        selected_id = st.selectbox("Select a request to view details", filtered["Request ID"].tolist())
        if st.button("View Details"):
            selected_row = filtered[filtered["Request ID"] == selected_id].iloc[0]
            view_request_details_dialog(selected_row)


elif page == "Profile":
    st.title("My Profile")

    profile_picture = st.user.get("picture")

    col1, col2 = st.columns([1, 3])
    with col1:
        if profile_picture:
            st.image(profile_picture, width=120)
    with col2:
        st.subheader(current_user_name)
        st.write(f"**Email:** {current_user_email}")
        st.write(f"**Role:** {'Approver' if is_approver else 'Employee'}")
        st.write("**Team:** Credit & Underwriting")



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
                    current_user_name,
                    leave_type,
                    str(start_date),
                    str(end_date),
                    reason,
                    "Pending",
                    other_description,
                    document_link,
                    str(date.today()),
                ])

                notify_ranjeet(new_id, current_user_name, leave_type, str(start_date), str(end_date), reason)

                st.success(f"Leave request {new_id} submitted successfully!")
                st.cache_data.clear()

else:
    st.title(page)
    st.write("This page isn't built yet — coming in a later milestone.")