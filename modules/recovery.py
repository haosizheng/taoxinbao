import streamlit as st
import json
from st_click_detector import click_detector

def render():
    st.markdown("### 🛠️ 讨薪工具箱") 
    
    # Define the 4 features with simplified, colloquial descriptions
    features = [
        {"icon": "💬", "title": "找话说", "sub": "教你怎么跟老板谈判"},
        {"icon": "📷", "title": "存证据", "sub": "帮你整理聊天记录和转账"},
        {"icon": "⚖️", "title": "出公函", "sub": "自动生成正式的催款函"},
        {"icon": "🆘", "title": "找援助", "sub": "24小时AI律师在线咨询"}
    ]
    
    with st.container(border=True):
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
                grid-template-columns: 1fr; /* 1 Column Layout */
                gap: 12px;
                width: 100%;
                padding: 2px;
                background-color: #FFFFFF;
            }
            .card-link {
                display: block;
                background-color: #D9534F;
                border-radius: 12px;
                padding: 16px 20px; /* More padding for list items */
                text-decoration: none;
                color: white !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: transform 0.1s, background-color 0.1s;
                width: 100%;
            }
            .card-link:visited, .card-link:hover, .card-link:active, .card-link:focus {
                color: white !important;
                text-decoration: none;
            }
            .card-link:active {
                transform: scale(0.98); /* Less scale on wide buttons */
                background-color: #C9302C;
            }
            .card-content {
                display: flex;
                align-items: center;
                /* justify-content: space-between; Optional: push arrow to right? */
            }
            .card-icon {
                font-size: 28px;
                margin-right: 16px;
                background: rgba(255,255,255,0.2);
                width: 48px;
                height: 48px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .text-group {
                display: flex;
                flex-direction: column;
            }
            .card-title {
                font-size: 18px;
                font-weight: 700;
                line-height: 1.2;
                margin-bottom: 4px;
            }
            .card-sub {
                font-size: 14px;
                opacity: 0.95;
                font-weight: 400;
            }
        </style>
        """
        
        html_content = f'{css_styles}<div class="grid-container">'
        
        for feat in features:
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
        clicked = click_detector(html_content, key="feature_grid_click_recovery")
    
    # Handle Clicks
    if clicked:
        if not st.session_state.cases:
            st.toast("请先去「首页」建立「案卷」 📂")
        else:
            # Navigation Logic
            nav_view_map = {
                "找话说": "negotiator",
                "存证据": "archivist",
                "出公函": "archivist",
                "找援助": "lawyer"
            }
            
            active_case = st.session_state.cases[0]
            target_view = nav_view_map.get(clicked, "negotiator")
            
            st.session_state.active_case_id = active_case['id']
            st.session_state.app_mode = "WORKSPACE"
            st.session_state.workspace_view = target_view
            
            st.rerun()
