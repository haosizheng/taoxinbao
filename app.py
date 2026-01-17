import streamlit as st
import utils
import os

# Page Config
st.set_page_config(
    page_title="Salary Shield 薪盾",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed" # Default collapsed for mobile feel
)

# Initialize Session State
if "evidence_data" not in st.session_state:
    st.session_state.evidence_data = {}
if "case_file" not in st.session_state:
    st.session_state.case_file = {}
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "您好，我是薪盾平台的公益援助律师。请问遇到了什么法律问题？"})
if "user_info" not in st.session_state:
    st.session_state.user_info = {"name": "张伟", "id": "U-8823102", "credits": 100}

# Helper to load token
def get_api_token():
    # Priority: Session State (Settings) > Chat Input > Env > Local Config
    if "custom_api_key" in st.session_state and st.session_state.custom_api_key:
        return st.session_state.custom_api_key
    return os.getenv("MODELSCOPE_ACCESS_TOKEN") or utils.load_local_token()

# --- Main Mobile Layout ---
st.title("🛡️ 薪盾 Salary Shield")

# Use Tabs for Bottom Navigation Simulation (Top Tabs are standard in Streamlit)
# Order: 话术 (Negotiator) | 告知书 (Archivist) | 律师 (Lawyer) | 我的 (Profile)
tab1, tab2, tab3, tab4 = st.tabs(["💬 话术咨询", "📄 生成告知书", "⚖️ 律师服务", "👤 个人中心"])

# --- Tab 1: Negotiator ---
with tab1:
    st.caption("智能分析老板心理，生成高情商回复")
    
    # Input Area
    input_method = st.radio("输入方式", ["🎤 语音录入", "📝 文字粘贴"], horizontal=True, label_visibility="collapsed")
    
    user_input_text = ""
    if input_method == "🎤 语音录入":
        audio_value = st.audio_input("按住录音")
        if audio_value:
            st.warning("⚠️ 模拟语音识别中... (暂未对接 Paraformer)")
            user_input_text = "老板说最近工程款还没到账，让我再等等，下个月一定给。"
            st.info(f"识别结果：{user_input_text}")
    else:
        user_input_text = st.text_area("粘贴老板发来的文字", height=120, placeholder="例如：兄弟，不是我不给，是上面没拨款...")

    if st.button("🚀 生成回怼策略", key="btn_neg"):
        token = get_api_token()
        if not user_input_text:
            st.toast("⚠️ 请先提供内容")
        elif not token:
             st.error("请先在【个人中心】配置 API Token")
        else:
            with st.spinner("分析中..."):
                prompt_content = f"老板的回复是：{user_input_text}。请帮我分析他的心理，并生成三个维度的回复策略。"
                response = utils.call_qwen_max(prompt_content, api_key=token)
                st.markdown("### 💡 建议回复")
                st.write(response)

