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


# Force Spacer at the bottom to ensure scroll passes fixed nav
st.markdown("<div style='height: 150px; visibility: hidden;'>Spacer</div>", unsafe_allow_html=True)

# --- Navigation Component (Fixed Bottom) ---
from streamlit_extras.bottom_container import bottom
from st_click_detector import click_detector

with bottom():
    # Current Mode for Styling
    curr = st.session_state.app_mode
    
    # Define Colors
    active_color = "#E63946" # Deep red for active state
    inactive_color = "#8E8E93" # iOS-style grey
    
    # Helper to get style
    def get_nav_style(is_active):
        color = active_color if is_active else inactive_color
        weight = "600" if is_active else "400"
        return f"color: {color}; font-weight: {weight};"

    # SVG Icons (Simple Paths)
    # Home Icon
    svg_home = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16"><path d="M8.707 1.5a1 1 0 0 0-1.414 0L.646 8.146a.5.5 0 0 0 .708.708L2 8.207V13.5A1.5 1.5 0 0 0 3.5 15h9a1.5 1.5 0 0 0 1.5-1.5V8.207l.646.647a.5.5 0 0 0 .708-.708L13 5.793V2.5a.5.5 0 0 0-.5-.5h-1a.5.5 0 0 0-.5.5v1.293L8.707 1.5Z"/><path d="m8 3.293 6 6V13.5a.5.5 0 0 1-.5.5h-9a.5.5 0 0 1-.5-.5V9.293l6-6Z"/></svg>"""
    if curr in ["HOME", "WIZARD", "WORKSPACE"]: svg_home = svg_home.replace("currentColor", active_color) # Fill if active? Or just use stroke/fill style. SVG inherits color usually.
    
    # Folder Icon (Recovery) - User asked for Folder icon style
    svg_rec = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16"><path d="M9.828 3h3.982a2 2 0 0 1 1.992 2.181l-.637 7A2 2 0 0 1 13.174 14H2.826a2 2 0 0 1-1.991-1.819l-.637-7a1.99 1.99 0 0 1 .342-1.31A2.197 2.197 0 0 1 2.189 3h2.711A1.936 1.936 0 0 1 6.608 2h2.72a1.936 1.936 0 0 1 1.5 1zM3.5 3a.5.5 0 0 0-.5.5V13a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5V3.5a.5.5 0 0 0-.5-.5H3.5z"/></svg>"""
    # Use a filled folder for better visibility
    svg_rec = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16"><path d="M1 3.5A1.5 1.5 0 0 1 2.5 2h2.764c.958 0 1.76.56 2.311 1.184C7.985 3.648 8.48 4 9 4h4.5A1.5 1.5 0 0 1 15 5.5v7a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 1 12.5v-9zM2.5 3a.5.5 0 0 0-.5.5V6h12v-.5a.5.5 0 0 0-.5-.5H9c-.964 0-1.71-.629-2.174-1.154C6.374 3.334 5.82 3 5.264 3H2.5zM14 7H2v5.5a.5.5 0 0 0 .5.5h11a.5.5 0 0 0 .5-.5V7z"/></svg>"""

    # Person Icon
    svg_me = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16"><path d="M11 6a3 3 0 1 1-6 0 3 3 0 0 1 6 0z"/><path fill-rule="evenodd" d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm8-7a7 7 0 0 0-5.468 11.37C3.242 11.226 4.805 10 8 10s4.757 1.225 5.468 2.37A7 7 0 0 0 8 1z"/></svg>"""

    # Determine Active States
    is_home = curr in ["HOME", "WIZARD", "WORKSPACE"]
    is_rec = curr == "RECOVERY"
    is_me = curr == "PROFILE"

    # CSS for Nav
    nav_css = """
    <style>
        body { margin: 0; padding: 0; background: #F8F9FA; overflow: hidden; }
        .nav-container {
            display: flex;
            justify-content: space-around;
            align-items: center;
            background: #F8F9FA;
            padding-top: 10px;
            padding-bottom: calc(15px + env(safe-area-inset-bottom, 0px));
            border-top: none; 
            width: 100%;
            height: 100%;
            box-sizing: border-box;
        }
        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            text-decoration: none;
            cursor: pointer;
            width: 33%;
            -webkit-tap-highlight-color: transparent;
            transition: all 0.2s;
        }
        .nav-icon {
            margin-bottom: 2px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .nav-text {
            font-size: 11px; /* Slightly smaller for iOS look */
            line-height: 1.2;
        }
    </style>
    """

    # HTML Structure
    html = f"""
    {nav_css}
    <div class="nav-container">
        <a class="nav-item" href="#" id="nav_home" style="{get_nav_style(is_home)}">
            <div class="nav-icon">{svg_home}</div>
            <div class="nav-text">首页</div>
        </a>
        <a class="nav-item" href="#" id="nav_recovery" style="{get_nav_style(is_rec)}">
            <div class="nav-icon">{svg_rec}</div>
            <div class="nav-text">讨薪</div>
        </a>
        <a class="nav-item" href="#" id="nav_profile" style="{get_nav_style(is_me)}">
            <div class="nav-icon">{svg_me}</div>
            <div class="nav-text">我的</div>
        </a>
    </div>
    """

    # Render - Explicitly set height to avoid the bottom gap
    # height=85 is enough for icons + text + safe area
    clicked_nav = click_detector(html, key="bottom_nav_click_v7")

    # Handle Navigation
    if clicked_nav == "nav_home" and not is_home:
        st.session_state.app_mode = "HOME"
        st.rerun()
    elif clicked_nav == "nav_recovery" and not is_rec:
        st.session_state.app_mode = "RECOVERY"
        st.rerun()
    elif clicked_nav == "nav_profile" and not is_me:
        st.session_state.app_mode = "PROFILE"
        st.rerun()