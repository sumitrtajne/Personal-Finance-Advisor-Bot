import json
import os
import re
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

try:
    import google.generativeai as genai
except ImportError:
    genai = None

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "finance-advisor-demo")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finance_advisor.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Budget guidance used by prompt engineering.
CATEGORY_TIPS = {
    "rent": "should not exceed 30% of income",
    "food": "should generally stay under 5% of income",
    "transport": "should generally stay within 10% of income",
    "dining": "should generally stay within 5% of income",
    "entertainment": "should generally stay within 5-8% of income",
    "utilities": "should generally stay within 10% of income",
    "savings": "should ideally be at least 20% of income",
}

GOAL_DESCRIPTIONS = {
    "emergency fund": "build a safety reserve for unexpected expenses",
    "vacation": "save a planned amount for a future trip",
    "gadget purchase": "save gradually for a planned technology purchase",
    "investment": "build long-term savings; do not provide specific investment products",
}

class MonthlyRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_name = db.Column(db.String(120), nullable=False)
    income = db.Column(db.Float, nullable=False)
    total_expense = db.Column(db.Float, nullable=False)
    balance = db.Column(db.Float, nullable=False)
    score = db.Column(db.Float, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    goal = db.Column(db.String(120), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def clean_category(value):
    return re.sub(r"[^a-zA-Z0-9 _-]", "", str(value)).strip()[:50]

def validate_input(data):
    if not isinstance(data, dict):
        return False, "Invalid JSON body."

    name = str(data.get("name", "User")).strip()
    if len(name) > 100:
        return False, "Name is too long."

    try:
        income = float(data.get("income", 0))
    except (TypeError, ValueError):
        return False, "Income must be a number."

    if income <= 0 or income > 100000000:
        return False, "Income must be greater than 0 and within a reasonable limit."

    expenses = data.get("expenses")
    if not isinstance(expenses, dict) or not expenses:
        return False, "Provide at least one expense category."

    cleaned = {}
    for category, amount in expenses.items():
        category = clean_category(category)
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return False, f"Invalid amount for {category or 'expense'}."
        if not category:
            continue
        if amount < 0 or amount > 100000000:
            return False, f"Invalid amount for {category}."
        cleaned[category] = amount

    if not cleaned:
        return False, "Provide at least one valid expense category."

    goal = clean_category(data.get("goal", "Emergency Fund"))
    if len(goal) > 100:
        return False, "Goal is too long."

    return True, {
        "name": name or "User",
        "income": income,
        "expenses": cleaned,
        "goal": goal or "Emergency Fund",
    }

def build_prompt(data):
    income = data["income"]
    expenses = data["expenses"]
    goal = data["goal"]

    tips = "\n".join(
        f"- {key}: {value}" for key, value in CATEGORY_TIPS.items()
    )
    goal_description = GOAL_DESCRIPTIONS.get(
        goal.lower(), "provide practical, non-speculative savings guidance"
    )
    expense_lines = "\n".join(
        f"- {category}: ₹{amount:.2f}" for category, amount in expenses.items()
    )

    return f"""
You are the Personal Finance Advisor Bot. Analyze the user's monthly finances.

User: {data['name']}
Monthly income: ₹{income:.2f}
Financial goal: {goal} ({goal_description})

Recorded expenses:
{expense_lines}

General category guidance:
{tips}

Return ONLY valid JSON. No markdown, no code fences, no extra text.
The JSON must contain exactly these top-level keys:
budget, analysis, suggestions, summary

budget must be an array of objects. Each object should contain:
category, recommended_amount, percentage, reason

analysis must be an array of objects. Each object should contain:
category, spent_amount, percentage_of_income, status, message

suggestions must be an array of 3 to 5 objects. Each object should contain:
title, amount, target, action

summary must be a short string.

Use Indian rupees. Do not invent expenses that were not provided.
For percentages, calculate from the provided income.
Keep advice practical and educational. Do not recommend specific financial products.
""".strip()

def extract_json(text):
    """Robustly parse direct JSON, fenced JSON, or a raw JSON object."""
    if not text:
        raise ValueError("Empty Gemini response.")

    text = text.strip()

    # 1. Direct JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Markdown code block
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except json.JSONDecodeError:
            pass

    # 3. Raw JSON object fallback
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    raise ValueError("Could not parse a valid JSON object from Gemini response.")

def local_demo_response(data):
    """Fallback so the capstone can be demonstrated without an API key."""
    income = data["income"]
    expenses = data["expenses"]
    total = sum(expenses.values())
    balance = income - total

    budget = []
    analysis = []
    for category, spent in expenses.items():
        pct = round((spent / income) * 100, 2)
        if category.lower() == "rent":
            limit = 30
        elif category.lower() in ("food", "dining"):
            limit = 5
        elif category.lower() == "transport":
            limit = 10
        elif category.lower() == "entertainment":
            limit = 8
        else:
            limit = 10
        status = "overspending" if pct > limit else "on track"
        analysis.append({
            "category": category,
            "spent_amount": round(spent, 2),
            "percentage_of_income": pct,
            "status": status,
            "message": f"{category} uses {pct}% of income; suggested guideline is around {limit}%."
        })
        budget.append({
            "category": category,
            "recommended_amount": round(income * min(limit, 20) / 100, 2),
            "percentage": min(limit, 20),
            "reason": "Set a clear category limit based on a general budgeting guideline."
        })

    biggest = max(expenses, key=expenses.get)
    biggest_pct = round(expenses[biggest] / income * 100, 2)
    suggestions = [
        {"title": "Review the largest expense", "amount": round(expenses[biggest] * 0.10, 2),
         "target": biggest, "action": f"Try reducing {biggest} gradually and redirect the difference to savings."},
        {"title": "Build an emergency fund", "amount": round(max(balance, 0) * 0.10, 2),
         "target": "Emergency Fund", "action": "Set aside a small fixed amount every month."},
        {"title": "Use a category limit", "amount": round(income * 0.05, 2),
         "target": "Discretionary spending", "action": "Set a weekly limit for non-essential purchases."}
    ]

    savings_rate = round((balance / income) * 100, 2)
    summary = (
        f"Income ₹{income:,.2f}, expenses ₹{total:,.2f}, and balance ₹{balance:,.2f}. "
        f"The largest recorded category is {biggest} at {biggest_pct}% of income."
    )
    return {"budget": budget, "analysis": analysis, "suggestions": suggestions, "summary": summary}

def call_gemini(data):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or genai is None:
        return local_demo_response(data), "demo-fallback"

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        generation_config={"temperature": 0.7, "max_output_tokens": 2048},
    )
    response = model.generate_content(build_prompt(data))
    parsed = extract_json(response.text)

    required = {"budget", "analysis", "suggestions", "summary"}
    if not required.issubset(parsed.keys()):
        raise ValueError("Gemini response is missing required keys.")

    if not isinstance(parsed["budget"], list) or not isinstance(parsed["analysis"], list):
        raise ValueError("Gemini returned an invalid structured response.")
    if not isinstance(parsed["suggestions"], list):
        raise ValueError("Gemini suggestions are not in list format.")

    return parsed, "gemini-2.0-flash"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyse", methods=["POST"])
def analyse():
    data = request.get_json(silent=True)
    valid, result = validate_input(data)
    if not valid:
        return jsonify({"success": False, "error": result}), 400

    try:
        result_data, source = call_gemini(result)

        total_expense = sum(result["expenses"].values())
        balance = result["income"] - total_expense
        rate = (balance / result["income"] * 100) if result["income"] else 0
        score = max(0, min(100, round(rate * 2, 2)))

        record = MonthlyRecord(
            person_name=result["name"],
            income=result["income"],
            total_expense=total_expense,
            balance=balance,
            score=score,
            rate=round(rate, 2),
            goal=result["goal"],
        )
        db.session.add(record)
        db.session.commit()

        return jsonify({
            "success": True,
            "budget": result_data["budget"],
            "analysis": result_data["analysis"],
            "suggestions": result_data["suggestions"],
            "summary": result_data["summary"],
            "source": source,
            "totals": {
                "income": round(result["income"], 2),
                "expense": round(total_expense, 2),
                "balance": round(balance, 2),
                "rate": round(rate, 2),
                "score": score,
            },
        })

    except Exception as exc:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": f"Financial analysis failed: {str(exc)}"
        }), 500

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=5090)
