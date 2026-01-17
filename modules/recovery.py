import streamlit as st
import utils
import json
from st_click_detector import click_detector

def render():
    utils.render_header_with_icon("toolkit", "讨薪工具箱") 
    
    # Define the 4 features with simplified, colloquial descriptions using flat SVGs
    features = [
        {"icon": utils.ICONS["negotiator"], "title": "找话说", "sub": "教你怎么跟老板谈判"},
        {"icon": utils.ICONS["camera"], "title": "存证据", "sub": "帮你整理聊天记录和转账"},
        {"icon": utils.ICONS["archivist"], "title": "出公函", "sub": "自动生成正式的催款函"},
        {"icon": utils.ICONS["lawyer"], "title": "找援助", "sub": "24小时AI律师在线咨询"}
    ]
    
    # Define styles for the button grid
    css_styles = """
    <style>
        .grid-container {
            display: flex;
            flex-direction: column;
            gap: 12px;
            width: 100%;
            padding: 2px 0; /* Minimal vertical padding */
            margin: 0 !important; /* Force no margin */
        }
        .card-link {
            display: block;
            background-color: #D9534F;
            border-radius: 12px;
            padding: 12px 16px;
            margin: 0 !important; /* Force no margin - crucial fix */
            text-decoration: none;
            color: white !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            transition: transform 0.1s;
            width: 100% !important;
            border: none;
            outline: none;
            box-sizing: border-box; /* Ensure padding doesn't push width */
        }
        .card-link:visited, .card-link:hover, .card-link:active, .card-link:focus {
            color: white !important;
            text-decoration: none;
        }
        .card-link:active {
            transform: scale(0.98);
            background-color: #C9302C;
        }
        .card-content {
            display: flex;
            align-items: center;
            width: 100%;
            pointer-events: none; /* Let the <a> handle clicks */
        }
        .card-icon-box {
            font-size: 22px;
            margin-right: 14px;
            background: rgba(255,255,255,0.22);
            width: 44px;
            height: 44px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        .text-group {
            display: flex;
            flex-direction: column;
            justify-content: center;
            flex-grow: 1;
            text-align: left;
        }
        .card-title {
            font-size: 17px;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 2px;
            color: white !important;
            display: block;
        }
        .card-sub {
            font-size: 13px;
            opacity: 0.9;
            font-weight: 400;
            color: white !important;
            display: block;
        }
    </style>
    """
    
    # We display a cleaner container without 'outer-card' to avoid nesting
    html_content = f'{css_styles}<div class="grid-container">'
    
    for feat in features:
        html_content += f"""
        <a href='#' id='{feat['title']}' class='card-link'>
            <div class='card-content'>
                <div class='card-icon-box'>{feat['icon']}</div>
                <div class='text-group'>
                    <span class='card-title'>{feat['title']}</span>
                    <span class='card-sub'>{feat['sub']}</span>
                </div>
            </div>
        </a>
        """
    html_content += "</div>"
    
    # Use a native container to match other pages' look
    with st.container(border=True):
        # Render Click Detector
        clicked = click_detector(html_content, key="feature_grid_click_recovery_v3")
    
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
            st.session_state.force_scroll_top = True
            
            st.rerun()
