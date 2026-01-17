import streamlit as st
import utils
import os
import tempfile
import json
import re

def render(case, token):
    d = case["dossier"]
    
    utils.render_header_with_icon("archivist", "告知书")
    
    # Hack to translate File Uploader
    st.markdown("""
        <style>
            [data-testid="stFileUploader"] section > div:first-child {
                display: none;
            }
            [data-testid="stFileUploader"] section::after {
                content: "点击或拖拽上传图片";
                display: block;
                padding: 1rem;
                text-align: center;
                color: #666;
            }
        </style>
    """, unsafe_allow_html=True)
    
    uploaded = st.file_uploader("上传已有的证据截图", accept_multiple_files=True)
    if uploaded:
        st.image(uploaded, caption=[f"图{i}" for i in range(len(uploaded))], width=80)
        
        if st.button("智能提取要素"):
            if not token:
                st.error("请先在【个人中心】配置 API 密钥以使用智能提取功能。")
            else:
                with st.spinner("正在调用 Qwen-VL 分析图片..."):
                    # 1. Save temp files
                    temp_paths = []
                    try:
                        for uf in uploaded:
                            # Verify suffix
                            suffix = f".{uf.name.split('.')[-1]}" if '.' in uf.name else ".jpg"
                            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
                                f.write(uf.getbuffer())
                                temp_paths.append(f.name)
                        
                        # 2. Call Real API with Context
                        # Combine Context
                        d_ctx = f"已知案件背景：欠款人[{d.get('boss','Unknown')}]，欠款金额[{d.get('amount','Unknown')}]，起止时间[{d.get('date','Unknown')}]。"
                        prompt = f"{d_ctx} 请提取图片中的关键要素（欠款人/金额/日期），如果图片信息与背景冲突，请以图片为准。如果图片缺失某些信息，请结合背景推断但不强行编造。返回JSON。"
                        
                        res_text = utils.call_qwen_vl(temp_paths, prompt_text=prompt, api_key=token)
                        
                        # 3. Parse JSON & Smart Merge
                        match = re.search(r'\{.*\}', res_text, re.DOTALL)
                        if match:
                            try:
                                extracted = json.loads(match.group(0))
                                # Smart Merge: Only overwrite if new value is roughly valid (not empty/zero if old value exists)
                                current_ev = case["evidence_data"]
                                for k, v in extracted.items():
                                    # If new value is not empty, update. 
                                    # If new value looks like "0" or "Unknown" and we have better data in dossier, ignore.
                                    if v and str(v) not in ["0", "Unknown", "None", ""]:
                                        current_ev[k] = v
                                    elif k not in current_ev and k in d:
                                         # Fallback to dossier if extraction failed for this key
                                         current_ev[k] = d[k]

                                case["evidence_data"] = current_ev
                                st.success("✅ 提取成功! 信息已智能合并。")
                            except:
                                st.warning("提取成功但格式解析失败，请参考下方手动填写。")
                                st.caption(f"原始返回: {res_text}")
                        else:
                            st.warning("模型未返回标准 JSON格式。")
                            st.caption(f"原始返回: {res_text}")
                            
                    except Exception as e:
                        st.error(f"发生错误: {e}")
                    finally:
                        # Cleanup
                        for p in temp_paths:
                            try: os.remove(p)
                            except: pass
    
    # --- Content Generation Section ---
    st.markdown("---")
    utils.render_header_with_icon("robot", "告知书生成")
    
    # 1. Basic Info Inputs (Pre-filled)
    ev_data = case.get("evidence_data", {})
    
    with st.container(border=True):
        st.markdown("**👤 欠款人信息**")
        db = st.text_input("欠款单位/个人名称", value=ev_data.get("debtor", d.get("boss","")), key="arch_debtor", placeholder="例如：某某有限公司")
        un = st.text_input("您的正式称呼", value=ev_data.get("u_name", d.get("name","")), key="arch_uname", placeholder="例如：张三")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("**💰 欠款细节**")
        c1, c2 = st.columns(2)
        am = c1.text_input("欠款金额(元)", value=ev_data.get("amount", d.get("amount","")), key="arch_amount", placeholder="8000")
        dt = c2.text_input("欠款时间/期限", value=ev_data.get("date", d.get("date","")), key="arch_date", placeholder="2023年全年")
    
    # 2. Editor Section
    draft_key = f"letter_draft_{case['id']}"
    default_draft = st.session_state.get(draft_key, "")
    final_content = st.text_area("告知书内容预览 (可手动修改)", value=default_draft, height=400)
    
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("智能生成内容", type="primary", use_container_width=True):
            if not token:
                st.warning("请先配置 API 密钥")
            else:
                with st.spinner("正在撰写专业的法律告知书..."):
                    summary = ev_data.get("summary", "无额外证据，仅基于欠款事实。")
                    prompt_tpl = utils.PROMPTS.get("notice_letter_generator_prompt", "")
                    
                    if prompt_tpl:
                        full_prompt = prompt_tpl.format(
                            u_name=un, debtor=db, amount=am, date=dt, summary=summary
                        )
                        res = utils.call_qwen_max(full_prompt, api_key=token)
                        if "Error" not in res and "API Error" not in res:
                             st.session_state[draft_key] = res
                             st.rerun()
                        else:
                            st.error(res)
                    else:
                        st.error("系统错误：缺失提示词配置。")
    
    with col2:
        if not final_content:
            st.button("⬇️ 生成并下载 PDF", disabled=True, use_container_width=True, help="请先生成或输入内容")
        else:
            # Prepare PDF bytes on the fly
            data_pdf = {"debtor": db, "amount": am, "date": dt, "u_name": un}
            try:
                pdf_path = utils.generate_pdf(data_pdf, content=final_content)
                # Persist basic data too
                case["evidence_data"].update(data_pdf)
                
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                
                st.download_button(
                    label="⬇️ 下载 PDF 文件",
                    data=pdf_bytes,
                    file_name=f"正式告知书_{un}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF 生成失败: {e}")

    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
