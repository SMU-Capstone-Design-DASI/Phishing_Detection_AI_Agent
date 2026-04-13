from pydantic import BaseModel
from typing import Optional


# ── 모듈1에서 받는 데이터 ──────────────────────────────
class VisionResult(BaseModel):
    is_deepfake: bool
    confidence: float
    media_type: str                          # "image" / "video"
    artifacts_detected: list[str]


# ── 모듈2에서 받는 데이터 ──────────────────────────────
class AudioResult(BaseModel):
    is_synthetic_voice: bool
    confidence: float
    transcribed_text: str
    phishing_keywords: list[str]


# ── Agent 분석 요청 ────────────────────────────────────
# 모듈1·2가 없을 땐 mock_mode=True로 보내면 가짜 데이터로 대체
class AgentRequest(BaseModel):
    vision_result: Optional[VisionResult] = None
    audio_result: Optional[AudioResult] = None
    text_input: Optional[str] = None
    mock_mode: bool = True                 # True면 가짜 데이터로 테스트


# ── Agent 분석 응답 ────────────────────────────────────
class AgentResponse(BaseModel):
    risk_score: int
    is_phishing: bool
    deepfake_score: Optional[int] = None         # 딥페이크 위험도 0~100
    synthetic_voice_score: Optional[int] = None  # 합성 음성 위험도 0~100
    text_score: Optional[int] = None             # 텍스트 내용 위험도 0~100
    attack_type: str
    suspicious_keywords: list[str]               # 의심 주요 단어
    reason: str                                  # 판단 근거
    countermeasure: str                          # 일반 대응 방안
    emergency_guide: Optional[str] = None        # 긴급 대처법 (위험도 80+ 시만)
    report_agencies: list[str]
