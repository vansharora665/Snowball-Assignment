# Snowball-Assignment
# School Backend System

A simplified FastAPI backend for report generation, predictive analysis, and voice query interpretation using CSV-based data.

## Features

- JWT-based authentication
- Predict student dropout risk
- Forecast school revenue
- Generate student, teacher, payment reports
- Interpret voice commands using SpaCy
- Docker and docker-compose support

## Project Structure

```
backend_project/
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── data/
    ├── students.csv
    ├── teachers.csv
    └── payments.csv
```

## Setup

### Local Development

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn main:app --reload
```

Visit: `http://127.0.0.1:8000/docs`

### Authentication

Login with:
- **username:** admin
- **password:** admin123

Use the `/token` endpoint to get a JWT.

### Docker Setup

```bash
docker-compose up --build
```

## Endpoints

- `POST /token` - Get JWT token
- `GET /report/students` - Student report
- `GET /report/teachers` - Teacher report
- `GET /report/payments` - Payment report
- `POST /predict/student` - Dropout prediction
- `GET /predict/revenue?next_month=6` - Revenue forecast
- `POST /voice/interpret` - Interpret voice query

## Example Voice Queries

- “Show student performance”
- “Give me the teacher report”
- “What’s the revenue forecast?”

---

Built for academic demonstration purposes. Easy to extend and deploy.
