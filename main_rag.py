import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from college_predictor_engine.services.college_query_service import get_colleges_filtered
from career_engine.services.profile_extractor import extract_profile
from career_engine.services.career_matcher import get_top_careers, load_careers, build_career_context

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from fastapi import Depends
from sqlalchemy.orm import Session

from college_predictor_engine.services.college_query_service import (
    get_all_colleges,
    get_colleges_by_tier,
    get_colleges_by_exam,
    get_colleges_by_state
)

from college_predictor_engine.app.database.db_config import get_db
import os
import json
import tempfile
import assemblyai as aai
from dotenv import load_dotenv

from typing import Optional
from pydantic import BaseModel

class PredictCollegeRequest(BaseModel):
    jee_mains_rank: int
    boards_percentage: float
    jee_advanced_rank: Optional[int] = None
    bitsat_score: Optional[int] = None
    preferred_location: Optional[str] = "Any"

class CareerRequest(BaseModel):
    query: str

load_dotenv()

app = FastAPI()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing in .env")

if not ASSEMBLYAI_API_KEY:
    raise ValueError("ASSEMBLYAI_API_KEY is missing in .env")

aai.settings.api_key = ASSEMBLYAI_API_KEY

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    temperature=0.3
)

ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".webm", ".mpeg", ".mp4", ".ogg"}


class ChatRequest(BaseModel):
    message: str
class CollegeRequest(BaseModel):
    tier: str | None = None
    exam: str | None = None
    state: str | None = None

def detect_query_type(user_query: str) -> str:
    q = user_query.lower()

    learning_keywords = [
        "how do i learn", "how to learn", "roadmap", "from scratch",
        "beginner", "new to", "how do i start", "what should i learn",
        "step by step", "guide me", "first year", "how will i do it",
        "how can i learn", "where do i start", "learn deeply", "deeply"
    ]

    career_keywords = [
        "career", "job", "role", "profession", "what suits me",
        "which career", "career options", "best career", "what careers",
        "what career", "which jobs", "future job", "future career"
    ]

    learning_score = sum(1 for kw in learning_keywords if kw in q)
    career_score = sum(1 for kw in career_keywords if kw in q)

    if learning_score > 0 and career_score > 0:
        return "hybrid"
    elif learning_score > 0:
        return "learning_roadmap"
    else:
        return "career_recommendation"


def clean_llm_json(raw_output: str) -> str:
    raw_output = raw_output.strip()
    if raw_output.startswith("```"):
        raw_output = raw_output.replace("```json", "").replace("```", "").strip()
    return raw_output

def ensure_list(x):
    import re

    if isinstance(x, list):
        return x

    if isinstance(x, str):
        # extract <li> items if HTML
        items = re.findall(r'<li>(.*?)</li>', x)
        if items:
            return [re.sub('<.*?>', '', i).strip() for i in items]

        # fallback: split text
        clean = re.sub('<.*?>', '', x)
        return [i.strip() for i in clean.split(",") if i.strip()]

    return []


def validate_career_response(result: dict):
    if "career_recommendations" not in result or not isinstance(result["career_recommendations"], list):
        raise ValueError("Missing or invalid career_recommendations")

    if len(result["career_recommendations"]) != 3:
        raise ValueError("Model did not return exactly 3 career recommendations")

    for rec in result["career_recommendations"]:
        if not isinstance(rec, dict):
            raise ValueError("Each recommendation must be an object")

        required_fields = [
            "career",
            "source_type",
            "grounded_in_dataset",
            "match_score",
            "why_it_fits",
            "skills_required",
            "learning_roadmap"
        ]

        for field in required_fields:
            if field not in rec:
                raise ValueError(f"Missing field: {field}")

        if rec["source_type"] not in ["grounded", "exploratory"]:
            raise ValueError("source_type must be 'grounded' or 'exploratory'")

        if not isinstance(rec["grounded_in_dataset"], bool):
            raise ValueError("grounded_in_dataset must be boolean")

        if rec["source_type"] == "grounded" and rec["grounded_in_dataset"] is not True:
            raise ValueError("grounded recommendation must have grounded_in_dataset=true")

        if rec["source_type"] == "exploratory" and rec["grounded_in_dataset"] is not False:
            raise ValueError("exploratory recommendation must have grounded_in_dataset=false")

        score = rec["match_score"]
        if not isinstance(score, (int, float)) or not (0 <= score <= 1):
            raise ValueError("match_score must be a number between 0 and 1")

        if not isinstance(rec["skills_required"], list) or len(rec["skills_required"]) == 0:
            raise ValueError("skills_required must be a non-empty list")

        if not isinstance(rec["learning_roadmap"], list) or len(rec["learning_roadmap"]) == 0:
            raise ValueError("learning_roadmap must be a non-empty list")