# --- Tab 2: Archivist ---
with tab2:
    st.caption("截图自动提取，一键生成法律告知书")
    
    uploaded_files = st.file_uploader("上传截图", accept_multiple_files=True, type=['png', 'jpg'], label_visibility="collapsed")
    
    if uploaded_files:
        captions = [f"证据 {i+1}" for i in range(len(uploaded_files))]
        st.image(uploaded_files, caption=captions, width=100)
        
        if st.button("🔍 提取要素", key="btn_ocr"):
            token = get_api_token()
            if not token:
                 st.error("请先在【个人中心】配置 API Token")
            else:
                with st.spinner("提取中..."):
                    import tempfile
                    temp_paths = []
                    try:
                        for uf in uploaded_files:
                            suffix = f".{uf.name.split('.')[-1]}" if '.' in uf.name else ".jpg"
                            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
                                f.write(uf.getbuffer())
                                temp_paths.append(f.name)
                        
                        res_text = utils.call_qwen_vl(temp_paths, api_key=token)
                        # Simple JSON extraction logic
                        import re, json
                        match = re.search(r'\{.*\}', res_text, re.DOTALL)
                        if match:
                            try:
                                extracted = json.loads(match.group(0))
                                st.session_state.evidence_data.update(extracted)
                                st.toast("✅ 提取成功")
                            except:
                                st.warning("格式解析失败，请手动填写")
                        else:
                            st.warning("识别结果非标准JSON") 
                    except Exception as e:
                        st.error(f"Error: {e}")
                    finally:
                        for p in temp_paths:
                            try: os.remove(p)
                            except: pass

    with st.form("evidence_form"):
        st.markdown("##### 📝 确认信息")
        col1, col2 = st.columns(2)
        debtor = col1.text_input("欠款人", value=st.session_state.evidence_data.get("debtor", ""))
        amount = col2.text_input("金额", value=st.session_state.evidence_data.get("amount", ""))
        date = col1.text_input("承诺日期", value=st.session_state.evidence_data.get("date", ""))
        u_name = col2.text_input("您的称呼", value=st.session_state.evidence_data.get("u_name", ""))
        
        submitted = st.form_submit_button("生成告知书")
    
    if submitted:
        data = {"debtor": debtor, "amount": amount, "date": date, "u_name": u_name}
        pdf_file = utils.generate_pdf(data)
        
        # Save mock case file
        st.session_state.case_file = data
        
        with open(pdf_file, "rb") as f:
            st.download_button("⬇️ 下载PDF", f, "告知书.pdf", "application/pdf")

# --- Tab 3: Lawyer ---
with tab3:
    st.caption("模拟真实律师咨询 (支持附件)")
    
    # Case File Preview
    case_data = st.session_state.get('case_file', {})
    if case_data:
        st.info(f"📂 已关联案卷：向 {case_data.get('debtor')} 追讨 {case_data.get('amount')} 元")
    
    with st.expander("📎 发送补充材料", expanded=False):
        st.file_uploader("上传附件", accept_multiple_files=True, key="lawyer_upload")

    # Chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("请描述案情..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if case_data: st.toast("✅ 案卷已同步律师")
            token = get_api_token()
            
            if not token:
                 st.error("请先在【个人中心】配置 Token")
                 response_content = "请配置 API Key。"
            else:
                with st.spinner("律师思考中..."):
                    context_str = str(case_data) if case_data else "无详细案卷。"
                    sys_prompt = utils.LAWYER_SYSTEM_PROMPT_TEMPLATE.format(case_context=context_str)
                    response_content = utils.call_qwen_max(prompt, system_prompt=sys_prompt, api_key=token)
            
            st.markdown(response_content)
        st.session_state.messages.append({"role": "assistant", "content": response_content})

# --- Tab 4: Profile (Mine) ---
with tab4:
    # 1. Header
    col_u1, col_u2 = st.columns([1, 3])
    with col_u1:
        st.image("https://api.dicebear.com/9.x/micah/svg?seed=Felix", width=80) 
    with col_u2:
        st.subheader(st.session_state.user_info["name"])
        st.caption(f"ID: {st.session_state.user_info['id']}")
        st.caption(f"维权信用分: {st.session_state.user_info['credits']}")
    
    st.divider()
    
    # 2. Local Map (Moved from Module 3)
    st.subheader("📍 本地维权地图")
    city = st.text_input("当前定位", "石家庄")
    if  city:
        st.success(f"已定位 {city} 周边机构")
        st.markdown(f"""
        - 🏛️ **{city}劳动监察支队**  
          📞 12333 | 📍 此处显示距离 (1.2km)
        - ⚖️ **{city}法律援助中心**  
          📞 0311-12345678 | 📍 此处显示距离 (3.5km)
        """)
        
    st.divider()
    
    # 3. Settings (API Config)
    with st.expander("⚙️ 设置 (API Config)", expanded=True):
        current_token = get_api_token()
        display_token = current_token[:8] + "..." if current_token else ""
        st.text_input("当前已加载 Token", value=display_token, disabled=True)
        
        new_key = st.text_input("更新 ModelScope Token", type="password", key="custom_api_key")
        if new_key:
            st.success("Token 已更新 (当前会话有效)")
    
    st.divider()
    st.caption("关于薪盾 | 版本 v1.0.0")