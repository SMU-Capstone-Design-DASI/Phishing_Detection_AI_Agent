import os
import json
from groq import Groq
# from anthropic import Anthropic

from .schemas import AgentRequest, AgentResponse
from .rag import RAGService
from .report import build_report
from .mock_data import MOCK_VISION_RESULT, MOCK_AUDIO_RESULT

client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
# client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

rag_service = RAGService()

# ────────────────────────────────────────────────────────────
# 시스템 프롬프트 — 케이스별로 분리
# 공통 규칙: JSON만 응답, 한국어만 사용
# 없는 모달리티의 score는 반드시 null로 반환
# ────────────────────────────────────────────────────────────

# 케이스1: 영상 + 음성 둘 다 있음
SYSTEM_PROMPT_FULL = """
당신은 온라인 금융사기(피싱) 탐지 전문 AI입니다.
이미지/영상 딥페이크 분석 결과와 음성 합성 분석 결과를 종합해 피싱 여부를 판단합니다.

반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트는 절대 포함하지 마세요.
모든 텍스트는 반드시 한국어로만 작성하세요.

{
  "risk_score": 세 항목을 종합한 최종 위험도 (0~100 정수),
  "text_score": 변환된 텍스트 내용만의 피싱 위험도 (0~100 정수),
  "attack_type": "공격 유형 (예: 투자 리딩방 사칭, 정부기관 사칭 등)",
  "suspicious_keywords": ["의심 단어1", "의심 단어2"],
  "reason": "종합 판단 근거 (한국어만)",
  "countermeasure": "일반 대응 방안 (한국어만)"
}
"""

# 케이스2: 영상만 있음 (음성 없음)
SYSTEM_PROMPT_VISION_ONLY = """
당신은 온라인 금융사기(피싱) 탐지 전문 AI입니다.
음성 분석 결과는 제공되지 않았습니다. 이미지/영상 딥페이크 분석 결과만으로 피싱 여부를 판단합니다.

반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트는 절대 포함하지 마세요.
모든 텍스트는 반드시 한국어로만 작성하세요.

{
  "risk_score": 딥페이크 분석 기반 최종 위험도 (0~100 정수),
  "text_score": null,
  "attack_type": "공격 유형 (예: 딥페이크 사칭 영상 등)",
  "suspicious_keywords": ["의심 단어1", "의심 단어2"],
  "reason": "판단 근거 (한국어만)",
  "countermeasure": "일반 대응 방안 (한국어만)"
}
"""

# 케이스3: 음성만 있음 (영상 없음) — 음성에서 텍스트도 함께 분석
SYSTEM_PROMPT_AUDIO_ONLY = """
당신은 온라인 금융사기(피싱) 탐지 전문 AI입니다.
영상 분석 결과는 제공되지 않았습니다. 음성 합성 여부와 변환된 텍스트 내용만으로 피싱 여부를 판단합니다.

반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트는 절대 포함하지 마세요.
모든 텍스트는 반드시 한국어로만 작성하세요.

{
  "risk_score": 음성+텍스트를 종합한 최종 위험도 (0~100 정수),
  "text_score": 변환된 텍스트 내용만의 피싱 위험도 (0~100 정수),
  "attack_type": "공격 유형 (예: 보이스피싱, 투자 유도 전화 등)",
  "suspicious_keywords": ["의심 단어1", "의심 단어2"],
  "reason": "판단 근거 (한국어만)",
  "countermeasure": "일반 대응 방안 (한국어만)"
}
"""

# 케이스4: 텍스트만 있음 (영상·음성 없음)
SYSTEM_PROMPT_TEXT_ONLY = """
당신은 온라인 금융사기(피싱) 탐지 전문 AI입니다.
영상·음성 분석 결과는 제공되지 않았습니다. 입력된 텍스트 내용만으로 피싱 여부를 판단합니다.

반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트는 절대 포함하지 마세요.
모든 텍스트는 반드시 한국어로만 작성하세요.

{
  "risk_score": 텍스트 분석 기반 최종 위험도 (0~100 정수),
  "text_score": 텍스트 내용만의 피싱 위험도 (0~100 정수),
  "attack_type": "공격 유형 (예: 스미싱, 피싱 문자, 채팅 사기 등)",
  "suspicious_keywords": ["의심 단어1", "의심 단어2"],
  "reason": "판단 근거 (한국어만)",
  "countermeasure": "일반 대응 방안 (한국어만)"
}
"""

