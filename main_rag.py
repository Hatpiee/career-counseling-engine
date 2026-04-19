from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from services.profile_extractor import extract_profile
from services.career_matcher import get_top_careers, load_careers, build_career_context

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

import os
import json
import tempfile
import assemblyai as aai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
print("GROQ:", os.getenv("GROQ_API_KEY"))
print("GOOGLE:", os.getenv("GOOGLE_API_KEY"))

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

Important selection logic:
- A grounded recommendation should be included only if it is clearly relevant to the user's question.
- If grounded options are weak, indirect, or only loosely related, do not include them.
- It is completely acceptable for all 3 recommendations to be exploratory.
- Do not invent weak links just to justify a grounded recommendation.
- Ranking must reflect actual career fit, not dataset availability.
- Avoid duplicate or near-duplicate roles.
- For broad beginner prompts, prefer roles that are understandable and practical before highly niche or overly advanced roles.
- Do not over-concentrate all 3 recommendations in the same narrow subdomain unless the user's prompt clearly asks for that.

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

Rules:
- Recommend exactly 3 careers.
- source_type must be either "grounded" or "exploratory".
- grounded_in_dataset must be true when source_type is "grounded" and false when source_type is "exploratory".
- Keep match_score between 0 and 1.
- Use higher scores only for genuinely strong matches.
- why_it_fits must directly reflect the user's stated interests, goals, or strengths.
- Do not justify a career using weak, speculative, or indirect connections.
- skills_required should be concise and relevant.
- learning_roadmap should contain short actionable steps.
- Do not include explanations outside JSON.
- Do not use markdown formatting.
"""

    elif query_type == "learning_roadmap":
        prompt = f"""
You are an AI learning and career guidance assistant.

User Profile:
{profile}

User Question:
{user_query}

Top career matches from rule-based matching:
{top_career_names}

Career Dataset Context:
{context}

Task:
The user is primarily asking how to learn a topic, where to start, or how to build skills from scratch.
Provide a beginner-friendly learning roadmap instead of focusing mainly on career recommendations.

Return ONLY valid JSON in exactly this format:

{{
  "topic": "",
  "current_level": "beginner",
  "beginner_friendly_explanation": "",
  "why_this_topic_is_useful": "",
  "skills_to_learn_first": ["", "", ""],
  "step_by_step_roadmap": ["", "", "", "", ""],
  "tools_or_technologies": ["", "", ""],
  "beginner_project_ideas": ["", "", ""],
  "common_mistakes_to_avoid": ["", "", ""],
  "possible_careers_after_learning": ["", "", ""]
}}

Rules:
- Assume the user is a beginner unless the query clearly says otherwise.
- Make the roadmap practical, simple, and step by step.
- Start from true beginner foundations before advanced or specialized tools.
- For first-year students or beginners, avoid jumping too quickly into niche technologies.
- The roadmap should progress from basics -> core concepts -> tools -> projects -> next-level learning.
- beginner_friendly_explanation should be simple and easy to understand.
- skills_to_learn_first should contain foundational skills, not advanced specialization.
- step_by_step_roadmap should be in the correct learning order.
- beginner_project_ideas should be simple starter projects before advanced builds.
- possible_careers_after_learning should be realistic and directly related to the topic.
- Do not include explanations outside JSON.
- Do not use markdown formatting.
"""

    else:
        prompt = f"""
You are an AI learning and career guidance assistant.

User Profile:
{profile}

User Question:
{user_query}

Top career matches from rule-based matching:
{top_career_names}

Career Dataset Context:
{context}

Task:
The user is asking both about suitable careers and how to start learning.
Return BOTH career recommendations and beginner-friendly learning guidance.

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
  ],
  "learning_guidance": {{
    "topic": "",
    "current_level": "beginner",
    "beginner_friendly_explanation": "",
    "why_this_topic_is_useful": "",
    "skills_to_learn_first": ["", "", ""],
    "step_by_step_roadmap": ["", "", "", "", ""],
    "tools_or_technologies": ["", "", ""],
    "beginner_project_ideas": ["", "", ""],
    "common_mistakes_to_avoid": ["", "", ""],
    "possible_careers_after_learning": ["", "", ""]
  }}
}}

Rules:
- Recommend exactly 3 careers.
- source_type must be either "grounded" or "exploratory".
- grounded_in_dataset must be true when source_type is "grounded" and false when source_type is "exploratory".
- Keep match_score between 0 and 1.
- Career recommendations must be genuinely relevant.
- Career recommendations must stay tightly aligned to the user's stated field of interest.
- Do not include careers from adjacent domains unless they are a strong and direct fit.
- Avoid speculative cross-domain recommendations.
- Learning guidance must be beginner-friendly and step by step.
- Start from foundations before advanced tools.
- Do not include explanations outside JSON.
- Do not use markdown formatting.
"""

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

    return result