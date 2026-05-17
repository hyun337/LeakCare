import os
from anthropic import Anthropic

CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")

def generate_removal_text(url: str, ai_results: list, evidence_info: dict) -> str:
    """
    Claude API를 단독 사용하여 가해 서버 위치 맞춤형 삭제 요청 메일 생성
    """
    if not CLAUDE_API_KEY:
        print("⚠️ CLAUDE_API_KEY 없음, 기본 템플릿 사용")
        return _default_template(url, evidence_info)

    try:
        # 클라이언트 초기화
        client = Anthropic(api_key=CLAUDE_API_KEY)

        detected_count = len(ai_results)
        top_score = ai_results[0]["score"] if ai_results else 0
        is_deepfake = any(r.get("is_deepfake") for r in ai_results)
        content_type = "딥페이크 합성물" if is_deepfake else "불법 촬영 유출물"

        # [영어 + IP 기반 현지 언어] 동적 타겟팅 프롬프트
        prompt = f"""
당신은 불법 촬영 유출물 및 딥페이크 피해자를 돕는 글로벌 법률 지원 전문가입니다.
아래 정보를 바탕으로 콘텐츠 삭제 요청 메일을 작성해주세요.

[탐지 정보]
- 게시 URL: {url}
- 서버 위치(국가): {evidence_info.get('country', 'Unknown')}
- 서버 위치(도시): {evidence_info.get('city', 'Unknown')}
- 서버 IP: {evidence_info.get('ip', 'Unknown')}
- 수집 일시: {evidence_info.get('timestamp', 'Unknown')}
- 탐지 건수: {detected_count}건
- 최고 유사도: {top_score:.2%}
- 콘텐츠 유형: {content_type}

[작성 조건 - 중요]
1. 메일은 총 두 가지 버전으로 작성해야 합니다:
   - 첫 번째 버전: 글로벌 표준인 [영어(English)]
   - 두 번째 버전: 탐지된 서버 위치 국가인 [{evidence_info.get('country', 'Unknown')}]의 공식 현지 언어
2. 만약 탐지된 국가가 미국(USA)이거나 Unknown일 경우, 두 번째 버전은 [한국어]로 대체하여 작성해 주세요.
3. 아래의 구분선 형식을 정확히 지켜주세요:
===영어===
(영어 메일 내용 - DMCA 가이드라인 포함)
===[{evidence_info.get('country', 'Unknown')}] 현지어===
(해당 국가 언어로 번역된 메일 내용 및 현지 법적 대응 경고 포함)

4. 24시간 내 삭제 요청 및 미이행 시 국제 사법당국 고발 등 법적 조치 경고를 강력한 어조로 포함해주세요.
5. 수신자란은 [Site Operator/Administrator], 발신자란은 [Victim]으로 표시해주세요.
"""

        # Claude 3.5 Sonnet 호출
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4000,
            temperature=0.2,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        result_text = response.content[0].text.strip()
        print("✅ Claude 단독 엔진 - 삭제 요청서 생성 완료")
        print(f"\n[출력 확인] 생성된 삭제 요청서:\n{result_text}\n")
        return result_text

    except Exception as e:
        print(f"⚠️ Claude API 호출 실패: {e}, 기본 템플릿 사용")
        return _default_template(url, evidence_info)


def _default_template(url: str, evidence_info: dict) -> str:
    """LLM 실패 시 기본 템플릿"""
    return f"""===영어===
To: Site Administrator/Manager

I am writing to request the immediate removal of illegal content posted on your platform.

[Content to be Removed]
- URL: {url}
- Server Location: {evidence_info.get('country', 'Unknown')}
- Collected At: {evidence_info.get('timestamp', 'Unknown')}

This content violates applicable laws including the Digital Millennium Copyright Act (DMCA) and constitutes non-consensual intimate imagery.

Please remove the content within 24 hours of receiving this notice.
Failure to comply will result in legal action.

From: Victim
"""
