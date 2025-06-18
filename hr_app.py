import streamlit as st
import json
from datetime import datetime, timedelta, date
import os
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import base64
from passlib.hash import pbkdf2_sha256 # For password hashing

# --- SET STREAMLIT PAGE CONFIG (MUST BE THE VERY FIRST STREAMLIT COMMAND) ---
st.set_page_config(
    page_title="Polaris Digitech HR Portal",
    layout="wide", # Use wide layout for more space
    initial_sidebar_state="expanded"
)
# --- END CORRECT PLACEMENT ---

# --- Configuration & Paths ---
DATA_DIR = "hr_data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
LEAVE_REQUESTS_FILE = os.path.join(DATA_DIR, "leave_requests.json")
OPEX_CAPEX_REQUESTS_FILE = os.path.join(DATA_DIR, "opex_capex_requests.json")
PERFORMANCE_GOALS_FILE = os.path.join(DATA_DIR, "performance_goals.json")
SELF_APPRAISALS_FILE = os.path.join(DATA_DIR, "self_appraisals.json")
PAYROLL_FILE = os.path.join(DATA_DIR, "payroll.json")
BENEFICIARIES_FILE = os.path.join(DATA_DIR, "beneficiaries.json")
HR_POLICIES_FILE = os.path.join(DATA_DIR, "hr_policies.json") # New

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

ICON_BASE_DIR = "Project_Resources" # Assuming you create this folder and put images inside
if not os.path.exists(ICON_BASE_DIR):
    os.makedirs(ICON_BASE_DIR)

LOGO_FILE_NAME = "polaris_digitech_logo.png"
LOGO_PATH = os.path.join(ICON_BASE_DIR, LOGO_FILE_NAME)

ABDULAHI_IMAGE_FILE_NAME = "abdulahi_image.png"
ABDULAHI_IMAGE_PATH = os.path.join(ICON_BASE_DIR, ABDULAHI_IMAGE_FILE_NAME)

# --- Define Approval Route Roles and simulate emails (Updated to fetch from users) ---
APPROVAL_ROLES = ["Admin", "HR", "Finance", "MD"] # These correspond to departments for approval logic

# --- Data Loading/Saving Functions ---
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

def load_data(filename, default_value=None):
    if default_value is None:
        default_value = []
    try:
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            with open(filename, "r") as file:
                return json.load(file)
        return default_value
    except json.JSONDecodeError:
        st.warning(f"Error decoding JSON from {filename}. File might be corrupted or empty. Resetting data.")
        return default_value
    except FileNotFoundError:
        return default_value

def save_data(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4, cls=DateEncoder)

def save_uploaded_file(uploaded_file, destination_folder="uploaded_documents"):
    if uploaded_file is not None:
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        
        file_path = os.path.join(destination_folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return None

# --- Initial Data Setup (Users, Policies, Beneficiaries) ---
def setup_initial_data():
    # Initial Users (Admin + 6 Staff Members)
    initial_users = [
        # Admin User
        {
            "username": "abdul_bolaji@yahoo.com",
            "password": pbkdf2_sha256.hash("admin123"), # Hashed password
            "role": "admin",
            "staff_id": "ADM/2024/000",
            "profile": {
                "name": "Abdul Bolaji (Admin)",
                "date_of_birth": "1980-01-01",
                "gender": "Male",
                "grade_level": "MD",
                "department": "Admin",
                "education_background": "MBA, Computer Science",
                "professional_experience": "15+ years in IT Management",
                "address": "123 Admin Lane, Lagos",
                "phone_number": "+2348011112222",
                "email_address": "abdul_bolaji@yahoo.com",
                "training_attended": [],
                "work_anniversary": "2010-09-01"
            }
        },
        # Staff Members (with generic password 123456)
        {
            "username": "ada_ama",
            "password": pbkdf2_sha256.hash("123456"),
            "role": "staff",
            "staff_id": "POL/2024/001",
            "profile": {
                "name": "Ada Ama",
                "date_of_birth": "1995-01-01",
                "gender": "Male", # Corrected from Male in table
                "grade_level": "MD", # This is a grade level not a role in a typical HR system.
                "department": "Executive", # This is a department not a role in a typical HR system.
                "education_background": "",
                "professional_experience": "",
                "address": "",
                "phone_number": "",
                "email_address": "ada.ama@example.com",
                "training_attended": [],
                "work_anniversary": "2024-01-15"
            }
        },
        {
            "username": "udu_aka",
            "password": pbkdf2_sha256.hash("123456"),
            "role": "staff",
            "staff_id": "POL/2024/002",
            "profile": {
                "name": "Udu Aka",
                "date_of_birth": "2000-02-01",
                "gender": "Male",
                "grade_level": "Manager",
                "department": "Finance",
                "education_background": "",
                "professional_experience": "",
                "address": "",
                "phone_number": "",
                "email_address": "udu.aka@example.com",
                "training_attended": [],
                "work_anniversary": "2024-03-01"
            }
        },
        {
            "username": "abdulahi_ibrahim",
            "password": pbkdf2_sha256.hash("123456"),
            "role": "staff",
            "staff_id": "POL/2024/003",
            "profile": {
                "name": "Abdulahi Ibrahim",
                "date_of_birth": "1998-03-03",
                "gender": "Female",
                "grade_level": "Manager",
                "department": "Administration",
                "education_background": "",
                "professional_experience": "",
                "address": "",
                "phone_number": "",
                "email_address": "abdulahi.ibrahim@example.com",
                "training_attended": [],
                "work_anniversary": "2024-02-10"
            }
        },
        {
            "username": "addidas_puma",
            "password": pbkdf2_sha256.hash("123456"),
            "role": "staff",
            "staff_id": "POL/2024/004", # Note: Duplicated Staff ID in prompt, corrected for uniqueness
            "profile": {
                "name": "Addidas Puma",
                "date_of_birth": "1999-09-04",
                "gender": "Male",
                "grade_level": "Manager",
                "department": "HR",
                "education_background": "",
                "professional_experience": "",
                "address": "",
                "phone_number": "",
                "email_address": "addidas.puma@example.com",
                "training_attended": [],
                "work_anniversary": "2023-07-20"
            }
        },
        {
            "username": "big_kola",
            "password": pbkdf2_sha256.hash("123456"),
            "role": "staff",
            "staff_id": "POL/2024/005", # Corrected for uniqueness
            "profile": {
                "name": "Big Kola",
                "date_of_birth": "2001-06-13",
                "gender": "Female",
                "grade_level": "Manager",
                "department": "CV", # Assuming 'CV' is a department name
                "education_background": "",
                "professional_experience": "",
                "address": "",
                "phone_number": "",
                "email_address": "big.kola@example.com",
                "training_attended": [],
                "work_anniversary": "2022-04-05"
            }
        },
        {
            "username": "king_queen",
            "password": pbkdf2_sha256.hash("123456"),
            "role": "staff",
            "staff_id": "POL/2024/006", # Corrected for uniqueness
            "profile": {
                "name": "King Queen",
                "date_of_birth": "2002-06-16",
                "gender": "Female",
                "grade_level": "Officer",
                "department": "Administration",
                "education_background": "",
                "professional_experience": "",
                "address": "",
                "phone_number": "",
                "email_address": "king.queen@example.com",
                "training_attended": [],
                "work_anniversary": "2023-11-01"
            }
        }
    ]
    
    # Only create initial users if the file doesn't exist or is empty
    if not os.path.exists(USERS_FILE) or os.path.getsize(USERS_FILE) == 0:
        save_data(initial_users, USERS_FILE)
        st.success("Initial user data created.")

    # Initial HR Policies
    initial_policies = {
        "Staff Handbook": "This handbook outlines the policies, procedures, and expectations for all employees of Polaris Digitech. It covers topics such as conduct, benefits, and company culture...",
        "HSE Policy": "Polaris Digitech is committed to providing a safe and healthy working environment for all employees, contractors, and visitors. This policy details our approach to Health, Safety, and Environment management...",
        "Data Privacy Security Policy": "This policy establishes guidelines for the collection, use, storage, and disclosure of personal data to ensure compliance with data protection laws and safeguard sensitive information...",
        "Procurement Policy": "This policy governs all procurement activities at Polaris Digitech, ensuring transparency, fairness, and cost-effectiveness in acquiring goods and services...",
        "Password Secrecy Policy": "This policy sets forth the requirements for creating, using, and protecting passwords within Polaris Digitech to safeguard company information systems and data from unauthorized access."
    }
    if not os.path.exists(HR_POLICIES_FILE) or os.path.getsize(HR_POLICIES_FILE) == 0:
        save_data(initial_policies, HR_POLICIES_FILE)
        st.success("Initial HR policies created.")

    # Initial Beneficiaries Data (from prompt)
    initial_beneficiaries = {
        "Bestway Engineering Services Ltd": {"Account Name": "Benjamin", "Account No": "1234567890", "Bank": "GTB"},
        "Alpha Link Technical Services": {"Account Name": "Oladele", "Account No": "2345678900", "Bank": "Access Bank"},
        "AFLAC COM SPECs": {"Account Name": "Fasco", "Account No": "1234567890", "Bank": "Opay"},
        "Emmafem Resources Nig. Ent.": {"Account Name": "Radius", "Account No": "2345678901", "Bank": "UBA"},
        "Neptune Global Services": {"Account Name": "Folashade", "Account No": "12345678911", "Bank": "Union Bank"},
        "Other (Manually Enter Details)": {"Account Name": "", "Account No": "", "Bank": ""} # Option for manual entry
    }
    if not os.path.exists(BENEFICIARIES_FILE) or os.path.getsize(BENEFICIARIES_FILE) == 0:
        save_data(initial_beneficiaries, BENEFICIARIES_FILE)
        st.success("Initial Beneficiaries data created.")

# --- Session State Initialization ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state: # Stores full user object if logged in
    st.session_state.current_user = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "login"

# Load all persistent data into session state
st.session_state.users = load_data(USERS_FILE)
st.session_state.leave_requests = load_data(LEAVE_REQUESTS_FILE, [])
st.session_state.opex_capex_requests = load_data(OPEX_CAPEX_REQUESTS_FILE, [])
st.session_state.performance_goals = load_data(PERFORMANCE_GOALS_FILE, [])
st.session_state.self_appraisals = load_data(SELF_APPRAISALS_FILE, [])
st.session_state.payroll_data = load_data(PAYROLL_FILE, []) # New payroll data
st.session_state.beneficiaries = load_data(BENEFICIARIES_FILE, {}) # New beneficiaries data
st.session_state.hr_policies = load_data(HR_POLICIES_FILE, {}) # New policies data

# Ensure payroll data has necessary columns for DataFrame creation
# This handles cases where payroll.json might be empty or malformed initially
if not st.session_state.payroll_data:
    st.session_state.payroll_data = [] # Ensure it's an empty list if data is missing

# --- Common UI Elements ---
def display_logo():
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=150)
    else:
        st.error(f"Company logo not found at: {LOGO_PATH}")
        st.warning(f"Please ensure '{LOGO_FILE_NAME}' is in '{ICON_BASE_DIR}'.")

