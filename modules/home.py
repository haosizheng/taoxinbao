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
    
    # Create 2x2 Grid using st-click-detector (Guarantees layout on mobile)
    from st_click_detector import click_detector
    
    # CSS for the custom component
    # We embed this directly to ensure it works within the component frame
    css_styles = """
    <style>
        /* Global Reset for this component */
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        .grid-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            width: 100%;
            padding: 2px; /* Prevent shadow clip */
        }
        .card-link {
            display: block;
            background-color: #D9534F;
            border-radius: 12px;
            padding: 12px 16px;
            text-decoration: none;
            color: white !important; /* Force white for all states */
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.1s, background-color 0.1s;
            height: 100%; /* Ensure equal height */
            width: 100%;
        }
        .card-link:visited, .card-link:hover, .card-link:active, .card-link:focus {
            color: white !important;
            text-decoration: none;
        }
        .card-link:active {
            transform: scale(0.96);
            background-color: #C9302C;
        }
        .card-content {
            display: flex;
            align-items: center;
        }
        .card-icon {
            font-size: 24px;
            margin-right: 10px;
        }
        .text-group {
            display: flex;
            flex-direction: column;
        }
        .card-title {
            font-size: 17px;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 2px;
        }
        .card-sub {
            font-size: 13px;
            opacity: 0.9;
            font-weight: 400;
        }
    </style>
    """
    
    html_content = f'{css_styles}<div class="grid-container">'
    
    for feat in features:
        # Use title as ID
        html_content += f"""
        <a href='#' id='{feat['title']}' class='card-link'>
            <div class='card-content'>
                <span class='card-icon'>{feat['icon']}</span>
                <div class='text-group'>
                    <span class='card-title'>{feat['title']}</span>
                    <span class='card-sub'>{feat['sub']}</span>
                </div>
            </div>
        </a>
        """
    html_content += "</div>"
    
    # Render Click Detector
    clicked = click_detector(html_content, key="feature_grid_click")
    
    # Handle Clicks
    if clicked:
        if not st.session_state.cases:
            st.toast("请先建立档案 📂")
        else:
            # Navigation Logic
            nav_map = {
                "找话说": "话术咨询",
                "存证据": "生成告知书",
                "出公函": "生成告知书",
                "找援助": "律师顾问"
            }
            
            active_case = st.session_state.cases[0]
            target_tab = nav_map.get(clicked, '话术咨询')
            
            # Update Session State
            st.session_state.active_case_id = active_case['id']
            st.session_state.app_mode = "WORKSPACE"
            st.session_state["main_nav_bar"] = "讨薪"
            
            # Pre-select Workspace Tab
            tab_key = f"workspace_tabs_{active_case['id']}"
            st.session_state[tab_key] = target_tab
            
            st.rerun()
