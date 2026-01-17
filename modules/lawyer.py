import streamlit as st
import utils
import os

def render(case, token):
    d = case["dossier"]
    context_summary = f"用户身份：{d['name']}({d['job']})，地点：{d.get('place','未填')}。欠款人：{d['boss']}，金额：{d['amount']}元。"
    
    # 1. AI Case Brief Generator
    with st.expander("智能生成案件法律事实摘要"):
        st.info("AI 将自动梳理您的建档信息、聊天记录和上传的证据，生成一份专业的报告。")
        
        brief_key = f"case_brief_{case['id']}"
        
        if st.button("开始生成", type="primary"):
            if not token:
                st.error("请先配置 API 密钥")
            else:
                with st.spinner("AI 正在阅读您的案件资料..."):
                    # 1. Gather Context
                    # Messages
                    msg_text = "\n".join([f"{m['role']}: {m['content']}" for m in case.get('messages', [])[-10:]]) # Last 10 msgs
                    # Evidence
                    evidence_list = case.get("evidence_data", {}).keys() # Just filenames for now
                    evidence_text = ", ".join(evidence_list) if evidence_list else "无图片证据"
                    
                    # 2. Call AI
                    prompt_template = utils.PROMPTS.get("case_brief_synthesis", "")
                    prompt = prompt_template.format(
                        dossier_summary=context_summary, 
                        negotiator_context=msg_text,
                        evidence_context=evidence_text
                    )
                    
                    brief_res = utils.call_qwen_max(prompt, api_key=token)
                    st.session_state[brief_key] = brief_res
                    st.success("生成成功！")
        
        # Display & Download
        if brief_key in st.session_state:
            brief_content = st.text_area("摘要预览 (可修改)", value=st.session_state[brief_key], height=300)
            
            # Download Button
            if st.button("下载完整 PDF (含证据图)"):
                # Get images list
                images = []
                # Assuming evidence is stored in case['evidence_data'] as {filename: path} 
                # (Need to verify structure, Archvist usually stores files. 
                # For now assume we scan 'evidence_files' dir or similar if implemented, 
                # OR user manually adds. Let's assume modules/archivist.py puts file paths in evidence_data values.)
                # If structure is unknown, we skip images for MVP safety, or try st.session_state approach.
                # Re-checking archivist... it uses st.file_uploader.
                # Let's check session state for uploaded files paths.
                # For now, pass empty list if not strictly managed.
                 
                # Refined Plan: Look into case['evidence_data'].
                # If empty, we just pass None.
                evidence_map = case.get("evidence_data", {})
                img_paths = [v for k,v in evidence_map.items() if isinstance(v, str) and os.path.exists(v)]
                 
                pdf_path = utils.generate_case_brief_pdf(brief_content, images=img_paths)
                 
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "点击保存文件",
                        data=f,
                        file_name=f"案件摘要_{d['name']}.pdf",
                        mime="application/pdf"
                    )

    st.markdown("---")

    utils.render_header_with_icon("lawyer", "律师顾问")
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
