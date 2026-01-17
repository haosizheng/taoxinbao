import os
import json
import base64
from openai import OpenAI
from fpdf import FPDF
import streamlit as st
import io
import time
import requests
from aliyunsdkcore.request import CommonRequest

# --- UI CONSTANTS ---
ICONS = {
    "negotiator": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M5 8a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm4 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm4 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/><path d="M2.165 15.803l.02-.004c1.83-.363 2.948-.842 3.468-1.105A9.06 9.06 0 0 0 8 15c4.418 0 8-3.134 8-7s-3.582-7-8-7-8 3.134-8 7c0 1.76.743 3.37 1.97 4.6a10.437 10.437 0 0 1-1.805 2.203zM13.84 4.01a.5.5 0 0 1 .157.651l-3.75 6a.5.5 0 0 1-.702.12l-2.5-1.875-3.007 3.34a.5.5 0 1 1-.742-.673l3.5-3.889a.5.5 0 0 1 .702-.047l2.5 1.875 3.257-5.211a.5.5 0 0 1 .635-.15z"/></svg>""",
    "archivist": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M14 4.5V14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h5.5L14 4.5zm-3 0A1.5 1.5 0 0 1 9.5 3V1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V4.5h-2z"/></svg>""",
    "lawyer": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M8 1a1 1 0 0 1 1 1v.618l.39.39a.5.5 0 0 1-.708.707L8.3 3.325V13H9a1 1 0 1 1 0 2H7a1 1 0 1 1 0-2h.7V3.325L7.31 3.712a.5.5 0 1 1-.707-.707l.39-.39V2a1 1 0 0 1 1-1zM2 11.5a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 0 1h-2a.5.5 0 0 1-.5-.5zm9 0a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 0 1h-2a.5.5 0 0 1-.5-.5zM1.5 14a.5.5 0 0 1 .5-.5h12a.5.5 0 0 1 0 1H2a.5.5 0 0 1-.5-.5z"/></svg>""",
    "home": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16"><path d="M8.354 1.146a.5.5 0 0 0-.708 0l-6 6A.5.5 0 0 0 2.146 7.5L3 6.707V13.5a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5V6.707l.854.793a.5.5 0 0 0 .708-.708l-6-6z"/></svg>""",
    "plus": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-0 1h-1a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/></svg>""",
    "trash": """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16"><path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/><path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/></svg>""",
    "robot": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M6 12.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5ZM3 8.062C3 6.76 4.235 5.765 5.53 5.886a26.58 26.58 0 0 0 4.94 0C11.765 5.765 13 6.76 13 8.062v1.157a4.417 4.417 0 0 1 0 8.357V19a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1v-1.424a4.417 4.417 0 0 1 0-8.357V8.062Zm4.5 3.938a.5.5 0 1 0 0-1 .5.5 0 0 0 0 1Zm2.5 0a.5.5 0 1 0 0-1 .5.5 0 0 0 0 1ZM4.5 13a.5.5 0 1 1 0-1 .5.5 0 0 1 0 1Zm7 0a.5.5 0 1 1 0-1 .5.5 0 0 1 0 1Z"/></svg>""",
    "rocket": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M8 8s.5-4 3-7c0 0 1.5 4 4 6 0 0-4 1.5-6 4 0 0-4 .5-7 3 0 0 4 1.5 6 4zM2 14.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 0 1h-1a.5.5 0 0 1-.5-.5z"/></svg>""",
    "toolkit": """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="currentColor" viewBox="0 0 16 16"><path d="M8 1a2 2 0 0 1 2 2v2H6V3a2 2 0 0 1 2-2zm3 4V3a3 3 0 0 0-6 0v2H2a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-3zM2 6h12a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1z"/></svg>""",
    "camera": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M15 12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h1.172a3 3 0 0 0 2.12-.879l.83-.828A1 1 0 0 1 6.827 3h2.344a1 1 0 0 1 .707.293l.828.828A3 3 0 0 0 12.828 5H14a1 1 0 0 1 1 1v6zM2 4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-1.172a2 2 0 0 1-1.414-.586l-.828-.828A2 2 0 0 0 9.172 2H6.828a2 2 0 0 0-1.414.586l-.828.828A2 2 0 0 1 3.172 4H2z"/><path d="M8 11a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5zm0 1a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zM3 6.5a.5.5 0 1 1-1 0 .5.5 0 0 1 1 0z"/></svg>""",
    "back": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z"/></svg>""",
    "sos": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1zm0 1a6 6 0 1 1 0 12A6 6 0 0 1 8 2z"/><path d="M8 10a2 2 0 1 0 0-4 2 2 0 0 0 0 4z"/><path d="M8 11.5a3.5 3.5 0 1 1 0-7 3.5 3.5 0 0 1 0 7z"/></svg>""",
    "book": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M1 2.828c.885-.37 2.154-.769 3.388-.893 1.33-.134 2.458.063 3.112.752v9.746c-.935-.53-2.12-.603-3.213-.493-1.18.12-2.37.461-3.287.811V2.828zm7.5-.141c.654-.689 1.782-.886 3.112-.752 1.234.124 2.503.523 3.388.893v9.923c-.918-.35-2.107-.692-3.287-.81-1.094-.111-2.278-.039-3.213.492V2.687zM8 1.783C7.015.936 5.587.81 4.287.94c-1.514.153-3.042.672-3.994 1.105A.5.5 0 0 0 0 2.5v11a.5.5 0 0 0 .707.455c.882-.4 2.303-.881 3.68-.971 1.409-.092 2.599.176 3.243.81a.5.5 0 0 0 .73 0c.644-.634 1.834-.902 3.242-.81 1.377.09 2.798.572 3.68.971A.5.5 0 0 0 16 13.5v-11a.5.5 0 0 0-.293-.455c-.952-.433-2.48-.952-3.994-1.105C10.413.809 8.985.936 8 1.783z"/></svg>""",
    "warning": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/></svg>""",
    "feedback": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M16 8c0 3.866-3.582 7-8 7a9.06 9.06 0 0 1-2.347-.306c-.584.296-1.925.864-4.181 1.234-.2.032-.352-.176-.273-.362.354-.836.674-1.95.77-2.966C.744 11.37 0 9.76 0 8c0-3.866 3.582-7 8-7s8 3.134 8 7zM5 8a1 1 0 1 0-2 0 1 1 0 0 0 2 0zm4 0a1 1 0 1 0-2 0 1 1 0 0 0 2 0zm3 1a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/></svg>""",
    "person": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16"><path d="M11 6a3 3 0 1 1-6 0 3 3 0 0 1 6 0z"/><path fill-rule="evenodd" d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm8-7a7 7 0 0 0-5.468 11.37C3.242 11.226 4.805 10 8 10s4.757 1.225 5.468 2.37A7 7 0 0 0 8 1z"/></svg>""",
}

def render_header_with_icon(icon_key, title, level=3):
    icon_svg = ICONS.get(icon_key, "")
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 1rem; gap: 8px;">
        <span style="color: #E63946; display: flex; align-items: center;">{icon_svg}</span>
        <h{level} style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #333;">{title}</h{level}>
    </div>
    """, unsafe_allow_html=True)

