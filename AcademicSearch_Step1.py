import google.generativeai as genai
from app.configs.gemini_config import client_config
import json
import asyncio
import os

client = client_config

ANALYZE_GEMINI_PROMPT= """
# [Instruction]
지정한 형식의 JSON 객체를 추출하라, 입력된 'user_input'을 분석하여

## [Information]
user_input = {user_input}

### [Output Format]
반드시 다음에 제시된 키 순서와 형태로만 이루어진 JSON 객체를 출력해야 합니다.
• concept_tags: 질문에서 파악할 주제·관심사·키워드 배열 (단, 책, 도서와 같은 키워드 제외)  
• user_intents: 다음의 2가지가 반영된 배열 (5개 이내) 
1. 'user_input'의 핵심 의도 
2. 사용자 후속 질의로 확장될 가능성이 높은 개념

#### [Strong Rules]
1. 출력은 오직 JSON 문법에 맞는 객체 하나만 있어야 하며, 어떠한 추가 설명, 주석, 마크다운도 포함하지 마세요.
2. 키 순서는 위 목록과 동일해야 합니다.
3. JSON에 대한 value 값은 '한국어'로 출력되어야 합니다.
"""

async def analyze_gemini(user_prompt):
    import logging
    
    prompt = ANALYZE_GEMINI_PROMPT.format(user_input=user_prompt)
    
    if client is None:
        logging.error("❌ Gemini 클라이언트가 초기화되지 않았습니다.")
        return "llm error"
    
    try:
        # Gemini 모델 인스턴스 생성
        model = client.GenerativeModel('gemini-2.5-flash-lite-preview-06-17')
        
        # 컨텐츠 생성
        response = model.generate_content(prompt)
        
        # 실제 응답 로깅 (디버깅용)
        logging.info(f"🔍 Gemini 원본 응답: {response.text}")
        
        return response.text
    except Exception as e:
        logging.error(f"❌ Gemini API 오류: {e}")
        return "llm error"
    
# --- 3. 실제 API를 호출하는 비동기 함수 ---
async def analyze_gemini_real(user_prompt: str) -> str | None:
    """실제 Gemini API를 호출하여 결과를 반환하는 비동기 함수"""
    print(f"\n[INFO] Gemini API에 실제 요청을 보냅니다...")
    print(f"ㄴ 입력된 질문: '{user_prompt}'")
    
    try:
        # 사용할 모델 인스턴스 생성
        model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-06-17')
        
        # 프롬프트 포맷에 사용자 질문 삽입
        prompt = ANALYZE_GEMINI_PROMPT.format(user_input=user_prompt)
        
        # API를 통해 콘텐츠 생성 요청 (비동기 호출)
        response = await model.generate_content_async(prompt)
        
        return response.text
        
    except Exception as e:
        print(f"\n[ERROR] API 호출 중 오류가 발생했습니다: {e}")
        return None

# --- 4. 테스트 실행을 위한 메인 비동기 함수 ---
async def main():
    # 테스트하고 싶은 질문을 여기에 입력합니다.
    sample_question = "한강의 소설 작품을 찾아보고 싶어"
    
    # 실제 API 호출 함수를 실행합니다.
    result_str = await analyze_gemini_real(sample_question)
    
    print("\n-----------[ 실제 API 결과 ]-----------")
    if result_str:
        print(f"결과 (Raw String):\n{result_str}")
    else:
        print("API로부터 결과를 받아오지 못했습니다.")
        
    print("----------------------------------------")

# --- 5. 프로그램 실행 ---
if __name__ == "__main__":
    asyncio.run(main())
