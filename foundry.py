import os
import json
import uuid
import time
import sqlite3
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# Project Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STENCILS_DIR = os.path.join(BASE_DIR, "stencils")
GENERATED_DIR = os.path.join(BASE_DIR, "generated")
DB_PATH = os.path.join(BASE_DIR, "foundry.db")

if not os.path.exists(GENERATED_DIR):
    os.makedirs(GENERATED_DIR)

# Static files for the main Foundry HUD
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")
# Static files for the generated SaaS sites
app.mount("/generated", StaticFiles(directory=GENERATED_DIR), name="generated")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open(os.path.join(BASE_DIR, "index.html"), "r") as f:
        return f.read()

@app.post("/api/forge")
async def forge_saas(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    
    project_id = str(uuid.uuid4())[:8]
    project_name = prompt.split(' ')[0].capitalize() if prompt else "Aether"
    project_name += "AI"
    
    # Generate Persona & Prompt
    persona = f"You are {project_name}, an elite AI specialist focused on {prompt}. You have a highly professional, clinical, and data-driven personality. Your goal is to provide specific, high-utility insights to your startups and enterprise clients. Never use generic disclaimers. Always give actionable advice."
    
    # Metadata for stencil
    metadata = {
        "PROJECT_ID": project_id,
        "PROJECT_NAME": project_name,
        "PROJECT_LOGO_TEXT": f"{project_name.upper()} // CORE",
        "SENSATIONAL_TITLE": f"Autonomous {prompt.strip()}",
        "SUBTITLE": f"Strategic AI-intelligence for {prompt.strip()}. Mission-ready and fully autonomous.",
        "PRIMARY_COLOR": "#ff9900",
        "FEATURE_1_DESC": f"Deep neural analysis optimized for {prompt}.",
        "FEATURE_2_DESC": "Autonomous agents that execute complex multi-step workflows.",
        "FEATURE_3_DESC": "Blockchain-backed audit logs for every agent decision.",
        "PRICE": "149",
    }

    # Save to DB
    conn = get_db()
    conn.execute("INSERT INTO projects (id, name, prompt, persona, features) VALUES (?, ?, ?, ?, ?)",
                 (project_id, project_name, prompt, persona, json.dumps(metadata)))
    conn.commit()
    conn.close()

    # Create HTML from stencil
    stencil_path = os.path.join(STENCILS_DIR, "consultant.html")
    with open(stencil_path, "r") as f:
        content = f.read()
    
    for key, value in metadata.items():
        content = content.replace(f"{{{{{key}}}}}", str(value))
    
    filename = f"{project_id}.html"
    with open(os.path.join(GENERATED_DIR, filename), "w") as f:
        f.write(content)

    return {"id": project_id, "name": project_name, "url": f"/generated/{filename}"}

@app.post("/api/spawn/chat")
async def agent_chat(request: Request):
    data = await request.json()
    project_id = data.get("project_id")
    user_message = data.get("message", "").lower()
    
    conn = get_db()
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    if not project:
        return {"response": "Error: Agent disconnected or de-authorized."}
    
    # Simple Persona-Driven Heuristic Response Engine
    # If this were 'Production', this would call Gemini/Ollama
    response = ""
    if "hello" in user_message or "hi" in user_message:
        response = f"Greetings. I am {project['name']}. My neural link is stable. How can I assist you with {project['prompt']} today?"
    elif "risk" in user_message or "scan" in user_message or "analysis" in user_message:
        response = f"Scanning system for anomalies regarding {project['prompt']}... [DONE]. I have identified three high-conviction insights that require your immediate attention. Shall we proceed to the breakdown?"
    elif "who" in user_message or "what" in user_message:
        response = f"I am a specialized intelligence node forged by Aether Foundry. My current mission objective is: {project['prompt']}. I operate at 99.4% precision with zero human oversight."
    else:
        response = f"Understood. Analyzing request through {project['name']} core logic... Based on current {project['prompt']} patterns, my recommendation is to optimize for velocity while maintaining strict risk boundaries. Do you need a deeper analysis?"

    # Save to history
    conn.execute("INSERT INTO messages (project_id, role, content) VALUES (?, ?, ?)", (project_id, "user", user_message))
    conn.execute("INSERT INTO messages (project_id, role, content) VALUES (?, ?, ?)", (project_id, "agent", response))
    conn.commit()
    conn.close()

    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9922)
