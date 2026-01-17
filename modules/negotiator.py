import streamlit as st
import utils

import streamlit_antd_components as sac

def render(case, token):
    d = case["dossier"]
    context_summary = f"用户身份：{d['name']}({d['job']})，地点：{d.get('place','未填')}。欠款人：{d['boss']}，金额：{d['amount']}元。"
    
    # Custom CSS for iOS-style UI
    st.markdown("""
    <style>
        /* 1. iOS Style Segmented Control Override */
        .st-emotion-cache-12w0qpk { 
            background-color: #EEEEEF !important;
            border-radius: 8px !important;
            padding: 2px !important;
        }
        
        /* 2. Recording Card */
        .recording-card {
            background-color: white;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            border: 1px solid rgba(0,0,0,0.02);
            margin: 10px 0;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        /* 3. Floating Pill Button */
        .pill-button-container {
            position: fixed;
            bottom: 90px; /* Above nav bar */
            left: 50%;
            transform: translateX(-50%);
            width: 100%;
            max-width: 460px; /* Screen width minus padding */
            z-index: 1000;
            padding: 0 20px;
            pointer-events: none; /* Let clicks pass through except for the button */
        }
        .pill-button {
            pointer-events: auto;
            background-color: #E63946;
            color: white !important;
            border-radius: 50px;
            padding: 16px 0;
            text-align: center;
            font-weight: 700;
            font-size: 16px;
            box-shadow: 0 8px 24px rgba(230, 57, 70, 0.3);
            cursor: pointer;
            transition: transform 0.1s, background-color 0.2s;
            width: 100%;
            display: block;
            text-decoration: none;
            border: none;
        }
        .pill-button:active {
            transform: scale(0.96);
            background-color: #D62839;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.subheader("💬 话术咨询")
    st.info(f"正在对抗：{d['boss']} (欠 {d['amount']}元)")
    
    # Mode Switcher - sac already looks fairly good, but we can wrap it
    mode = sac.segmented(
        items=[
            sac.SegmentedItem(label='主动要钱', icon='megaphone'),
            sac.SegmentedItem(label='回复拖延', icon='shield-check'),
        ],
        align='center', 
        use_container_width=True,
        return_index=False
    )
    
    st.markdown("<br>", unsafe_allow_html=True)

    if mode == "主动要钱":
        st.write("还没开口，或者想发新一轮消息？让老张帮你写。")
        
        # Use a hidden button that is triggered by the custom pill UI or just style the button
        # For simplicity and functionality, we use a container with a button and style it.
        # But Streamlit buttons are hard to "pill" perfectly without st.button native quirks.
        # We'll use the native button but style it as a pill in this specific context.
        
        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
        if st.button("🚀 生成主动催款话术", type="primary", use_container_width=True, key="initiate_btn"):
            if not token: st.error("请去【我的】配置 Token")
            else:
                with st.spinner("老张正在斟酌语气..."):
                    sys_prompt = utils.PROMPTS.get("negotiator_initiate_template", "")
                    prompt = f"【背景】：{context_summary}\n请根据以上情况生成催款话术。"
                    res = utils.call_qwen_max(prompt, system_prompt=sys_prompt, api_key=token)
                    st.write(res)
                    
    else: # 回复拖延
        st.write("老板回消息了？把他的话贴进来，我们拆解套路。")
        
        tab1, tab2 = st.tabs(["🎤 语音识别", "📝 文字输入"])
        
        user_txt = st.session_state.get("negotiator_user_txt", "")
        with tab1:
            audio_val = st.audio_input("点击开始说话", key="voice_input")
            
            if audio_val:
                # Use hash to detect actual new recording
                import hashlib
                audio_bytes = audio_val.read()
                current_hash = hashlib.md5(audio_bytes).hexdigest()
                last_hash = st.session_state.get("last_audio_hash")
                
                if current_hash != last_hash:
                    with st.spinner("老张正在听..."):
                        user_txt = utils.transcribe_audio_alibaba(audio_bytes)
                        st.session_state.last_audio_hash = current_hash
                        st.session_state.negotiator_user_txt = user_txt
                
                if user_txt.startswith("Error") or user_txt.startswith("ASR Error"):
                    st.error(user_txt)
                    user_txt = "" 
                else:
                    st.success(f"已识别：\"{user_txt}\"")
        
        with tab2:
            user_txt_input = st.text_area("输入老板的原话", height=120, placeholder="例如：过两天肯定给你...", key="text_input_area")
            if user_txt_input:
                user_txt = user_txt_input
                st.session_state.negotiator_user_txt = user_txt

        # Floating Pill Button Implementation
        # We use a trick: A hidden real button and a visible pill-styled link/div
        # However, to avoid complexity with st.button triggers, we'll style the ACTUAL button if possible
        # or use click_detector. Let's use click_detector for the Pill Button to maintain control.
        from st_click_detector import click_detector
        
        # Inject CSS directly into the component to handle iframe isolation
        pill_html = f"""
        <style>
            .pill-button-container {{
                display: flex;
                justify-content: center;
                width: 100%;
                padding: 10px 0;
            }}
            .pill-button {{
                background-color: #E63946;
                color: white !important;
                border-radius: 50px;
                padding: 16px 32px;
                text-align: center;
                font-weight: 700;
                font-size: 16px;
                box-shadow: 0 8px 24px rgba(230, 57, 70, 0.3);
                cursor: pointer;
                transition: transform 0.1s, background-color 0.2s;
                text-decoration: none;
                display: inline-block;
                width: 90%;
            }}
            .pill-button:active {{
                transform: scale(0.96);
                background-color: #D62839;
            }}
        </style>
        <div class="pill-button-container">
            <a href='#' id='analyze_trigger' class='pill-button'>
                🚀 分析并回击
            </a>
        </div>
        """
        clicked = click_detector(pill_html, key="pill_btn_click_v2")
        
        # Hidden native button as fallback or for state tracking if needed
        # But click_detector is enough.
        
        if clicked == "analyze_trigger":
            if not token: st.error("请去【我的】配置 Token")
            elif not user_txt: st.toast("请输入或录入内容")
            else:
                with st.spinner("老张正在分析套路..."):
                    sys_prompt = utils.PROMPTS.get("negotiator_system", "")
                    prompt = f"【背景】：{context_summary}\n【对方回复】：{user_txt}\n请分析对方心理并给出回击。"
                    res = utils.call_qwen_max(prompt, system_prompt=sys_prompt, api_key=token)
                    st.write(res)
                    # Add spacer to ensure results are visible above floating button
                    st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True)
