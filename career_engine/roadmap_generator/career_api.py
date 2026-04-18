from fastapi import FastAPI
from pydantic import BaseModel

from text_cleaner import normalize_text
from entity_extractor import extract_entities
from role_detector import detect_role
from profile_builder import build_profile
from career_dataset_loader import load_dataset
from roadmap_personalizer import personalize
from roadmap_generator import generate_roadmap

app = FastAPI()


class UserInput(BaseModel):
    user_text: str


@app.post("/generate-roadmap")
def generate_career_roadmap(input: UserInput):

    user_text = input.user_text

    text = normalize_text(user_text)

    entities = extract_entities(text)

    role = detect_role(text)

    profile = build_profile(role, entities)

    dataset = load_dataset()

    personalized = personalize(dataset, profile)

    roadmap = generate_roadmap(personalized)

    return {
        "career_goal": role,
        "roadmap": roadmap
    }