from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from module3_proto.router import router as agent_router

app = FastAPI(title="피싱 검출 AI Agent")
app.include_router(agent_router)


@app.get("/")
def root():
    return {"message": "피싱 검출 AI Agent 프로토타입 실행 중"}


"""
.\venv\Scripts\activate 입력!
pip install fastapi uvicorn groq
여기서부터
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
http://localhost:8000/docs
uvicorn main:app --reload
http://127.0.0.1:8000/docs 주소 입력
POST /agent/analyze
Try it out
"mock_mode": true로 바꾸기
Execute 클릭
종료하고 싶으면 ctrl+C
"""