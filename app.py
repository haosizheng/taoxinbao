import streamlit as st
import utils
import os
import streamlit_antd_components as sac
import modules.home as home
import modules.wizard as wizard
import modules.workspace as workspace
import modules.profile as profile
import modules.recovery as recovery

# Page Config
st.set_page_config(
    page_title="Salary Shield 薪盾",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 1. Inject Mobile CSS
utils.inject_custom_css()

# --- Session State Init ---
if "cases" not in st.session_state:
    st.session_state.cases = []  # List of dicts
if "active_case_id" not in st.session_state:
    st.session_state.active_case_id = None
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "HOME" # HOME, WIZARD, WORKSPACE, RECOVERY
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

# Helper: Render Fixed Header
def render_header(title):
    # Check if title is long (simple heuristic for Chinese chars, approx 12-15)
    is_long = len(title) > 12
    
    content_html = title
    if is_long:
        # Wrap in marquee
        content_html = f'<div class="marquee-container"><span class="marquee-text">{title} &nbsp;&nbsp;&nbsp;&nbsp; {title}</span></div>'
        
    st.markdown(f"""
    <div class="custom-navbar">
        {content_html}
    </div>
    """, unsafe_allow_html=True)

# --- Main Layout ---
# Placeholder for content
content_placeholder = st.container()

# --- Dispatcher Logic ---
with content_placeholder:
    mode = st.session_state.app_mode
    
    if mode == "HOME":
        render_header("首页")
        home.render()
    elif mode == "RECOVERY":
        # Dynamic Header Logic
        case = get_active_case()
        if case:
            # Construct info string
            # e.g. "张三 - 5000元 - 拖欠3个月"
            d = case.get('dossier', {})
            boss = d.get('boss', '未知老板')
            amt = d.get('amount', '?')
            date = d.get('date', '')
            
            header_text = f"{boss} 欠薪{amt}元 {date}"
            render_header(header_text)
        else:
            render_header("讨薪")
            
        recovery.render()
    elif mode == "WIZARD":
        render_header("建立档案")
        wizard.render()
    elif mode == "WORKSPACE":
        # Dynamic Header based on case
        case = get_active_case()
        if not case:
            st.session_state.app_mode = "HOME"
            st.rerun()
        else:
            render_header("案卷工作台")
            token = get_api_token()
            workspace.render(case, token)
    elif mode == "PROFILE":
        render_header("我的")
        token = get_api_token()
        profile.render(None, token)

# --- Navigation Component (Fixed Bottom) ---
from streamlit_extras.bottom_container import bottom

with bottom():
    # Determine default index based on mode
    default_idx = 0
    if st.session_state.app_mode == "RECOVERY":
        default_idx = 1
    elif st.session_state.app_mode == "PROFILE":
        default_idx = 2
        
    selected_nav = sac.tabs(
        [
            sac.TabsItem(label='首页', icon='house'),
            sac.TabsItem(label='讨薪', icon='hammer'), # Hammer for recovery
            sac.TabsItem(label='我的', icon='person-circle'),
        ],
        align='center', 
        return_index=False,
        index=default_idx,
        key="main_nav_bar",
        use_container_width=True,
        variant='outline',
        height=60
    )

    # Logic to handle nav changes
    # Only rerun if the selection differs from the current mode's logical tab
    if selected_nav == '首页' and st.session_state.app_mode != "HOME" and st.session_state.app_mode != "WIZARD" and st.session_state.app_mode != "WORKSPACE": 
        # Note: WIZARD/WORKSPACE are sub-views of HOME technically, but typically clicking Home resets to root Home
        st.session_state.app_mode = "HOME"
        st.rerun()
    elif selected_nav == '讨薪' and st.session_state.app_mode != "RECOVERY":
        st.session_state.app_mode = "RECOVERY"
        st.rerun()
    elif selected_nav == '我的' and st.session_state.app_mode != "PROFILE":
        st.session_state.app_mode = "PROFILE"
        st.rerun()