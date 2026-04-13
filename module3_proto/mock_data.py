from .schemas import VisionResult, AudioResult

# 모듈1·2가 완성되기 전까지 테스트용 가짜 데이터
# 실제 연동 후 삭제 예정

MOCK_VISION_RESULT = VisionResult(
    is_deepfake=True,
    confidence=0.91,
    media_type="video",
    artifacts_detected=["face_warp", "GAN"]
)

MOCK_AUDIO_RESULT = AudioResult(
    is_synthetic_voice=True,
    confidence=0.87,
    #transcribed_text="안녕하세요, 금융감독원입니다. 고객님 계좌에서 불법 거래가 감지되어 긴급히 계좌이체가 필요합니다.",
    transcribed_text="단독 천 원으로 미국 주식사기. 딱 10만원으로 연습하세요. 3일 뒤 100만원 됩니다.",
    phishing_keywords=["금융감독원", "계좌이체", "긴급", "불법 거래"],
)
