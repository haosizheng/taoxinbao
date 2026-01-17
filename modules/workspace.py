import streamlit as st
import streamlit_antd_components as sac
import modules.negotiator as negotiator
import modules.archivist as archivist
import modules.lawyer as lawyer
import modules.profile as profile

def render(case, token):
    with st.container(border=True):
        # Header Badge
        # Custom Back Button Header
        c_back, c_title = st.columns([1, 4])
        with c_back:
            if st.button("↩", key="exit_ws_btn"):
                st.session_state.app_mode = "HOME"
                st.rerun()
        with c_title:
            st.caption(f"当前案卷: {case['name']}")
        
        # Determine which view to render based on Home selection
        view = st.session_state.get("workspace_view", "negotiator")
        
        if view == 'negotiator':
            negotiator.render(case, token)
        elif view == 'archivist':
            archivist.render(case, token)
        elif view == 'lawyer':
            lawyer.render(case, token)
        # Profile handled by main bottom nav now
