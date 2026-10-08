import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import requests
from datetime import date
import calendar
import altair as alt

st.set_page_config(page_title="Leave Management Dashboard", layout="wide")

st.markdown(
    """
    <style>
        .block-container {
        padding-top: 3rem !important;
    }
    [data-testid="stSidebar"] {
        background-color: #0F1A3D;
    }
    [data-testid="stSidebar"] * {
        color: #F5F7FA !important;
    }
    [data-testid="stSidebarContent"] {
    display: flex;
    flex-direction: column;
    height: 100%;
}
[class*="st-key-top_bar_container"] {
    padding: 8px 16px !important;
}
[data-testid="stSidebarUserContent"] {
    width: 100%;
}

.sidebar-account-spacer {
    flex: 1;
    min-height: 40px;
}

.sidebar-account {
    width: 100%;
    overflow: hidden;
}

.sidebar-account-name {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
    width: 100%;
}

[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > div {
    min-width: 0;
}

[data-testid="stSidebar"] button {
    flex-shrink: 0;
}
    
    [data-testid="stSidebar"] [role="radiogroup"] {
    gap: 4px !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label {
        display: block;
        padding: 10px 14px;
        border-radius: 8px;
        margin: 0 !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background-color: #3B7DFF;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label div:first-child {
        display: none;
    }
    [data-testid="stSidebar"] button {
        background-color: transparent;
        border: 1px solid #F5F7FA;
        color: #F5F7FA !important;
    }
    [data-testid="stSidebar"] button:hover {
        background-color: rgba(245,247,250,0.15);
        border-color: #F5F7FA;
    }
    [data-testid="stSidebar"] a {
        text-decoration: none !important;
    }
    [data-testid="stDataFrame"] {
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 1px 2px rgba(16,24,40,0.04), 0 2px 6px rgba(16,24,40,0.06);
        padding: 0px;
        background: white;
    }

    /* Bottom account section */
.sidebar-account-row {
    width: 100%;
}

/* Avatar */
.sidebar-avatar {
    width: 36px;
    height: 36px;
    min-width: 36px;
    border-radius: 50%;
    background: #3B7DFF;
    color: white !important;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
}

/* User information */
.sidebar-user-info {
    min-width: 0;
    width: 100%;
    overflow: hidden;
    line-height: 1.3;
}

/* Name truncates instead of pushing the gear */
.sidebar-user-name {
    width: 100%;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 14px;
    font-weight: 700;
}

/* Employee / Approver */
.sidebar-user-role {
    font-size: 12px;
    color: #AAB4C8 !important;
    white-space: nowrap;
}

/* Gear button */
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] button {
    width: 36px !important;
    min-width: 36px !important;
    height: 36px !important;
    padding: 0 !important;
    flex-shrink: 0 !important;
}

/* Prevent sidebar columns from overflowing */
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > div {
    min-width: 0 !important;
}

[data-testid="stTextInput"] input {
    border-radius: 10px;
    border: 1px solid #E2E8F0;
}

.topbar-profile {
    display: flex;
    align-items: center;
    gap: 10px;
    justify-content: flex-end;
}
.topbar-name {
    font-size: 14px;
    font-weight: 700;
    color: #1A1A2E;
    line-height: 1.3;
}
.topbar-role {
    font-size: 12px;
    color: #6B7280;
    line-height: 1.3;
}
[class*="_next_wrap"] {
    display: flex;
    justify-content: flex-end;
}
[class*="st-key-leave_type_chart_center"] {
    display: flex;
    justify-content: center;
}
[class*="st-key-table_wide_"] {
    padding-bottom: 8px !important;
    margin-bottom: 0 !important;
}
[class*="st-key-calendar_box"] {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 12px 16px 16px 16px;
    margin: 8px 0 20px 0;
    width: 100%;
}
[class*="st-key-calendar_box"] button {
    border: none !important;
    background: transparent !important;
    font-size: 16px !important;
    padding: 0 !important;
    height: 26px !important;
    min-height: 26px !important;
}
.cal-month {
    font-size: 13px;
    font-weight: 700;
    text-align: center;
    line-height: 26px;
}
.cal-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
    text-align: center;
    margin-top: 8px;
}
.cal-weekday {
    font-size: 11px;
    color: #AAB4C8;
    font-weight: 600;
    padding-bottom: 4px;
}
.cal-day {
    font-size: 12px;
    padding: 5px 0;
    border-radius: 50%;
}
.cal-day-today {
    background: #3B7DFF;
    color: white !important;
    font-weight: 700;
}
.cal-day-empty {
    visibility: hidden;
}
[data-testid="stSidebar"] {
    border-radius: 0 10px 10px 0;
    box-shadow: 4px 0 20px rgba(0,0,0,0.15);
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px !important;
    border-color: #E5E7EB !important;
    box-shadow: 0 1px 2px rgba(16,24,40,0.04), 0 1px 3px rgba(16,24,40,0.06);
}
h1, h2, h3 {
    color: #111827;
    letter-spacing: -0.01em;
}
    </style>
    """,
    unsafe_allow_html=True,
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_ID = "1mfb3VL-6bHoD9SPQdXhoyFl5lmBY5LwLxrosbYdE_6o"
DRIVE_FOLDER_ID = "0AGQ8hSSgFX9SUk9PVA" 
APPROVER_EMAIL = "ranjeet@grayquest.com"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbx5QJ04f-0IVWZNDIT21Aj8S92Z5Wip-PNIxHzphdwMiDfe4OVzue8a0h_y7PO9Cw3e/exec"
APPROVAL_TOKEN = st.secrets["general"]["approval_token"]

if not st.user.is_logged_in:
    st.login()
    st.stop()

current_user_email = st.user.email
current_user_name = st.user.name

is_approver = (current_user_email == APPROVER_EMAIL)

def render_top_bar():
    role_label = "Approver" if is_approver else "Employee"
    search_placeholder = (
        "Search by employee name, ID or leave type..." if is_approver
        else "Search anything..."
    )
    initial = current_user_name[0].upper() if current_user_name else "?"

    with st.container(border=True, key="top_bar_container"):
        search_col, spacer_col, profile_col = st.columns([4, 4, 2.6])

        with search_col:
            st.text_input(
                "Search",
                placeholder=search_placeholder,
                label_visibility="collapsed",
                key="top_bar_search",
            )

        with profile_col:
            st.markdown(
                f"""
                <div class="topbar-profile">
                    <div class="sidebar-avatar">{initial}</div>
                    <div>
                        <div class="topbar-name">{current_user_name}</div>
                        <div class="topbar-role">{role_label}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

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
    media = MediaIoBaseUpload(
        io.BytesIO(uploaded_file.getvalue()), mimetype=uploaded_file.type, resumable=True
    )

    uploaded = drive_service.files().create(
        body=file_metadata, media_body=media, fields="id", supportsAllDrives=True
    ).execute(num_retries=3)
    file_id = uploaded["id"]

    drive_service.permissions().create(
        fileId=file_id, body={"type": "anyone", "role": "reader"}, supportsAllDrives=True
    ).execute(num_retries=3)

    file_info = drive_service.files().get(
        fileId=file_id, fields="webViewLink", supportsAllDrives=True
    ).execute(num_retries=3)
    return file_info["webViewLink"]


@st.cache_data(ttl=30)
def load_leave_requests():
    sheet = get_sheet()
    return sheet.get_all_records()

@st.cache_resource
def get_employees_sheet():
    creds = Credentials.from_service_account_file("secrets/service_account.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).worksheet("Employees")

@st.cache_data(ttl=30)
def load_employees():
    sheet = get_employees_sheet()
    return sheet.get_all_records()

EMPLOYEE_COLUMNS = ["Employee Name", "Email", "Active"]

def employees_to_df(records):
    if not records:
        return pd.DataFrame(columns=EMPLOYEE_COLUMNS)
    return pd.DataFrame(records)

def register_employee_if_new(name, email):
    if not email:
        return
    sheet = get_employees_sheet()
    records = sheet.get_all_records()
    for r in records:
        if str(r.get("Email", "")).strip().lower() == email.strip().lower():
            return
    sheet.append_row([name, email, "TRUE"])
    st.cache_data.clear()

def deactivate_employee(email):
    sheet = get_employees_sheet()
    records = sheet.get_all_records()
    for idx, r in enumerate(records, start=2):
        if str(r.get("Email", "")).strip().lower() == email.strip().lower():
            sheet.update_cell(idx, 3, "FALSE")
            break
    st.cache_data.clear()

if "employee_registered" not in st.session_state:
    register_employee_if_new(current_user_name, current_user_email)
    st.session_state.employee_registered = True

LEAVE_COLUMNS = [
    "Request ID", "Employee Name", "Leave Type", "From", "To",
    "Reason", "Status", "Other Description", "Document Link", "Applied On",
]

def records_to_df(records):
    if not records:
        return pd.DataFrame(columns=LEAVE_COLUMNS)
    return pd.DataFrame(records)


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
    except Exception as e:
        st.warning(f"Could not send the notification email, but your leave request was saved. (Debug: {e})")

def render_stat_card(icon, label, value, subtitle, bg_color, icon_color, size="normal"):
    padding = "20px 24px" if size == "large" else "16px 20px"
    card_height = "180px" if size == "large" else "156px"
    st.markdown(
        f"""
        <div style="background:#FFFFFF; border:1px solid rgba(16,24,40,0.04); border-radius:12px; padding:{padding}; height:{card_height}; box-sizing:border-box; margin-bottom:32px; box-shadow:0 0 16px rgba(16,24,40,0.12); text-align:left;">
            <div style="font-size:16px; font-weight:700; color:{icon_color}; text-transform:uppercase; letter-spacing:0.04em;">{label}</div>
            <div style="font-size:40px; font-weight:800; margin-top:10px; color:{icon_color}; letter-spacing:-0.02em;">{value}</div>
            <div style="font-size:13px; color:#6B7280; margin-top:6px;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def style_status(val):
    colors = {
        "Pending": "background-color:#FEF6E7; color:#B45309; font-weight:600;",
        "Approved": "background-color:#ECFDF5; color:#047857; font-weight:600;",
        "Rejected": "background-color:#FEF2F2; color:#B91C1C; font-weight:600;",
        "Withdrawn": "background-color:#F3F4F6; color:#4B5563; font-weight:600;",
    }
    return colors.get(val, "")

def filter_by_search(data, search_text, columns):
    if not search_text:
        return data
    mask = pd.Series(False, index=data.index)
    for col in columns:
        if col in data.columns:
            mask = mask | data[col].astype(str).str.contains(search_text, case=False, na=False)
    return data[mask]

def render_paginated_table(data, key_prefix, column_config=None, page_size=20):
    page_key = f"{key_prefix}_page"
    if page_key not in st.session_state:
        st.session_state[page_key] = 1

    total_rows = len(data)
    total_pages = max(1, -(-total_rows // page_size))

    if st.session_state[page_key] > total_pages:
        st.session_state[page_key] = total_pages
    if st.session_state[page_key] < 1:
        st.session_state[page_key] = 1

    current_page = st.session_state[page_key]
    start = (current_page - 1) * page_size
    end = start + page_size
    page_data = data.iloc[start:end]

    if "Status" in page_data.columns:
        display_data = page_data.style.map(style_status, subset=["Status"])
    else:
        display_data = page_data

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True,
        column_config=column_config or {},
    )

    prev_col, mid_col, next_col = st.columns([1, 11, 1])
    with prev_col:
        if st.button("‹ Prev", key=f"{key_prefix}_prev", disabled=(current_page <= 1)):
            st.session_state[page_key] -= 1
            st.rerun()
    with mid_col:
        st.markdown(
            f"<div style='text-align:center; padding-top:8px; color:#6B7280; font-size:13px; white-space:nowrap;'>Page {current_page} of {total_pages}</div>",
            unsafe_allow_html=True,
        )
    with next_col:
        with st.container(key=f"{key_prefix}_next_wrap"):
            if st.button("Next ›", key=f"{key_prefix}_next", disabled=(current_page >= total_pages)):
                st.session_state[page_key] += 1
                st.rerun()

def render_sidebar_calendar():
    if "calendar_month_offset" not in st.session_state:
        st.session_state.calendar_month_offset = 0

    today = date.today()
    total_months = (today.month - 1) + st.session_state.calendar_month_offset
    view_year = today.year + total_months // 12
    view_month = total_months % 12 + 1
    month_name = date(view_year, view_month, 1).strftime("%B %Y")
    is_current_month = (view_year == today.year and view_month == today.month)

    with st.sidebar.container(key="calendar_box"):
        nav_col1, nav_col2, nav_col3 = st.columns([1, 4, 1])
        with nav_col1:
            if st.button("‹", key="cal_prev"):
                st.session_state.calendar_month_offset -= 1
                st.rerun()
        with nav_col2:
            st.markdown(f'<div class="cal-month">{month_name}</div>', unsafe_allow_html=True)
        with nav_col3:
            if st.button("›", key="cal_next"):
                st.session_state.calendar_month_offset += 1
                st.rerun()

        cal = calendar.Calendar(firstweekday=6)
        weeks = cal.monthdayscalendar(view_year, view_month)
        weekday_labels = ["S", "M", "T", "W", "T", "F", "S"]

        header_html = "".join(f'<div class="cal-weekday">{d}</div>' for d in weekday_labels)
        rows_html = ""
        for week in weeks:
            for day in week:
                if day == 0:
                    rows_html += '<div class="cal-day cal-day-empty">0</div>'
                elif is_current_month and day == today.day:
                    rows_html += f'<div class="cal-day cal-day-today">{day}</div>'
                else:
                    rows_html += f'<div class="cal-day">{day}</div>'

        st.markdown(
            f'<div class="cal-grid">{header_html}{rows_html}</div>',
            unsafe_allow_html=True,
        )


# --- Sidebar navigation (now functional) ---
st.sidebar.markdown(
    """
    <div style="display:flex; align-items:center; gap:10px; padding:0 0 24px 0;">
        <div style="background:#F5F7FA; width:36px; height:36px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:18px;">🍃</div>
        <span style="font-size:18px; font-weight:700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">Leave Management</span>
    </div>
    """,
    unsafe_allow_html=True,
)

if is_approver:
    nav_options = ["Dashboard", "All Leave Requests", "Team Overview", "Profile"]
else:
    nav_options = ["Dashboard", "Apply for Leave", "Add Past Leave", "My Leave Requests", "Profile"]

page = st.sidebar.radio("Navigate", nav_options, label_visibility="collapsed")

render_sidebar_calendar()


if "show_account_menu" not in st.session_state:
    st.session_state.show_account_menu = False

with st.sidebar.container():
    avatar_col, info_col, menu_col = st.columns(
        [0.9, 3.8, 0.9],
        vertical_alignment="center"
    )

    with avatar_col:
        initial = current_user_name[0].upper() if current_user_name else "?"

        st.markdown(
            f"""
            <div class="sidebar-avatar">
                {initial}
            </div>
            """,
            unsafe_allow_html=True
        )

    with info_col:
        role_label = "Approver" if is_approver else "Employee"

        st.markdown(
            f"""
            <div class="sidebar-user-info">
                <div class="sidebar-user-name" title="{current_user_name}">
                    {current_user_name}
                </div>
                <div class="sidebar-user-role">
                    {role_label}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with menu_col:
        if st.button("⚙️", key="account_menu_toggle"):
            st.session_state.show_account_menu = not st.session_state.show_account_menu

    if st.session_state.get("show_account_menu"):
        if st.button("Log out", key="logout_btn"):
            st.logout()



if is_approver and page == "Dashboard":
    st.title(f"Hello {current_user_name},")
    st.write("Here's the latest overview of team leave requests.")

    records = load_leave_requests()
    df = records_to_df(records)

    pending_count = (df["Status"] == "Pending").sum()
    approved_count = (df["Status"] == "Approved").sum()
    rejected_count = (df["Status"] == "Rejected").sum()
    total_count = len(df[df["Status"] != "Withdrawn"])


    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_stat_card("🕐", "Pending", pending_count, "Request awaiting approval", "#FEF6E7", "#D97706")
    with col2:
        render_stat_card("✅", "Approved", approved_count, "Successfully approved", "#ECFDF5", "#059669")
    with col3:
        render_stat_card("❌", "Rejected", rejected_count, "Rejected requests", "#FEF2F2", "#DC2626")
    with col4:
        render_stat_card("📅", "Total Requests", total_count, "All time requests", "#EFF6FF", "#2563EB")

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    with st.container(border=True, key="table_wide_approver_dash"):
        st.subheader("All Leave Requests")
        search_text = st.session_state.get("top_bar_search", "").strip()
        display_df = filter_by_search(df, search_text, ["Request ID", "Employee Name", "Leave Type"])
        render_paginated_table(
            display_df,
            key_prefix="approver_dash",
            column_config={
                "Applied On": st.column_config.TextColumn("Applied On", width="small"),
                "Document Link": st.column_config.LinkColumn("Document", display_text="Open", width="small"),
            },
        )

    with st.container(border=True):
        st.subheader("Pending Requests")

        pending_requests = df[df["Status"] == "Pending"]

        if pending_requests.empty:
            st.write("No pending requests right now.")
        else:
            for _, row in pending_requests.iterrows():
                info_col, approve_col, decline_col = st.columns([4, 1, 1])
                with info_col:
                    st.write(f"**{row['Request ID']}** — {row['Employee Name']} · {row['Leave Type']} · {row['From']} to {row['To']}")
                with approve_col:
                    if st.button("Approve", key=f"dash_approve_{row['Request ID']}", use_container_width=True):
                        update_status(row["Request ID"], "Approved")
                        st.cache_data.clear()
                        st.rerun()
                with decline_col:
                    if st.button("Decline", key=f"dash_decline_{row['Request ID']}", use_container_width=True):
                        update_status(row["Request ID"], "Rejected")
                        st.cache_data.clear()
                        st.rerun()


elif is_approver and page == "All Leave Requests":
    st.title("All Leave Requests")

    records = load_leave_requests()
    df = records_to_df(records)

    with st.container(border=True, key="table_wide_all_requests"):
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

        search_text = st.session_state.get("top_bar_search", "").strip()
        filtered = filter_by_search(filtered, search_text, ["Request ID", "Employee Name", "Leave Type"])

        render_paginated_table(
            filtered[["Request ID", "Employee Name", "Leave Type", "From", "To", "Reason", "Status", "Applied On", "Document Link"]],
            key_prefix="all_requests",
            column_config={
                "Applied On": st.column_config.TextColumn("Applied On", width="small"),
                "Document Link": st.column_config.LinkColumn("Document", display_text="Open", width="small"),
            },
        )

    with st.container(border=True):
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
    df = records_to_df(records)

    team_pending = (df["Status"] == "Pending").sum()
    team_approved = (df["Status"] == "Approved").sum()
    team_rejected = (df["Status"] == "Rejected").sum()
    team_total = len(df[df["Status"] != "Withdrawn"])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_stat_card("🕐", "Pending", team_pending, "Awaiting approval", "#FEF6E7", "#D97706")
    with col2:
        render_stat_card("✅", "Approved", team_approved, "Successfully approved", "#ECFDF5", "#059669")
    with col3:
        render_stat_card("❌", "Rejected", team_rejected, "Rejected requests", "#FEF2F2", "#DC2626")
    with col4:
        render_stat_card("📅", "Total Requests", team_total, "All time requests", "#EFF6FF", "#2563EB")

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    summary = df.groupby("Employee Name").agg(
        total_requests=("Status", lambda s: (s != "Withdrawn").sum()),
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

    with st.container(border=True, key="table_wide_team_summary"):
        st.subheader("Requests per Employee")
        render_paginated_table(summary, key_prefix="team_summary", page_size=10)

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    approved_all = df[df["Status"] == "Approved"].copy()
    daily_rows = []
    for _, r in approved_all.iterrows():
        start = pd.to_datetime(r["From"], errors="coerce")
        end = pd.to_datetime(r["To"], errors="coerce")
        if pd.isna(start) or pd.isna(end):
            continue
        for d in pd.date_range(start, end):
            daily_rows.append({"Employee Name": r["Employee Name"], "Date": d, "Leave Type": r["Leave Type"]})
    daily_leaves_df = pd.DataFrame(daily_rows, columns=["Employee Name", "Date", "Leave Type"])

    employee_options = ["All Employees"] + sorted(df["Employee Name"].dropna().unique().tolist())

    with st.container(border=True, key="date_wise_leave_overview"):
        st.subheader("Leave Overview by Date")
        selected_date = st.date_input("Select Date", value=date.today(), key="team_overview_date_select")
        selected_date_ts = pd.Timestamp(selected_date)

        approved_all["_From"] = pd.to_datetime(approved_all["From"], errors="coerce")
        approved_all["_To"] = pd.to_datetime(approved_all["To"], errors="coerce")

        on_leave_today = approved_all[
            (approved_all["_From"] <= selected_date_ts) & (approved_all["_To"] >= selected_date_ts)
        ]

        people_count = on_leave_today["Employee Name"].nunique()
        st.markdown(f"**People on Leave: {people_count}**")

        if on_leave_today.empty:
            st.info("No employees are on leave on this date.")
        else:
            display_table = on_leave_today.copy()
            display_table["From"] = display_table["_From"].dt.strftime("%d %b")
            display_table["To"] = display_table["_To"].dt.strftime("%d %b")
            display_table = display_table[["Employee Name", "Leave Type", "From", "To", "Status"]].rename(
                columns={"Employee Name": "Employee"}
            )
            st.dataframe(display_table, use_container_width=True, hide_index=True)

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    with st.container(border=True, key="team_leave_trend"):
        st.subheader("Team Leave Trend")
        trend_range = st.selectbox(
            "Date Range",
            ["Previous 7 Days", "Next 7 Days", "Next 30 Days", "Next 90 Days"],
            key="team_overview_trend_range",
        )

        today_ts = pd.Timestamp(date.today())
        if trend_range == "Previous 7 Days":
            range_start = today_ts - pd.Timedelta(days=6)
            range_end = today_ts
        else:
            range_days = {"Next 7 Days": 7, "Next 30 Days": 30, "Next 90 Days": 90}[trend_range]
            range_start = today_ts
            range_end = range_start + pd.Timedelta(days=range_days - 1)

        trend_data = daily_leaves_df[
            (daily_leaves_df["Date"] >= range_start) & (daily_leaves_df["Date"] <= range_end)
        ]

        trend_summary = trend_data.groupby("Date").agg(
            Employees=("Employee Name", "nunique"),
            Names=("Employee Name", lambda names: ", ".join(sorted(set(names)))),
        ).reset_index()

        all_dates = pd.DataFrame({"Date": pd.date_range(range_start, range_end)})
        trend_summary = all_dates.merge(trend_summary, on="Date", how="left")
        trend_summary["Employees"] = trend_summary["Employees"].fillna(0).astype(int)
        trend_summary["Names"] = trend_summary["Names"].fillna("None")
        trend_summary["Date_Label"] = trend_summary["Date"].dt.strftime("%d %b")

        line = alt.Chart(trend_summary).mark_line(
            color="#2563EB", strokeWidth=3, point=alt.OverlayMarkDef(color="#2563EB", size=60)
        ).encode(
            x=alt.X(
                "Date_Label:O", title=None, sort=list(trend_summary["Date_Label"]),
                axis=alt.Axis(labelAngle=0, labelFontSize=12)
            ),
            y=alt.Y("Employees:Q", title="Employees on Leave", axis=alt.Axis(tickMinStep=1, format="d")),
            tooltip=[
                alt.Tooltip("Date:T", title="Date", format="%d %b %Y"),
                alt.Tooltip("Employees:Q", title="Employees on Leave"),
                alt.Tooltip("Names:N", title="Employees"),
            ],
        ).properties(height=300).configure_view(strokeWidth=0).configure_axis(
            domain=False, gridColor="#F1F5F9", tickColor="#F1F5F9"
        )

        st.altair_chart(line, use_container_width=True)

        # st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

        # with st.container(border=True, key="employee_leave_days_summary"):
        #     st.subheader("Employee-wise Leave Summary")

    # st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    # with st.container(border=True, key="employee_leave_days_summary"):
    #     st.subheader("Employee-wise Leave Summary")

    #     if daily_leaves_df.empty:
    #         st.info("No approved leave days recorded yet.")
    #     else:
    #         days_per_employee = daily_leaves_df.groupby("Employee Name").size().reset_index(name="Leave Days")
    #         emp_chart = alt.Chart(days_per_employee).mark_bar(
    #             color="#2563EB", cornerRadiusTopRight=6, cornerRadiusBottomRight=6
    #         ).encode(
    #             y=alt.Y("Employee Name", sort="-x", title=None),
    #             x=alt.X("Leave Days", title="Leave Days"),
    #             tooltip=["Employee Name", "Leave Days"],
    #         ).properties(height=max(300, 24 * days_per_employee.shape[0]))
    #         st.altair_chart(emp_chart, use_container_width=True)

    # st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    # with st.container(border=True, key="leave_calendar_heatmap"):
    #     st.subheader("Leave Calendar")
    #     selected_calendar_employee = st.selectbox("Employee", employee_options, key="team_overview_calendar_employee")

    #     if selected_calendar_employee == "All Employees":
    #         calendar_data = daily_leaves_df.copy()
    #     else:
    #         calendar_data = daily_leaves_df[daily_leaves_df["Employee Name"] == selected_calendar_employee]

    #     if calendar_data.empty:
    #         st.info("No approved leave days to show.")
    #     else:
    #         calendar_counts = calendar_data.groupby("Date").agg(People=("Employee Name", "nunique")).reset_index()
    #         calendar_counts["Day"] = calendar_counts["Date"].dt.day_name()
    #         week_start = calendar_counts["Date"] - pd.to_timedelta(calendar_counts["Date"].dt.weekday, unit="D")
    #         calendar_counts["Week"] = week_start.dt.strftime("%d %b")
    #         day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    #         heatmap = alt.Chart(calendar_counts).mark_rect(
    #         cornerRadius=6, stroke="#FFFFFF", strokeWidth=3
    #         ).encode(
    #             x=alt.X("Week:O", title=None, sort=None, axis=alt.Axis(labelAngle=0, labelFontSize=12, labelColor="#6B7280")),
    #             y=alt.Y("Day:O", title=None, sort=day_order, axis=alt.Axis(labelFontSize=12, labelColor="#6B7280")),
    #             color=alt.Color(
    #                 "People:Q",
    #                 legend=None,
    #                 scale=alt.Scale(scheme="blues"),
    #             ),
    #             tooltip=[
    #                 alt.Tooltip("Date:T", title="Date", format="%d %b %Y"),
    #                 alt.Tooltip("People:Q", title="People on Leave", format="d"),
    #             ],
    #         ).properties(
    #             width=alt.Step(70), height=alt.Step(42)
    #         ).configure_view(strokeWidth=0).configure_axis(
    #             domain=False, grid=False, tickColor="#F1F5F9"
    #         )
    #         st.altair_chart(heatmap, use_container_width=False)

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        with st.container(border=True, key="leave_type_distribution"):
            st.subheader("Leave Type Distribution")
            selected_type_employee = st.selectbox("Employee", employee_options, key="team_overview_type_employee")

            if selected_type_employee == "All Employees":
                type_data = daily_leaves_df.copy()
            else:
                type_data = daily_leaves_df[daily_leaves_df["Employee Name"] == selected_type_employee]

            if type_data.empty:
                st.info("No approved leave days to show.")
            else:
                type_days = type_data.groupby("Leave Type").size().reset_index(name="Leave Days")
                total_days = int(type_days["Leave Days"].sum())
                type_days["Percent"] = (type_days["Leave Days"] / total_days * 100).round(0).astype(int)
                type_days["Legend Label"] = type_days["Leave Type"] + "   " + type_days["Leave Days"].astype(str) + " days"

                professional_palette = ["#1E3A8A", "#2563EB", "#0EA5E9", "#0D9488", "#7C3AED", "#64748B"]

                donut = alt.Chart(type_days).mark_arc(
                    innerRadius=60, outerRadius=105, cornerRadius=4, padAngle=0.015
                ).encode(
                    theta=alt.Theta("Leave Days:Q", stack=True),
                    color=alt.Color(
                        "Legend Label:N",
                        scale=alt.Scale(range=professional_palette),
                        legend=alt.Legend(
                            title=None,
                            orient="right",
                            legendY=95,
                            labelFontSize=13,
                            symbolSize=140,
                            symbolType="circle",
                            offset=20,
                            rowPadding=15,
                        ),
                    ),
                    tooltip=["Leave Type", "Leave Days", "Percent"],
                )

                slice_labels = alt.Chart(type_days).mark_text(
                    radius=72, fontSize=12, fontWeight="bold", color="#FFFFFF"
                ).encode(
                    theta=alt.Theta("Leave Days:Q", stack=True),
                    text=alt.Text("Leave Days:Q"),
                )

                center_number = alt.Chart(pd.DataFrame({"text": [str(total_days)]})).mark_text(
                    fontSize=26, fontWeight="bold", color="#1F2937", dy=-6
                ).encode(text="text:N")

                center_caption = alt.Chart(pd.DataFrame({"text": ["Total Leave Days"]})).mark_text(
                    fontSize=10, color="#6B7280", dy=14
                ).encode(text="text:N")

                type_chart = (donut + slice_labels + center_number + center_caption).properties(
                    height=288
                ).configure_view(strokeWidth=0)

            with st.container(key="leave_type_chart_center"):
                st.altair_chart(type_chart, use_container_width=False)
                st.markdown("<div style='height:0px;'></div>", unsafe_allow_html=True)

    with col_right:
        with st.container(border=True, key="team_availability"):
            st.subheader("Team Availability")

            employee_records = load_employees()
            employees_df = employees_to_df(employee_records)
            active_employees_df = employees_df[employees_df["Active"].astype(str).str.upper() == "TRUE"]
            TOTAL_TEAM_MEMBERS = len(active_employees_df)

            selected_avail_date = st.date_input("Select Date", value=date.today(), key="team_overview_availability_date")
            avail_date_ts = pd.Timestamp(selected_avail_date)

            on_leave_mask = (approved_all["_From"] <= avail_date_ts) & (approved_all["_To"] >= avail_date_ts)
            on_leave_employees = approved_all.loc[on_leave_mask, "Employee Name"].nunique()
            available_count = max(0, TOTAL_TEAM_MEMBERS - on_leave_employees)

            members_col, leave_col = st.columns(2)
            with members_col:
                st.markdown(f"**Total Team Members:** {TOTAL_TEAM_MEMBERS}")
            with leave_col:
                st.markdown(f"**On Leave:** {on_leave_employees}")
            st.markdown(
                f"<div style='font-size:26px; font-weight:600; color:#059669; margin-top:0px;'>Available: {available_count}</div>",
                unsafe_allow_html=True,
            )

            if on_leave_employees == 0:
                st.caption("All team members are available on this date.")
            else:
                st.caption(f"{on_leave_employees} employees are on leave on this date.")

            # st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
            # st.markdown("**Lowest Availability**")
            # if daily_leaves_df.empty:
            #     st.caption(f"{TOTAL_TEAM_MEMBERS} employees (no approved leave data recorded yet)")
            # else:
            #     leave_counts_by_date = daily_leaves_df.groupby("Date")["Employee Name"].nunique()
            #     availability_by_date = TOTAL_TEAM_MEMBERS - leave_counts_by_date
            #     min_avail = int(availability_by_date.min())
            #     min_date = availability_by_date[availability_by_date == min_avail].index.min()
            #     st.caption(f"Lowest Availability: {min_avail} employees — Date: {min_date.strftime('%d %b %Y')}")

            # st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
            # st.markdown("**Upcoming Availability**")
            # upcoming_dates = pd.date_range(date.today(), periods=7)
            # upcoming_rows = []
            # for d in upcoming_dates:
            #     day_on_leave = approved_all.loc[
            #         (approved_all["_From"] <= d) & (approved_all["_To"] >= d), "Employee Name"
            #     ].nunique()
            #     upcoming_rows.append({"Date": d.strftime("%d %b"), "Available": TOTAL_TEAM_MEMBERS - day_on_leave})
            # upcoming_df = pd.DataFrame(upcoming_rows)
            # st.dataframe(upcoming_df, use_container_width=True, hide_index=True)

            if is_approver:
                st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
                st.markdown("**Manage Team Members**")
                if active_employees_df.empty:
                    st.caption("No active employees registered yet.")
                else:
                    remove_name = st.selectbox(
                        "Select employee to remove",
                        active_employees_df["Employee Name"].tolist(),
                        key="team_availability_remove_select",
                    )
                    if st.button("Remove from team", key="team_availability_remove_button"):
                        remove_email = active_employees_df.loc[
                            active_employees_df["Employee Name"] == remove_name, "Email"
                        ].iloc[0]
                        deactivate_employee(remove_email)
                        st.success(f"{remove_name} has been removed from the active team list.")
                        st.rerun()

# --- Dashboard page ---
elif page == "Dashboard" and not is_approver:
    st.title(f"Welcome back, {current_user_name}")
    st.write("Here's a quick overview of your leave requests and status.")

    records = load_leave_requests()
    df = records_to_df(records)
    df = df[df["Employee Name"] == current_user_name].copy()

    pending_count = (df["Status"] == "Pending").sum()
    approved_count = (df["Status"] == "Approved").sum()
    rejected_count = (df["Status"] == "Rejected").sum()
    total_count = len(df[df["Status"] != "Withdrawn"])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_stat_card("🕐", "Pending", pending_count, "Request awaiting approval", "#FEF6E7", "#D97706")
    with col2:
        render_stat_card("✅", "Approved", approved_count, "Successfully approved", "#ECFDF5", "#059669")
    with col3:
        render_stat_card("❌", "Rejected", rejected_count, "Rejected requests", "#FEF2F2", "#DC2626")
    with col4:
        render_stat_card("📅", "Total Requests", total_count, "All time requests", "#EFF6FF", "#2563EB")

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    with st.container(border=True, key="table_wide_employee_dash"):
        st.subheader("My Leave Requests")
        search_text = st.session_state.get("top_bar_search", "").strip()
        display_df = filter_by_search(df, search_text, ["Request ID", "Employee Name", "Leave Type"])
        render_paginated_table(
            display_df,
            key_prefix="employee_dash",
            column_config={
                "Applied On": st.column_config.TextColumn("Applied On", width="small"),
                "Document Link": st.column_config.LinkColumn("Document", display_text="Open", width="small"),
            },
        )


elif page == "My Leave Requests":
    st.title("My Leave Requests")

    records = load_leave_requests()
    df = records_to_df(records)
    my_requests = df[df["Employee Name"] == current_user_name].copy()

    with st.container(border=True, key="table_wide_my_requests"):
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

        search_text = st.session_state.get("top_bar_search", "").strip()
        filtered = filter_by_search(filtered, search_text, ["Request ID", "Employee Name", "Leave Type"])

        render_paginated_table(
            filtered[["Request ID", "Leave Type", "From", "To", "Reason", "Status", "Applied On", "Document Link"]],
            key_prefix="my_requests",
            column_config={
                "Applied On": st.column_config.TextColumn("Applied On", width="small"),
                "Document Link": st.column_config.LinkColumn("Document", display_text="Open", width="small"),
            },
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

    with st.container(border=True):
        initial = current_user_name[0].upper() if current_user_name else "?"
        role_label = "Approver" if is_approver else "Employee"
        role_bg = "#EFF6FF" if is_approver else "#ECFDF5"
        role_color = "#2563EB" if is_approver else "#059669"

        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:24px; padding:8px 0 24px 0;">
                <div style="width:80px; height:80px; min-width:80px; border-radius:50%; background:#3B7DFF; color:white; display:flex; align-items:center; justify-content:center; font-size:32px; font-weight:700;">{initial}</div>
                <div>
                    <div style="font-size:26px; font-weight:800; color:#111827;">{current_user_name}</div>
                    <div style="margin-top:6px;">
                        <span style="background:{role_bg}; color:{role_color}; font-size:14px; font-weight:700; padding:5px 14px; border-radius:999px;">{role_label}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<hr style='border:none; border-top:1px solid #E5E7EB; margin:0 0 20px 0;'>", unsafe_allow_html=True)

        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.markdown(
                f"""
                <div style="padding-bottom:20px;">
                    <div style="font-size:12px; color:#9CA3AF; text-transform:uppercase; letter-spacing:0.04em; font-weight:600;">Email</div>
                    <div style="font-size:15px; color:#111827; margin-top:4px;">{current_user_email}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with info_col2:
            st.markdown(
                f"""
                <div style="padding-bottom:20px;">
                    <div style="font-size:12px; color:#9CA3AF; text-transform:uppercase; letter-spacing:0.04em; font-weight:600;">Team</div>
                    <div style="font-size:15px; color:#111827; margin-top:4px;">Credit & Underwriting</div>
                </div>
                """,
                unsafe_allow_html=True,
            )



# --- Apply for Leave page ---
elif page == "Apply for Leave":
    st.title("Apply for Leave")

    with st.container(border=True):
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
                        except Exception as e:
                            st.error(f"Upload failed: {e}")

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


elif page == "Add Past Leave":
    st.title("Add Past Leave")
    st.write("Use this to log leave you've already taken in the past — it's recorded directly, no approval needed.")

    with st.container(border=True):
        leave_types = ["Planned Leave", "Sick Leave", "Emergency Leave", "Personal Leave", "Other"]
        leave_type = st.selectbox("Leave Type", leave_types, key="past_leave_type")

        other_description = ""
        if leave_type == "Other":
            other_description = st.text_input("Please describe this leave type (required)", key="past_leave_other_desc")

        with st.form("add_past_leave_form"):
            first_date = st.date_input("First Date", value=date.today())
            num_days = st.number_input("Number of Days", min_value=1, max_value=31, value=1, step=1)
            reason = st.text_area("Reason (optional)")

            submitted = st.form_submit_button("Add")

            if submitted:
                if leave_type == "Other" and not other_description.strip():
                    st.error("Please provide a description for 'Other' leave type before submitting.")
                else:
                    start_date = first_date
                    end_date = first_date + pd.Timedelta(days=int(num_days) - 1)

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
                        "Approved",
                        other_description,
                        "",
                        str(date.today()),
                    ])

                    st.success(f"Past leave logged successfully ({start_date} to {end_date}, {num_days} day(s)).")
                    st.cache_data.clear()


else:
    st.title(page)
    st.write("This page isn't built yet — coming in a later milestone.")