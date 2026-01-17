import os
import json
import base64
from openai import OpenAI
from fpdf import FPDF
import streamlit as st
import io
import time
import requests
from pydub import AudioSegment
from pydub import AudioSegment
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

def inject_custom_css():
    st.markdown("""
        <style>
            /* 1. Global Reset & Fonts */
            /* 1. Global Reset & Fonts */
            .stApp {
                background-color: #F8F9FA !important; /* Synced with mobile surface */
                color: #333333;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }
            
            /* 2. Hide Streamlit Branding */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;} 
            
            /* 3. Mobile Viewport Simulation (The "Phone") */
            ::-webkit-scrollbar { display: none; }
            
            /* Target all possible main containers to ensure transparency */
            section.main, 
            div[data-testid="stAppViewBlockContainer"],
            div[data-testid="stAppViewContainer"] {
                background-color: transparent !important;
                overflow: visible !important;
            }

            /* 4. The Central "Mobile Surface" */
            .block-container, div[data-testid="stMainBlockContainer"] {
                max-width: 500px !important;
                padding-top: 20px !important;
                padding-bottom: 50px !important;
                padding-left: 15px !important;
                padding-right: 15px !important;
                background-color: #F8F9FA !important; /* Fully synced with .stApp */
                min-height: 100vh !important;
                box-shadow: 0 0 40px rgba(0,0,0,0.05);
                margin: auto;
                border: 0.5px solid rgba(0,0,0,0.1);
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
                background-color: white !important; /* Force root to white */
                padding: 0 !important;
                margin: 0 !important;
            }

            /* Aggressive removal of gaps in the bottom container hierarchy */
            div[data-testid="stBottomBlockContainer"],
            div[data-testid="stBottom"] [data-testid="stVerticalBlock"],
            div[data-testid="stBottom"] div {
                padding: 0 !important;
                margin: 0 !important;
                background-color: white !important; /* Force all intermediate levels to white */
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
        pdf.cell(0, 10, "Error: Chinese font not found.", 0, 1)

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
