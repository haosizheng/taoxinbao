import streamlit as st
import utils

import streamlit_antd_components as sac

def parse_negotiator_response(text):
    """Parses old Zhang's response into Dict structure for UI cards."""
    import re
    
    analysis = ""
    strategies = []
    
    # Extract Analysis (Steps 1 & 2)
    # The prompt structure: 📌【第一步：一句话定心丸】... 🔍【第二步：一眼看穿】... 💡【第三步：三个锦囊】...
    step1 = re.search(r"📌【第一步：一句话定心丸】(.*?)(?=🔍|$)", text, re.S)
    step2 = re.search(r"🔍【第二步：一眼看穿】(.*?)(?=💡|$)", text, re.S)
    
    if step1: analysis += f"**定心丸**：{step1.group(1).strip()}\n\n"
    if step2: analysis += f"**点套路**：{step2.group(1).strip()}"
    
    # Extract Strategies
    # They look like: 1. 🍵 **讲情面**...
    strat_parts = re.findall(r"(\d\.\s?.*?)\n(.*?)(?=\d\.\s?|$)", text, re.S)
    for title, content in strat_parts:
        strategies.append({
            "title": title.strip(),
            "content": content.strip()
        })
        
    return analysis, strategies

def render_ai_result(res):
    analysis, strategies = parse_negotiator_response(res)
    
    # 1. Analysis Card
    st.markdown(f"""
    <div class="analysis-card">
        <div class="analysis-title">👨‍🦳 老张点拨</div>
        <div class="analysis-text">{analysis}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. Strategies
    st.markdown("#### 💡 三个锦囊话术")
    for i, s in enumerate(strategies):
        with st.container():
            st.markdown(f"""
            <div class="strategy-card">
                <div class="strategy-header">{s['title']}</div>
                <div class="strategy-text">{s['content']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action Row
            col1, col2 = st.columns([2, 1])
            with col2:
                if st.button("一键复制话术", key=f"copy_{i}", icon=":material/content_copy:", use_container_width=True):
                    st.components.v1.html(f"""
                        <script>
                        const text = `{s['content']}`;
                        const el = document.createElement('textarea');
                        el.value = text;
                        document.body.appendChild(el);
                        el.select();
                        document.execCommand('copy');
                        document.body.removeChild(el);
                        </script>
                    """, height=0)
                    st.toast("话术已复制，快去发给老板吧！")

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
        
        /* 4. AI Response Cards */
        .analysis-card {
            background-color: #E3F2FD;
            border-radius: 12px;
            padding: 20px;
            border-left: 5px solid #2196F3;
            margin-bottom: 20px;
        }
        .analysis-title {
            color: #0D47A1;
            font-weight: 700;
            margin-bottom: 8px;
            font-size: 1.1rem;
        }
        .analysis-text {
            color: #1565C0;
            line-height: 1.6;
            font-size: 1.05rem;
        }
        
        .strategy-card {
            background-color: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            border: 1px solid #F1F3F5;
            margin-bottom: 15px;
        }
        .strategy-header {
            font-weight: 700;
            font-size: 1rem;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .strategy-text {
            font-size: 1.1rem;
            line-height: 1.5;
            color: #333;
            margin-bottom: 5px;
            background: #F8F9FA;
            padding: 12px;
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    utils.render_header_with_icon("negotiator", "话术咨询")
    st.info(f"正在对抗：{d['boss']} (欠 {d['amount']}元)")
    
    # Mode Switcher
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
        
        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
        if st.button("生成主动催款话术", type="primary", use_container_width=True, key="initiate_btn"):
            if not token: st.error("请去【我的】配置 API 密钥")
            else:
                with st.spinner("老张正在斟酌语气..."):
                    sys_prompt = utils.PROMPTS.get("negotiator_initiate_template", "")
                    prompt = f"【背景】：{context_summary}\n请根据以上情况生成催款话术。"
                    res = utils.call_qwen_max(prompt, system_prompt=sys_prompt, api_key=token)
                    render_ai_result(res)
                    
    else: # 回复拖延
        st.write("老板回消息了？把他的话贴进来，我们拆解套路。")
        
        tab1, tab2 = st.tabs(["🎤 语音识别", "📝 文字输入"])
        
        user_txt = st.session_state.get("negotiator_user_txt", "")
        with tab1:
            audio_val = st.audio_input("点击开始说话", key="voice_input")
            
            if audio_val:
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

        from st_click_detector import click_detector
        
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
                分析并回击
            </a>
        </div>
        """
        clicked = click_detector(pill_html, key="pill_btn_click_v2")
        
        if clicked == "analyze_trigger":
            if not token: st.error("请去【我的】配置 API 密钥")
            elif not user_txt: st.toast("请输入或录入内容")
            else:
                with st.spinner("老张正在分析套路..."):
                    sys_prompt = utils.PROMPTS.get("negotiator_system", "")
                    prompt = f"【背景】：{context_summary}\n【对方回复】：{user_txt}\n请分析对方心理并给出回击。"
                    res = utils.call_qwen_max(prompt, system_prompt=sys_prompt, api_key=token)
                    render_ai_result(res)
                    # Add spacer to ensure results are visible above floating button
                    st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True)
