from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import uvicorn
import jwt
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import spacy
import json

SECRET_KEY = "your_secret_key"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()
nlp = spacy.load("en_core_web_sm")

students_df = pd.read_csv("data/students.csv")
teachers_df = pd.read_csv("data/teachers.csv")
payments_df = pd.read_csv("data/payments.csv")

users = {"admin": {"password": "admin123", "role": "admin"}}

class Token(BaseModel):
    access_token: str
    token_type: str

def create_token(username: str):
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user = payload.get("sub")
        if user not in users:
            raise HTTPException(status_code=403)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(form_data.username)
    return {"access_token": token, "token_type": "bearer"}

class StudentPerformance(BaseModel):
    student_id: int
    score: float
    attendance: float
    behavior: int

class RevenuePrediction(BaseModel):
    month: str
    revenue: float

student_model = RandomForestClassifier()
X = students_df[["score", "attendance", "behavior"]]
y = students_df["dropout"]
student_model.fit(X, y)

time_series = payments_df.groupby("month")["amount"].sum().reset_index()
time_series["month_num"] = range(len(time_series))
revenue_model = LinearRegression()
revenue_model.fit(time_series[["month_num"]], time_series["amount"])

@app.get("/report/students", dependencies=[Depends(get_current_user)])
def student_report():
    return students_df.to_dict(orient="records")

@app.get("/report/teachers", dependencies=[Depends(get_current_user)])
def teacher_report():
    return teachers_df.to_dict(orient="records")

@app.get("/report/payments", dependencies=[Depends(get_current_user)])
def payment_report():
    return payments_df.to_dict(orient="records")

@app.post("/predict/student", dependencies=[Depends(get_current_user)])
def predict_dropout(perf: StudentPerformance):
    input_data = [[perf.score, perf.attendance, perf.behavior]]
    pred = student_model.predict(input_data)[0]
    return {"dropout_risk": int(pred)}

@app.get("/predict/revenue", dependencies=[Depends(get_current_user)])
def predict_revenue(next_month: int):
    pred = revenue_model.predict([[next_month]])[0]
    return {"predicted_revenue": round(pred, 2)}

@app.post("/voice/interpret", dependencies=[Depends(get_current_user)])
def interpret_voice(request: Request):
    body = json.loads(request.body().decode())
    text = body.get("text", "")
    doc = nlp(text.lower())
    if "student" in text and "performance" in text:
        return {"intent": "student_report"}
    elif "teacher" in text:
        return {"intent": "teacher_report"}
    elif "revenue" in text or "payment" in text:
        return {"intent": "payment_report"}
    else:
        return {"intent": "unknown"}

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
