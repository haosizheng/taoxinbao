import streamlit as st
import json
import random
import os

def load_random_slogan():
    try:
        with open("slogans.json", "r", encoding="utf-8") as f:
            slogans = json.load(f)
        return random.choice(slogans)
    except:
        return "经营风险不该由您承担，生活开支等不了明天。"

def render():
    # 1. Dynamic Banner
    slogan = load_random_slogan()
    st.markdown(f"""
    <div class="orange-banner">
        {slogan}
    </div>
    """, unsafe_allow_html=True)
    
    # 3. My Cases
    with st.container(border=True):
        st.subheader("📂 我的案卷 (My Cases)")
        if not st.session_state.cases:
            # Empty State
            st.info("暂无记录，请点击下方按钮开始维护您的权益。")
        else:
            # Wrap the list in a scrollable fixed-height container
            # Note: We want the LIST to scroll, but the Card to be fixed size? 
            # Or Card grows and list scrolls inside.
            with st.container(height=280, border=False):
                for case in st.session_state.cases:
                    with st.container(border=True): # Inner card for each case
                        # Custom Layout for Case Card
                        st.markdown(f"**{case['name']}**")
                        
                        # Check for dossier data validity
                        job = case.get('dossier', {}).get('job', '未填写')
                        date = case.get('created_at', '-')
                        
                        st.caption(f"创建时间: {date} | 岗位: {job}")
                        
                        if st.button("🚀 开始讨薪", key=f"enter_{case['id']}", use_container_width=False):
                            st.session_state.active_case_id = case['id']
                            st.session_state.app_mode = "RECOVERY"
                            # st.session_state["main_nav_bar"] = "讨薪" # Auto-sync handled in app.py logic logic
                            st.rerun()

    # 4. Start New Case Button (Large, Red)
    st.markdown("<br>", unsafe_allow_html=True) # Spacing
    if st.button("新建维权档案", type="primary", use_container_width=True):
        st.session_state.app_mode = "WIZARD"
        st.session_state.wizard_step = 1
        st.session_state.temp_dossier = {}
        # st.session_state["main_nav_bar"] = "首页" 
        st.rerun()


