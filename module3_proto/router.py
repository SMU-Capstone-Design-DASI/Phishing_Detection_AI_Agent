from fastapi import APIRouter
from .schemas import AgentRequest, AgentResponse
from .service import AgentService

router = APIRouter(prefix="/agent", tags=["agent"])
service = AgentService()


@router.post("/analyze", response_model=AgentResponse)
async def analyze(request: AgentRequest):
    """
    피싱 분석 요청

    - vision_result + audio_result → 영상 + 음성 종합 분석
    - vision_result만              → 딥페이크 영상 단독 분석
    - audio_result만               → 합성 음성 + 텍스트 분석
    - text_input만                 → 텍스트(채팅·문자) 단독 분석
    
    - mock_mode: true → 모듈1·2 없이 가짜 데이터로 테스트
    - mock_mode: false → vision_result, audio_result 직접 입력
    """
    return service.analyze(request)
