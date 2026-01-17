import streamlit as st
import uuid
import time
import re

def create_new_case(dossier_data):
    # Map fuzzy duration to date string if needed, or just store the duration
    # Logic to ensure amount is a clean number
    new_case = {
        "id": str(uuid.uuid4()),
        "created_at": time.strftime("%Y-%m-%d"),
        "name": f"{dossier_data.get('boss', '未命名')} - {dossier_data.get('amount', '欠款')}元",
        "dossier": dossier_data,
        "evidence_data": {},
        "messages": [{"role": "assistant", "content": "您好，我是薪盾法律顾问(AI)。我已经了解了您的基本情况，请问有什么可以帮您？"}],
        "case_file": {} 
    }
    st.session_state.cases.insert(0, new_case)
    return new_case["id"]

def render():
    # Initialize wizard state if not present
    if "wizard_step" not in st.session_state:
        st.session_state.wizard_step = 1
    if "temp_dossier" not in st.session_state:
        st.session_state.temp_dossier = {}

    step = st.session_state.wizard_step
    total_steps = 3
    progress = step / total_steps
    
    # Header & Progress
    st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>📝 维权建档</h2>", unsafe_allow_html=True)
    st.progress(progress, text=f"第 {step} 步 / 共 {total_steps} 步")
    
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        if step == 1:
            st.markdown("### 💰 利益锚定")
            st.write("老乡，咱们先把这笔账记清楚。对方欠了你多少钱？大概欠了多久了？")
            
            # Big Input for Amount
            st.markdown("<div style='text-align: center; margin: 20px 0;'>", unsafe_allow_html=True)
            amt = st.text_input("欠款总额 (元)", 
                               value=st.session_state.temp_dossier.get("amount", ""), 
                               placeholder="比如：8000",
                               help="输入大概的数字也可以")
            st.markdown("</div>", unsafe_allow_html=True)
            
            duration = st.text_input("欠了多久了？", 
                                    value=st.session_state.temp_dossier.get("date", ""), 
                                    placeholder="比如：半年、去年年底、3个月...")
            
            st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
            
            st.markdown('<div class="big-btn-wrapper">', unsafe_allow_html=True)
            if st.button("下一步：谁欠的钱？", use_container_width=True, type="primary"):
                if amt and duration:
                    st.session_state.temp_dossier["amount"] = amt
                    st.session_state.temp_dossier["date"] = duration
                    st.session_state.wizard_step = 2
                    st.rerun()
                else:
                    st.warning("这两项都很关键，老乡咱还是填上吧。")
            st.markdown('</div>', unsafe_allow_html=True)

        elif step == 2:
            st.markdown("### 🎯 责任锁定")
            st.write("冤有头债有主，咱们得明确是哪里、又是谁欠的这笔钱。")
            
            boss = st.text_input("老板或公司名字", 
                                value=st.session_state.temp_dossier.get("boss", ""), 
                                placeholder="例如：某某包工头、某某劳务公司")
            
            place = st.text_input("干活的地点", 
                                 value=st.session_state.temp_dossier.get("place", ""), 
                                 placeholder="例如：苏州昆山、上海浦东...")

            st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="secondary-btn-wrapper big-btn-wrapper">', unsafe_allow_html=True)
                if st.button("返回上一步", use_container_width=True):
                    st.session_state.wizard_step = 1
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="big-btn-wrapper">', unsafe_allow_html=True)
                if st.button("下一步：您的身份", use_container_width=True, type="primary"):
                    if boss:
                        st.session_state.temp_dossier["boss"] = boss
                        st.session_state.temp_dossier["place"] = place
                        st.session_state.wizard_step = 3
                        st.rerun()
                    else:
                        st.warning("总得确认是谁欠的钱，以后才好维权。")
                st.markdown('</div>', unsafe_allow_html=True)

        elif step == 3:
            st.markdown("### 🛡️ 身份赋权")
            st.write("最后，咱们得确认是您本人在维权。怎么称呼您？当时是在什么岗位干活？")
            
            name = st.text_input("您的称呼", 
                                value=st.session_state.user_info["name"] if not st.session_state.temp_dossier.get("name") else st.session_state.temp_dossier.get("name"), 
                                placeholder="比如：老张、张三")
            
            job = st.text_input("当时的岗位/工种", 
                               value=st.session_state.temp_dossier.get("job", ""), 
                               placeholder="比如：瓦工、普工、技术员...")

            st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="secondary-btn-wrapper big-btn-wrapper">', unsafe_allow_html=True)
                if st.button("返回上一步", use_container_width=True, key="back_to_2"):
                    st.session_state.wizard_step = 2
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="big-btn-wrapper">', unsafe_allow_html=True)
                # Success style final button
                if st.button("✨ 完成建档", use_container_width=True, type="primary"):
                    if name and job:
                        st.session_state.temp_dossier["name"] = name
                        st.session_state.temp_dossier["job"] = job
                        
                        # Final Summary Overlay logic could go here, but let's just create.
                        with st.spinner("正在加急建立档案..."):
                            new_id = create_new_case(st.session_state.temp_dossier)
                            st.session_state.active_case_id = new_id
                            st.session_state.app_mode = "HOME"
                            st.session_state.wizard_step = 1 # Reset for next time
                            st.session_state.temp_dossier = {} 
                            st.toast("✅ 档案已建立，老乡加油！")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.warning("请留下您的称呼和岗位，方便我们提供建议。")
                st.markdown('</div>', unsafe_allow_html=True)

    # Global Cancel at the bottom
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    if st.button("❌ 放弃建档并返回", help="放弃当前输入的内容"):
        st.session_state.wizard_step = 1
        st.session_state.temp_dossier = {}
        st.session_state.app_mode = "HOME"
        st.rerun()
