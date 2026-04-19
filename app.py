import streamlit as st
import requests
import subprocess
import time
import os
import sys

# ================= PATH SETUP =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_URL = "http://127.0.0.1:8000"
BASE_URL = "http://127.0.0.1:8000"

# ================= BACKEND START FUNCTION =================
def start_backend():
    try:
        requests.get(f"{BACKEND_URL}/docs", timeout=2)
        return None
    except:
        pass

    process = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn",
            "main_rag:app",
            "--host", "127.0.0.1",
            "--port", "8000"
        ],
        cwd=BASE_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    for _ in range(25):
        try:
            requests.get(f"{BACKEND_URL}/docs", timeout=2)
            return process
        except:
            time.sleep(1)

    return process


# ================= START BACKEND =================
if "backend_process" not in st.session_state:
    st.session_state.backend_process = start_backend()

# ================= SESSION =================
if "page" not in st.session_state:
    st.session_state.page = "home"


# ================= HOME =================
def show_home():
    st.title("🎓 Career Counseling Platform")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎯 College Predictor", use_container_width=True):
            st.session_state.page = "college"
            st.rerun()

    with col2:
        if st.button("💼 Career Recommendation", use_container_width=True):
            st.session_state.page = "career"
            st.rerun()


# ================= COLLEGE =================
def show_college():
    col1, col2 = st.columns([10, 1])

    with col1:
        st.title("🎯 College Predictor")

    with col2:
        if st.button("←"):
            st.session_state.page = "home"
            st.rerun()

    col1, col2 = st.columns(2)

    with col1:
        jee_mains_rank = st.number_input("JEE Mains Rank", min_value=1, value=50000)

    with col2:
        boards_percentage = st.number_input("Boards Percentage", value=85.0)

    if st.button("🔍 Predict Colleges", use_container_width=True):

        payload = {
            "jee_mains_rank": int(jee_mains_rank),
            "boards_percentage": float(boards_percentage)
        }

        with st.spinner("Analyzing..."):
            try:
                res = requests.post(f"{BASE_URL}/predict-college", json=payload)
                data = res.json()

                colleges = data.get("predicted_colleges", [])

                dream, target, safe = [], [], []

                for c in colleges:
                    fit = c.get("your_rank_fit", "")
                    if fit == "Dream":
                        dream.append(c)
                    elif fit == "Target":
                        target.append(c)
                    elif fit == "Safe":
                        safe.append(c)

                def show_section(title, items, color):
                    st.markdown(f"### {title}")

                    if not items:
                        st.write("No colleges")
                        return

                    for i, c in enumerate(items, 1):

                        st.markdown(f"""<div style="
padding:18px;
border-radius:14px;
background: linear-gradient(145deg, #1e1e1e, #262626);
margin-bottom:12px;
box-shadow: 0 4px 10px rgba(0,0,0,0.4);
">
<h4 style="margin-bottom:8px;">
#{i} {c.get('college_name','')}
</h4>

<div style="color:#bbbbbb; font-size:14px;">
<b>Tier:</b> {c.get('tier','')} |
<b>Exam:</b> {c.get('exam','')} <br>
<b>State:</b> {c.get('state','')}
</div>

<div style="
color:{color};
font-weight:bold;
margin-top:8px;
">
{c.get('your_rank_fit','')}
</div>
</div>""", unsafe_allow_html=True)

                show_section("🔴 Dream Colleges", dream, "#ff4b4b")
                show_section("🟡 Target Colleges", target, "#ffd700")
                show_section("🟢 Safe Colleges", safe, "#00ff9f")

            except Exception as e:
                st.error(str(e))


# ================= CAREER =================
def show_career():
    col1, col2 = st.columns([10, 1])

    with col1:
        st.title("💼 Career Recommendation")

    with col2:
        if st.button("←"):
            st.session_state.page = "home"
            st.rerun()

    user_input = st.text_area("Enter your interest")

    if st.button("💡 Get Recommendation", use_container_width=True):

        if not user_input.strip():
            st.error("Enter something")
            return

        with st.spinner("Analyzing your profile..."):
            try:
                res = requests.post(
                    f"{BASE_URL}/chat",
                    json={"message": user_input.strip()}
                )

                data = res.json()

                if "career_recommendations" in data:

                    for r in data["career_recommendations"]:

                        score = int(round(r.get('match_score', 0) * 100))

                        with st.container():

                            # ===== MODERN CARD =====
                            st.markdown(f"""
                            <div style="
                                padding:20px;
                                border-radius:14px;
                                background: linear-gradient(145deg, #1e1e1e, #262626);
                                margin-bottom:10px;
                                box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                            ">
                                <h2 style="margin-bottom:5px;">
                                    {r.get('career','')}
                                </h2>
                                <p style="margin-top:6px; color:#cfcfcf;">
                                    {r.get('why_it_fits','')}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)

                            # ===== MATCH SCORE =====
                            st.markdown("**Match Score**")
                            st.progress(score / 100)

                            skills = r.get("skills_required", [])
                            roadmap = r.get("roadmap", [])

                            # ===== TWO COLUMN LAYOUT =====
                            col1, col2 = st.columns(2)

                            # ===== SKILLS =====
                            with col1:
                                st.markdown("### 🛠 Skills")
                                if isinstance(skills, list):
                                    for s in skills:
                                        st.markdown(f"- {s}")
                                else:
                                    st.markdown(f"- {skills}")

                            # ===== ROADMAP =====
                            with col2:
                                st.markdown("### 🧭 Roadmap")
                                if isinstance(roadmap, list):
                                    for step in roadmap:
                                        st.markdown(f"- {step}")
                                else:
                                    st.markdown(f"- {roadmap}")

                            st.markdown("<hr style='margin:15px 0;'>", unsafe_allow_html=True)

                else:
                    st.error("Unexpected response format")

            except Exception as e:
                st.error(str(e))


# ================= ROUTING =================
if st.session_state.page == "home":
    show_home()
elif st.session_state.page == "college":
    show_college()
elif st.session_state.page == "career":
    show_career()