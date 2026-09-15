# Personal Finance Advisor Bot — SkillWallet AI Specialist Capstone

This implementation follows the supplied SkillWallet project workflow:
- Gemini API key configuration
- Gemini `gemini-2.0-flash` model
- Flask backend
- `/analyse` POST endpoint using JSON/AJAX
- `build_prompt()` prompt-engineering helper
- `CATEGORY_TIPS` and `GOAL_DESCRIPTIONS`
- `extract_json()` robust response parser
- Single-page HTML/CSS/JavaScript interface
- Dynamic budget, analysis and saving-suggestion rendering
- Local deployment on port 5090
- Public deployment with Ngrok using `run_public.py`

## Features

1. Personalized monthly budget
2. Spending analysis by category
3. 3–5 saving suggestions
4. Financial goal selection
5. Monthly income and expense input
6. Balance and saving-rate calculation
7. SQLite/SQLAlchemy record storage
8. Responsive frontend
9. Gemini AI integration
10. Demo fallback when no Gemini API key is configured

## Folder structure

```text
Personal_Finance_Advisor_Bot_SkillWallet/
├── app.py
├── run_public.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## 1. Create environment

Windows Command Prompt:

```bat
python -m venv myenv
myenv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configure Gemini

Copy `.env.example` to `.env` and put your Gemini API key in:

```text
GEMINI_API_KEY=your_gemini_api_key_here
```

Never commit `.env` to GitHub.

## 3. Run locally

```bat
python app.py
```

Open:

```text
http://127.0.0.1:5090
```

## 4. Test

Example:

```text
Name: Sumit
Income: 30000

Rent: 8000
Food: 2500
Transport: 2000
Dining: 1500
Entertainment: 2500
Utilities: 2000
Shopping: 1000

Goal: Emergency Fund
```

Click **Analyse My Finances**.

The frontend sends a JSON POST request to `/analyse`. Flask validates the data, constructs the financial prompt, calls Gemini, parses the JSON response and returns structured results.

## 5. Public deployment with Ngrok

Add your token to `.env`:

```text
NGROK_AUTHTOKEN=your_ngrok_authtoken_here
```

Then run:

```bat
python run_public.py
```

The terminal prints a public `ngrok-free.app` URL. Keep the terminal running while demonstrating the project.

## Important

The project has a transparent local fallback. If `GEMINI_API_KEY` is missing, the application still demonstrates the complete UI and budgeting workflow using deterministic analysis. When a valid key is supplied, the response source badge changes to `Gemini AI`.

This is an educational budgeting assistant, not professional financial or investment advice.
