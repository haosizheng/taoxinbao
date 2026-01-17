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
import dashscope
from dashscope.audio.asr import Transcription

def inject_custom_css():
    st.markdown("""
        <style>
            /* 1. Global Reset & Fonts */
            .stApp {
                background-color: #e0e0e0; /* Desktop Background: Neural Grey */
                background-image: linear-gradient(#e0e0e0, #cfcfcf);
                background-attachment: fixed; /* Fix background during scroll */
                background-repeat: no-repeat;
                background-size: cover;
                color: #333333;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }
            
            /* 2. Hide Streamlit Branding */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;} 
            
            /* 3. Mobile Viewport Simulation (The "Phone") */
            ::-webkit-scrollbar {
                display: none;
            }
            
            /* Target both the section and the container for robust background */
            section.main {
                overflow: visible !important;
            }
            
            div[data-testid="stAppViewBlockContainer"] {
                overflow: visible !important;
            }

            .block-container {
                max-width: 500px !important;
                padding-top: 20px !important;
                padding-bottom: 200px !important; /* Back to generous padding */
                margin: 0 auto !important;
                
                /* Phone Screen Look */
                background-color: #F5F7FA;
                position: relative;
                display: flex !important;
                flex-direction: column !important;
                min-height: 100vh !important;
                height: auto !important;
                overflow: visible !important;
                box-shadow: 0 0 30px rgba(0,0,0,0.1); 
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
            
            /* Fixed Bottom Nav - Constrained to Phone Width */
            div[data-testid="stBottom"] {
                position: fixed;
                bottom: 0;
                left: 50% !important;
                transform: translateX(-50%) !important;
                width: 100%;
                max-width: 500px; /* Constrain */
                z-index: 999999;
                background-color: transparent; /* Container is transparent, child is white */
            }
            
            div[data-testid="stBottom"] > div {
                background-color: white; /* The actual nav bar bg */
                padding-bottom: 0px;
                box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
            }

            /* 4. Card Style for Containers (Native st.container(border=True)) */
            div[data-testid="stVerticalBlockBorderWrapper"] {
                background-color: white;
                border-radius: 16px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.04); /* Soft shadow */
                border: 1px solid rgba(0,0,0,0.03); /* Very subtle border */
                padding: 1.2rem;
                margin-bottom: 1.2rem;
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

def transcribe_audio_dashscope(audio_bytes):
    """
    Transcribe audio bytes using DashScope SenseVoice model.
    This replaces the previous NLS Token-based ASR.
    Supports local bytes processing.
    """
    # Prefer DASHSCOPE_API_KEY, fallback to MODELSCOPE_ACCESS_TOKEN
    api_key = os.getenv("DASHSCOPE_API_KEY") or st.secrets.get("DASHSCOPE_API_KEY") or os.getenv("MODELSCOPE_ACCESS_TOKEN") or load_local_token()
    
    if not api_key:
        return "Error: DASHSCOPE_API_KEY not found."

    dashscope.api_key = api_key
    
    # 1. Normalize Audio (SenseVoice is robust, but 16kHz WAV is standard)
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        out_buf = io.BytesIO()
        audio.export(out_buf, format="wav")
        processed_data = out_buf.getvalue()
    except Exception as e:
        return f"Audio Processing Error: {e}"

    # 2. Call SenseVoice (Non-streaming for simplicity in this demo)
    try:
        # Save temp file for DashScope local file upload support
        temp_filename = f"temp_voice_{int(time.time())}.wav"
        with open(temp_filename, "wb") as f:
            f.write(processed_data)
        
        task_response = dashscope.audio.asr.Transcription.call(
            model='sensevoice-v1',
            file_urls=[f"file://{os.path.abspath(temp_filename)}"],
            language_hints=['zh', 'en']
        )
        
        # Cleanup
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            
        if task_response.status_code == 200:
            # SenseVoice returns a list of results
            results = task_response.output.get('results', [])
            if results:
                # Get the transcription from the first file
                return results[0].get('transcription', "")
            return "Error: No transcription result found."
        else:
            return f"ASR Error: {task_response.message}"
            
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
