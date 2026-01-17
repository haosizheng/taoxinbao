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
    # 1. Header
    st.markdown("## 讨薪宝")
    
    # 2. Dynamic Banner
    slogan = load_random_slogan()
    st.markdown(f"""
        <div class="orange-banner">
            {slogan}
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
    if st.button("➕ 开启新的维权 (Start New Case)", type="primary", use_container_width=True):
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
    
    # Create 2x2 Grid
    col1, col2 = st.columns(2)
    
    for i, feat in enumerate(features):
        # Determine column
        target_col = col1 if i % 2 == 0 else col2
        
        with target_col:
            # We use HTML to render the button appearance strictly as requested.
            # Since "logic is not needed yet", this div is just visual.
            st.markdown(f"""
            <div class="feature-grid-col">
                <button class="feature-button">
                    <div style="display:flex; align-items:center;">
                        <span class="feature-icon">{feat['icon']}</span>
                        <div>
                            <div class="feature-text">{feat['title']}</div>
                            <div class="feature-sub">{feat['sub']}</div>
                        </div>
                    </div>
                </button>
            </div>
            """, unsafe_allow_html=True)
