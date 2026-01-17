import streamlit as st

# Page Config
st.set_page_config(
    page_title="Salary Shield 薪盾",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar Navigation
st.sidebar.title("🛡️ Salary Shield 薪盾")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "功能导航",
    ["主页", "1. 沟通博弈 (Negotiator)", "2. 证据 & 告知书 (Archivist)", "3. 公益导航 & 律师 (Lighthouse)"]
)

st.sidebar.markdown("---")
st.sidebar.caption("赋能劳动者，让维权更简单。")

# Main Content
if page == "主页":
    st.title("🛡️ Salary Shield 薪盾")
    st.markdown("""
    ### 您的私人 AI 法律顾问
    
    我们为您提供一站式的讨薪支持：
    
    1. **沟通博弈**: 老板推诿不给钱？AI 帮您生成高情商回复。
    2. **证据存证**: 自动识别聊天截图，一键生成法律告知书。
    3. **公益导航**: 连接模拟律师与线下维权机构，让您不再孤单。
    
    👈 请在左侧选择功能开始使用。
    """)

elif page == "1. 沟通博弈 (Negotiator)":
    st.header("💬 沟通博弈模块")
    st.markdown("---")
    
    # API Key Configuration (Temporary for Dev)
    api_key = st.sidebar.text_input("DashScope API Key", type="password")
    if api_key:
        dashscope.api_key = api_key
    
    # Input Area
    st.subheader("1. 录入老板的回复")
    input_method = st.radio("选择输入方式", ["🎤 语音录入", "📝 文字粘贴"], horizontal=True)
    
    user_input_text = ""
    
    if input_method == "🎤 语音录入":
        audio_value = st.audio_input("按住录音 (或上传音频)")
        if audio_value:
            st.success("录音成功！正在识别...")
            # Todo: Save audio temp file and call recognize_audio
            # For now, let's mock it or use a placeholder if utils not fully ready
            st.info("语音识别功能需要连接 API。此处暂模拟识别结果。")
            user_input_text = "老板说最近工程款还没到账，让我再等等，下个月一定给。"
            st.text_area("识别结果：", value=user_input_text, height=100)
            
    else:
        user_input_text = st.text_area("直接粘贴老板发来的文字/语音转文字内容", height=150, placeholder="例如：兄弟，不是我不给，是上面没拨款啊...")

    # Analysis & Generation
    st.subheader("2. 生成博弈话术")
    if st.button("🚀 生成回怼策略"):
        if not user_input_text:
            st.warning("请先提供老板的回复内容。")
        elif not api_key:
             st.error("请输入 DashScope API Key 才能使用 AI 功能。")
        else:
            with st.spinner("老张正在分析老板的心理..."):
                # Call AI
                import utils
                
                # Construct Prompt
                prompt_content = f"老板的回复是：{user_input_text}。请帮我分析他的心理，并生成三个维度的回复策略。"
                
                response = utils.call_qwen_max(prompt_content, system_prompt=utils.NEGOTIATOR_SYSTEM_PROMPT)
                
                st.markdown("### AI 分析与建议")
                st.write(response)
                
                # We could structure this better if we ask JSON, but text is fine for 'v1'
                # Let's assume the model returns a formatted text for now.

