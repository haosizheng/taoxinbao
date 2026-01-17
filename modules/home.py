import streamlit as st
import uuid
import time
from utils import load_local_token

def render():
    st.title("🛡️ 薪盾 Salary Shield")
    st.caption("您的个人 AI 维权顾问")
    
    # 1. New Case Button
    if st.button("➕ 开启新的维权 (Start New Case)", type="primary", use_container_width=True):
        st.session_state.app_mode = "WIZARD"
        st.session_state.wizard_step = 1
        st.session_state.temp_dossier = {}
        st.rerun()
        
    st.divider()
    
    # 2. Case List
    st.subheader("📂 我的案卷 (My Cases)")
    if not st.session_state.cases:
        st.info("暂无记录，请点击上方按钮开始维护您的权益。")
    else:
        for case in st.session_state.cases:
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{case['name']}**")
                    st.caption(f"创建时间: {case['created_at']} | 岗位: {case['dossier'].get('job', '-')}")
                with col2:
                    if st.button("进入", key=f"enter_{case['id']}"):
                        st.session_state.active_case_id = case['id']
                        st.session_state.app_mode = "WORKSPACE"
                        st.rerun()
