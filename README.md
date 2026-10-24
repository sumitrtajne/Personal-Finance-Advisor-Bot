# Finova — Personal Finance Advisor

A Flask-based web application for reviewing monthly income and expenses, analysing spending, viewing suggested category budgets, and receiving practical saving suggestions.

## Live Demo
https://personal-finance-advisor-bot-9phg.onrender.com

Please open and test the live link before evaluation. The link alone does not guarantee that the service is currently available.

## Features
- Enter monthly income, expense categories, and a financial goal.
- View total expenses, remaining balance, and saving rate.
- Review category-wise spending analysis and recommended budgets.
- Get practical saving suggestions.
- Use Gemini AI when `GEMINI_API_KEY` is configured.
- Use a demo fallback when Gemini is not configured.
- Save analysis records using SQLite.
- Responsive dark interface with blank inputs on page load and a Reset Form action.

## Technology Stack
Python, Flask, Flask-SQLAlchemy, SQLite, Google Gemini API (`google-generativeai`), HTML, CSS, JavaScript, Gunicorn, and Render.

## Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/sumittajne/Personal-Finance-Advisor-Bot.git
cd Personal-Finance-Advisor-Bot
```

### 2. Create a virtual environment
Windows PowerShell:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If activation is blocked, use Command Prompt:
```bat
.venv\Scripts\activate.bat
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```
Ensure `gunicorn` is in `requirements.txt` for Render.

### 4. Configure Gemini (optional)
Create a local `.env` file:
```text
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=replace_with_a_random_secret
```
Never commit `.env` or publish your API key. Without a Gemini key, the app can use its demo fallback.

### 5. Start the app
```bash
python app.py
```
Open http://127.0.0.1:5090

## How to Use
1. Open the application.
2. Enter a positive monthly income and, optionally, your name.
3. Add expense categories and amounts.
4. Choose a financial goal.
5. Click **Analyse My Finances**.
6. Review the overview, spending analysis, recommended budget, and saving suggestions.
7. Click **Reset Form** to clear inputs and results.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Displays the web application |
| POST | `/analyse` | Validates inputs and returns the financial analysis |
| GET | `/health` | Returns a simple health status |

Example request to `/analyse`:
```json
{
  "name": "Alex",
  "income": 30000,
  "expenses": {"Rent": 8000, "Food": 2500, "Transport": 1500},
  "goal": "Emergency Fund"
}
```

A successful response includes `success`, `totals`, `analysis`, `budget`, `suggestions`, `summary`, and `source`.

## Render Deployment
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Add `GEMINI_API_KEY` under Render Environment settings if Gemini analysis is needed.
- After deployment, test the homepage, `/health`, form submission, analysis results, and reset button.

## Important Notes
- Suggestions are general educational guidance, not professional financial, tax, or investment advice.
- The app uses SQLite. Data on a hosting provider's local filesystem may not persist across redeploys or instance replacement unless persistent storage is configured.
- Do not enter sensitive real financial information into a demo deployment.
- A successful deployment does not prove every feature works; test the live demo before evaluation.

## Project Structure
```text
Personal-Finance-Advisor-Bot/
├── app.py
├── requirements.txt
├── run_public.py
├── templates/
│   └── index.html
├── .env.example
├── .gitignore
├── package.json
└── README.md
```

## Author
**Sumit Tajne**

Personal Finance Advisor Bot — project submission documentation.
