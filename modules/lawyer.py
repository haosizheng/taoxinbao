import streamlit as st
import utils

def render(case, token):
    d = case["dossier"]
    context_summary = f"用户身份：{d['name']}({d['job']})，地点：{d.get('place','未填')}。欠款人：{d['boss']}，金额：{d['amount']}元。"

    st.subheader("⚖️ 律师顾问")
    # Chat History from Case
    for m in case["messages"]:
        with st.chat_message(m["role"]): st.write(m["content"])
        
    if prompt := st.chat_input("咨询律师..."):
        case["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        with st.chat_message("assistant"):
            if not token: 
                    resp = "请配置 Token。"
                    st.error(resp)
            else:
                with st.spinner("..."):
                    sys = utils.LAWYER_SYSTEM_PROMPT_TEMPLATE.format(case_context=context_summary)
                    resp = utils.call_qwen_max(prompt, system_prompt=sys, api_key=token)
                st.write(resp)
        case["messages"].append({"role": "assistant", "content": resp})
