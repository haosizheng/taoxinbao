import streamlit as st
import utils
import os
import tempfile
import json
import re

def render(case, token):
    d = case["dossier"]
    
    st.subheader("📄 告知书")
    
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
        
        if st.button("🔍 提取要素 (消耗 Token)"):
            if not token:
                st.error("请先在【个人中心】配置 API Token 以使用智能提取功能。")
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
    
    submitted = False
    with st.form("doc_form"):
        c1, c2 = st.columns(2)
        # Pre-fill from Case Data > Dossier Data
        # Ensure we don't crash if keys missing
        ev_data = case.get("evidence_data", {})
        
        db = c1.text_input("欠款人", value=ev_data.get("debtor", d.get("boss","")))
        am = c2.text_input("金额", value=ev_data.get("amount", d.get("amount","")))
        dt = c1.text_input("日期", value=ev_data.get("date", d.get("date","")))
        un = c2.text_input("您的称呼", value=ev_data.get("u_name", d.get("name","")))
        
        submitted = st.form_submit_button("生成PDF")

    if submitted:
        data = {"debtor": db, "amount": am, "date": dt, "u_name": un}
        pdf = utils.generate_pdf(data)
        
        # Update Case Data persistence
        case["evidence_data"].update(data) 
        
        with open(pdf, "rb") as f:
            st.download_button("⬇️ 下载 (Download PDF)", f, "告知书.pdf", "application/pdf")
