import streamlit as st
import streamlit_antd_components as sac
import modules.negotiator as negotiator
import modules.archivist as archivist
import modules.lawyer as lawyer
import modules.profile as profile

def render(case, token):
    # Header Badge
    st.caption(f"当前案卷: {case['name']}")
    
    # Segmented Control for Workspace Tabs (Touch friendly, no gap)
    selected_tab = sac.tabs(
        [
            sac.TabsItem(label='话术咨询', icon='chat-dots'),
            sac.TabsItem(label='生成告知书', icon='file-earmark-pdf'),
            sac.TabsItem(label='律师顾问', icon='briefcase'),
            sac.TabsItem(label='个人中心', icon='person') # Keeping profile here as requested, though it's also in bottom nav? 
            # User said: "话术咨询、生成告知书、律师服务、个人中心四个按钮不要有间距"
            # It seems they want 4 tabs here.
        ],
        align='center', 
        variant='segmented', # This removes spacing typically
        return_index=False,
        key=f"workspace_tabs_{case['id']}", 
        use_container_width=True
    )

    if selected_tab == '话术咨询':
        negotiator.render(case, token)
    elif selected_tab == '生成告知书':
        archivist.render(case, token)
    elif selected_tab == '律师顾问':
        lawyer.render(case, token)
    elif selected_tab == '个人中心':
        profile.render(case, token)
