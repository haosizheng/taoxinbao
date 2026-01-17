import streamlit as st
import utils

@st.dialog("📖 使用指南")
def show_guide():
    st.markdown("""
    **三步维权法：**
    1. **建立档案**：在首页点击“新建维权档案”，输入欠薪的基本情况。
    2. **存证据**：点击“讨薪”->“存证据”，上传你的聊天记录、转账截图。
    3. **找援助**：点击“讨薪”->“找援助”，一键生成法律文书，或咨询AI律师。
    """)

@st.dialog("⚠️ 免责声明")
def show_disclaimer():
    st.markdown("""
    **法律责任声明：**
    
    1. **AI 辅助性质**：本应用提供的所有建议、文书及分析结果均由人工智能生成，仅供参考。
    2. **非律师意见**：AI 不是执业律师，不能替代线下法律咨询、诉讼代理等专业法律服务。
    3. **免责条款**：用户据此采取的任何法律行动（如发送告知书、提起仲裁等），产生的后果均由用户自行承担。本平台不承担任何连带责任。
    """)

def render(case, token):
    with st.container(border=True):
        st.subheader("👤 个人中心")
        u = st.session_state.user_info
        st.write(f"**用户**: {u['name']}")
        st.caption(f"ID: {u['id']}")
        
        st.markdown("---")
        
        # Action Buttons Row
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📖 使用指南", use_container_width=True):
                show_guide()
        with c2:
            if st.button("⚠️ 免责声明", use_container_width=True):
                show_disclaimer()
                
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🗑️ 退出并清除所有数据", type="primary", use_container_width=True):
            st.session_state.clear()
            st.rerun()
            
        st.divider()
        with st.expander("⚙️ 设置 Token"):
            val = st.text_input("ModelScope Token", type="password", key="custom_api_key")
            if val: st.success("已更新")
            st.caption(f"当前: {token[:8]}..." if token else "未配置")
