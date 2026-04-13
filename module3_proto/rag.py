# DB 연동 전 프로토타입용
# 실제 MySQL 대신 메모리에 올린 가짜 피싱 사례 데이터를 사용

MOCK_PHISHING_CASES = [
    {
        "id": 1,
        "keyword": "금융감독원",
        "attack_type": "정부기관 사칭",
        "description": "금융감독원 직원을 사칭해 계좌 동결 위협 후 송금 유도"
    },
    {
        "id": 2,
        "keyword": "계좌이체",
        "attack_type": "긴급 송금 유도",
        "description": "긴급 상황을 만들어 즉각적인 계좌이체를 요구하는 수법"
    },
    {
        "id": 3,
        "keyword": "긴급",
        "attack_type": "공포 조장",
        "description": "긴급하다는 심리적 압박으로 피해자가 생각할 시간을 빼앗는 수법"
    },
    {
        "id": 4,
        "keyword": "불법 거래",
        "attack_type": "계좌 동결 협박",
        "description": "불법 거래 연루 협박으로 피해자를 패닉 상태로 만든 뒤 송금 유도"
    },
    {
        "id": 5,
        "keyword": "투자",
        "attack_type": "투자 리딩방 사칭",
        "description": "주식·코인 고수를 사칭해 투자금 편취"
    },
]


class RAGService:

    def search_similar_cases(self, keywords: list[str], limit: int = 5) -> list[dict]:
        """
        키워드와 일치하는 피싱 사례를 메모리에서 검색 (DB 없이)
        """
        if not keywords:
            return []

        results = []
        seen_ids = set()

        for keyword in keywords:
            for case in MOCK_PHISHING_CASES:
                if keyword in case["keyword"] and case["id"] not in seen_ids:
                    results.append(case)
                    seen_ids.add(case["id"])
                if len(results) >= limit:
                    break

        return results

    def format_cases_for_prompt(self, cases: list[dict]) -> str:
        """
        검색된 피싱 사례를 LLM 프롬프트용 텍스트로 변환
        """
        if not cases:
            return "관련 피싱 사례 없음"

        lines = []
        for i, case in enumerate(cases, 1):
            lines.append(
                f"{i}. [{case['attack_type']}] 키워드: {case['keyword']} - {case['description']}"
            )
        return "\n".join(lines)
