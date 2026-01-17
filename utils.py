import os
import json
import base64
from openai import OpenAI
from fpdf import FPDF
import streamlit as st

def inject_custom_css():
    st.markdown("""
        <style>
            /* 1. Global Reset & Fonts */
            .stApp {
                background-color: #F5F7FA; /* Light Grey Background */
                color: #333333; /* Force Dark Text */
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
            }
            
            /* 2. Hide Streamlit Branding */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;} 
            
            /* 3. Mobile Viewport Optimization */
            .block-container {
                padding-top: 2rem !important;
                padding-bottom: 90px !important; /* Space for fixed bottom sac nav (approx 60-80px) */
                max-width: 100% !important;
            }

            /* 4. Card Style for Containers (Native st.container(border=True)) */
            div[data-testid="stVerticalBlockBorderWrapper"] {
                background-color: white;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.05);
                border: 1px solid #F0F0F0;
                padding: 1rem;
                margin-bottom: 1rem;
            }
            div[data-testid="stVerticalBlockBorderWrapper"] > div {
                 /* Fix internal padding if needed */
            }

            /* 5. Input Fields Styling */
            .stTextInput input, .stSelectbox div[data-baseweb="select"] {
                border-radius: 12px !important;
                border: 1px solid #E0E0E0;
            }
            
            /* 6. Button Styling */
            .stButton button {
                border-radius: 12px;
                height: 3rem;
                font-weight: 600;
            }

            /* 7. Tabs Styling */
            .stTabs [data-baseweb="tab-list"] {
                gap: 1rem;
                background-color: transparent;
            }
            .stTabs [data-baseweb="tab"] {
                background-color: white;
                border-radius: 8px;
                padding: 0.5rem 1rem;
                border: 1px solid #eee;
            }
            .stTabs [aria-selected="true"] {
                background-color: #FF4B4B !important;
                color: white !important;
                border: none;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Inject scoped styles for Home Page elements
    st.markdown("""
        <style>
        .orange-banner {
            background-color: #E88349;
            color: white;
            padding: 1.2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 10px rgba(232, 131, 73, 0.2);
            font-size: 0.95rem;
        }
        
        .blue-info-box {
            background-color: #E3F2FD;
            color: #0D47A1;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            border: 1px solid #BBDEFB;
        }

        .feature-button {
            background-color: #D9534F; /* Reddish */
            color: white !important;
            border-radius: 12px;
            padding: 1rem;
            text-align: left;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border: none;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0px;
            text-decoration: none;
        }
        .feature-button:hover {
            opacity: 0.9;
            color: white !important;
        }
        .feature-icon {
            font-size: 1.5rem;
            margin-right: 0.5rem;
        }
        .feature-text {
            font-weight: 600;
            font-size: 1rem;
        }
        .feature-sub {
            font-size: 0.75rem;
            opacity: 0.9;
            font-weight: normal;
        }
        
        /* Grid Alignment Helper */
        .feature-grid-col {
            padding: 0.3rem !important;
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

def generate_pdf(data, filename="evidence.pdf"):
    """
    Generate PDF using specific Chinese font.
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

    # Use template from prompts.json
    template = PROMPTS.get("pdf_template_text", "Notice to Pay: {amount}")
    
    try:
        # Basic validation to avoid KeyError
        safe_data = {k: data.get(k, 'N/A') for k in ['debtor', 'u_name', 'amount', 'date']}
        content = template.format(**safe_data)
        
        pdf.multi_cell(0, 10, content)
    except Exception as e:
        pdf.cell(0, 10, f"Error generating content: {e}", 0, 1)

    pdf.output(filename)
    return filename

# Expose constants for APP
LAWYER_SYSTEM_PROMPT_TEMPLATE = PROMPTS.get("lawyer_system_template", "")