def display_sidebar():
    st.sidebar.image(LOGO_PATH, width=200)
    st.sidebar.title("Navigation")
    st.sidebar.markdown("---")

    # Dynamic sidebar based on user role
    if st.session_state.logged_in:
        st.sidebar.button("📊 Dashboard", key="nav_dashboard", on_click=lambda: st.session_state.update(current_page="dashboard"))
        st.sidebar.button("📝 My Profile", key="nav_my_profile", on_click=lambda: st.session_state.update(current_page="my_profile"))
        st.sidebar.button("🏖️ Apply for Leave", key="nav_apply_leave", on_click=lambda: st.session_state.update(current_page="leave_request"))
        st.sidebar.button("📈 Performance Goal Setting", key="nav_performance_goals", on_click=lambda: st.session_state.update(current_page="performance_goal_setting"))
        st.sidebar.button("✍️ Self-Appraisal", key="nav_self_appraisal", on_click=lambda: st.session_state.update(current_page="self_appraisal"))
        st.sidebar.button("📄 HR Policies", key="nav_hr_policies", on_click=lambda: st.session_state.update(current_page="hr_policies"))
        st.sidebar.button("💰 My Payslips", key="nav_my_payslips", on_click=lambda: st.session_state.update(current_page="my_payslips")) # New
        st.sidebar.button("💲 OPEX/CAPEX Requisition", key="nav_submit_opex_capex", on_click=lambda: st.session_state.update(current_page="opex_capex_form"))

        if st.session_state.current_user and st.session_state.current_user['role'] == 'admin':
            st.sidebar.markdown("---")
            st.sidebar.subheader("Admin Functions")
            st.sidebar.button("👥 Manage Users", key="admin_manage_users", on_click=lambda: st.session_state.update(current_page="manage_users")) # New
            st.sidebar.button("📤 Upload Payroll", key="admin_upload_payroll", on_click=lambda: st.session_state.update(current_page="upload_payroll")) # New
            st.sidebar.button("✅ Manage OPEX/CAPEX Approvals", key="admin_manage_approvals", on_click=lambda: st.session_state.update(current_page="manage_opex_capex_approvals")) # New
            st.sidebar.button("🏦 Manage Beneficiaries", key="admin_manage_beneficiaries", on_click=lambda: st.session_state.update(current_page="manage_beneficiaries")) # New
            st.sidebar.button("📜 Manage HR Policies", key="admin_manage_policies", on_click=lambda: st.session_state.update(current_page="manage_hr_policies")) # New

        st.sidebar.markdown("---")
        st.sidebar.button("Logout", key="nav_logout", on_click=logout)
    else:
        st.sidebar.info("Please log in to access the portal.")

def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.current_page = "login"
    st.rerun()

# --- Login Form ---
def login_form():
    st.title("Polaris Digitech Staff Portal - Login")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        username_input = st.text_input("User ID", key="login_username_input")
        password_input = st.text_input("Password", type="password", key="login_password_input")

        if st.button("Login", key="login_button"):
            found_user = None
            for user in st.session_state.users:
                # Check for both username and email (for admin login)
                if user['username'] == username_input:
                    if pbkdf2_sha256.verify(password_input, user['password']):
                        found_user = user
                        break
            
            if found_user:
                st.session_state.logged_in = True
                st.session_state.current_user = found_user
                st.success("Logged in successfully!")
                st.session_state.current_page = "dashboard"
                st.rerun()
            else:
                st.error("Invalid credentials")

# --- Dashboard Display ---
def display_dashboard():
    st.title("📊 Polaris Digitech HR Portal - Dashboard")

    if st.session_state.current_user:
        current_user_profile = st.session_state.current_user.get('profile', {})
        st.markdown(f"## Welcome, {current_user_profile.get('name', st.session_state.current_user['username']).title()}!")
        st.write(f"Your Staff ID: **{current_user_profile.get('staff_id', 'N/A')}**")
        st.write(f"Department: **{current_user_profile.get('department', 'N/A')}**")

        st.markdown("---")
        st.subheader("Upcoming Birthdays")
        today = date.today()
        upcoming_birthdays = []
        for user in st.session_state.users:
            profile = user.get('profile', {})
            dob_str = profile.get('date_of_birth')
            name = profile.get('name')
            if dob_str and name:
                try:
                    dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                    # Calculate birthday for current year
                    birthday_this_year = dob.replace(year=today.year)
                    # If birthday already passed this year, check next year
                    if birthday_this_year < today:
                        birthday_this_year = dob.replace(year=today.year + 1)
                    
                    days_until_birthday = (birthday_this_year - today).days

                    if 0 <= days_until_birthday <= 30: # Within next 30 days
                        upcoming_birthdays.append({
                            "Name": name,
                            "Birthday": birthday_this_year.strftime('%B %d'),
                            "Days Until": days_until_birthday
                        })
                except ValueError:
                    continue # Skip if DOB is malformed

        if upcoming_birthdays:
            df_birthdays = pd.DataFrame(upcoming_birthdays).sort_values(by="Days Until")
            st.dataframe(df_birthdays, use_container_width=True, hide_index=True)
            if any(b['Days Until'] == 0 for b in upcoming_birthdays):
                st.balloons()
                st.success("🎉 Happy Birthday to our staff members today! 🎉")
        else:
            st.info("No upcoming birthdays in the next 30 days.")

        st.markdown("---")
        st.subheader("HR Analytics Overview")

        total_employees = len(st.session_state.users)
        st.metric("Total Employees", total_employees)

        # Staff Distribution by Department
        if st.session_state.users:
            departments = [user.get('profile', {}).get('department', 'Unassigned') for user in st.session_state.users]
            df_departments = pd.DataFrame(departments, columns=['Department'])
            dept_counts = df_departments['Department'].value_counts().reset_index()
            dept_counts.columns = ['Department', 'Count']
            fig_dept = px.pie(dept_counts, values='Count', names='Department', title='Staff Distribution by Department', hole=0.3)
            st.plotly_chart(fig_dept, use_container_width=True)

            # Staff Distribution by Gender
            genders = [user.get('profile', {}).get('gender', 'N/A') for user in st.session_state.users]
            df_genders = pd.DataFrame(genders, columns=['Gender'])
            gender_counts = df_genders['Gender'].value_counts().reset_index()
            gender_counts.columns = ['Gender', 'Count']
            fig_gender = px.pie(gender_counts, values='Count', names='Gender', title='Staff Distribution by Gender', hole=0.3)
            st.plotly_chart(fig_gender, use_container_width=True)
        else:
            st.info("No staff data to display distributions.")

        # Staff On Leave
        current_on_leave = 0
        today = date.today()
        for req in st.session_state.leave_requests:
            try:
                start_date = datetime.strptime(req.get('start_date', '1900-01-01'), '%Y-%m-%d').date()
                end_date = datetime.strptime(req.get('end_date', '1900-01-01'), '%Y-%m-%d').date()
                if start_date <= today <= end_date and req.get('status') == 'Approved':
                    current_on_leave += 1
            except ValueError:
                continue # Skip malformed date entries
        st.metric("Staff Currently On Leave (Approved)", current_on_leave)

        st.markdown("---")
        st.subheader("Your Pending Requests")
    # 🔔 Notify if current user is an approver on any pending requests
    approver_name = st.session_state.current_user.get('profile', {}).get('name')
    pending_approver_tasks = []

    for req in st.session_state.opex_capex_requests:
        if (
            (req.get('admin_manager_approver') == approver_name and req.get('status_admin_manager') == "Pending") or
            (req.get('hr_manager_approver') == approver_name and req.get('status_hr_manager') == "Pending") or
            (req.get('finance_manager_approver') == approver_name and req.get('status_finance_manager') == "Pending") or
            (req.get('md_approver') == approver_name and req.get('status_md') == "Pending")
        ):
            pending_approver_tasks.append(req)

    if pending_approver_tasks:
        st.warning(f"🔔 You have {len(pending_approver_tasks)} OPEX/CAPEX requisition(s) awaiting your approval.")

        
        user_pending_leave = [
            req for req in st.session_state.leave_requests 
            if req.get('staff_id') == current_user_profile.get('staff_id') and req.get('status') == 'Pending'
        ]
        user_pending_opex_capex = [
            req for req in st.session_state.opex_capex_requests 
            if req.get('requester_staff_id') == current_user_profile.get('staff_id') and req.get('final_status') == 'Pending'
        ]

        if user_pending_leave:
            st.info(f"You have {len(user_pending_leave)} pending leave requests.")
        if user_pending_opex_capex:
            st.info(f"You have {len(user_pending_opex_capex)} pending OPEX/CAPEX requests.")
        if not user_pending_leave and not user_pending_opex_capex:
            st.info("You have no pending requests.")


    else:
        st.warning("User not logged in.")

