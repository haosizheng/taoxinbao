import streamlit as st
import utils

import streamlit_antd_components as sac

def render(case, token):
    d = case["dossier"]
    context_summary = f"用户身份：{d['name']}({d['job']})，地点：{d.get('place','未填')}。欠款人：{d['boss']}，金额：{d['amount']}元。"
    
    st.subheader("💬 话术咨询")
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
        if st.button("🚀 生成主动催款话术", type="primary", use_container_width=True):
            if not token: st.error("请去【我的】配置 Token")
            else:
                with st.spinner("老张正在斟酌语气..."):
                    # Use new initiator prompt
                    sys_prompt = utils.PROMPTS.get("negotiator_initiate_template", "")
                    # No user input needed for initiation, just context
                    prompt = f"【背景】：{context_summary}\n请根据以上情况生成催款话术。"
                    res = utils.call_qwen_max(prompt, system_prompt=sys_prompt, api_key=token)
                    st.write(res)
                    
    else: # 回复拖延
        st.write("老板回消息了？把他的话贴进来，我们拆解套路。")
        input_type = st.radio("input_mode", ["🎤 语音", "📝 文字"], horizontal=True, label_visibility="collapsed")
        user_txt = ""
        if input_type == "🎤 语音":
            audio_val = st.audio_input("录制老板的声音或您的描述")
            if audio_val:
                with st.spinner("老张正在听..."):
                    audio_bytes = audio_val.read()
                    user_txt = utils.transcribe_audio_dashscope(audio_bytes)
                
                if user_txt.startswith("Error") or user_txt.startswith("ASR Error"):
                    st.error(user_txt)
                    user_txt = "" # Reset if error
                else:
                    st.success(f"老张听懂了：\"{user_txt}\"")
        else:
            user_txt = st.text_area("老板怎么说？", height=100, placeholder="例如：过两天肯定给你...")
            
        if st.button("🚀 分析并回击", type="primary", use_container_width=True):
            if not token: st.error("请去【我的】配置 Token")
            elif not user_txt: st.toast("请输入内容")
            else:
                with st.spinner("老张正在分析套路..."):
                    # Use standard negotiator prompt
                    sys_prompt = utils.PROMPTS.get("negotiator_system", "")
                    prompt = f"【背景】：{context_summary}\n【对方回复】：{user_txt}\n请分析对方心理并给出回击。"
                    res = utils.call_qwen_max(prompt, system_prompt=sys_prompt, api_key=token)
                    st.write(res)