elif page == "2. 证据 & 告知书 (Archivist)":
    st.header("📂 证据链与告知书模块")
    st.markdown("---")
    
    uploaded_files = st.file_uploader("上传聊天记录/转账截图 (支持多图)", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
    
    # Session state for extracted data
    if "evidence_data" not in st.session_state:
        st.session_state.evidence_data = {}
        
    if uploaded_files:
        st.image(uploaded_files, caption="已上传证据", width=150)
        
        if st.button("🔍 AI 智能提取要素"):
            if 'api_key' not in locals() and not getattr(dashscope, 'api_key', None):
                 st.error("请先在侧边栏或模块一中配置 API Key")
            else:
                with st.spinner("Qwen-VL 正在阅读您的截图..."):
                    # Mocking the file path handling for Streamlit (need to save to temp)
                    import tempfile
                    temp_paths = []
                    for uploaded_file in uploaded_files:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as f:
                            f.write(uploaded_file.getbuffer())
                            temp_paths.append(f.name)
                            
                    import utils
                    prompt = "请分析这些图片，提取以下信息：1.欠款人姓名/称呼 2.欠款金额 3.承诺还款日期 4.用户(债权人)可能的称呼。请以JSON格式返回。"
                    
                    # Call VL
                    # res = utils.call_qwen_vl(temp_paths, prompt) # Uncomment when key is ready
                    
                    # Mock Result for Dev
                    import time
                    time.sleep(1)
                    st.session_state.evidence_data = {
                        "debtor": "王总",
                        "amount": "15000",
                        "date": "2023年12月31日",
                        "u_name": "小李"
                    }
                    st.success("提取成功！")
    
    st.subheader("📝 确认告知书内容")
    with st.form("evidence_form"):
        col1, col2 = st.columns(2)
        debtor = col1.text_input("欠款人/老板", value=st.session_state.evidence_data.get("debtor", ""))
        amount = col2.text_input("欠款金额 (元)", value=st.session_state.evidence_data.get("amount", ""))
        date = col1.text_input("承诺/截止日期", value=st.session_state.evidence_data.get("date", ""))
        u_name = col2.text_input("您的称呼", value=st.session_state.evidence_data.get("u_name", ""))
        
        submitted = st.form_submit_button("📄 生成《限期支付告知书》")
        if submitted:
            import utils
            data = {"debtor": debtor, "amount": amount, "date": date, "u_name": u_name, "current_date": "2024-01-17"}
            pdf_file = utils.generate_pdf(data)
            
            with open(pdf_file, "rb") as f:
                st.download_button(
                    label="⬇️ 下载告知书 PDF",
                    data=f,
                    file_name="限期支付告知书.pdf",
                    mime="application/pdf"
                )
            st.success("告知书已生成！您可以下载发送给老板。")
            
            # Save to global case file (mock)
            st.session_state['case_file'] = data
            st.session_state['case_file']['evidence_summary'] = f"Uploaded {len(uploaded_files) if uploaded_files else 0} images."

elif page == "3. 公益导航 & 律师 (Lighthouse)":
    st.header("⚖️ 公益导航与模拟律师")
    st.markdown("---")
    
    # 1. Check Case File
    case_data = st.session_state.get('case_file', {})
    
    with st.expander("📂 查看当前维权案卷包 (Case File)", expanded=True):
        if case_data:
            st.json(case_data)
        else:
            st.warning("暂无案卷信息，建议先去【模块2】生成告知书，或手动补充信息。")
    
    # 2. Offline Navigation
    st.subheader("📍 线下维权地图")
    city = st.text_input("请输入您所在的城市", "石家庄")
    if city:
        st.info(f"为您找到 {city} 的维权机构（示例数据）：\n\n1. {city}劳动保障监察支队 - 电话：12333\n2. {city}法律援助中心 - 地址：市中心XX路XX号")
        
    st.markdown("---")
    
    # 3. AI Lawyer Chat
    st.subheader("👨‍⚖️ AI 公益律师在线咨询")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Initial greeting based on case file
        if case_data:
            welcome_msg = f"你好，我是公益律师。我已经看了你的案卷，也就是向 {case_data.get('debtor', '老板')} 追讨 {case_data.get('amount', '工资')} 的事。我们可以直接开始聊，你想先问什么？"
        else:
            welcome_msg = "你好，我是公益律师。请问遇到了什么劳动纠纷？"
        st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("向律师提问 (例如：老板如果不回消息怎么办？)"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if 'api_key' not in locals() and not getattr(dashscope, 'api_key', None):
                 st.error("请先配置 API Key")
                 response_content = "请配置 API Key 以使用 AI 律师。"
            else:
                import utils
                # Context injection
                context_str = str(case_data) if case_data else "暂无具体案卷，请引导用户补充。"
                system_prompt = utils.LAWYER_SYSTEM_PROMPT_TEMPLATE.format(case_context=context_str)
                
                # We should append history for context window, but for MVP simple turn or last few is okay
                # Let's pass the current prompt to qwen-max with the system prompt
                response_content = utils.call_qwen_max(prompt, system_prompt=system_prompt)
            
            st.markdown(response_content)
        st.session_state.messages.append({"role": "assistant", "content": response_content})