# --- My Profile Page ---
def display_my_profile():
    st.title("📝 My Profile")

    user_index = -1
    for i, user in enumerate(st.session_state.users):
        if user['username'] == st.session_state.current_user['username']:
            user_index = i
            break

    if user_index == -1:
        st.error("Could not find your profile. Please log out and log in again.")
        return

    current_user_profile = st.session_state.users[user_index]['profile']

    with st.form("profile_edit_form"):
        st.subheader("Personal Details")
        current_user_profile['name'] = st.text_input("Full Name", value=current_user_profile.get("name", ""), key="profile_name_edit")
        
        # New fields: Staff ID, Date of Birth, Gender, Grade Level, Department
        st.text_input("Staff ID", value=current_user_profile.get("staff_id", ""), disabled=True, help="Staff ID cannot be changed.")
        
        dob_value = None
        if current_user_profile.get("date_of_birth"):
            try:
                dob_value = datetime.strptime(current_user_profile["date_of_birth"], '%Y-%m-%d').date()
            except ValueError:
                st.warning("Invalid date of birth format in existing profile. Please update.")
                dob_value = date.today()
        else:
            dob_value = date.today() # Default if no DOB exists
        
        current_user_profile['date_of_birth'] = st.date_input("Date of Birth", value=dob_value, key="profile_dob")
        current_user_profile['gender'] = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(current_user_profile.get("gender", "Male")), key="profile_gender")
        current_user_profile['grade_level'] = st.text_input("Grade Level", value=current_user_profile.get("grade_level", ""), key="profile_grade")
        
        department_options = ["Admin", "HR", "Finance", "IT", "Marketing", "Operations", "Sales", "Executive", "Administration", "CV", "Other", "Unassigned"]
        current_dept = current_user_profile.get("department", "Unassigned")
        current_dept_index = department_options.index(current_dept) if current_dept in department_options else 0
        current_user_profile['department'] = st.selectbox("Department", options=department_options, index=current_dept_index, key="profile_department_edit")

        current_user_profile['address'] = st.text_area("Address", value=current_user_profile.get("address", ""), key="profile_address_edit")
        current_user_profile['phone_number'] = st.text_input("Phone Number", value=current_user_profile.get("phone_number", ""), key="profile_phone_edit")
        st.text_input("Email Address (Login ID)", value=st.session_state.current_user['username'], disabled=True, help="Your login email cannot be changed here.", key="profile_email_edit")
        
        st.subheader("Professional Background")
        current_user_profile['education_background'] = st.text_area("Education Background", value=current_user_profile.get("education_background", ""), height=100, key="profile_education_edit")
        current_user_profile['professional_experience'] = st.text_area("Professional Experience", value=current_user_profile.get("professional_experience", ""), height=150, key="profile_experience_edit")

        st.subheader("Change Password")
        new_password = st.text_input("New Password", type="password", key="new_password_input")
        confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_password_input")

        save_profile_button = st.form_submit_button("Save Profile and Change Password (if entered)")

        if save_profile_button:
            # Update profile details
            st.session_state.users[user_index]['profile'] = current_user_profile
            
            # Handle password change
            if new_password:
                if new_password == confirm_password:
                    st.session_state.users[user_index]['password'] = pbkdf2_sha256.hash(new_password)
                    st.success("Password changed successfully!")
                else:
                    st.error("New password and confirm password do not match.")
                    st.rerun() # Stop execution to show error
            
            save_data(st.session_state.users, USERS_FILE)
            st.success("Profile details saved successfully!")
            st.rerun()

    st.markdown("---")
    st.subheader("Training Attended")
    with st.form("new_training_form"):
        new_training_name = st.text_input("New Training Name")
        new_training_date = st.date_input("Training Date", value=datetime.now())
        
        add_training_button = st.form_submit_button("Add Training Record")

        if add_training_button:
            if new_training_name:
                training_record = {"name": new_training_name, "date": str(new_training_date)}
                # Ensure 'training_attended' key exists in profile
                if "training_attended" not in current_user_profile:
                    current_user_profile["training_attended"] = []
                current_user_profile["training_attended"].append(training_record)
                save_data(st.session_state.users, USERS_FILE)
                st.success(f"Added training: {new_training_name}")
                st.rerun()
            else:
                st.error("Training name cannot be empty.")

    current_trainings = current_user_profile.get("training_attended", [])
    if current_trainings:
        st.write("---")
        st.markdown("#### Existing Training Records:")
        training_container = st.container()
        with training_container:
            for i, training in enumerate(current_trainings):
                col_tr1, col_tr2, col_tr3 = st.columns([0.6, 0.3, 0.1])
                with col_tr1:
                    st.write(f"- **{training.get('name', 'N/A')}**")
                with col_tr2:
                    st.write(f"({training.get('date', 'N/A')})")
                with col_tr3:
                    # Use a unique key for the button
                    if st.button("x", key=f"delete_training_{i}_btn_{training.get('name', '')}"):
                        current_user_profile["training_attended"].pop(i)
                        save_data(st.session_state.users, USERS_FILE)
                        st.info("Training record deleted.")
                        st.rerun()
    else:
        st.info("No training records added yet.")


# --- Leave Request Form (Existing) ---
def leave_request_form():
    st.title("🏖️ Apply for Leave")
    st.write("Fill out the form below to submit a leave request.")

    current_user_profile = st.session_state.current_user.get('profile', {})
    
    with st.form("leave_application_form"):
        st.subheader(f"Leave Application for {current_user_profile.get('name', 'N/A')}")
        
        leave_type = st.selectbox("Leave Type", ["Annual Leave", "Sick Leave", "Maternity Leave", "Paternity Leave", "Compassionate Leave", "Study Leave", "Other"])
        start_date = st.date_input("Start Date", value=datetime.now().date())
        end_date = st.date_input("End Date", value=datetime.now().date() + timedelta(days=7))
        reason = st.text_area("Reason for Leave", height=100)
        
        # Calculate number of days
        num_days = (end_date - start_date).days + 1
        st.info(f"Number of days requested: {num_days} days")

        supporting_document = st.file_uploader("Upload Supporting Document (Optional)", type=["pdf", "jpg", "jpeg", "png"])
        
        submitted = st.form_submit_button("Submit Leave Request")

        if submitted:
            if start_date > end_date:
                st.error("End Date cannot be before Start Date.")
            elif num_days <= 0:
                st.error("Number of days requested must be at least 1.")
            else:
                doc_path = save_uploaded_file(supporting_document, "leave_documents")
                
                new_request = {
                    "request_id": len(st.session_state.leave_requests) + 1,
                    "staff_id": current_user_profile.get('staff_id', 'N/A'),
                    "staff_name": current_user_profile.get('name', 'N/A'),
                    "leave_type": leave_type,
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "num_days": num_days,
                    "reason": reason,
                    "document_path": doc_path,
                    "submission_date": str(datetime.now().date()),
                    "status": "Pending" # Initial status
                }
                st.session_state.leave_requests.append(new_request)
                save_data(st.session_state.leave_requests, LEAVE_REQUESTS_FILE)
                st.success("Leave request submitted successfully! It is now pending approval.")
                st.rerun()

# --- View Leave Applications (Admin/Manager View) ---
def view_leave_applications():
    st.title("📋 View Leave Applications")

    # Filter for logged-in user if not admin
    if st.session_state.current_user['role'] == 'admin':
        st.subheader("All Leave Requests")
        display_requests_raw = st.session_state.leave_requests
    else:
        st.subheader("Your Leave Requests")
        current_staff_id = st.session_state.current_user['profile'].get('staff_id')
        display_requests_raw = [req for req in st.session_state.leave_requests if req.get('staff_id') == current_staff_id]
        
    if not display_requests_raw:
        st.info("No leave applications to display.")
        return

    # Define expected columns and their default values
    expected_cols = {
        "request_id": None, "staff_id": "N/A", "staff_name": "N/A", "leave_type": "N/A", 
        "start_date": None, "end_date": None, "num_days": 0, "reason": "N/A", 
        "document_path": None, "submission_date": None, "status": "N/A"
    }
    
    # Create a list of dictionaries with all expected keys
    cleaned_requests = []
    for req in display_requests_raw:
        cleaned_req = {key: req.get(key, default_val) for key, default_val in expected_cols.items()}
        cleaned_requests.append(cleaned_req)

    df_leave_requests = pd.DataFrame(cleaned_requests)
    
    # Convert dates to datetime objects for processing, then back to date for display
    df_leave_requests['start_date'] = pd.to_datetime(df_leave_requests['start_date'], errors='coerce').dt.date
    df_leave_requests['end_date'] = pd.to_datetime(df_leave_requests['end_date'], errors='coerce').dt.date
    df_leave_requests['submission_date'] = pd.to_datetime(df_leave_requests['submission_date'], errors='coerce').dt.date

    # Sort and display
    df_leave_requests_sorted = df_leave_requests.sort_values(by="submission_date", ascending=False)
    
    display_cols_for_df = [
        "request_id", "staff_name", "leave_type", "start_date", "end_date", 
        "num_days", "status", "submission_date", "reason"
    ]
    # Filter display columns to only include those that actually exist in the DataFrame
    final_display_cols = [col for col in display_cols_for_df if col in df_leave_requests_sorted.columns]

    st.dataframe(df_leave_requests_sorted[final_display_cols], use_container_width=True, hide_index=True)

    if st.session_state.current_user['role'] == 'admin':
        st.markdown("---")
        st.subheader("Approve/Reject Leave Requests")
        
        pending_requests = [req for req in cleaned_requests if req['status'] == 'Pending'] # Use cleaned requests for safety

        if not pending_requests:
            st.info("No pending leave requests to approve/reject.")
            return

        request_options = [""] + [f"ID: {req['request_id']} - {req['staff_name']} ({req['leave_type']} {req['start_date']} to {req['end_date']})" for req in pending_requests if req.get('request_id') is not None]
        selected_request_info = st.selectbox("Select Leave Request to Review", options=request_options)

        if selected_request_info:
            request_id = int(selected_request_info.split(" - ")[0].replace("ID: ", ""))
            selected_request = next(req for req in st.session_state.leave_requests if req.get('request_id') == request_id) # Use original for updating

            st.write(f"**Staff Name:** {selected_request.get('staff_name', 'N/A')}")
            st.write(f"**Leave Type:** {selected_request.get('leave_type', 'N/A')}")
            st.write(f"**Dates:** {selected_request.get('start_date', 'N/A')} to {selected_request.get('end_date', 'N/A')} ({selected_request.get('num_days', 'N/A')} days)")
            st.write(f"**Reason:** {selected_request.get('reason', 'N/A')}")
            if selected_request.get('document_path') and os.path.exists(selected_request['document_path']):
                with open(selected_request['document_path'], "rb") as file:
                    btn = st.download_button(
                        label="Download Supporting Document",
                        data=file.read(),
                        file_name=os.path.basename(selected_request['document_path']),
                        mime="application/octet-stream"
                    )
            else:
                st.info("No supporting document uploaded.")

            col_approve, col_reject = st.columns(2)
            with col_approve:
                if st.button("Approve Request", key=f"approve_{request_id}"):
                    for i, req in enumerate(st.session_state.leave_requests):
                        if req.get('request_id') == request_id:
                            st.session_state.leave_requests[i]['status'] = 'Approved'
                            break
                    save_data(st.session_state.leave_requests, LEAVE_REQUESTS_FILE)
                    st.success(f"Leave request {request_id} approved.")
                    st.rerun()
            with col_reject:
                if st.button("Reject Request", key=f"reject_{request_id}"):
                    for i, req in enumerate(st.session_state.leave_requests):
                        if req.get('request_id') == request_id:
                            st.session_state.leave_requests[i]['status'] = 'Rejected'
                            break
                    save_data(st.session_state.leave_requests, LEAVE_REQUESTS_FILE)
                    st.warning(f"Leave request {request_id} rejected.")
                    st.rerun()

