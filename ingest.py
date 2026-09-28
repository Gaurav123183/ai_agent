import json
import os

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types


# =========================================
# LOAD ENVIRONMENT
# =========================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in .env file."
    )


# =========================================
# GEMINI
# =========================================

client = genai.Client(
    api_key=api_key
)


# =========================================
# CHROMADB
# =========================================

chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = chroma_client.get_or_create_collection(
    name="emergency_guidelines"
)


# =========================================
# LOAD YOUR DATABASE
# =========================================

with open(
    "data/emergency_guidelines.json",
    "r",
    encoding="utf-8"
) as file:

    database = json.load(file)


# =========================================
# READ SITUATIONS
# =========================================

situations = database["situations"]


# =========================================
# ADD EACH SITUATION TO CHROMADB
# =========================================

for situation in situations:

    emergency_type = situation["type"]
    label = situation["label"]
    actions = situation["actions"]


    # Combine all verified actions
    content = "\n".join(
        f"{i + 1}. {action}"
        for i, action in enumerate(actions)
    )


    document = f"""
Emergency type: {emergency_type}

Situation: {label}

Verified actions:
{content}
"""


    print(
        f"Creating embedding for: {label}"
    )


    # =====================================
    # CREATE EMBEDDING
    # =====================================

    response = client.models.embed_content(

        model="gemini-embedding-001",

        contents=document,

        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT"
        )
    )


    embedding = response.embeddings[0].values


    # =====================================
    # STORE IN CHROMADB
    # =====================================

    collection.upsert(

        ids=[f"situation_{emergency_type}"],

        documents=[document],

        embeddings=[embedding],

        metadatas=[
            {
                "type": emergency_type,
                "label": label
            }
        ]
    )


print()
print("======================================")
print("YOUR EMERGENCY DATABASE IS READY")
print("======================================")
print(
    f"Stored {len(situations)} emergency situations."
)