import streamlit as st
import json
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

def load_questions():
    try:
        with open("wizard_questions.json", "r", encoding="utf-8") as f:
            return {q["step"]: q for q in json.load(f)}
    except:
        return {}

def section_header(q_data):
    if not q_data: return
    st.subheader(q_data.get("title", ""))
    st.caption(q_data.get("caption", ""))

def render():
    step = st.session_state.wizard_step
    total_steps = 5
    progress = step / total_steps
    
    questions = load_questions()
    q = questions.get(step, {})

    st.progress(progress, text=f"档案建立中... ({step}/{total_steps})")
    
    # Wizard Content
    with st.container(border=True):
        if step == 1:
            section_header(q)
            val = st.text_input(q.get("label", "姓名"), key=q.get("key", "wiz_name"))
            if st.button("下一步"):
                if val:
                    st.session_state.temp_dossier["name"] = val
                    st.session_state.wizard_step += 1
                    st.rerun()
                else:
                    st.toast(q.get("required_msg", "请填写信息"))
                    
        elif step == 2:
            section_header(q)
            val = st.text_input(q.get("label", "岗位"), key=q.get("key", "wiz_job"))
            if st.button("下一步"):
                if val:
                    st.session_state.temp_dossier["job"] = val
                    st.session_state.wizard_step += 1
                    st.rerun()
                else: 
                    st.toast(q.get("required_msg", "请填写信息"))

        elif step == 3:
            section_header(q)
            val = st.text_input(q.get("label", "地点"), key=q.get("key", "wiz_place"))
            if st.button("下一步"):
                st.session_state.temp_dossier["place"] = st.session_state.wiz_place # Optional
                st.session_state.wizard_step += 1
                st.rerun()

        elif step == 4:
            section_header(q)
            c1, c2 = st.columns(2)
            # JSON defines inputs array for step 4
            inputs = q.get("inputs", [
                {"label": "老板", "key": "wiz_boss"},
                {"label": "欠款", "key": "wiz_amt"}
            ])
            
            boss = c1.text_input(inputs[0]["label"], key=inputs[0]["key"])
            amt = c2.text_input(inputs[1]["label"], key=inputs[1]["key"])
            
            if st.button("下一步"):
                if boss and amt:
                    st.session_state.temp_dossier["boss"] = boss
                    st.session_state.temp_dossier["amount"] = amt
                    st.session_state.wizard_step += 1
                    st.rerun()
                else:
                    st.toast(q.get("required_msg", "请完善信息"))

        elif step == 5:
            section_header(q)
            val = st.text_input(q.get("label", "时间"), key=q.get("key", "wiz_date"), placeholder=q.get("placeholder", ""))
            
            if st.button("✨ 完成创建"):
                st.session_state.temp_dossier["date"] = val
                # Create Case
                new_id = create_new_case(st.session_state.temp_dossier)
                st.session_state.active_case_id = new_id
                st.session_state.app_mode = "HOME"
                # st.session_state["main_nav_bar"] = "首页" # Default
                st.rerun()

    if st.button("🔙 取消", type="secondary"):
        st.session_state.active_case_id = None
        st.session_state.app_mode = "HOME"
        st.session_state["main_nav_bar"] = "首页" # Sync Nav
        st.rerun()
