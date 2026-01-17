import streamlit as st
import utils

def render(case, token):
    with st.container(border=True):
        st.subheader("👤 个人中心")
        u = st.session_state.user_info
        st.write(f"**用户**: {u['name']}")
        st.caption(f"ID: {u['id']}")
        
        if st.button("🔁 切换/管理案卷 (Switch Case)", type="secondary", use_container_width=True):
            st.session_state.active_case_id = None
            st.session_state.app_mode = "HOME"
            st.rerun()
            
        st.divider()
        with st.expander("⚙️ 设置 Token"):
            val = st.text_input("ModelScope Token", type="password", key="custom_api_key")
            if val: st.success("已更新")
            st.caption(f"当前: {token[:8]}..." if token else "未配置")
