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
    # 1. Header & Dynamic Banner (Wrapped for Sticky)
    slogan = load_random_slogan()
    st.markdown(f"""
    <div class="sticky-header">
        <h2 style="margin-bottom: 20px;">讨薪宝</h2>
        <div class="orange-banner">
            {slogan}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 3. My Cases
    st.markdown("### 📂 我的案卷 (My Cases)")
    
    if not st.session_state.cases:
        # Empty State
        st.markdown("""
            <div class="blue-info-box">
                暂无记录，请点击下方按钮开始维护您的权益。
            </div>
        """, unsafe_allow_html=True)
    else:
        # Show MOST RECENT case (just one, or list? Wireframe shows one "card" style list)
        # We will list them, but maybe just limit to a few if too many? For now list all or just first.
        # Wireframe implies a list of cards. We'll show the top one or all.
        
        # Wrap the list in a scrollable fixed-height container
        with st.container(height=280, border=False):
            for case in st.session_state.cases:
                with st.container(border=True):
                    # Custom Layout for Case Card
                    st.markdown(f"**{case['name']}**")
                    
                    # Check for dossier data validity
                    job = case.get('dossier', {}).get('job', '未填写')
                    date = case.get('created_at', '-')
                    
                    st.caption(f"创建时间: {date} | 岗位: {job}")
                    
                    if st.button("进入", key=f"enter_{case['id']}", use_container_width=False):
                        st.session_state.active_case_id = case['id']
                        st.session_state.app_mode = "WORKSPACE"
                        st.session_state["main_nav_bar"] = "讨薪" # Sync Nav
                        st.rerun()

    # 4. Start New Case Button (Large, Red)
    # Note: Streamlit primary button color is configured in theme, but we injected CSS to make tabs red. 
    # Let's trust type="primary" coupled with our CSS or Streamlit theme.
    st.markdown("<br>", unsafe_allow_html=True) # Spacing
    if st.button("建立维权档案", type="primary", use_container_width=True):
        st.session_state.app_mode = "WIZARD"
        st.session_state.wizard_step = 1
        st.session_state.temp_dossier = {}
        st.session_state["main_nav_bar"] = "首页" # Sync Nav
        st.rerun()

    # 5. Feature Grid (2x2)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Define the 4 features
    features = [
        {"icon": "💬", "title": "找话说", "sub": "博弈助手"},
        {"icon": "📷", "title": "存证据", "sub": "智能提取"},
        {"icon": "⚖️", "title": "出公函", "sub": "法律威慑"},
        {"icon": "🆘", "title": "找援助", "sub": "法律地图"}
    ]
    
    # Create 2x2 Grid with Interactive Buttons
    # Mappings for navigation
    # key: button title, value: workspace tab name
    nav_map = {
        "找话说": "话术咨询",
        "存证据": "生成告知书",
        "出公函": "生成告知书",
        "找援助": "律师顾问"
    }

    # Use native columns for interaction
    col1, col2 = st.columns(2)
    
    for i, feat in enumerate(features):
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            # Button Text: Icon + Title + Newline + Sub
            # Note: Streamlit buttons support minimal styling. We rely on the text content.
            btn_label = f"{feat['icon']} {feat['title']}\n{feat['sub']}"
            
            if st.button(btn_label, key=f"feat_btn_{i}", use_container_width=True):
                # Logic: Check for cases
                if not st.session_state.cases:
                    st.toast("请先建立档案 📂")
                else:
                    # Get most recent case (index 0)
                    active_case = st.session_state.cases[0]
                    target_tab = nav_map.get(feat['title'], '话术咨询')
                    
                    # Set Session State for Navigation
                    st.session_state.active_case_id = active_case['id']
                    st.session_state.app_mode = "WORKSPACE"
                    st.session_state["main_nav_bar"] = "讨薪"
                    
                    # Pre-select the correct tab in Workspace
                    # The key format in workspace.py is f"workspace_tabs_{case['id']}"
                    tab_key = f"workspace_tabs_{active_case['id']}"
                    st.session_state[tab_key] = target_tab
                    
                    st.rerun()
