import streamlit as st
import uuid
import time

def create_new_case(dossier_data):
    new_case = {
        "id": str(uuid.uuid4()),
        "created_at": time.strftime("%Y-%m-%d"),
        "name": f"{dossier_data.get('boss', '未命名')} - {dossier_data.get('amount', '欠款')}元",
        "dossier": dossier_data,
        "evidence_data": {},
        "messages": [{"role": "assistant", "content": "您好，我是薪盾法律顾问(AI)。我已经了解了您的基本情况，请问有什么可以帮您？"}], # Init chat with context
        "case_file": {} # For PDF generation data
    }
    st.session_state.cases.insert(0, new_case) # Add to top
    return new_case["id"]

def render():
    step = st.session_state.wizard_step
    total_steps = 5
    progress = step / total_steps
    
    st.progress(progress, text=f"档案建立中... ({step}/{total_steps})")
    
    # Wizard Content
    with st.container(border=True):
        if step == 1:
            st.subheader("1. 您的称呼")
            st.caption("我们该如何称呼您？")
            val = st.text_input("姓名/昵称", key="wiz_name")
            if st.button("下一步"):
                if val:
                    st.session_state.temp_dossier["name"] = val
                    st.session_state.wizard_step += 1
                    st.rerun()
                else:
                    st.toast("请填写称呼")
                    
        elif step == 2:
            st.subheader("2. 您的岗位")
            st.caption("您从事什么工作？(例如：外卖员、设计师、工地小工)")
            val = st.text_input("岗位", key="wiz_job")
            if st.button("下一步"):
                if val:
                    st.session_state.temp_dossier["job"] = val
                    st.session_state.wizard_step += 1
                    st.rerun()
                else: 
                    st.toast("请填写岗位")

        elif step == 3:
            st.subheader("3. 工作地点")
            st.text_input("大概在哪工作？(选填)", key="wiz_place")
            if st.button("下一步"):
                st.session_state.temp_dossier["place"] = st.session_state.wiz_place # Optional
                st.session_state.wizard_step += 1
                st.rerun()

        elif step == 4:
            st.subheader("4. 欠款详情")
            st.caption("老板/公司叫什么？大概欠了多少钱？")
            c1, c2 = st.columns(2)
            boss = c1.text_input("老板/公司称呼", key="wiz_boss")
            amt = c2.text_input("欠款金额", key="wiz_amt")
            if st.button("下一步"):
                if boss and amt:
                    st.session_state.temp_dossier["boss"] = boss
                    st.session_state.temp_dossier["amount"] = amt
                    st.session_state.wizard_step += 1
                    st.rerun()
                else:
                    st.toast("请完善欠款信息")

        elif step == 5:
            st.subheader("5. 时间跨度")
            st.caption("是什么时候的工资？")
            val = st.text_input("起止时间", key="wiz_date", placeholder="例如：去年年底")
            
            if st.button("✨ 完成创建"):
                st.session_state.temp_dossier["date"] = val
                # Create Case
                new_id = create_new_case(st.session_state.temp_dossier)
                st.session_state.active_case_id = new_id
                st.session_state.app_mode = "WORKSPACE"
                st.rerun()

    if st.button("🔙 取消", type="secondary"):
        st.session_state.active_case_id = None
        st.session_state.app_mode = "HOME"
        st.rerun()
