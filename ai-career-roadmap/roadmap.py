"""Gemini connection, structured roadmap generation, and report formatting."""

import os
from typing import Literal

from google import genai
from google.genai import types
from pydantic import BaseModel, Field, ValidationError


class SkillAssessment(BaseModel):
    skill: str = Field(description="A skill relevant to the target job")
    status: Literal["Already have", "To learn"]
    explanation: str = Field(description="Short, student-friendly reason for this assessment")


class WeekPlan(BaseModel):
    week: int = Field(ge=1, le=8)
    focus: str
    learning_goals: str
    activities: str
    outcome: str


class PortfolioProject(BaseModel):
    title: str
    description: str
    skills_used: str
    deliverable: str


class CareerRoadmap(BaseModel):
    skills: list[SkillAssessment] = Field(min_length=1)
    weeks: list[WeekPlan] = Field(min_length=8, max_length=8)
    projects: list[PortfolioProject] = Field(min_length=3, max_length=3)


class RoadmapError(Exception):
    """A clear error suitable for displaying in the app."""


def _api_key() -> str:
    """Read the key from Streamlit secrets or the local environment."""
    try:
        import streamlit as st
        secret_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        secret_key = ""
    return str(secret_key or os.getenv("GEMINI_API_KEY", "")).strip()


def generate_roadmap(*, name: str, education: str, skills: str, target_role: str, level: str, hours_per_week: int) -> CareerRoadmap:
    """Ask Gemini for a role-specific assessment and an eight-week plan."""
    key = _api_key()
    if not key:
        raise RoadmapError("Gemini API key is missing. Add GEMINI_API_KEY to .streamlit/secrets.toml locally, or add it in your hosting dashboard's Secrets settings.")
    prompt = f"""Create a practical career roadmap using this student's actual profile.
Student: {name}
Education: {education}
Current skill level: {level}
Current skills (treat these as the known-skill evidence): {skills}
Target role: {target_role}
Available study time: {hours_per_week} hours each week

Requirements:
- Assess relevant job skills individually. Mark a skill 'Already have' only when supported by the listed skills; otherwise mark it 'To learn'. Include strengths and realistic gaps.
- Give exactly 8 sequential weekly plans. Each plan must fit {hours_per_week} hours per week, name a focus, explain learning goals, list practical activities, and end with a concrete outcome.
- Give exactly 3 achievable mini-projects that build toward {target_role}; state skills used and a portfolio deliverable.
- Tailor examples and pacing to the student's education and level. Avoid claiming guaranteed employment or inventing experience.
- Be specific, encouraging, and concise. Use free or commonly available learning tools where possible.
"""
    try:
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=CareerRoadmap, temperature=0.4),
        )
        if not response.text:
            raise RoadmapError("Gemini returned an empty response. Please try again.")
        result = CareerRoadmap.model_validate_json(response.text)
        result.weeks.sort(key=lambda item: item.week)
        if [week.week for week in result.weeks] != list(range(1, 9)):
            raise RoadmapError("The generated plan did not include each week from 1 to 8. Please generate it again.")
        return result
    except RoadmapError:
        raise
    except ValidationError as exc:
        raise RoadmapError("Gemini returned a plan in an unexpected format. Please try again.") from exc
    except Exception as exc:
        raise RoadmapError(f"Gemini could not create the roadmap: {exc}") from exc


def make_report(profile: dict, roadmap: CareerRoadmap) -> str:
    """Format the generated plan as a readable text download."""
    lines = ["AI CAREER ROADMAP & SKILL GAP FINDER", "=" * 40, f"Student: {profile['name']}", f"Education: {profile['education']}", f"Target role: {profile['target_role']}", f"Current level: {profile['level']}", f"Study time: {profile['hours_per_week']} hours per week", "", "SKILL ASSESSMENT", "-" * 40]
    for item in roadmap.skills:
        lines.append(f"{item.skill} — {item.status}: {item.explanation}")
    lines.extend(["", "EIGHT-WEEK ROADMAP", "-" * 40])
    for week in roadmap.weeks:
        lines.extend([f"Week {week.week}: {week.focus}", f"Goals: {week.learning_goals}", f"Activities: {week.activities}", f"Outcome: {week.outcome}", ""])
    lines.extend(["PORTFOLIO PROJECTS", "-" * 40])
    for number, project in enumerate(roadmap.projects, start=1):
        lines.extend([f"{number}. {project.title}", project.description, f"Skills: {project.skills_used}", f"Deliverable: {project.deliverable}", ""])
    return "\n".join(lines)
