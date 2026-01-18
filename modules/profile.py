import streamlit as st
import utils

@st.dialog("使用指南")
def show_guide():
    st.markdown("""
    **三步维权法：**
    1. **建立档案**：在首页点击“新建维权档案”，输入欠薪的基本情况。
    2. **存证据**：点击“讨薪”->“存证据”，上传你的聊天记录、转账截图。
    3. **找援助**：点击“讨薪”->“找援助”，一键生成法律文书，或咨询AI律师。
    """)

@st.dialog("免责声明")
def show_disclaimer():
    st.markdown("""
    **法律责任声明：**
    
    1. **AI 辅助性质**：本应用提供的所有建议、文书及分析结果均由人工智能生成，仅供参考。
    2. **非律师意见**：AI 不是执业律师，不能替代线下法律咨询、诉讼代理等专业法律服务。
    3. **免责条款**：用户据此采取的任何法律行动（如发送告知书、提起仲裁等），产生的后果均由用户自行承担。本平台不承担任何连带责任。
    """)

@st.dialog("维权地图 - 石家庄地区")
def show_rights_map():
    st.markdown("""
    **周边维权机构（模拟数据）：**
    
    1. **石家庄市劳动保障监察局**
       - **地址**：长安区裕华东路99号
       - **电话**：0311-8668XXXX
    
    2. **桥西区法律援助中心**
       - **地址**：桥西区中山西路168号
       - **电话**：0311-8703XXXX
    
    3. **正定县劳动争议调解中心**
       - **地址**：正定县恒山路2号
       - **电话**：0311-8802XXXX
    
    ---
    **全国法律服务官方热线：**
    - **电话**：[12348](tel:12348) (24小时免费法律咨询)
    """)