def validate_roadmap_response(result: dict):
    required_fields = [
        "topic",
        "current_level",
        "beginner_friendly_explanation",
        "why_this_topic_is_useful",
        "skills_to_learn_first",
        "step_by_step_roadmap",
        "tools_or_technologies",
        "beginner_project_ideas",
        "common_mistakes_to_avoid",
        "possible_careers_after_learning"
    ]

    for field in required_fields:
        if field not in result:
            raise ValueError(f"Missing field: {field}")

    if not isinstance(result["topic"], str) or not result["topic"].strip():
        raise ValueError("topic must be a non-empty string")

    if not isinstance(result["current_level"], str) or not result["current_level"].strip():
        raise ValueError("current_level must be a non-empty string")

    list_fields = [
        "skills_to_learn_first",
        "step_by_step_roadmap",
        "tools_or_technologies",
        "beginner_project_ideas",
        "common_mistakes_to_avoid",
        "possible_careers_after_learning"
    ]

    for field in list_fields:
        if not isinstance(result[field], list) or len(result[field]) == 0:
            raise ValueError(f"{field} must be a non-empty list")


def validate_hybrid_response(result: dict):
    if "career_recommendations" not in result or "learning_guidance" not in result:
        raise ValueError("Hybrid response must contain career_recommendations and learning_guidance")

    validate_career_response({"career_recommendations": result["career_recommendations"]})
    validate_roadmap_response(result["learning_guidance"])


def transcribe_audio_file(audio_bytes: bytes, original_filename: str) -> str:
    file_ext = os.path.splitext(original_filename)[1].lower()

    if file_ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format. Allowed formats: {', '.join(sorted(ALLOWED_AUDIO_EXTENSIONS))}"
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext or ".wav") as temp_audio:
            temp_audio.write(audio_bytes)
            temp_path = temp_audio.name

        config = aai.TranscriptionConfig(
    speech_models=["universal-3-pro", "universal-2"]
)

        transcriber = aai.Transcriber(config=config)
        transcript = transcriber.transcribe(temp_path)

        if transcript.status == aai.TranscriptStatus.error:
            raise HTTPException(
                status_code=500,
                detail=f"AssemblyAI transcription failed: {transcript.error}"
            )

        transcript_text = (transcript.text or "").strip()

        if not transcript_text:
            raise HTTPException(status_code=500, detail="Transcription returned empty text")

        return transcript_text

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    audio_bytes = await file.read()

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")

    transcript_text = transcribe_audio_file(audio_bytes, file.filename)

    return {
        "success": True,
        "filename": file.filename,
        "transcript": transcript_text
    }


@app.post("/chat")
async def chat(request: ChatRequest):
    user_query = request.message
    query_type = detect_query_type(user_query)

    profile = extract_profile(llm, user_query)

    try:
        career_db = load_careers()
    except Exception as e:
        return {"error": "Failed to load career database", "details": str(e)}

    top_careers = get_top_careers(profile, career_db)

    top_career_names = []
    for c in top_careers:
        if isinstance(c, dict) and "role_name" in c:
            top_career_names.append(c["role_name"])

    try:
        context = build_career_context(user_query)
    except Exception as e:
        return {"error": "Failed to retrieve career context", "details": str(e)}

    if query_type == "career_recommendation":
        prompt = f"""
You are an AI career counseling assistant.

Your job is to recommend careers using a HYBRID strategy:
1. Use the career dataset context as the grounded base whenever it is genuinely relevant.
2. Prefer top rule-based matched careers only when they strongly fit the user's actual intent.
3. Never force a grounded career into the final list just because it exists in the dataset.
4. If the dataset does not contain strong relevant matches, you should return exploratory careers instead.
5. Relevance to the user's stated interest is the highest priority.

User Profile:
{profile}

User Question:
{user_query}

Top career matches from rule-based matching:
{top_career_names}

Career Dataset Context:
{context}

Task:
Recommend the 3 most suitable careers for the user.

Return ONLY valid JSON in exactly this format:

{{
  "career_recommendations": [
    {{
      "career": "",
      "source_type": "",
      "grounded_in_dataset": false,
      "match_score": 0.0,
      "why_it_fits": "",
      "skills_required": ["", "", ""],
      "learning_roadmap": ["", "", "", ""]
    }},
    {{
      "career": "",
      "source_type": "",
      "grounded_in_dataset": false,
      "match_score": 0.0,
      "why_it_fits": "",
      "skills_required": ["", "", ""],
      "learning_roadmap": ["", "", "", ""]
    }},
    {{
      "career": "",
      "source_type": "",
      "grounded_in_dataset": false,
      "match_score": 0.0,
      "why_it_fits": "",
      "skills_required": ["", "", ""],
      "learning_roadmap": ["", "", "", ""]
    }}
  ]
}}
"""

    elif query_type == "learning_roadmap":
        prompt = f""" ... (UNCHANGED FULL BLOCK HERE) ... """

    else:
        prompt = f""" ... (UNCHANGED FULL BLOCK HERE) ... """

    response = llm.invoke([HumanMessage(content=prompt)])
    raw_output = clean_llm_json(response.content)

    try:
        result = json.loads(raw_output)

        if query_type == "career_recommendation":
            validate_career_response(result)
        elif query_type == "learning_roadmap":
            validate_roadmap_response(result)
        else:
            validate_hybrid_response(result)

    except (json.JSONDecodeError, ValueError) as e:
        result = {
            "error": "Model returned invalid JSON",
            "query_type": query_type,
            "details": str(e),
            "raw_response": raw_output
        }

    if "career_recommendations" in result:
        for rec in result["career_recommendations"]:

            if "learning_roadmap" in rec:
                rec["roadmap"] = rec["learning_roadmap"]

            if "roadmap" not in rec:
                rec["roadmap"] = []

    # ================= ✅ ADDITION =================
    def ensure_list(x):
        import re
        if isinstance(x, list):
            return x
        if isinstance(x, str):
            items = re.findall(r'<li>(.*?)</li>', x)
            if items:
                return [re.sub('<.*?>', '', i).strip() for i in items]
            clean = re.sub('<.*?>', '', x)
            return [i.strip() for i in clean.split(",") if i.strip()]
        return []

    if "career_recommendations" in result:
        for rec in result["career_recommendations"]:
            rec["skills_required"] = ensure_list(rec.get("skills_required", []))
            rec["roadmap"] = ensure_list(rec.get("roadmap", []))
    # =============================================

    if "career_recommendations" in result:
        print(result["career_recommendations"][0])
    else:
        print("No career recommendations in this response:", result)

    return result



