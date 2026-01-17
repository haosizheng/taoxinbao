import streamlit as st
import utils
import os
import modules.home as home
import modules.wizard as wizard
import modules.workspace as workspace

# Page Config
st.set_page_config(
    page_title="Salary Shield 薪盾",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Session State Init ---
if "cases" not in st.session_state:
    st.session_state.cases = []  # List of dicts
if "active_case_id" not in st.session_state:
    st.session_state.active_case_id = None
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "HOME" # HOME, WIZARD, WORKSPACE
if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 0
if "user_info" not in st.session_state:
    st.session_state.user_info = {"name": "张伟", "id": "U-8823102", "credits": 100}

# Helper: Get Token
def get_api_token():
    if "custom_api_key" in st.session_state and st.session_state.custom_api_key:
        return st.session_state.custom_api_key
    return os.getenv("MODELSCOPE_ACCESS_TOKEN") or utils.load_local_token()

# Helper: Get Active Case
def get_active_case():
    if not st.session_state.active_case_id:
        return None
    for c in st.session_state.cases:
        if c["id"] == st.session_state.active_case_id:
            return c
    return None

# --- Main Dispatcher ---
mode = st.session_state.app_mode

if mode == "HOME":
    home.render()
elif mode == "WIZARD":
    wizard.render()
elif mode == "WORKSPACE":
    case = get_active_case()
    if not case:
        st.session_state.app_mode = "HOME"
        st.rerun()
    else:
        token = get_api_token()
        workspace.render(case, token)