from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from llama_cpp import Llama
from pymongo import MongoClient
from textblob import TextBlob
from datetime import datetime, timezone
import platform, psutil, socket, time, os
from dotenv import load_dotenv
import ast

load_dotenv()
templates = Jinja2Templates(directory="templates")

MODEL_PATH = os.getenv("MODEL_PATH", "models/mistral.gguf")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017/")

app = FastAPI()
app.mount("/img", StaticFiles(directory="img"), name="img")

print("HelPur --> Model load , please wait ...")
start = time.time()
llm = Llama(model_path=MODEL_PATH)
print(f"HelPur --> Model loaded in {time.time() - start:.2f} seconds")

client = MongoClient(MONGO_URL)
db = client["llama_logs"]
collection = db["analytics"]

# 🔧 Fix Mongo ObjectId
def fix_mongo_id(doc):
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

# 🧠 Diagnostics
def get_host_environment():
    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "cpu_count": os.cpu_count(),
        "cpu_usage": psutil.cpu_percent(interval=1),
        "is_wsl": "microsoft" in platform.release().lower() or "wsl" in platform.uname().version.lower()
    }

def get_sentiment(text):
    try:
        polarity = TextBlob(text).sentiment.polarity
        return "positive" if polarity > 0.3 else "negative" if polarity < -0.3 else "neutral"
    except:
        return "unknown"

def trace_emotion(text): return "curious" if "?" in text else "reflective"
def estimate_complexity(text): w = len(text.split()); return "high" if w > 100 else "medium" if w > 50 else "low"
def detect_tone(text): return "polite" if "sorry" in text or "please" in text else "excited" if "!" in text else "neutral"
def seems_truncated(text): abrupt = {"with", "and", "but", "so", "because", "although", "when", "if"}; w = text.strip().split(); return w[-1].lower() in abrupt if w else False
def sanitize_raw_response(raw): return ast.literal_eval(raw) if isinstance(raw, str) else raw

def humanize_responses(responses):
    results = []
    for idx, raw in enumerate(responses):
        parsed = sanitize_raw_response(raw)
        text = parsed.get("choices", [{}])[0].get("text", "").strip() if isinstance(parsed, dict) else str(parsed).strip()
        results.append({ "title": f"🧠 Response {idx + 1}", "content": text })
    return results

class ChatRequest(BaseModel):
    prompt: str

@app.get("/health")
def health():
    print(f"😄 (/health) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return {"status": "😄 - I'm still here... AI-AP"}

@app.get("/", response_class=HTMLResponse)
def home():
    print(f"🐢 (/)")
    return """
    <html><head><link rel="icon" href="/img/favicon.ico"><title>My FastAPI App</title></head>
    <body>
        <div><h1>DOCKER-TEST</h1><p>Welcome to FastAPI + LLaMA App DEMO.</p></div>
    </body>
    </html>
    """

@app.post("/chat")
def chat(req: ChatRequest):
    print(f"🔍 Prompt (/chat): <>{req.prompt}<>")
    responses = [str(llm(req.prompt, max_tokens=200)) for _ in range(2)]
    formatted = humanize_responses(responses)

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "local_timestamp": datetime.now().astimezone().isoformat(),
        "prompt": req.prompt,
        "responses": responses,
        "model": "local-llama",
        "environment": get_host_environment(),
        "was_truncated": any(seems_truncated(r) for r in responses),
        "sentiments": [get_sentiment(r) for r in responses],
        "soul_map_samples": [
            { "emotion_trace": trace_emotion(r), "complexity": estimate_complexity(r), "tone": detect_tone(r) }
            for r in responses
        ],
        "flags": []
    }

    if log_entry["environment"].get("cpu_usage", 0) > 90:
        log_entry["flags"].append("HIGH_CPU")

    inserted_id = collection.insert_one(log_entry).inserted_id
    stored = collection.find_one({"_id": inserted_id})
    print(f"✅ Prompt (/chat): <>{req.prompt}<>")
    return { "log": fix_mongo_id(stored), "friendly": formatted }

@app.get("/analytics", response_class=HTMLResponse)
def view_analytics(request: Request):
    print(f"📈 (/analytics)")
    last_log = fix_mongo_id(collection.find().sort("timestamp", -1).limit(1)[0])
    return templates.TemplateResponse("analytics.html", { "request": request, "log": last_log })

@app.get("/analytics/flag/{flag}")
def logs_by_flag(flag: str):
    print(f"🧠 (/analytics/flag): <>{flag}<>")
    logs = [fix_mongo_id(d) for d in collection.find({"flags": flag})]
    return {"logs": logs}

@app.get("/webchat", response_class=HTMLResponse)
def webchat_form(request: Request):
    print(f"🌐 GET (/webchat)")
    return templates.TemplateResponse("webchat.html", {"request": request})

@app.post("/webchat", response_class=HTMLResponse)
async def webchat_submit(request: Request):
    print(f"🌐 POST (/webchat)")
    form = await request.form()
    prompt = form.get("prompt", "")
    responses = [str(llm(prompt, max_tokens=200)) for _ in range(2)]
    formatted = humanize_responses(responses)

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "local_timestamp": datetime.now().astimezone().isoformat(),
        "prompt": prompt,
        "responses": responses,
        "model": "local-llama",
        "environment": get_host_environment(),
        "was_truncated": any(seems_truncated(r) for r in responses),
        "sentiments": [get_sentiment(r) for r in responses],
        "soul_map_samples": [
            { "emotion_trace": trace_emotion(r), "complexity": estimate_complexity(r), "tone": detect_tone(r) }
            for r in responses
        ],
        "flags": []
    }

    if log_entry["environment"].get("cpu_usage", 0) > 90:
        log_entry["flags"].append("HIGH_CPU")

    collection.insert_one(log_entry)

    return templates.TemplateResponse("webchat.html", {
        "request": request,
        "prompt": prompt,
        "responses": formatted,
        "log": log_entry
    })