@app.post("/predict-college")
def predict_college(request: PredictCollegeRequest, db: Session = Depends(get_db)):
    try:
        jee_mains_rank = request.jee_mains_rank
        boards_percentage = request.boards_percentage
        jee_advanced_rank = request.jee_advanced_rank
        bitsat_score = request.bitsat_score

        colleges = get_colleges_filtered(db)

        def normalize(text):
            return str(text).lower().strip()

        def classify_rank(rank, cutoff):
            # More realistic bands
            if rank <= cutoff:
                return "Safe"
            elif rank <= 1.25 * cutoff:
                return "Target"
            elif rank <= 2.0 * cutoff:
                return "Dream"
            return "Ignore"

        def is_private(name):
            name = normalize(name)
            return any(k in name for k in [
                "vit", "srm", "kiit", "amity", "lpu", "manipal", "thapar"
            ])

        results = []

        for c in colleges:
            if c.cutoff is None:
                continue

            exam = normalize(c.entrance_exam)

            # IIT filtering stays same
            if not jee_advanced_rank and "jee advanced" in exam:
                continue

            cutoff = float(c.cutoff)
            tag = "Ignore"
            score = None

            # -------------------------
            # JEE MAIN
            # -------------------------
            if "jee main" in exam:
                score = jee_mains_rank
                tag = classify_rank(score, cutoff)

            # -------------------------
            # BITSAT
            # -------------------------
            elif "bitsat" in exam:
                if not bitsat_score:
                    continue
                score = bitsat_score
                if score >= cutoff:
                    tag = "Safe"
                elif score >= 0.92 * cutoff:
                    tag = "Target"
                else:
                    tag = "Dream"

            # -------------------------
            # PRIVATE / OTHERS
            # -------------------------
            else:
                score = jee_mains_rank
                # Slight relaxation but not overpowered
                tag = classify_rank(score, cutoff * 1.3)

            if tag == "Ignore":
                continue

            # Ranking logic (keep your structure but fix bias)
            relative_gap = abs(score - cutoff) / (cutoff + 1)

            private_penalty = 1.1 if is_private(c.college_name) else 1.0

            ranking_score = relative_gap * private_penalty

            results.append({
                "college_name": c.college_name,
                "branch": "General Engineering",
                "tier": c.tier,
                "exam": c.entrance_exam,
                "state": c.state,
                "your_rank_fit": tag,
                "ranking_score": ranking_score
            })

        # =========================
        # SORTING (consistent)
        # =========================
        def sort_key(x):
            exam = normalize(x["exam"])
            priority = 0 if "jee main" in exam else 1
            return (priority, x["ranking_score"])

        dream = sorted([r for r in results if r["your_rank_fit"] == "Dream"], key=sort_key)
        target = sorted([r for r in results if r["your_rank_fit"] == "Target"], key=sort_key)
        safe = sorted([r for r in results if r["your_rank_fit"] == "Safe"], key=sort_key)

        # Keep your 3-5-3 structure
        final = []
        final.extend(dream[:3])
        final.extend(target[:5])
        final.extend(safe[:3])

        # Fill remaining if needed
        if len(final) < 11:
            remaining = sorted(results, key=sort_key)
            for r in remaining:
                if r not in final:
                    final.append(r)
                if len(final) == 11:
                    break

        for r in final:
            r.pop("ranking_score", None)

        return {"predicted_colleges": final}

    except Exception as e:
        print("❌ ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/recommend-career")
async def recommend_career(request: CareerRequest):
    return await chat(ChatRequest(message=request.query))
