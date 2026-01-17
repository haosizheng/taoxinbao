import streamlit as st
import utils

def render(case, token):
    d = case["dossier"]
    context_summary = f"用户身份：{d['name']}({d['job']})，地点：{d.get('place','未填')}。欠款人：{d['boss']}，金额：{d['amount']}元。"
    
    st.subheader("💬 话术咨询")
    st.info(f"正在对抗：{d['boss']} (欠 {d['amount']}元)")
    
    input_type = st.radio("input_mode", ["🎤 语音", "📝 文字"], horizontal=True, label_visibility="collapsed")
    user_txt = ""
    if input_type == "🎤 语音":
        audio_val = st.audio_input("录音")
        if audio_val:
            st.warning("⚠️ 模拟语音识别...")
            user_txt = "老板说还没钱，让我等等。"
            st.success(f"识别：{user_txt}")
    else:
        user_txt = st.text_area("对方回复", height=100)
        
    if st.button("🚀 分析策略"):
        if not token: st.error("请去【我的】配置 Token")
        elif not user_txt: st.toast("请输入内容")
        else:
            with st.spinner("思考中..."):
                prompt = f"【背景】：{context_summary}\n【对方回复】：{user_txt}\n请分析对方心理并给出三个维度的回复建议（情理/坚定/法律）。"
                res = utils.call_qwen_max(prompt, api_key=token)
                st.write(res)
