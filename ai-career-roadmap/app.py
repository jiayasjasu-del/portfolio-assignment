"""AI Career Roadmap & Skill Gap Finder - Streamlit entry point."""

import streamlit as st

from roadmap import RoadmapError, generate_roadmap, make_report

st.set_page_config(page_title="CareerPath AI | Career Roadmap", page_icon="🧭", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
.stApp { background:#f5f7fb; } .block-container { padding-top:2.2rem; max-width:1180px; }
.hero { padding:1.7rem 2rem; border-radius:22px; color:white; background:linear-gradient(120deg,#142944,#315b8a 65%,#657fe0); margin-bottom:1.2rem; }
.hero p { color:#dfe8f6; margin-bottom:0; } .card { background:white; border:1px solid #e6eaf1; border-radius:15px; padding:1rem 1.2rem; margin:.6rem 0; box-shadow:0 3px 12px #172b4d0a; }
.muted { color:#627087; } div[data-testid="stMetric"] { background:white; border:1px solid #e6eaf1; border-radius:14px; padding:14px 16px; }
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>🧭 Your next career move, made clearer.</h1><p>Turn your current skills and study time into an AI-personalized eight-week plan.</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Your profile")
    with st.form("profile_form"):
        name = st.text_input("Your name", placeholder="e.g. Priya")
        education = st.text_input("Education", placeholder="e.g. B.Tech AI, 2nd year")
        skills = st.text_area("Skills you already have", placeholder="e.g. Python basics, HTML, communication", help="Separate skills with commas.", height=100)
        target_role = st.text_input("Target job role", placeholder="e.g. Data Scientist")
        level = st.selectbox("Current level", ["Beginner", "Intermediate", "Advanced"])
        hours = st.slider("Study hours per week", min_value=2, max_value=30, value=8)
        submitted = st.form_submit_button("Build my roadmap", type="primary", use_container_width=True)

if submitted:
    missing = [label for label, value in (("name", name), ("education", education), ("skills", skills), ("target job role", target_role)) if not value.strip()]
    if missing:
        st.sidebar.error("Please fill in: " + ", ".join(missing) + ".")
    else:
        try:
            with st.spinner("Gemini is matching your skills and planning your next eight weeks…"):
                st.session_state["roadmap"] = generate_roadmap(name=name.strip(), education=education.strip(), skills=skills.strip(), target_role=target_role.strip(), level=level, hours_per_week=hours)
                st.session_state["profile"] = {"name": name.strip(), "education": education.strip(), "skills": skills.strip(), "target_role": target_role.strip(), "level": level, "hours_per_week": hours}
        except RoadmapError as exc:
            st.sidebar.error(str(exc))

roadmap = st.session_state.get("roadmap")
profile = st.session_state.get("profile")
if not roadmap:
    st.info("Fill out your profile on the left, then choose **Build my roadmap** to get started.")
    st.markdown("### What you’ll get")
    a, b, c = st.columns(3)
    a.markdown('<div class="card"><h3>🎯 Skill check</h3><p class="muted">See what you know and what to learn next.</p></div>', unsafe_allow_html=True)
    b.markdown('<div class="card"><h3>🗓️ Eight-week plan</h3><p class="muted">A weekly schedule sized to your available study time.</p></div>', unsafe_allow_html=True)
    c.markdown('<div class="card"><h3>🛠️ Portfolio projects</h3><p class="muted">Three practical projects to show what you can do.</p></div>', unsafe_allow_html=True)
else:
    st.subheader(f"Roadmap for {profile['name']} · {profile['target_role']}")
    st.caption(f"{profile['education']}  ·  {profile['level']}  ·  {profile['hours_per_week']} study hours per week")
    overview = st.columns(3)
    overview[0].metric("Skills assessed", len(roadmap.skills))
    overview[1].metric("Weeks planned", len(roadmap.weeks))
    overview[2].metric("Portfolio projects", len(roadmap.projects))
    skills_tab, plan_tab, projects_tab = st.tabs(["📊 Skill gap", "🗓️ 8-week roadmap", "🛠️ Portfolio projects"])
    with skills_tab:
        st.markdown("### Your skills against the role")
        st.dataframe([{"Skill": item.skill, "Status": item.status, "Why it matters": item.explanation} for item in roadmap.skills], use_container_width=True, hide_index=True, column_config={"Status": st.column_config.TextColumn(width="small")})
    with plan_tab:
        st.markdown("### A steady plan that fits your week")
        for week in roadmap.weeks:
            with st.expander(f"Week {week.week}: {week.focus}", expanded=week.week == 1):
                st.write(week.learning_goals)
                st.caption(f"**Activities:** {week.activities}")
                st.success(f"**By the end:** {week.outcome}")
    with projects_tab:
        st.markdown("### Build proof of your skills")
        for number, project in enumerate(roadmap.projects, start=1):
            st.markdown(f'<div class="card"><h4>{number}. {project.title}</h4><p>{project.description}</p><p><b>Skills:</b> {project.skills_used}</p><p><b>Portfolio result:</b> {project.deliverable}</p></div>', unsafe_allow_html=True)
    st.download_button("⬇️ Download your roadmap (.txt)", data=make_report(profile, roadmap), file_name="my_career_roadmap.txt", mime="text/plain", type="primary")

st.divider()
st.caption("AI-generated guidance is a starting point. Check current job postings and adapt the plan to your goals.")