def inject_custom_css():
    st.markdown("""
        <style>
            /* 1. Global Reset & Fonts */
            html, body, [data-testid="stAppViewContainer"], .stApp {
                background-color: #F8F9FA !important;
                color: #333333;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                margin: 0;
                padding: 0;
            }
            
            /* 2. Hide Streamlit Branding Truly */
            #MainMenu, footer, header, [data-testid="stHeader"] {
                display: none !important;
                height: 0 !important;
                width: 0 !important;
            }
            
            /* 3. Mobile Viewport Simulation (No Scrollbar) */
            ::-webkit-scrollbar { display: none; }
            
            /* Target all possible main containers to ensure total transparency */
            section.main, 
            div[data-testid="stAppViewBlockContainer"] {
                background-color: transparent !important;
                overflow: visible !important;
            }

            /* 4. The Central "Mobile Surface" Container */
            .block-container, div[data-testid="stMainBlockContainer"] {
                max-width: 500px !important;
                padding-top: 20px !important;
                padding-bottom: 200px !important; /* Fixed bottom room */
                padding-left: 15px !important;
                padding-right: 15px !important;
                background-color: #F8F9FA !important; /* Match root exactly */
                min-height: 100vh !important;
                box-shadow: 0 0 50px rgba(0,0,0,0.03);
                margin: auto;
                border-left: 0.5px solid rgba(0,0,0,0.03);
                border-right: 0.5px solid rgba(0,0,0,0.03);
            }
            
            /* Fixed Top Navbar - Constrained to Phone Width */
            .custom-navbar {
                position: fixed;
                top: 0;
                left: 50%;
                transform: translateX(-50%);
                width: 100%;
                max-width: 500px; /* Constrain */
                height: 50px;
                background-color: white;
                z-index: 999;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                font-weight: 600;
                font-size: 16px;
                color: #333;
            }
            
            /* Marquee Effect for Header */
            .marquee-container {
                width: 100%;
                overflow: hidden;
                white-space: nowrap;
                box-sizing: border-box;
                text-align: center; 
            }
            
            .marquee-text {
                display: inline-block;
                padding-left: 0;
                animation: marquee 10s linear infinite;
            }
            
            @keyframes marquee {
                0%   { transform: translate(0, 0); }
                100% { transform: translate(-100%, 0); }
            }
            
            /* 3. Bottom Layout & Navigation Cleanup (Fixed Point) */
            div[data-testid="stBottom"] {
                position: fixed !important;
                bottom: 0px !important;
                left: 50% !important;
                transform: translateX(-50%) !important;
                width: 100%;
                max-width: 500px; 
                z-index: 999999;
                background-color: #F8F9FA !important; /* Fully synced */
                padding: 0 !important;
                margin: 0 !important;
            }

            /* Aggressive removal of gaps in the bottom container hierarchy */
            div[data-testid="stBottomBlockContainer"],
            div[data-testid="stBottom"] [data-testid="stVerticalBlock"],
            div[data-testid="stBottom"] div {
                padding: 0 !important;
                margin: 0 !important;
                background-color: #F8F9FA !important; /* Sync background */
                border-top: none !important;
                gap: 0 !important;
                overflow: visible !important;
            }

            /* Custom fix for the click_detector iframe parent */
            div[data-testid="stBottom"] iframe {
                height: 85px !important;
                display: block !important;
                vertical-align: bottom !important;
            }

            /* 5. Modern Input Fields (Search-bar style) - Single Border Fix */
            div[data-testid="stTextInput"] input, 
            div[data-testid="stTextArea"] textarea {
                background-color: #F1F3F5 !important;
                border: none !important; /* Force no border on inner element */
                border-radius: 12px !important;
                padding: 12px 16px !important;
                color: #212529 !important;
                transition: all 0.2s ease !important;
                box-shadow: none !important;
            }

            /* Target the wrapper for the focus border to avoid double lines */
            div[data-testid="stTextInput"] > div, 
            div[data-testid="stTextArea"] > div {
                border: 1px solid transparent !important;
                border-radius: 12px !important;
                transition: all 0.2s ease !important;
                background-color: #F1F3F5 !important;
            }

            div[data-testid="stTextInput"] > div:focus-within, 
            div[data-testid="stTextArea"] > div:focus-within {
                border: 1px solid #E63946 !important;
                background-color: white !important;
                box-shadow: 0 0 0 3px rgba(230, 57, 70, 0.1) !important;
            }

            /* Fix label spacing */
            div[data-testid="stWidgetLabel"] p {
                font-size: 14px !important;
                font-weight: 500 !important;
                margin-bottom: 6px !important;
                color: #495057 !important;
            }
            /* 6. Wizard & Progress Styles */
            .stProgress > div > div > div > div {
                background-color: #E63946 !important;
            }
            .stProgress p {
                font-weight: 600 !important;
                color: #495057 !important;
            }

            /* Custom Big Button Utility (used in Wizard) */
            .big-btn-wrapper div[data-testid="stButton"] button {
                height: 3.5rem !important;
                font-size: 1.1rem !important;
                font-weight: 700 !important;
                border-radius: 14px !important;
            }
            .secondary-btn-wrapper div[data-testid="stButton"] button {
                background-color: #F1F3F5 !important;
                color: #495057 !important;
                border: 1px solid #DEE2E6 !important;
            /* 7. Card Style for Containers (Native st.container(border=True)) */
            div[data-testid="stVerticalBlockBorderWrapper"] {
                background-color: white !important;
                border-radius: 16px !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
                border: 1px solid rgba(0,0,0,0.02) !important;
                padding: 1.5rem !important;
                margin-bottom: 1.2rem;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Inject scoped styles for Home Page elements
    st.markdown("""
        <style>
        .orange-banner {
            background-color: #E88349;
            color: white;
            padding: .5rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 10px rgba(232, 131, 73, 0.2);
            font-size: 0.95rem;
        }
        

        </style>
    """, unsafe_allow_html=True)

# Load Prompts
try:
    with open("prompts.json", "r", encoding="utf-8") as f:
        PROMPTS = json.load(f)
except FileNotFoundError:
    PROMPTS = {}

# Configuration
MODELSCOPE_API_BASE = "https://api-inference.modelscope.cn/v1/"
# User provided specific model IDs
MODEL_TEXT = "Qwen/Qwen3-235B-A22B-Instruct-2507"
MODEL_VL = "Qwen/Qwen3-VL-235B-A22B-Instruct"

def load_local_token():
    """
    Helper to load token from ms_deploy.json for local development
    if environment variable is missing.
    """
    try:
        with open("ms_deploy.json", "r") as f:
            config = json.load(f)
            for env in config.get("environment_variables", []):
                if env["name"] == "MODELSCOPE_ACCESS_TOKEN":
                    return env["value"]
    except:
        pass
    return None

def get_client(api_key=None):
    """
    Get OpenAI client configured for ModelScope.
    Prioritize explicitly passed key, then env var, then ms_deploy.json.
    """
    token = api_key or os.getenv("MODELSCOPE_ACCESS_TOKEN") or os.getenv("DASHSCOPE_API_KEY") or load_local_token()
    if not token:
        return None
    return OpenAI(
        api_key=token,
        base_url=MODELSCOPE_API_BASE,
    )

def call_qwen_max(prompt, system_prompt=None, api_key=None):
    """
    Call Qwen-3 Text Model via OpenAI SDK.
    """
    client = get_client(api_key)
    if not client:
        return "Error: Please configure API Token."
    
    sys_prompt = system_prompt or PROMPTS.get("negotiator_system", "You are a helpful assistant.")
    
    try:
        completion = client.chat.completions.create(
            model=MODEL_TEXT,
            messages=[
                {'role': 'system', 'content': sys_prompt},
                {'role': 'user', 'content': prompt}
            ],
            stream=False
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"API Error: {str(e)}"

def get_alibaba_asr_token(ak_id, ak_secret):
    """Get temporary token for Alibaba Cloud NLS service using classic stable SDK."""
    client = AcsClient(ak_id, ak_secret, "cn-shanghai")
    request = CommonRequest()
    request.set_domain("nls-meta.cn-shanghai.aliyuncs.com")
    request.set_version("2019-02-28")
    request.set_action_name("CreateToken")
    request.set_protocol_type('https')
    request.set_accept_format('json')
    try:
        response = client.do_action_with_exception(request)
        j = json.loads(response)
        if "Token" in j:
            return j["Token"]["Id"]
        else:
            print(f"Alibaba API error response: {j}")
            return None
    except Exception as e:
        print(f"Alibaba Token classic SDK error: {e}")
        return None

def transcribe_audio_alibaba(audio_bytes):
    """
    Transcribe audio bytes utilizing Alibaba Cloud NLS REST API (Short Sentence Recognition).
    Normalizes audio to 16kHz WAV format first.
    """
    ak_id = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID") or st.secrets.get("ALIBABA_CLOUD_ACCESS_KEY_ID")
    ak_secret = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET") or st.secrets.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
    app_key = os.getenv("ALIBABA_CLOUD_APP_KEY") or st.secrets.get("ALIBABA_CLOUD_APP_KEY")
    
    if not all([ak_id, ak_secret, app_key]):
        return "Error: Alibaba Cloud credentials (AK_ID, AK_Secret, APP_KEY) not found in environment or st.secrets."
    
    token = get_alibaba_asr_token(ak_id, ak_secret)
    if not token:
        return "Error: Failed to obtain Alibaba ASR token. Check permissions (AliyunNLSFullAccess)."
    
    # 1. Normalize Audio (16k 16bit mono WAV)
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        out_buf = io.BytesIO()
        audio.export(out_buf, format="wav")
        processed_data = out_buf.getvalue()
    except Exception as e:
        return f"Audio Processing Error: {e}"

    # 2. Call Alibaba ASR REST API
    url = f"http://nls-gateway-cn-shanghai.aliyuncs.com/stream/v1/asr?appkey={app_key}"
    headers = {
        "X-NLS-Token": token,
        "Content-Type": "application/octet-stream"
    }
    
    try:
        res = requests.post(url, headers=headers, data=processed_data)
        res_json = res.json()
        if res_json.get("status") == 20000000:
            return res_json.get("result", "")
        else:
            return f"ASR Error: {res_json.get('message', 'Unknown error code: ' + str(res_json.get('status')))}"
    except Exception as e:
        return f"ASR Request Error: {e}"

def call_qwen_vl(image_paths, prompt_text=None, api_key=None):
    """
    Call Qwen-3 VL Model via OpenAI SDK.
    image_paths: list of local file paths.
    """
    client = get_client(api_key)
    if not client:
        return "Error: Please configure API Token."
    
    prompt_text = prompt_text or PROMPTS.get("evidence_extract_prompt", "Describe this image.")
    
    content_payload = []
    
    # 1. Add Images (Base64 encoding required for local files with OpenAI Schema usually, 
    # but ModelScope API might support URLs. For local Streamlit, we must use Base64).
    for img_path in image_paths:
        try:
            with open(img_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                # Determine detailed mime type if possible, default to jpeg
                mime_type = "image/jpeg"
                if img_path.lower().endswith(".png"):
                    mime_type = "image/png"
                
                content_payload.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{base64_image}"
                    }
                })
        except Exception as e:
            return f"Error reading image {img_path}: {str(e)}"

    # 2. Add Text
    content_payload.append({"type": "text", "text": prompt_text})

    try:
        completion = client.chat.completions.create(
            model=MODEL_VL,
            messages=[
                {
                    "role": "user",
                    "content": content_payload
                }
            ],
            stream=False
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"VL API Error: {str(e)}"

def generate_pdf(data, filename="evidence.pdf", content=None):
    """
    Generate PDF using specific Chinese font.
    If 'content' is provided, use it directly.
    Otherwise, fallback to template using 'data'.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Register Font
    font_path = "public/fonts/SourceHanSansSC-Medium.ttf"
    try:
        pdf.add_font('SourceHanSansSC', '', font_path, uni=True)
        pdf.set_font('SourceHanSansSC', '', 12)
    except Exception as e:
        # Fallback if font missing (Dev environment)
        print(f"Font loading error: {e}")
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, "Error: Chinese font not found. Displaying fallback text.", 0, 1)

    # Content Logic
    if content:
        # Use full AI generated text
        try:
            pdf.multi_cell(0, 10, content)
        except Exception as e:
            pdf.cell(0, 10, f"Error rendering content: {e}", 0, 1)
    else:
        # Legacy: Use template from prompts.json
        template = PROMPTS.get("pdf_template_text", "Notice to Pay: {amount}")
        try:
            # Basic validation to avoid KeyError
            safe_data = {k: data.get(k, 'N/A') for k in ['debtor', 'u_name', 'amount', 'date']}
            text = template.format(**safe_data)
            pdf.multi_cell(0, 10, text)
        except Exception as e:
            pdf.cell(0, 10, f"Error generating content: {e}", 0, 1)

    pdf.output(filename)
    return filename