def render(case, token):
    u = st.session_state.user_info
    
    # Custom CSS for Profile Page
    st.markdown("""
    <style>
        /* Modern Profile Card */
        .profile-container {
            background-color: white;
            border-radius: 12px !important;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            margin-bottom: 20px;
            border: 1px solid rgba(0,0,0,0.02);
        }
        .profile-header {
            display: flex;
            align-items: center;
        }
        .avatar-circle {
            width: 64px;
            height: 64px;
            background-color: #F8F9FA;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-right: 18px;
            font-size: 28px;
            color: #ADB5BD;
            border: 2px solid white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .user-name {
            font-size: 20px;
            font-weight: 700;
            color: #212529;
            margin: 0;
            line-height: 1.2;
        }
        .user-id {
            font-size: 13px;
            color: #8E8E93;
            margin-top: 4px;
            letter-spacing: 0.2px;
        }
        
        /* List Menu Styling */
        .list-menu-card {
            background-color: white;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(0,0,0,0.02);
            box-shadow: 0 2px 10px rgba(0,0,0,0.02);
        }
        .list-item {
            display: flex;
            align-items: center;
            padding: 18px 20px;
            text-decoration: none;
            color: #495057;
            transition: background-color 0.2s;
            border-bottom: 1px solid #F1F3F5;
        }
        .list-item:last-child {
            border-bottom: none;
        }
        .list-item:active {
            background-color: #F8F9FA;
        }
        .list-icon {
            font-size: 20px;
            margin-right: 14px;
            width: 24px;
            text-align: center;
            opacity: 0.9;
        }
        .list-text {
            flex-grow: 1;
            font-size: 16px;
            font-weight: 500;
            color: #333;
        }
        .list-arrow {
            color: #D1D1D6;
            font-size: 16px;
            font-weight: 300;
        }

        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            background: white;
            border-radius: 12px;
            border: 1px dashed #DEE2E6;
        }
        .empty-icon {
            font-size: 48px;
            margin-bottom: 15px;
            display: block;
            opacity: 0.5;
        }
        .version-footer {
            text-align: center;
            padding: 30px 0;
            color: #CED4DA;
            font-size: 12px;
            letter-spacing: 1px;
        }

        /* Override st.container(border=True) radius */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 12px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # 1. User Profile Header
    st.markdown(f"""
    <div class="profile-container">
        <div class="profile-header">
            <div class="avatar-circle">{utils.ICONS["person"]}</div>
            <div class="user-meta">
                <div class="user-name">{u['name']}</div>
                <div class="user-id">用户 ID: {u['id']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Functional List Menu
    from st_click_detector import click_detector
    
    # CSS MUST be inside the HTML string for click_detector to apply it inside the iframe
    menu_html = f"""
    <style>
        .list-menu-card {{
            background-color: white;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(0,0,0,0.05);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        .list-item {{
            display: flex;
            align-items: center;
            padding: 18px 20px;
            text-decoration: none !important;
            color: #333 !important;
            border-bottom: 1px solid #F1F3F5;
            transition: background 0.2s;
        }}
        .list-item:last-child {{
            border-bottom: none;
        }}
        .list-item:active {{
            background-color: #F8F9FA;
        }}
        .list-icon {{
            font-size: 20px;
            margin-right: 15px;
            width: 24px;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .list-text {{
            flex-grow: 1;
            font-size: 16px;
            font-weight: 500;
        }}
        .list-arrow {{
            color: #D1D1D6;
            font-size: 16px;
            font-weight: bold;
        }}
    </style>
    <div class="list-menu-card">
        <a href='#' id='guide' class='list-item'>
            <span class='list-icon' style='color: #E63946;'>{utils.ICONS["book"]}</span>
            <span class='list-text'>使用指南</span>
            <span class='list-arrow'>&gt;</span>
        </a>
        <a href='#' id='map' class='list-item'>
            <span class='list-icon' style='color: #E63946;'>{utils.ICONS["map"]}</span>
            <span class='list-text'>维权地图</span>
            <span class='list-arrow'>&gt;</span>
        </a>
        <a href='#' id='disclaimer' class='list-item'>
            <span class='list-icon' style='color: #E63946;'>{utils.ICONS["warning"]}</span>
            <span class='list-text'>免责声明</span>
            <span class='list-arrow'>&gt;</span>
        </a>
        <a href='#' id='feedback' class='list-item'>
            <span class='list-icon' style='color: #E63946;'>{utils.ICONS["feedback"]}</span>
            <span class='list-text'>系统反馈</span>
            <span class='list-arrow'>&gt;</span>
        </a>
    </div>
    """
    clicked = click_detector(menu_html, key="profile_menu_click_v3")
    
    if clicked == "guide":
        show_guide()
    elif clicked == "map":
        show_rights_map()
    elif clicked == "disclaimer":
        show_disclaimer()
    elif clicked == "feedback":
        st.toast("反馈功能正在开发中，感谢关注！")

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # 3. Case Management
    utils.render_header_with_icon("archivist", "档案管理")
    if not st.session_state.get("cases"):
        st.markdown("""
        <div class="empty-state">
            <span class="empty-icon">🗄️</span>
            <div style="color: #8E8E93;">您的维权档案库还是空的</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for c in st.session_state.cases:
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    d = c['dossier']
                    st.write(f"**{d.get('boss', '未知老板')}**")
                    st.caption(f"欠薪: {d.get('amount', '0')}元 | {d.get('date', '未填日期')}")
                with col2:
                    if st.button("删除", key=f"del_{c['id']}", help="删除此档案"):
                        st.session_state.cases.remove(c)
                        if st.session_state.get("active_case_id") == c['id']:
                            st.session_state.active_case_id = None
                        st.rerun()
                            
    st.divider()
    with st.expander("⚙️ 设置 API 密钥"):
        val = st.text_input("ModelScope 密钥", type="password", key="custom_api_key")
        if val: st.success("已更新")
        st.caption(f"当前: {token[:8]}..." if token else "未配置")

    # 4. Version Footer
    st.markdown("""
    <div class="version-footer">
        讨薪宝 v1.0.1
    </div>
    """, unsafe_allow_html=True)
