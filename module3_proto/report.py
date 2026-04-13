from .schemas import AgentResponse
from typing import Optional

REPORT_AGENCIES = ["금융감독원 (1332)", "경찰청 사이버수사대 (182)"]


def build_report(
        llm_output: dict,
        deepfake_score: Optional[int],
        synthetic_voice_score: Optional[int],
) -> AgentResponse:
    """
    LLM 판단 결과를 AgentResponse로 변환
    """
    risk_score = llm_output.get("risk_score", 0)

    return AgentResponse(
        risk_score=risk_score,    # 위험도 점수
        is_phishing=risk_score >= 50,    # 피싱 여부
        deepfake_score=deepfake_score,    # 항목별 위험도 (없는 모달리티는 None)
        synthetic_voice_score=synthetic_voice_score,
        text_score=llm_output.get("text_score"),
        attack_type=llm_output.get("attack_type", "알 수 없음"),    # 공격 유형
        suspicious_keywords=llm_output.get("suspicious_keywords", []),    # 의심 단어
        reason=llm_output.get("reason", ""),    # 판단 근거
        countermeasure=llm_output.get("countermeasure", "주의가 필요합니다."),    # 일반 대응 방안
        emergency_guide=_build_emergency_guide(risk_score),    # 점수 80 이상일 경우 긴급 대처법
        report_agencies=REPORT_AGENCIES if risk_score >= 50 else [],    # 신고 기관
    )


def _build_warning_report(llm_output: dict) -> str:
    risk_score = llm_output.get("risk_score", 0)
    attack_type = llm_output.get("attack_type", "알 수 없음")
    reason = llm_output.get("reason", "")

    if risk_score >= 80:
        level = "🔴 매우 위험"
    elif risk_score >= 50:
        level = "🟠 위험"
    elif risk_score >= 30:
        level = "🟡 주의"
    else:
        level = "🟢 안전"

    return (
        f"판단 근거: {reason}"
    )


def _build_emergency_guide(risk_score: int) -> str | None:
    if risk_score < 80:
        return None

    return (
        "즉시 금전 이체를 중단하세요.\n"
        "개인정보(계좌번호, 비밀번호)를 절대 제공하지 마세요.\n"
        "금융감독원(1332) 또는 경찰청(182)에 신고하세요."
    )
