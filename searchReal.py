import google.generativeai as genai
import json
import asyncio
import os
import re

# --- API 키 설정 ---
# 사용자의 환경에 맞게 app.configs.gemini_config.py 파일에 client가 설정되어 있다고 가정합니다.
# --- API 키 설정 ---
# 1. client_config를 직접 임포트하여 API 키 설정을 위임합니다.
from app.configs.gemini_config import client_config

# 2. 코드 1과 동일하게 client 변수를 선언합니다.
client = client_config

# --- 프롬프트 정의 ---
# ⭐️ 1단계 프롬프트는 사용하지 않으므로 삭제되었습니다.

# 2단계: 최종 검색 JSON을 추출하기 위한 메인 프롬프트
EXTRACT_PARAMS_PROMPT = """
# [Instruction]
You are an expert AI that analyzes a user's book search query and generates a structured JSON object for optimal database search. Follow the steps below precisely.

# [Input Data]
- user_prompt: {user_prompt}
- user_intent: {user_intent}

---
# [Step 1: Classify Search Type]
First, classify the `user_prompt` into one of the 7 types defined below and find its corresponding number ID.

1.  **Title**: The user is looking for a specific book title. (e.g., "데미안 찾아줘")
2.  **Title + Author**: The user specifies both title and author. (e.g., "헤르만 헤세의 데미안 있어?")
3.  **Author**: The user is looking for works by a specific author. (e.g., "헤르만 헤세 작품 목록 보여줘")
4.  **Author + Genre**: The user specifies an author and a genre. (e.g., "한강 작가의 소설 작품을 찾아보고 싶어")
5.  **Concept + Target Audience**: The user is looking for books for a specific audience. (e.g., "초등학생이 읽을 만한 우주 관련 책")
6.  **Concept + Genre**: The user combines a concept with a genre. (e.g., "인공지능을 다루는 SF 소설 추천해줘")
7.  **Concept + Synopsis**: The user describes the plot or concept of a book. (e.g., "주인공이 갑자기 고양이로 변하는 소설 알아?")

---
# [Step 2: Generate JSON Output]
Based on the classification from Step 1, fill out the following JSON object.
- **Keys MUST be in English** as specified in the format below.
- **If the type ID is 1-4 (Simple Search)**: EXTRACT entities directly from the `user_prompt`.
- **If the type ID is 5-7 (In-depth Search)**: INFER and SUGGEST entities based on the `user_intent`. If the `user_intent` strongly suggests a famous book (e.g., "안네의 일기"), you MUST fill in the `title` and `author` fields.
- If a value cannot be found, leave it as an empty string "".

# [Unified Output JSON Format]
Respond with ONLY the following JSON object. Do not include any other text or explanations.
{{
  "searchType": "",         // String: "Simple Search" (for types 1-4) or "In-depth Search" (for types 5-7).
  "queryType": 0,           // Integer: The number ID from 1 to 7 determined in Step 1.
  "title": "",              // Inferred or extracted title of the book.
  "author": "",             // Inferred or extracted author of the book.
  "genre": "",              // Inferred or extracted genre.
  "concept": "",            // Core concept keywords from the user's query.
  "optimizedQuery": ""      // A 3-4 word keyword query for database search.
}}

# [Example for In-depth Search (Type 7)]
- user_prompt: "세계 2차대전에 쓰인 소녀의 일기에관한 책이 뭐지?"
- user_intent: "세계 2차 대전을 배경으로 한 소녀의 일기 관련 책 정보 탐색. ‘안네의 일기’일 가능성이 높음."
- Expected Output:
{{
  "searchType": "In-depth Search",
  "queryType": 7,
  "title": "안네의 일기",
  "author": "안네 프랑크",
  "genre": "에세이",
  "concept": "세계 2차대전, 소녀, 일기",
  "optimizedQuery": "세계 2차대전 소녀 일기"
}}

# [Example for Simple Search (Type 4)]
- user_prompt: "한강 작가의 소설 작품을 찾아보고 싶어"
- user_intent: "한강 작가의 소설 장르 도서 목록 검색"
- Expected Output:
{{
    "searchType": "Simple Search",
    "queryType": 4,
    "title": "",
    "author": "한강",
    "genre": "소설",
    "concept": "한강, 소설",
    "optimizedQuery": "한강 소설"
}}
"""

# --- 유틸리티 함수 ---
def clean_json_string(raw_str: str) -> str:
    """LLM 응답에서 JSON 마크다운 코드를 제거합니다."""
    match = re.search(r'```json\s*(\{.*?\})\s*```', raw_str, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw_str.strip()

# --- API 호출 함수 ---
async def call_gemini_api(prompt: str, model_name: str = 'gemini-1.5-flash-latest') -> str | None:
    """Gemini API를 호출하고 결과를 Raw String으로 반환하는 함수"""
    try:
        model = client.GenerativeModel(model_name)
        response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text
    except Exception as e:
        print(f"\n[오류] API 호출 중 문제가 발생했습니다: {e}")
        return None

# --- 메인 파이프라인 함수 ---
async def extract_search_params(user_prompt: str, user_intent: str):
    """지정된 user_intent를 사용하여 검색 파라미터를 추출합니다."""
    
    print(f"\n[INFO] 지정된 의도(user_intent)로 파라미터 추출 요청...")
    print(f"  - 원본 질문: {user_prompt}")
    print(f"  - 하드코딩된 의도: {user_intent}")
    
    prompt = EXTRACT_PARAMS_PROMPT.format(
        user_prompt=json.dumps(user_prompt, ensure_ascii=False),
        user_intent=json.dumps(user_intent, ensure_ascii=False)
    )
    
    result_str = await call_gemini_api(prompt)

    if not result_str:
        print("API 호출에 실패했습니다.")
        return
        
    try:
        cleaned_str = clean_json_string(result_str)
        search_params = json.loads(cleaned_str)
    except json.JSONDecodeError as e:
        print(f"\n[오류] JSON 파싱 중 오류가 발생했습니다: {e}")
        print(f"ㄴ Gemini 원본 응답:\n---\n{result_str}\n---")
        return

    print("\n--- [ 최종 추출된 검색 파라미터 ] ---")
    print(json.dumps(search_params, indent=2, ensure_ascii=False))
    print("------------------------------------")


# --- 메인 실행 ---
async def main():
    # ⭐️ 여기에 테스트 케이스를 직접 정의합니다.
    test_cases = [
        {
            "prompt": "주인공이 혼자 화성에 남겨져서 감자 키우고 살아남는 내용의 책 제목이 뭐야?",
            "intent": "화성에서 조난된 주인공이 생존하는 줄거리의 과학 소설 탐색. 앤디 위어의 '마션'일 가능성이 높음."
        }
    ]
    
    for case in test_cases:
        user_prompt = case["prompt"]
        hardcoded_intent = case["intent"]
        
        print(f"❓ 사용자 질문: \"{user_prompt}\"")
        await extract_search_params(user_prompt, hardcoded_intent)
        print("\n================================================\n")

if __name__ == "__main__":
    asyncio.run(main())