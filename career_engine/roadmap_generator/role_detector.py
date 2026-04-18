def detect_role(text):

    text = text.lower()

    role_keywords = {

        "software_engineer": [
            "software engineer", "sde", "developer", "programmer"
        ],

        "backend_developer": [
            "backend", "backend developer", "server side"
        ],

        "full_stack_developer": [
            "full stack", "fullstack", "frontend and backend"
        ],

        "machine_learning_engineer": [
            "machine learning", "ml engineer", "machine learning engineer"
        ],

        "data_scientist": [
            "data scientist", "data science"
        ],

        "data_engineer": [
            "data engineer", "data pipelines"
        ],

        "cloud_engineer": [
            "cloud engineer", "cloud computing", "aws", "azure", "gcp"
        ],

        "devops_engineer": [
            "devops", "ci cd", "infrastructure automation"
        ],

        "cybersecurity_engineer": [
            "cybersecurity", "security engineer", "ethical hacking", "penetration testing"
        ],

        "blockchain_developer": [
            "blockchain", "web3", "smart contracts"
        ],

        "game_developer": [
            "game developer", "game dev", "game development"
        ],

        "uiux_designer": [
            "ui", "ux", "ui ux", "designer", "product design"
        ],

        "ai_architect": [
            "ai architect", "ai systems"
        ],

        "prompt_engineer": [
            "prompt engineer", "prompt engineering", "prompting"
        ],

        "embedded_systems_engineer": [
            "embedded", "embedded systems", "firmware",
            "microcontroller", "arduino", "raspberry pi",
            "iot", "sensor systems"
        ],

        "electronics_engineer": [
            "electronics", "circuit design", "pcb",
            "analog electronics", "digital electronics"
        ]
    }

    for role, keywords in role_keywords.items():
        for keyword in keywords:
            if keyword in text:
                return role

    return "software_engineer"