def generate_case_brief_pdf(content, images=None, filename="case_brief.pdf"):
    """
    Generate a Case Brief PDF.
    content: Markdown-formatted text.
    images: List of image paths to append/embed.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Register Font (Reuse from generate_pdf)
    font_path = "public/fonts/SourceHanSansSC-Medium.ttf"
    try:
        pdf.add_font('SourceHanSansSC', '', font_path, uni=True)
        pdf.set_font('SourceHanSansSC', '', 12)
    except Exception as e:
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, "错误：未找到中文字体。", 0, 1)

    # 1. Title
    pdf.set_font('SourceHanSansSC', '', 18)
    pdf.cell(0, 15, "案件法律事实摘要（律师接案笔录）", 0, 1, 'C')
    pdf.ln(5)

    # 2. Main Content (Text)
    pdf.set_font('SourceHanSansSC', '', 12)
    # Simple line handling for now. 
    # Better: simple parser for ## Headers to bold them.
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            pdf.ln(2)
            continue
            
        if line.startswith("## "):
            pdf.ln(5)
            pdf.set_font('SourceHanSansSC', '', 14)
            pdf.cell(0, 10, line.replace("## ", ""), 0, 1)
            pdf.set_font('SourceHanSansSC', '', 12)
        else:
            pdf.multi_cell(0, 8, line)

    # 3. Evidence Images
    if images and len(images) > 0:
        pdf.add_page()
        pdf.set_font('SourceHanSansSC', '', 14)
        pdf.cell(0, 10, "附：关键证据图片", 0, 1)
        pdf.ln(5)
        
        for idx, img_path in enumerate(images):
            try:
                # Add Header
                pdf.set_font('SourceHanSansSC', '', 10)
                pdf.cell(0, 10, f"证据附件 {idx+1}: {os.path.basename(img_path)}", 0, 1)
                
                # Image
                # Calculate width to fit page (A4 width approx 210mm, margin 10mm*2 -> 190mm)
                pdf.image(img_path, w=170) 
                pdf.ln(10)
            except Exception as e:
                pdf.cell(0, 10, f"[无法加载图片: {os.path.basename(img_path)}]", 0, 1)

    pdf.output(filename)
    return filename

# Expose constants for APP
LAWYER_SYSTEM_PROMPT_TEMPLATE = PROMPTS.get("lawyer_system_template", "")

import time

def force_scroll_to_top():
    """
    Inject JS to force scroll to top. 
    Use a unique key or specific timestamp to ensure re-execution.
    """
    js = f"""
    <script>
        // Force scroll top for both body and main streamlit container
        window.scrollTo(0,0);
        var main = window.parent.document.querySelector('.main');
        if (main) {{ main.scrollTop = 0; }}
        
        var docs = window.parent.document.querySelectorAll('[data-testid="stAppViewContainer"]');
        if (docs && docs.length > 0) {{ docs[0].scrollTop = 0; }}
    </script>
    <div style="display:none;" id="scroll-marker-{int(time.time()*1000)}"></div>
    """
    st.components.v1.html(js, height=0)
