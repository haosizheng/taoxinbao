import streamlit as st
import modules.negotiator as negotiator
import modules.archivist as archivist
import modules.lawyer as lawyer
import modules.profile as profile

def render(case, token):
    # Header Badge
    st.caption(f"当前案卷: {case['name']}")
    
    # Tabs (Standard Top Navigation)
    t1, t2, t3, t4 = st.tabs(["💬 话术咨询", "📄 生成告知书", "⚖️ 律师服务", "👤 个人中心"])

    with t1: negotiator.render(case, token)
    with t2: archivist.render(case, token)
    with t3: lawyer.render(case, token)
    with t4: profile.render(case, token)
