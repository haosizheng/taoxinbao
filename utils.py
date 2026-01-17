import os
import dashscope
from dashscope.audio.asr import Recognition
from http import HTTPStatus
import json

# Ensure you set DASHSCOPE_API_KEY in your environment or passing it here
# dashscope.api_key = "YOUR_API_KEY"

def call_qwen_max(prompt, system_prompt="You are a helpful assistant."):
    """
    Call Qwen-Max for text generation.
    """
    try:
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': prompt}
        ]
        response = dashscope.Generation.call(
            dashscope.Generation.Models.qwen_max,
            messages=messages,
            result_format='message',  # set the result to be "message" format.
        )
        if response.status_code == HTTPStatus.OK:
            return response.output.choices[0]['message']['content']
        else:
            return f"Error: {response.code} - {response.message}"
    except Exception as e:
        return f"Exception: {str(e)}"

def recognize_audio(audio_file_path):
    """
    Use DashScope Paraformer for ASR (Speech to Text).
    This function assumes audio_file_path is a local path to a wav/mp3 file.
    """
    try:
        recognition = Recognition(model='paraformer-realtime-v1', format='wav', sample_rate=16000) 
        # Note: Paraformer-realtime might need specific format. 
        # For simple file file upload, 'paraformer-v1' (non-realtime) is easier for file processing.
        # Let's use 'paraformer-v1' for file transcription.
        
        # Simple implementation using the sensevoice or paraformer file API
        # Actually, let's use the standard Recognition call for file
        rec = Recognition(model='paraformer-v1', format='wav', sample_rate=16000)
        result = rec.call(audio_file_path)
        
        if result.status_code == HTTPStatus.OK:
            # The result format depends on the model, usually extracting text is needed
            # For paraformer-v1:
            if 'sentences' in result.output:
                 text = "".join([s['text'] for s in result.output['sentences']])
                 return text
            else:
                 # Fallback/Debug
                 return json.dumps(result.output, ensure_ascii=False)
        else:
             return f"ASR Error: {result.code} - {result.message}"
    except Exception as e:
        return f"ASR Exception: {str(e)}"

# System Prompts
NEGOTIATOR_SYSTEM_PROMPT = """
你是一位拥有15年经验的基层法律协调员，名字叫“老张”。你极具同理心，专门帮助工人讨薪。
你的语言风格接地气、稳重、有力量，通过“情理法”三个层面解决问题。
不要使用生硬的法律术语堆砌，而要把法律条文掰碎了讲给老板听。
"""

def call_qwen_vl(image_paths, prompt):
    """
    Call Qwen-VL-Max for image analysis.
    image_paths: list of local file paths or URLs.
    """
    try:
        messages = [
            {
                'role': 'user',
                'content': [
                    {'image': path} for path in image_paths
                ] + [{'text': prompt}]
            }
        ]
        response = dashscope.MultiModalConversation.call(
            model='qwen-vl-max',
            messages=messages
        )
        if response.status_code == HTTPStatus.OK:
            return response.output.choices[0]['message']['content'][0]['text']
        else:
            return f"Error: {response.code} - {response.message}"
    except Exception as e:
        return f"Exception: {str(e)}"

from fpdf import FPDF

def generate_pdf(data, filename="evidence.pdf"):
    """
    Generate a simple PDF 'Notice to Pay' based on extracted data.
    data: dict containing keys like 'debtor', 'amount', 'date', 'u_name'
    """
    class PDF(FPDF):
        def header(self):
            # Attempt to use a unicode font if available, otherwise standard
            # Since we can't easily rely on Chinese fonts being present in minimal env,
            # we will try to safe-guard or rely on system fonts if possible in dev.
            # IN PRODUCTION/COMPETITION: You must bundle a .ttf font.
            # For this MVP, we will try to use a standard font or just ASCII if font fails
            # But Chinese is required. Let's assume we can add a font or use a simple one if provided.
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, 'NOTICE TO PAY (DEMO)', 0, 1, 'C') # Fallback title

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # We really need a Chinese font for this to be useful.
    # In a real deployed app, we would bundle 'SimHei.ttf'
    # For now, let's write English placeholders or just the structure 
    # and instructions on how to enable Chinese.
    
    pdf.cell(0, 10, f"To: {data.get('debtor', 'Employer')}", 0, 1)
    pdf.cell(0, 10, f"From: {data.get('u_name', 'Employee')}", 0, 1)
    pdf.cell(0, 10, f"Date: {data.get('current_date', '')}", 0, 1)
    pdf.ln(10)
    
    pdf.multi_cell(0, 10, f"Subject: Formal Demand for Payment of {data.get('amount', '0')} RMB\n\n"
                          f"This letter serves as a formal notice regarding the unpaid wages...\n"
                          f"According to the Labor Law...\n\n"
                          f"(Note: Chinese font support requires uploading a .ttf file to the environment)")
    
    pdf.output(filename)
    return filename

