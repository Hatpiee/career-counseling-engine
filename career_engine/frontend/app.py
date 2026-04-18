import streamlit as st
import requests

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Career AI", page_icon="🚀", layout="centered")

# ---- CUSTOM STYLING ----
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
h1 {
    text-align: center;
}
.card {
    padding: 1.2rem;
    border-radius: 12px;
    background-color: #1e1e1e;
    margin-bottom: 1rem;
    border: 1px solid #333;
}
.section {
    margin-top: 1rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ---- HEADER ----
st.markdown("<h1>🚀 AI Career Recommendation System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Get career guidance and learning roadmaps instantly</p>", unsafe_allow_html=True)

st.markdown("---")

# ---- INPUT ----
user_input = st.text_area("💬 Enter your career interests or goals", height=120)

if st.button("✨ Get Recommendations", use_container_width=True):
    if not user_input.strip():
        st.warning("Please enter your career interests.")
    else:
        with st.spinner("Analyzing your request..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/chat",
                    json={"message": user_input},
                    timeout=30
                )

                if response.status_code != 200:
                    st.error("Backend error. Please try again.")
                else:
                    data = response.json()

                    # -------- CAREER MODE --------
                    if "career_recommendations" in data:
                        careers = data.get("career_recommendations", [])

                        if careers:
                            st.markdown("## 🎯 Career Recommendations")

                            for c in careers:
                                st.markdown('<div class="card">', unsafe_allow_html=True)

                                st.markdown(f"### {c.get('career', 'Unknown Career')}")

                                match_score = c.get("match_score", 0)
                                st.progress(match_score)
                                st.caption(f"Match Score: {int(match_score * 100)}%")

                                st.write(c.get("why_it_fits", "N/A"))

                                skills = c.get("skills_required", [])
                                if skills:
                                    st.markdown("**🛠 Skills Required**")
                                    for s in skills:
                                        st.write(f"• {s}")

                                roadmap = c.get("learning_roadmap", [])
                                if roadmap:
                                    st.markdown("**🧭 Roadmap**")
                                    for r in roadmap:
                                        st.write(f"• {r}")

                                st.markdown('</div>', unsafe_allow_html=True)

                    # -------- LEARNING MODE --------
                    if "topic" in data:
                        st.markdown("## 📘 Learning Plan")

                        st.markdown('<div class="card">', unsafe_allow_html=True)

                        st.markdown(f"### {data.get('topic', '')}")
                        st.write(data.get("beginner_friendly_explanation", ""))

                        st.markdown("**📌 Why this is useful**")
                        st.write(data.get("why_this_topic_is_useful", ""))

                        st.markdown("**🧠 Skills to Learn First**")
                        for s in data.get("skills_to_learn_first", []):
                            st.write(f"• {s}")

                        st.markdown("**🗺 Step-by-Step Roadmap**")
                        for step in data.get("step_by_step_roadmap", []):
                            st.write(f"• {step}")

                        tools = data.get("tools_or_technologies", [])
                        if tools:
                            st.markdown("**⚙️ Tools / Technologies**")
                            for t in tools:
                                st.write(f"• {t}")

                        projects = data.get("beginner_project_ideas", [])
                        if projects:
                            st.markdown("**💡 Project Ideas**")
                            for p in projects:
                                st.write(f"• {p}")

                        st.markdown('</div>', unsafe_allow_html=True)

                    # -------- FALLBACK --------
                    if "career_recommendations" not in data and "topic" not in data:
                        st.info("No results found")

            except requests.exceptions.RequestException:
                st.error("Backend error. Please try again.")