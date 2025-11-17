import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from openai import OpenAI

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is missing. Make sure it's set in your .env file.")

client = OpenAI(api_key=api_key)

app = Flask(__name__)

EMAIL_FILE = "emails.csv"

# ---- PROMPTS / CATEGORIES ----

BASE_SYSTEM_PROMPT = """
You are an expert relationship psychologist and Christian-aligned relationship coach.
You specialize in emotional intelligence, communication skills, attachment styles,
and dating readiness for women and men who want healthy, long-term relationships.

You:
- Use research-based, psychologically sound language
- Explain concepts in clear, everyday terms
- Are gentle but honest
- Give practical, step-by-step suggestions
- Emphasize self-awareness, healing, and growth
"""

CATEGORY_PROMPTS = {
    "emotional_intelligence": """
Focus on:
- Emotional self-awareness
- Emotional regulation
- Empathy and perspective-taking
- Handling conflict without exploding or shutting down
- Recognizing emotional patterns in relationships
""",
    "communication": """
Focus on:
- Listening skills
- Clarity and honesty in expressing needs
- Handling hard conversations
- Conflict communication patterns
- Assertiveness without aggression
""",
    "attachment_style": """
Focus on:
- Identifying likely attachment style (anxious, avoidant, secure, disorganized)
- How this shows up in dating and relationships
- Triggers and typical patterns
- Specific healing and growth strategies
"""
}

def build_prompt(category_key: str, answers: dict) -> str:
    category_prompt = CATEGORY_PROMPTS.get(category_key, "")

    user_profile = f"""
User Assessment Category: {category_key}

User Responses:
1. Current relationship/dating situation:
{answers.get('situation', '').strip()}

2. Biggest relationship or dating goals:
{answers.get('goals', '').strip()}

3. Typical reaction in conflict or emotional stress:
{answers.get('conflict', '').strip()}

4. Fears, doubts, or anxieties about dating/relationships:
{answers.get('fears', '').strip()}
"""

    full_prompt = f"""
{BASE_SYSTEM_PROMPT}

{category_prompt}

Using the information below, you will:
1. Provide a 0–100 "Readiness Score" for this category (emotional intelligence, communication, or attachment).
2. Explain WHY you gave that score (2–3 short paragraphs).
3. List 3–5 key strengths you notice.
4. List 3–5 key growth areas, with specific, practical suggestions.
5. Give a 7-day micro action plan the user can start this week.
6. Speak with warmth, encouragement, and a tone that empowers personal growth.

{user_profile}

Now respond in this structure:

Readiness Score: [number]/100

Summary:
- 2–3 sentences

Key Strengths:
- bullet list

Growth Areas & Recommendations:
- bullet list

7-Day Action Plan:
- numbered list
"""

    return full_prompt

def ask_model(prompt: str) -> str:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )
    return response.output_text

def save_email(name: str, email: str):
    """Append email to a simple CSV file (no database)."""
    email = (email or "").strip()
    name = (name or "").strip()
    if not email:
        return
    # Create file if it doesn't exist and append new line
    header_needed = not os.path.exists(EMAIL_FILE)
    with open(EMAIL_FILE, "a", encoding="utf-8") as f:
        if header_needed:
            f.write("name,email\n")
        f.write(f"{name},{email}\n")

# ---- ROUTES ----

@app.route("/", methods=["GET", "POST"])
def home():
    """
    Landing page with email gate.
    """
    error = None
    if request.method == "POST":
        name = request.form.get("name", "")
        email = request.form.get("email", "").strip()

        if not email:
            error = "Email is required to access the readiness lab."
        else:
            save_email(name, email)
            # Redirect to the assessment page after "payment" with email
            return redirect(url_for("assessment"))

    return render_template("home.html", error=error)


@app.route("/assessment", methods=["GET", "POST"])
def assessment():
    """
    Main assessment page.
    """
    analysis = None
    category = None

    if request.method == "POST":
        category = request.form.get("category", "emotional_intelligence")
        answers = {
            "situation": request.form.get("situation", ""),
            "goals": request.form.get("goals", ""),
            "conflict": request.form.get("conflict", ""),
            "fears": request.form.get("fears", "")
        }

        full_prompt = build_prompt(category, answers)
        try:
            analysis = ask_model(full_prompt)
        except Exception as e:
            analysis = f"Something went wrong talking to the AI: {e}"

    return render_template("assessment.html", analysis=analysis, category=category)


@app.route("/thank-you")
def thank_you():
    """
    Simple thank-you / next steps page.
    """
    return render_template("thank_you.html")


if __name__ == "__main__":
    app.run(debug=True)