# --- OPEX/CAPEX Form (Existing, will enhance approvals) ---
def opex_capex_form():
    st.title("💲 OPEX/CAPEX Requisition")
    st.write("Submit your operational or capital expenditure requisition.")

    current_user_profile = st.session_state.current_user.get('profile', {})

    with st.form("opex_capex_requisition_form"):
        st.subheader(f"Requisition by {current_user_profile.get('name', 'N/A')}")
        
        request_type = st.selectbox("Request Type", ["OPEX (Operational Expenditure)", "CAPEX (Capital Expenditure)"])
        item_description = st.text_area("Item/Service Description", height=100)
        quantity = st.number_input("Quantity", min_value=1, value=1)
        unit_price = st.number_input("Unit Price (₦)", min_value=0.0, value=0.0, format="%.2f")
        total_amount = quantity * unit_price
        st.write(f"**Total Amount: ₦{total_amount:,.2f}**")

        justification = st.text_area("Justification / Business Case", height=150)
        
        # --- Approvers Selection (New) ---
        st.subheader("Select Approvers")
        # Get all users who are "managers" in relevant departments or have 'admin' role
        # For simplicity, let's allow selection from all users, but ideally filtered by role/department
        # Ensure 'name' exists for user profiles
        all_staff_names = sorted([user.get('profile', {}).get('name') for user in st.session_state.users if user.get('profile', {}).get('name') is not None])
        approver_options = [""] + all_staff_names
        
        admin_manager_approver = st.selectbox("Admin Manager (Required)", options=approver_options, key="admin_manager_approver")
        hr_manager_approver = st.selectbox("HR Manager (Required)", options=approver_options, key="hr_manager_approver")
        finance_manager_approver = st.selectbox("Finance Manager (Required)", options=approver_options, key="finance_manager_approver")
        md_approver = st.selectbox("Managing Director (Required)", options=approver_options, key="md_approver")

        # Basic validation for approvers
        required_approvers_selected = all([admin_manager_approver, hr_manager_approver, finance_manager_approver, md_approver])

        submitted = st.form_submit_button("Submit Requisition")

        if submitted:
            if not required_approvers_selected:
                st.error("Please select all required approvers.")
            elif not item_description or total_amount <= 0:
                st.error("Please provide item description and a valid amount.")
            else:
                new_request = {
                    "req_id": len(st.session_state.opex_capex_requests) + 1,
                    "requester_staff_id": current_user_profile.get('staff_id', 'N/A'),
                    "requester_name": current_user_profile.get('name', 'N/A'),
                    "request_type": request_type,
                    "item_description": item_description,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_amount": total_amount,
                    "justification": justification,
                    "submission_date": str(datetime.now().date()),
                    "admin_manager_approver": admin_manager_approver, # Store selected approver name
                    "hr_manager_approver": hr_manager_approver,
                    "finance_manager_approver": finance_manager_approver,
                    "md_approver": md_approver,
                    "status_admin_manager": "Pending", # Initial status for each approver
                    "status_hr_manager": "Pending",
                    "status_finance_manager": "Pending",
                    "status_md": "Pending",
                    "final_status": "Pending" # Overall final status
                }
                st.session_state.opex_capex_requests.append(new_request)
                save_data(st.session_state.opex_capex_requests, OPEX_CAPEX_REQUESTS_FILE)
                st.success("OPEX/CAPEX requisition submitted successfully! It is now pending approval.")
                st.rerun()

