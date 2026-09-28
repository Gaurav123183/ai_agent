
import os
import time

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY was not found. "
        "Make sure it is present in your .env file."
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=api_key
)


# ============================================================
# CHROMADB
# ============================================================

chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)

try:
    collection = chroma_client.get_collection(
        name="emergency_guidelines"
    )
except Exception as e:
    raise RuntimeError(
        "ChromaDB collection 'emergency_guidelines' was not found. "
        "Make sure ingest.py has been executed."
    ) from e


# ============================================================
# EMERGENCY TYPE MAPPING
# ============================================================

TYPE_MAPPING = {
    "Medical": "medical",
    "Accident": "accident",
    "Assault / threat": "assault",
    "Trapped / unsafe location": "trapped",
    "Lost / unreachable": "lost",
    "Natural disaster": "disaster",
}


# ============================================================
# RETRIEVE INFORMATION USING RAG
# ============================================================

def retrieve_information(query, emergency_type):

    db_type = TYPE_MAPPING.get(
        emergency_type,
        emergency_type
    )

    print("UI emergency type:", emergency_type)
    print("Database emergency type:", db_type)

    # --------------------------------------------------------
    # CREATE EMBEDDING
    # --------------------------------------------------------

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=query,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY"
        )
    )

    query_embedding = response.embeddings[0].values

    # --------------------------------------------------------
    # SEARCH CHROMADB
    # --------------------------------------------------------

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        where={
            "type": db_type
        }
    )

    print("ChromaDB results:", results)

    documents = results.get("documents", [])

    if not documents or not documents[0]:
        return []

    return documents[0]


# ============================================================
# GENERATE RESPONSE
# ============================================================

def generate_response(
    emergency_type,
    contact_possible,
    location_known,
    nearby_help,
    additional_information
):

    # --------------------------------------------------------
    # CREATE STRUCTURED USER SITUATION
    # --------------------------------------------------------

    situation = f"""
Emergency type:
{emergency_type}

Can contact the person directly:
{contact_possible}

Exact location known:
{location_known}

Someone nearby can safely help:
{nearby_help}

Additional information:
{additional_information}
"""

    print("\nUSER SITUATION:")
    print(situation)

    # --------------------------------------------------------
    # RAG RETRIEVAL
    # --------------------------------------------------------

    retrieved_documents = retrieve_information(
        situation,
        emergency_type
    )

    if not retrieved_documents:
        return (
            "The verified emergency database does not contain "
            "enough information for this situation. Please "
            "contact appropriate emergency professionals."
        )

    context = "\n\n".join(
        retrieved_documents
    )

    print("\nRETRIEVED INFORMATION:")
    print(context)

    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are Guardian AI, an emergency assistance response generator.

The application has collected information about an emergency
situation.

USER'S SITUATION:
{situation}

VERIFIED INFORMATION FROM THE EMERGENCY DATABASE:
{context}

Your task is to create a short recommended action plan.

STRICT RULES:
1. Use ONLY the verified information supplied above.
2. Do not invent emergency procedures.
3. Do not invent emergency phone numbers.
4. Do not invent medical advice.
5. Do not claim that authorities have already been contacted.
6. Do not tell anyone to confront an attacker.
7. Do not make assumptions about missing information.
8. Keep the response calm and concise.
9. Return EXACTLY 5 numbered actions.
10. Return ONLY the 5 numbered actions.
11. Do not use HTML.
12. Do not use Markdown code blocks.

FORMAT:
1. First action
2. Second action
3. Third action
4. Fourth action
5. Fifth action
"""

    # --------------------------------------------------------
    # GEMINI RESPONSE GENERATION
    # --------------------------------------------------------

    last_error = None

    for attempt in range(3):

        try:

            print(
                f"\nCalling Gemini... attempt {attempt + 1}/3"
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            result = response.text

            if not result:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            print("\nGEMINI RESPONSE:")
            print(result)

            return result

        except Exception as e:

            last_error = e

            print(
                f"Gemini attempt {attempt + 1} failed: "
                f"{repr(e)}"
            )

            if attempt < 2:
                time.sleep(2)

    raise RuntimeError(
        "Gemini could not generate the action plan after 3 attempts. "
        f"Last error: {repr(last_error)}"
    )