# 케이스 → 시스템 프롬프트 매핑
PROMPT_MAP = {
    (True,  True ):  SYSTEM_PROMPT_FULL,         # 영상 + 음성
    (True,  False):  SYSTEM_PROMPT_VISION_ONLY,  # 영상만
    (False, True ):  SYSTEM_PROMPT_AUDIO_ONLY,   # 음성만
    (False, False):  SYSTEM_PROMPT_TEXT_ONLY,    # 텍스트만
}


class AgentService:

    def analyze(self, request: AgentRequest) -> AgentResponse:
        # mock_mode면 가짜 데이터로 모듈1·2 결과 대체
        if request.mock_mode:
            request.vision_result = MOCK_VISION_RESULT
            request.audio_result  = MOCK_AUDIO_RESULT

        has_vision = request.vision_result is not None
        has_audio  = request.audio_result is not None
        has_text   = bool(request.text_input)

        # 영상도 음성도 텍스트도 없으면 에러
        if not has_vision and not has_audio and not has_text:
            raise ValueError("vision_result, audio_result, text_input 중 하나 이상 필요합니다.")

        # 1. 키워드 수집 — 음성의 phishing_keywords 우선, 없으면 빈 리스트
        keywords = request.audio_result.phishing_keywords if has_audio else []

        # 2. RAG - 유사 피싱 사례 검색
        similar_cases = rag_service.search_similar_cases(keywords)
        rag_context = rag_service.format_cases_for_prompt(similar_cases)

        # 3. 케이스에 맞는 시스템 프롬프트 선택
        system_prompt = PROMPT_MAP[(has_vision, has_audio)]
        user_message = self._build_prompt(request, rag_context, has_vision, has_audio, has_text)

        # 4. LLM 호출 (Groq)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
            max_tokens=1000,
        )
        llm_output = json.loads(response.choices[0].message.content)

        # Claude API로 교체 시 아래 주석 해제, 위 Groq 블록 주석 처리
        # response = client.messages.create(
        #     model="claude-sonnet-4-20250514",
        #     max_tokens=1000,
        #     system=system_prompt,
        #     messages=[{"role": "user", "content": user_message}],
        # )
        # llm_output = json.loads(response.content[0].text)

        # 5. 리포트 생성 및 반환
        # deepfake_score, synthetic_voice_score는 모듈1·2의 confidence를 직접 사용
        deepfake_score = round(request.vision_result.confidence * 100) if has_vision else None
        synthetic_voice_score = round(request.audio_result.confidence * 100) if has_audio else None

        return build_report(llm_output, deepfake_score, synthetic_voice_score)

    def _build_prompt(
        self,
        request: AgentRequest,
        rag_context: str,
        has_vision: bool,
        has_audio: bool,
        has_text: bool,
    ) -> str:
        parts = []

        # 영상 분석 결과
        if has_vision:
            v = request.vision_result
            parts.append(
                f"[이미지/영상 분석 결과]\n"
                f"딥페이크 여부: {v.is_deepfake} (신뢰도: {v.confidence:.0%})\n"
                f"미디어 유형: {v.media_type}\n"
                f"탐지된 아티팩트: {', '.join(v.artifacts_detected)}"
            )
        else:
            parts.append("[이미지/영상 분석 결과]\n입력 없음 — deepfake_score는 null로 반환하세요.")

        # 음성 분석 결과
        if has_audio:
            a = request.audio_result
            parts.append(
                f"[음성 분석 결과]\n"
                f"합성 음성 여부: {a.is_synthetic_voice} (신뢰도: {a.confidence:.0%})\n"
                f"변환된 텍스트: {a.transcribed_text}\n"
                f"탐지된 키워드: {', '.join(a.phishing_keywords)}"
            )
        else:
            parts.append("[음성 분석 결과]\n입력 없음 — synthetic_voice_score는 null로 반환하세요.")

        # 텍스트 단독 입력 (채팅·문자 등)
        if has_text:
            parts.append(
                f"[텍스트 입력 (채팅·문자 등)]\n"
                f"{request.text_input}"
            )

        parts.append(f"[유사 피싱 사례 DB]\n{rag_context}")
        parts.append("위 정보를 종합해 피싱 여부를 판단하고 JSON으로만 응답하세요.")

        return "\n\n".join(parts)