# --- Manage OPEX/CAPEX Approvals (New Admin/Manager Functionality) ---
def manage_opex_capex_approvals():
    st.title("✅ Manage OPEX/CAPEX Approvals")

    current_user = st.session_state.current_user
    current_user_name = current_user.get('profile', {}).get('name')
    current_user_department = current_user.get('profile', {}).get('department')

    # Determine which requests the current user can approve
    requests_for_approval_list = [] # Use a list to collect and then deduplicate
    approver_role_display = "Reviewer" # Default display role

    # Admin can approve all
    if current_user['role'] == 'admin':
        requests_for_approval_list.extend([
            req for req in st.session_state.opex_capex_requests if req.get('final_status') == 'Pending'
        ])
        approver_role_display = "Administrator"
    else:
        # Check specific department manager roles
        if current_user_department == 'Admin':
            requests_for_approval_list.extend([
                req for req in st.session_state.opex_capex_requests
                if req.get('admin_manager_approver') == current_user_name and req.get('status_admin_manager') == 'Pending'
            ])
            approver_role_display = "Admin Manager"
        if current_user_department == 'HR':
            requests_for_approval_list.extend([
                req for req in st.session_state.opex_capex_requests
                if req.get('hr_manager_approver') == current_user_name and req.get('status_hr_manager') == 'Pending'
            ])
            if approver_role_display == "Reviewer": approver_role_display = "HR Manager"
        if current_user_department == 'Finance':
            requests_for_approval_list.extend([
                req for req in st.session_state.opex_capex_requests
                if req.get('finance_manager_approver') == current_user_name and req.get('status_finance_manager') == 'Pending'
            ])
            if approver_role_display == "Reviewer": approver_role_display = "Finance Manager"
        # Assuming MD/Executive role is for MD approvals
        if current_user_department in ['Executive', 'MD']: 
            requests_for_approval_list.extend([
                req for req in st.session_state.opex_capex_requests
                if req.get('md_approver') == current_user_name and req.get('status_md') == 'Pending'
            ])
            if approver_role_display == "Reviewer": approver_role_display = "Managing Director"

    # Deduplicate requests if a user falls into multiple approval categories or is admin
    unique_requests = {req.get('req_id'): req for req in requests_for_approval_list if req.get('req_id') is not None}.values()
    
    if not unique_requests:
        st.info("No OPEX/CAPEX requests pending your approval.")
        return

    df_requests = pd.DataFrame(list(unique_requests))

    st.subheader(f"Requests Pending Your Approval (As {approver_role_display})")
    
    # Define expected columns for robust DataFrame creation
    expected_cols = {
        "req_id": None, "requester_name": "N/A", "request_type": "N/A", 
        "item_description": "N/A", "total_amount": 0.0, "submission_date": None, 
        "status_admin_manager": "N/A", "status_hr_manager": "N/A",
        "status_finance_manager": "N/A", "status_md": "N/A", "final_status": "N/A"
    }

    # Clean the DataFrame based on expected columns
    cleaned_df_requests = []
    for index, row in df_requests.iterrows():
        cleaned_row = {col: row.get(col, default_val) for col, default_val in expected_cols.items()}
        cleaned_df_requests.append(cleaned_row)
    df_requests_cleaned = pd.DataFrame(cleaned_df_requests)


    # Define columns for display
    display_cols = [
        "req_id", "requester_name", "request_type", "item_description", "total_amount",
        "submission_date", "status_admin_manager", "status_hr_manager",
        "status_finance_manager", "status_md", "final_status"
    ]
    
    # Filter only columns present in the DataFrame to avoid KeyError on display
    current_display_cols = [col for col in display_cols if col in df_requests_cleaned.columns]

    df_requests_cleaned['submission_date'] = pd.to_datetime(df_requests_cleaned['submission_date'], errors='coerce').dt.date
    st.dataframe(df_requests_cleaned[current_display_cols].sort_values(by="submission_date", ascending=False), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Review Request")

    request_options = [""] + [f"ID: {req['req_id']} - {req['requester_name']} ({req['item_description']})" for req in unique_requests if req.get('req_id') is not None]
    selected_request_info = st.selectbox("Select Request to Review", options=request_options)

    if selected_request_info:
        req_id = int(selected_request_info.split(" - ")[0].replace("ID: ", ""))
        selected_req = next(req for req in st.session_state.opex_capex_requests if req.get('req_id') == req_id)

        st.write(f"**Requisition ID:** {selected_req.get('req_id', 'N/A')}")
        st.write(f"**Requester:** {selected_req.get('requester_name', 'N/A')}")
        st.write(f"**Type:** {selected_req.get('request_type', 'N/A')}")
        st.write(f"**Description:** {selected_req.get('item_description', 'N/A')}")
        st.write(f"**Quantity:** {selected_req.get('quantity', 'N/A')}")
        st.write(f"**Unit Price:** ₦{selected_req.get('unit_price', 0):,.2f}")
        st.write(f"**Total Amount:** ₦{selected_req.get('total_amount', 0):,.2f}")
        st.write(f"**Justification:** {selected_req.get('justification', 'N/A')}")
        st.write(f"**Submission Date:** {selected_req.get('submission_date', 'N/A')}")
        st.write("---")
        st.write("### Current Approval Status:")
        st.write(f"- Admin Manager ({selected_req.get('admin_manager_approver', 'N/A')}): {selected_req.get('status_admin_manager', 'N/A')}")
        st.write(f"- HR Manager ({selected_req.get('hr_manager_approver', 'N/A')}): {selected_req.get('status_hr_manager', 'N/A')}")
        st.write(f"- Finance Manager ({selected_req.get('finance_manager_approver', 'N/A')}): {selected_req.get('status_finance_manager', 'N/A')}")
        st.write(f"- MD ({selected_req.get('md_approver', 'N/A')}): {selected_req.get('status_md', 'N/A')}")
        st.write(f"**Overall Final Status:** {selected_req.get('final_status', 'N/A')}")


        # Approval Form for the current user's role
        with st.form(f"approve_opex_capex_form_{req_id}"):
            new_status = st.radio(f"Action for this Request (as {approver_role_display})", ["Approve", "Reject"], key=f"status_action_{req_id}")
            comment = st.text_area("Your Comment (Optional)", key=f"comment_{req_id}")

            col_submit_approval, col_cancel_approval = st.columns(2)
            with col_submit_approval:
                if st.form_submit_button("Submit Action", key=f"submit_action_{req_id}"):
                    for i, req_item in enumerate(st.session_state.opex_capex_requests):
                        if req_item.get('req_id') == req_id:
                            # Update status based on current user's role
                            # Admin role can override any status if needed, but here we'll stick to specific roles
                            # For simplicity, if admin is also the approver, they approve their specific step
                            if current_user_name == req_item.get('admin_manager_approver'):
                                st.session_state.opex_capex_requests[i]['status_admin_manager'] = new_status
                            if current_user_name == req_item.get('hr_manager_approver'):
                                st.session_state.opex_capex_requests[i]['status_hr_manager'] = new_status
                            if current_user_name == req_item.get('finance_manager_approver'):
                                st.session_state.opex_capex_requests[i]['status_finance_manager'] = new_status
                            if current_user_name == req_item.get('md_approver'):
                                st.session_state.opex_capex_requests[i]['status_md'] = new_status
                            
                            # Update final status - only if all are approved
                            current_req_statuses = st.session_state.opex_capex_requests[i]
                            all_approved = (
                                current_req_statuses.get('status_admin_manager') == 'Approve' and
                                current_req_statuses.get('status_hr_manager') == 'Approve' and
                                current_req_statuses.get('status_finance_manager') == 'Approve' and
                                current_req_statuses.get('status_md') == 'Approve'
                            )
                            any_rejected = (
                                current_req_statuses.get('status_admin_manager') == 'Reject' or
                                current_req_statuses.get('status_hr_manager') == 'Reject' or
                                current_req_statuses.get('status_finance_manager') == 'Reject' or
                                current_req_statuses.get('status_md') == 'Reject'
                            )

                            if all_approved:
                                st.session_state.opex_capex_requests[i]['final_status'] = 'Approved'
                                st.success(f"Requisition {req_id} has been fully approved!")
                            elif any_rejected:
                                st.session_state.opex_capex_requests[i]['final_status'] = 'Rejected'
                                st.error(f"Requisition {req_id} has been rejected.")
                            else:
                                st.session_state.opex_capex_requests[i]['final_status'] = 'Pending' # Still pending other approvals
                                st.info(f"Action recorded for Requisition {req_id}. Still pending other approvals.")

                            break # Found and updated the request

                    save_data(st.session_state.opex_capex_requests, OPEX_CAPEX_REQUESTS_FILE)
                    st.rerun() # Rerun to refresh the list of pending requests

            with col_cancel_approval:
                if st.form_submit_button("Cancel", key=f"cancel_action_{req_id}"):
                    st.info("Action cancelled.")
                    st.rerun()

# --- View OPEX/CAPEX Requests (User's historical view) ---
def view_opex_capex_requests():
    st.title("📄 View OPEX/CAPEX Requests")

    current_staff_id = st.session_state.current_user['profile'].get('staff_id')
    
    # Filter by current user
    user_requests_raw = [req for req in st.session_state.opex_capex_requests if req.get('requester_staff_id') == current_staff_id]

    if not user_requests_raw:
        st.info("You have no OPEX/CAPEX requisitions to display.")
        return

    # Define expected columns for robust DataFrame creation
    expected_cols = {
        "req_id": None, "requester_staff_id": "N/A", "requester_name": "N/A", "request_type": "N/A", 
        "item_description": "N/A", "quantity": 0, "unit_price": 0.0, "total_amount": 0.0, 
        "justification": "N/A", "submission_date": None, "admin_manager_approver": "N/A", 
        "hr_manager_approver": "N/A", "finance_manager_approver": "N/A", "md_approver": "N/A",
        "status_admin_manager": "N/A", "status_hr_manager": "N/A", "status_finance_manager": "N/A", 
        "status_md": "N/A", "final_status": "N/A"
    }
    
    # Create a list of dictionaries with all expected keys
    cleaned_user_requests = []
    for req in user_requests_raw:
        cleaned_req = {key: req.get(key, default_val) for key, default_val in expected_cols.items()}
        cleaned_user_requests.append(cleaned_req)

    df_user_requests = pd.DataFrame(cleaned_user_requests)
    
    df_user_requests['submission_date'] = pd.to_datetime(df_user_requests['submission_date'], errors='coerce').dt.date
    
    # Select columns for display
    display_cols = [
        "req_id", "request_type", "item_description", "total_amount", 
        "submission_date", "status_admin_manager", "status_hr_manager", 
        "status_finance_manager", "status_md", "final_status"
    ]
    # Filter display columns to only include those that actually exist in the DataFrame
    final_display_cols = [col for col in display_cols if col in df_user_requests.columns]

    st.dataframe(df_user_requests[final_display_cols].sort_values(by="submission_date", ascending=False), use_container_width=True, hide_index=True)

# --- Performance Goal Setting (Existing) ---
def performance_goal_setting():
    st.title("📈 Performance Goal Setting")
    st.write("Set and track your performance goals.")

    current_user_profile = st.session_state.current_user.get('profile', {})
    
    with st.form("goal_setting_form"):
        st.subheader(f"Set a New Goal for {current_user_profile.get('name', 'N/A')}")
        goal_title = st.text_input("Goal Title")
        goal_description = st.text_area("Goal Description", height=100)
        due_date = st.date_input("Due Date", value=datetime.now().date() + timedelta(days=90))
        
        submitted = st.form_submit_button("Set Goal")

        if submitted:
            if goal_title and goal_description:
                new_goal = {
                    "goal_id": len(st.session_state.performance_goals) + 1,
                    "staff_id": current_user_profile.get('staff_id', 'N/A'),
                    "staff_name": current_user_profile.get('name', 'N/A'),
                    "title": goal_title,
                    "description": goal_description,
                    "due_date": str(due_date),
                    "status": "Not Started", # Initial status
                    "set_date": str(datetime.now().date())
                }
                st.session_state.performance_goals.append(new_goal)
                save_data(st.session_state.performance_goals, PERFORMANCE_GOALS_FILE)
                st.success("Performance goal set successfully!")
                st.rerun()
            else:
                st.error("Goal Title and Description cannot be empty.")

    st.markdown("---")
    st.subheader("Your Performance Goals")
    
    user_goals_raw = [goal for goal in st.session_state.performance_goals if goal.get('staff_id') == current_user_profile.get('staff_id')]

    if not user_goals_raw:
        st.info("You have not set any performance goals yet.")
        return

    # Define expected columns for robust DataFrame creation
    expected_cols = {
        "goal_id": None, "staff_id": "N/A", "staff_name": "N/A", "title": "N/A", 
        "description": "N/A", "due_date": None, "status": "N/A", "set_date": None
    }
    
    # Create a list of dictionaries with all expected keys
    cleaned_user_goals = []
    for goal in user_goals_raw:
        cleaned_goal = {key: goal.get(key, default_val) for key, default_val in expected_cols.items()}
        cleaned_user_goals.append(cleaned_goal)

    df_user_goals = pd.DataFrame(cleaned_user_goals)
    
    df_user_goals['due_date'] = pd.to_datetime(df_user_goals['due_date'], errors='coerce').dt.date
    df_user_goals['set_date'] = pd.to_datetime(df_user_goals['set_date'], errors='coerce').dt.date

    st.dataframe(df_user_goals.sort_values(by="due_date"), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Update Goal Status")

    goal_options = [""] + [f"ID: {goal['goal_id']} - {goal['title']} (Current: {goal['status']})" for goal in cleaned_user_goals if goal.get('goal_id') is not None]
    selected_goal_info = st.selectbox("Select Goal to Update Status", options=goal_options)

    if selected_goal_info:
        goal_id = int(selected_goal_info.split(" - ")[0].replace("ID: ", ""))
        selected_goal = next(goal for goal in st.session_state.performance_goals if goal.get('goal_id') == goal_id)

        with st.form(f"update_goal_status_form_{goal_id}"):
            new_status = st.selectbox("New Status", ["Not Started", "In Progress", "On Hold", "Complete"], index=["Not Started", "In Progress", "On Hold", "Complete"].index(selected_goal.get('status', 'Not Started')))
            st.write(f"Current Status: **{selected_goal.get('status', 'N/A')}**")
            
            update_button = st.form_submit_button("Update Status")

            if update_button:
                for i, goal in enumerate(st.session_state.performance_goals):
                    if goal.get('goal_id') == goal_id:
                        st.session_state.performance_goals[i]['status'] = new_status
                        break
                save_data(st.session_state.performance_goals, PERFORMANCE_GOALS_FILE)
                st.success(f"Goal '{selected_goal.get('title', 'N/A')}' status updated to '{new_status}'.")
                st.rerun()

# --- Self-Appraisal (Existing) ---
def self_appraisal():
    st.title("✍️ Self-Appraisal")
    st.write("Complete your self-appraisal for the current period.")

    current_user_profile = st.session_state.current_user.get('profile', {})
    
    st.markdown("### Existing Appraisals")
    user_appraisals_raw = [app for app in st.session_state.self_appraisals if app.get('staff_id') == current_user_profile.get('staff_id')]
    if user_appraisals_raw:
        # Define expected columns for robust DataFrame creation
        expected_cols = {
            "appraisal_id": None, "staff_id": "N/A", "staff_name": "N/A", "appraisal_period": "N/A", 
            "achievements": "N/A", "challenges": "N/A", "development_needs": "N/A", 
            "overall_rating": 0, "submission_date": None
        }
        cleaned_user_appraisals = []
        for app in user_appraisals_raw:
            cleaned_app = {key: app.get(key, default_val) for key, default_val in expected_cols.items()}
            cleaned_user_appraisals.append(cleaned_app)

        df_appraisals = pd.DataFrame(cleaned_user_appraisals)
        
        df_appraisals['submission_date'] = pd.to_datetime(df_appraisals['submission_date'], errors='coerce').dt.date
        st.dataframe(df_appraisals.sort_values(by="submission_date", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("You have not submitted any self-appraisals yet.")

    st.markdown("---")
    st.markdown("### Submit New Self-Appraisal")

    with st.form("self_appraisal_form"):
        appraisal_period = st.text_input("Appraisal Period (e.g., Q2 2024, Annual 2023)")
        achievements = st.text_area("Key Achievements", height=150)
        challenges = st.text_area("Challenges Faced / Obstacles Overcome", height=150)
        development_needs = st.text_area("Development Needs / Training Required", height=100)
        overall_rating = st.slider("Overall Performance Rating (1-5, 5 being Excellent)", 1, 5, 3)

        submitted = st.form_submit_button("Submit Appraisal")

        if submitted:
            if appraisal_period and achievements:
                new_appraisal = {
                    "appraisal_id": len(st.session_state.self_appraisals) + 1,
                    "staff_id": current_user_profile.get('staff_id', 'N/A'),
                    "staff_name": current_user_profile.get('name', 'N/A'),
                    "appraisal_period": appraisal_period,
                    "achievements": achievements,
                    "challenges": challenges,
                    "development_needs": development_needs,
                    "overall_rating": overall_rating,
                    "submission_date": str(datetime.now().date())
                }
                st.session_state.self_appraisals.append(new_appraisal)
                save_data(st.session_state.self_appraisals, SELF_APPRAISALS_FILE)
                st.success("Self-appraisal submitted successfully!")
                st.rerun()
            else:
                st.error("Appraisal Period and Key Achievements cannot be empty.")

# --- HR Policies (New) ---
def display_hr_policies():
    st.title("📄 HR Policies")
    st.write("Browse the company's HR policies below.")

    if not st.session_state.hr_policies:
        st.info("No HR policies available yet. Please contact your administrator.")
        return

    # Allow admin to manage policies (informative message)
    if st.session_state.current_user and st.session_state.current_user['role'] == 'admin':
        st.info("Administrators can manage these policies from the 'Manage HR Policies' section in the Admin panel.")

    # Display policies
    for policy_name, policy_content in st.session_state.hr_policies.items():
        with st.expander(f"**{policy_name}**"):
            st.markdown(policy_content)
        st.markdown("---")

# --- My Payslips (New) ---
def display_my_payslips():
    st.title("💰 My Payslips")
    st.write("View and download your monthly payslips.")

    current_staff_id = st.session_state.current_user.get('profile', {}).get('staff_id')

    if not st.session_state.payroll_data:
        st.info("No payroll data available yet.")
        return

    # Filter payroll data for the current user
    user_payroll_records = [rec for rec in st.session_state.payroll_data if rec.get('staff_id') == current_staff_id]

    if not user_payroll_records:
        st.info("No payslips found for your Staff ID.")
        return

    # Define expected columns for robust DataFrame creation
    expected_cols = {
        "payslip_id": None, "staff_id": "N/A", "month": "N/A", "year": "N/A", "basic_salary": 0.0, 
        "allowances": 0.0, "deductions": 0.0, "net_pay": 0.0, "generated_date": None
    }
    cleaned_user_payroll_records = []
    for rec in user_payroll_records:
        cleaned_rec = {key: rec.get(key, default_val) for key, default_val in expected_cols.items()}
        cleaned_user_payroll_records.append(cleaned_rec)

    df_payslips = pd.DataFrame(cleaned_user_payroll_records)
    
    # Convert month and year to datetime for proper sorting
    # Handle potential errors if month/year are not valid
    df_payslips['pay_period'] = pd.to_datetime(
        df_payslips['year'].astype(str) + '-' + df_payslips['month'].astype(str), 
        format='%Y-%m', errors='coerce' # Coerce invalid dates to NaT
    )
    df_payslips = df_payslips.sort_values(by="pay_period", ascending=False)
    df_payslips['generated_date'] = pd.to_datetime(df_payslips['generated_date'], errors='coerce').dt.date

    display_cols = ['month', 'year', 'basic_salary', 'allowances', 'deductions', 'net_pay', 'generated_date']
    final_display_cols = [col for col in display_cols if col in df_payslips.columns]

    st.dataframe(df_payslips[final_display_cols], use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Generate Payslip PDF")

    # Filter for payslips with valid IDs for selection
    payslip_options = [""] + [f"{rec.get('month', 'N/A')}/{rec.get('year', 'N/A')} (ID: {rec.get('payslip_id', 'N/A')})" for rec in cleaned_user_payroll_records if rec.get('payslip_id') is not None]
    selected_payslip_info = st.selectbox("Select Payslip to Generate", options=payslip_options)

    if selected_payslip_info:
        try:
            payslip_id = int(selected_payslip_info.split("(ID: ")[1][:-1])
        except (IndexError, ValueError):
            st.error("Could not parse payslip ID. Please select a valid payslip.")
            return

        selected_payslip = next((rec for rec in user_payroll_records if rec.get('payslip_id') == payslip_id), None)

        if selected_payslip:
            # Get full user profile for payslip details
            payslip_user_profile = next((user.get('profile', {}) for user in st.session_state.users if user.get('profile', {}).get('staff_id') == selected_payslip.get('staff_id')), None)

            if payslip_user_profile:
                pdf_buffer = generate_payslip_pdf(selected_payslip, payslip_user_profile)
                st.download_button(
                    label=f"Download Payslip for {selected_payslip.get('month', 'N/A')}/{selected_payslip.get('year', 'N/A')}",
                    data=pdf_buffer,
                    file_name=f"Payslip_{selected_payslip.get('month', 'N/A')}_{selected_payslip.get('year', 'N/A')}_{selected_payslip.get('staff_id', 'N/A')}.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("User profile not found for this payslip.")
        else:
            st.error("Selected payslip record not found.")

# --- PDF Generation for Payslip (New) ---
def generate_payslip_pdf(payslip_record, user_profile):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Polaris Digitech - Payslip", 0, 1, 'C')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"For: {payslip_record.get('month', 'N/A')}/{payslip_record.get('year', 'N/A')}", 0, 1, 'C')
    pdf.ln(10)

    # Employee Details
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Employee Details:", 0, 1, 'L')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, f"Name: {user_profile.get('name', 'N/A')}", 0, 1)
    pdf.cell(0, 7, f"Staff ID: {user_profile.get('staff_id', 'N/A')}", 0, 1)
    pdf.cell(0, 7, f"Department: {user_profile.get('department', 'N/A')}", 0, 1)
    pdf.cell(0, 7, f"Grade Level: {user_profile.get('grade_level', 'N/A')}", 0, 1)
    pdf.ln(5)

    # Earnings
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Earnings:", 0, 1, 'L')
    pdf.set_font("Arial", '', 10)
    pdf.cell(80, 7, "Basic Salary:", 0, 0, 'L')
    pdf.cell(0, 7, f"₦{payslip_record.get('basic_salary', 0):,.2f}", 0, 1, 'R')
    pdf.cell(80, 7, "Allowances:", 0, 0, 'L')
    pdf.cell(0, 7, f"₦{payslip_record.get('allowances', 0):,.2f}", 0, 1, 'R')
    pdf.ln(5)

    # Deductions
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Deductions:", 0, 1, 'L')
    pdf.set_font("Arial", '', 10)
    pdf.cell(80, 7, "Total Deductions:", 0, 0, 'L')
    pdf.cell(0, 7, f"₦{payslip_record.get('deductions', 0):,.2f}", 0, 1, 'R')
    pdf.ln(5)

    # Net Pay
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(80, 10, "Net Pay:", 0, 0, 'L')
    pdf.cell(0, 10, f"₦{payslip_record.get('net_pay', 0):,.2f}", 0, 1, 'R')
    pdf.ln(10)

    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 5, f"Generated on: {payslip_record.get('generated_date', datetime.now().date()).strftime('%Y-%m-%d')}", 0, 1, 'C')

    # Save the PDF to a BytesIO object
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# --- Admin Section: Manage Users (New) ---
def admin_manage_users():
    st.title("👥 Admin Panel - Manage Users")

    if st.session_state.current_user and st.session_state.current_user['role'] == 'admin':
        st.subheader("Add New Staff Member")
        with st.form("add_staff_form", clear_on_submit=True):
            new_staff_name = st.text_input("Staff Name (e.g., John Doe)", key="new_staff_name_input")
            new_staff_username = st.text_input("Login Username (e.g., john.doe@example.com / john_doe)", help="This will be the user's login ID.", key="new_staff_username_input")
            new_staff_id = st.text_input("Staff ID (e.g., POL/2024/XXX)", help="Unique identifier for the staff.", key="new_staff_id_input")
            
            # Initial generic password
            st.info("New staff members will be assigned a generic password: **123456** (They can change it on their profile page)")
            
            col_add_staff1, col_add_staff2 = st.columns(2)
            with col_add_staff1:
                if st.form_submit_button("Add Staff"):
                    if new_staff_name and new_staff_username and new_staff_id:
                        if any(user['username'] == new_staff_username for user in st.session_state.users):
                            st.error("Username already exists!")
                        elif any(user.get('profile', {}).get('staff_id') == new_staff_id for user in st.session_state.users):
                            st.error("Staff ID already exists!")
                        else:
                            new_user = {
                                "username": new_staff_username,
                                "password": pbkdf2_sha256.hash("123456"), # Generic password
                                "role": "staff", # Default role
                                "staff_id": new_staff_id, # Store here for easy lookup
                                "profile": {
                                    "name": new_staff_name,
                                    "staff_id": new_staff_id, # Redundant but good for quick profile access
                                    "date_of_birth": "", # To be completed by staff
                                    "gender": "", # To be completed by staff
                                    "grade_level": "", # To be completed by staff
                                    "department": "Unassigned", # Default, can be updated by staff/admin
                                    "education_background": "",
                                    "professional_experience": "",
                                    "address": "",
                                    "phone_number": "",
                                    "email_address": new_staff_username,
                                    "training_attended": [],
                                    "work_anniversary": str(date.today()) # Default to today
                                }
                            }
                            st.session_state.users.append(new_user)
                            save_data(st.session_state.users, USERS_FILE)
                            st.success(f"Staff member '{new_staff_name}' with Staff ID '{new_staff_id}' added successfully!")
                            st.rerun()
                    else:
                        st.error("Please fill in Staff Name, Login Username, and Staff ID.")
            with col_add_staff2:
                if st.form_submit_button("Clear Form", type="secondary"):
                    pass # Handled by clear_on_submit=True

        st.markdown("---")
        st.subheader("All Staff Members")

        if st.session_state.users:
            # Filter out the admin user for regular staff display if desired, or display all
            display_users = [user for user in st.session_state.users if user['role'] == 'staff']
            
            if display_users:
                # Prepare data robustly for DataFrame creation
                cleaned_users_for_df = []
                expected_profile_cols = [
                    "name", "staff_id", "date_of_birth", "gender", "grade_level", 
                    "department", "education_background", "professional_experience", 
                    "address", "phone_number", "email_address", "work_anniversary"
                ]
                for user in display_users:
                    profile = user.get('profile', {})
                    cleaned_profile = {col: profile.get(col, '') for col in expected_profile_cols}
                    cleaned_users_for_df.append(cleaned_profile)

                df_users = pd.DataFrame(cleaned_users_for_df)
                
                # Convert date strings to date objects for sorting and display
                df_users['date_of_birth'] = df_users['date_of_birth'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').date() if isinstance(x, str) and x else None)
                df_users['work_anniversary'] = df_users['work_anniversary'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').date() if isinstance(x, str) and x else None)
                
                # Format dates for display
                df_users['date_of_birth'] = df_users['date_of_birth'].apply(lambda x: x.strftime('%Y-%m-%d') if x else 'N/A')
                df_users['work_anniversary'] = df_users['work_anniversary'].apply(lambda x: x.strftime('%Y-%m-%d') if x else 'N/A')

                display_cols = [
                    "name", "staff_id", "gender", "department", "grade_level",
                    "date_of_birth", "email_address", "phone_number", "address", "work_anniversary"
                ]
                final_display_cols = [col for col in display_cols if col in df_users.columns]

                st.dataframe(df_users[final_display_cols], use_container_width=True, hide_index=True)
            else:
                st.info("No staff members added yet (excluding admin).")
        else:
            st.info("No users registered in the system.")
        
        st.markdown("---")
        st.subheader("Edit/Delete Staff Member")

        # Create options robustly
        user_to_edit_options = [""] + sorted([user.get('profile', {}).get('name', user['username']) for user in st.session_state.users if user['role'] == 'staff'])
        selected_user_name = st.selectbox("Select Staff Member to Edit/Delete", options=user_to_edit_options, key="edit_staff_select")

        if selected_user_name:
            selected_user_obj = next((user for user in st.session_state.users if user.get('profile', {}).get('name') == selected_user_name or user['username'] == selected_user_name), None)

            if selected_user_obj:
                selected_user_index = st.session_state.users.index(selected_user_obj)
                current_profile = selected_user_obj['profile']

                with st.form(f"edit_staff_form_{selected_user_obj['staff_id']}"):
                    st.write(f"Editing: **{current_profile.get('name', 'N/A')}** (Login: {selected_user_obj['username']})")
                    
                    # Use .get() with default values for robustness in update form
                    updated_name = st.text_input("Full Name", value=current_profile.get('name', ''))
                    st.text_input("Staff ID", value=current_profile.get('staff_id', ''), disabled=True)
                    
                    # Ensure date_of_birth is a date object for date_input
                    dob_val = None
                    if current_profile.get("date_of_birth"):
                        try:
                            dob_val = datetime.strptime(current_profile["date_of_birth"], '%Y-%m-%d').date()
                        except ValueError:
                            dob_val = date.today() # Default if existing is invalid
                    else:
                        dob_val = date.today()

                    updated_dob = st.date_input("Date of Birth", value=dob_val)
                    updated_gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(current_profile.get("gender", "Male")))
                    updated_grade_level = st.text_input("Grade Level", value=current_profile.get('grade_level', ''))
                    
                    department_options = ["Admin", "HR", "Finance", "IT", "Marketing", "Operations", "Sales", "Executive", "Administration", "CV", "Other", "Unassigned"]
                    current_dept = current_profile.get("department", "Unassigned")
                    current_dept_index = department_options.index(current_dept) if current_dept in department_options else 0
                    updated_department = st.selectbox("Department", options=department_options, index=current_dept_index)

                    updated_address = st.text_area("Address", value=current_profile.get('address', ''))
                    updated_phone = st.text_input("Phone Number", value=current_profile.get('phone_number', ''))
                    st.text_input("Email Address (Login ID)", value=selected_user_obj['username'], disabled=True)
                    
                    # Work Anniversary
                    anniversary_val = None
                    if current_profile.get("work_anniversary"):
                        try:
                            anniversary_val = datetime.strptime(current_profile["work_anniversary"], '%Y-%m-%d').date()
                        except ValueError:
                            anniversary_val = date.today() # Default if existing is invalid
                    else:
                        anniversary_val = date.today()
                    updated_work_anniversary = st.date_input("Work Anniversary", value=anniversary_val)

                    col_edit_del1, col_edit_del2 = st.columns(2)
                    with col_edit_del1:
                        if st.form_submit_button("Update Staff"):
                            st.session_state.users[selected_user_index]['profile']['name'] = updated_name
                            st.session_state.users[selected_user_index]['profile']['date_of_birth'] = str(updated_dob)
                            st.session_state.users[selected_user_index]['profile']['gender'] = updated_gender
                            st.session_state.users[selected_user_index]['profile']['grade_level'] = updated_grade_level
                            st.session_state.users[selected_user_index]['profile']['department'] = updated_department
                            st.session_state.users[selected_user_index]['profile']['address'] = updated_address
                            st.session_state.users[selected_user_index]['profile']['phone_number'] = updated_phone
                            st.session_state.users[selected_user_index]['profile']['work_anniversary'] = str(updated_work_anniversary) # Save as string
                            
                            save_data(st.session_state.users, USERS_FILE)
                            st.success(f"Staff '{updated_name}' updated successfully!")
                            st.rerun()
                    with col_edit_del2:
                        if st.form_submit_button("Delete Staff", type="primary"):
                            # Filter out the selected user
                            st.session_state.users = [user for user in st.session_state.users if user['username'] != selected_user_obj['username']]
                            save_data(st.session_state.users, USERS_FILE)

                            # Clean up associated data (leave, opex/capex, goals, appraisals, payroll) based on staff_id
                            staff_id_to_delete = current_profile.get('staff_id')
                            if staff_id_to_delete:
                                st.session_state.leave_requests = [req for req in st.session_state.leave_requests if req.get('staff_id') != staff_id_to_delete]
                                save_data(st.session_state.leave_requests, LEAVE_REQUESTS_FILE)

                                st.session_state.opex_capex_requests = [req for req in st.session_state.opex_capex_requests if req.get('requester_staff_id') != staff_id_to_delete]
                                save_data(st.session_state.opex_capex_requests, OPEX_CAPEX_REQUESTS_FILE)

                                st.session_state.performance_goals = [goal for goal in st.session_state.performance_goals if goal.get('staff_id') != staff_id_to_delete]
                                save_data(st.session_state.performance_goals, PERFORMANCE_GOALS_FILE)

                                st.session_state.self_appraisals = [app for app in st.session_state.self_appraisals if app.get('staff_id') != staff_id_to_delete]
                                save_data(st.session_state.self_appraisals, SELF_APPRAISALS_FILE)

                                st.session_state.payroll_data = [pay for pay in st.session_state.payroll_data if pay.get('staff_id') != staff_id_to_delete]
                                save_data(st.session_state.payroll_data, PAYROLL_FILE)

                            st.success(f"Staff '{current_profile.get('name', 'N/A')}' deleted successfully!")
                            st.rerun()
            else:
                st.warning("Selected user not found. Please refresh.")
    else:
        st.info("Select a staff member to edit or delete.")


# --- Admin Section: Upload Payroll (New) ---
def admin_upload_payroll():
    st.title("📤 Admin Panel - Upload Payroll")
    st.write("Upload payroll data as a CSV file. The CSV should contain columns: `staff_id`, `month` (e.g., 1-12), `year` (e.g., 2024), `basic_salary`, `allowances`, `deductions`, `net_pay`.")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            df_payroll = pd.read_csv(uploaded_file)
            st.dataframe(df_payroll, use_container_width=True, hide_index=True)

            required_cols = ['staff_id', 'month', 'year', 'basic_salary', 'allowances', 'deductions', 'net_pay']
            if not all(col in df_payroll.columns for col in required_cols):
                st.error(f"Missing required columns in CSV. Please ensure the file contains: {', '.join(required_cols)}")
            else:
                if st.button("Process and Save Payroll Data"):
                    new_or_updated_payroll_records = []
                    
                    # Create a temporary lookup for existing payroll to easily check/update
                    payroll_lookup = {}
                    for p_rec in st.session_state.payroll_data:
                        key = (p_rec.get('staff_id'), p_rec.get('month'), p_rec.get('year'))
                        if all(x is not None for x in key):
                            payroll_lookup[key] = p_rec

                    for index, row in df_payroll.iterrows():
                        try:
                            # Basic validation and type conversion
                            staff_id = str(row['staff_id']).strip()
                            month = int(row['month'])
                            year = int(row['year'])
                            basic_salary = float(row['basic_salary'])
                            allowances = float(row['allowances'])
                            deductions = float(row['deductions'])
                            net_pay = float(row['net_pay'])

                            # Check if staff_id exists in users (using .get() for robustness)
                            if not any(user.get('profile', {}).get('staff_id') == staff_id for user in st.session_state.users):
                                st.warning(f"Skipping payroll for unknown Staff ID: {staff_id} in row {index+1}.")
                                continue
                            
                            current_payslip_key = (staff_id, month, year)
                            
                            payslip_data = {
                                "payslip_id": payroll_lookup.get(current_payslip_key, {}).get('payslip_id', len(st.session_state.payroll_data) + len(new_or_updated_payroll_records) + 1),
                                "staff_id": staff_id,
                                "month": month,
                                "year": year,
                                "basic_salary": basic_salary,
                                "allowances": allowances,
                                "deductions": deductions,
                                "net_pay": net_pay,
                                "generated_date": str(date.today())
                            }
                            
                            if current_payslip_key in payroll_lookup:
                                # Update existing record in place
                                for i, p_rec in enumerate(st.session_state.payroll_data):
                                    if (p_rec.get('staff_id'), p_rec.get('month'), p_rec.get('year')) == current_payslip_key:
                                        st.session_state.payroll_data[i] = payslip_data
                                        st.info(f"Updated payslip for {staff_id} - {month}/{year}")
                                        break
                            else:
                                new_or_updated_payroll_records.append(payslip_data)

                        except ValueError as ve:
                            st.error(f"Data conversion error in row {index+1}: {ve}. Please check numeric fields and dates.")
                            continue
                        except KeyError as ke:
                            st.error(f"Missing column in row {index+1}: {ke}. Please check CSV headers.")
                            continue
                        except Exception as ex:
                            st.error(f"An unexpected error occurred in row {index+1}: {ex}")
                            continue

                    # Add genuinely new records
                    st.session_state.payroll_data.extend(new_or_updated_payroll_records)
                    save_data(st.session_state.payroll_data, PAYROLL_FILE)
                    st.success("Payroll data uploaded and processed successfully!")
                    st.rerun()

        except Exception as e:
            st.error(f"Error reading or processing CSV: {e}")

# --- Admin Section: Manage Beneficiaries (New) ---
def admin_manage_beneficiaries():
    st.title("🏦 Admin Panel - Manage Beneficiaries")

    st.subheader("Current Beneficiaries")
    # Exclude the "Other (Manually Enter Details)" option from the display table
    display_beneficiaries = {k: v for k, v in st.session_state.beneficiaries.items() if k != "Other (Manually Enter Details)"}

    if display_beneficiaries:
        df_beneficiaries = pd.DataFrame(display_beneficiaries).T.reset_index()
        df_beneficiaries.columns = ['Beneficiary Name', 'Account Name', 'Account No', 'Bank']
        st.dataframe(df_beneficiaries, use_container_width=True, hide_index=True)
    else:
        st.info("No beneficiaries added yet.")

    st.markdown("---")
    st.subheader("Add New Beneficiary")
    with st.form("add_beneficiary_form", clear_on_submit=True):
        b_name = st.text_input("Beneficiary Name (e.g., Vendor Company Ltd)")
        b_acc_name = st.text_input("Account Name")
        b_acc_no = st.text_input("Account Number")
        b_bank = st.text_input("Bank Name")

        if st.form_submit_button("Add Beneficiary"):
            if b_name and b_acc_name and b_acc_no and b_bank:
                if b_name in st.session_state.beneficiaries:
                    st.warning("Beneficiary with this name already exists. Use update section to modify.")
                else:
                    st.session_state.beneficiaries[b_name] = {
                        "Account Name": b_acc_name,
                        "Account No": b_acc_no,
                        "Bank": b_bank
                    }
                    save_data(st.session_state.beneficiaries, BENEFICIARIES_FILE)
                    st.success(f"Beneficiary '{b_name}' added.")
                    st.rerun()
            else:
                st.error("Please fill all beneficiary fields.")

    st.markdown("---")
    st.subheader("Update/Delete Beneficiary")
    # Only allow selection of actual beneficiaries, not the "Other" placeholder
    b_edit_options = [""] + [k for k in st.session_state.beneficiaries.keys() if k != "Other (Manually Enter Details)"]
    selected_b_name = st.selectbox("Select Beneficiary to Update/Delete", options=b_edit_options)

    if selected_b_name:
        selected_b_data = st.session_state.beneficiaries.get(selected_b_name, {})
        with st.form(f"edit_beneficiary_form_{selected_b_name}"):
            updated_b_acc_name = st.text_input("Account Name", value=selected_b_data.get("Account Name", ""))
            updated_b_acc_no = st.text_input("Account Number", value=selected_b_data.get("Account No", ""))
            updated_b_bank = st.text_input("Bank Name", value=selected_b_data.get("Bank", ""))

            col_b_edit, col_b_del = st.columns(2)
            with col_b_edit:
                if st.form_submit_button("Update Beneficiary"):
                    if updated_b_acc_name and updated_b_acc_no and updated_b_bank:
                        st.session_state.beneficiaries[selected_b_name] = {
                            "Account Name": updated_b_acc_name,
                            "Account No": updated_b_acc_no,
                            "Bank": updated_b_bank
                        }
                        save_data(st.session_state.beneficiaries, BENEFICIARIES_FILE)
                        st.success(f"Beneficiary '{selected_b_name}' updated.")
                        st.rerun()
                    else:
                        st.error("Please fill all update fields.")
            with col_b_del:
                if st.form_submit_button("Delete Beneficiary", type="primary"):
                    # Add confirmation to delete
                    st.warning(f"Are you sure you want to delete '{selected_b_name}'?")
                    if st.button(f"Confirm Delete '{selected_b_name}'", key=f"confirm_delete_b_{selected_b_name}"):
                        del st.session_state.beneficiaries[selected_b_name]
                        save_data(st.session_state.beneficiaries, BENEFICIARIES_FILE)
                        st.success(f"Beneficiary '{selected_b_name}' deleted.")
                        st.rerun()
    else:
        st.info("Select a beneficiary to update or delete.")


# --- Admin Section: Manage HR Policies (New) ---
def admin_manage_hr_policies():
    st.title("📜 Admin Panel - Manage HR Policies")

    st.subheader("Edit Existing Policies")
    policy_names = list(st.session_state.hr_policies.keys())
    selected_policy_name = st.selectbox("Select Policy to Edit", options=[""] + policy_names)

    if selected_policy_name:
        current_policy_content = st.session_state.hr_policies.get(selected_policy_name, "")
        updated_policy_content = st.text_area(f"Edit Content for {selected_policy_name}", value=current_policy_content, height=400)
        
        col_policy_edit, col_policy_delete = st.columns(2)
        with col_policy_edit:
            if st.button(f"Save Changes to {selected_policy_name}"):
                st.session_state.hr_policies[selected_policy_name] = updated_policy_content
                save_data(st.session_state.hr_policies, HR_POLICIES_FILE)
                st.success(f"Policy '{selected_policy_name}' updated successfully!")
                st.rerun()
        with col_policy_delete:
            if st.button(f"Delete {selected_policy_name} Policy", type="primary"):
                # Add confirmation for deletion
                st.warning(f"Are you sure you want to delete the '{selected_policy_name}' policy?")
                if st.button(f"Confirm Delete Policy '{selected_policy_name}'", key=f"confirm_delete_policy_{selected_policy_name}"):
                    del st.session_state.hr_policies[selected_policy_name]
                    save_data(st.session_state.hr_policies, HR_POLICIES_FILE)
                    st.success(f"Policy '{selected_policy_name}' deleted.")
                    st.rerun()

    st.markdown("---")
    st.subheader("Add New Policy")
    with st.form("add_policy_form", clear_on_submit=True):
        new_policy_name = st.text_input("New Policy Name")
        new_policy_content = st.text_area("New Policy Content", height=300)

        if st.form_submit_button("Add New Policy"):
            if new_policy_name and new_policy_content:
                if new_policy_name in st.session_state.hr_policies:
                    st.error("Policy with this name already exists. Please choose a different name or edit the existing policy.")
                else:
                    st.session_state.hr_policies[new_policy_name] = new_policy_content
                    save_data(st.session_state.hr_policies, HR_POLICIES_FILE)
                    st.success(f"New policy '{new_policy_name}' added successfully!")
                    st.rerun()
            else:
                st.error("Please provide both a name and content for the new policy.")

# --- Main Application Logic ---
def main():
    setup_initial_data() # Ensure initial data is set up on first run or if files are empty

    if not st.session_state.logged_in:
        login_form()
    else:
        display_sidebar()

        # Display the selected page based on session state
        if st.session_state.current_page == "dashboard":
            display_dashboard()
        elif st.session_state.current_page == "my_profile":
            display_my_profile()
        elif st.session_state.current_page == "leave_request":
            leave_request_form()
        elif st.session_state.current_page == "view_leave_applications":
            view_leave_applications()
        elif st.session_state.current_page == "opex_capex_form":
            opex_capex_form()
        elif st.session_state.current_page == "manage_opex_capex_approvals": # New page
            # Only admin can access this
            if st.session_state.current_user and st.session_state.current_user['role'] == 'admin':
                manage_opex_capex_approvals()
            else:
                st.error("Access Denied: You do not have permission to view this page.")
                st.session_state.current_page = "dashboard" # Redirect to dashboard
                st.rerun()
        elif st.session_state.current_page == "view_opex_capex_requests":
            view_opex_capex_requests()
        elif st.session_state.current_page == "performance_goal_setting":
            performance_goal_setting()
        elif st.session_state.current_page == "self_appraisal":
            self_appraisal()
        elif st.session_state.current_page == "hr_policies": # New page
            display_hr_policies()
        elif st.session_state.current_page == "my_payslips": # New page
            display_my_payslips()
        elif st.session_state.current_page == "manage_users": # New admin page
            if st.session_state.current_user and st.session_state.current_user['role'] == 'admin':
                admin_manage_users()
            else:
                st.error("Access Denied: You do not have permission to view this page.")
                st.session_state.current_page = "dashboard"
                st.rerun()
        elif st.session_state.current_page == "upload_payroll": # New admin page
            if st.session_state.current_user and st.session_state.current_user['role'] == 'admin':
                admin_upload_payroll()
            else:
                st.error("Access Denied: You do not have permission to view this page.")
                st.session_state.current_page = "dashboard"
                st.rerun()
        elif st.session_state.current_page == "manage_beneficiaries": # New admin page
            if st.session_state.current_user and st.session_state.current_user['role'] == 'admin':
                admin_manage_beneficiaries()
            else:
                st.error("Access Denied: You do not have permission to view this page.")
                st.session_state.current_page = "dashboard"
                st.rerun()
        elif st.session_state.current_page == "manage_hr_policies": # New admin page
            if st.session_state.current_user and st.session_state.current_user['role'] == 'admin':
                admin_manage_hr_policies()
            else:
                st.error("Access Denied: You do not have permission to view this page.")
                st.session_state.current_page = "dashboard"
                st.rerun()

if __name__ == "__main__":
    main()
