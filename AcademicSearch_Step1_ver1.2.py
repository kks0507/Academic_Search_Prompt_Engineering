ANALYZE_INTENT_PROMPT= """
# [Instruction]
지정한 형식의 JSON 객체를 추출하라, 입력된 'user_input'을 분석하여

## [Information]
user_input = {user_input}

### [Output Format]
반드시 다음에 제시된 키 순서와 형태로만 이루어진 JSON 객체를 출력해야 합니다.
• concept_tags: 질문에서 파악할 주제·관심사·키워드 배열 (단, 책, 도서와 같은 키워드 제외)  
• user_intents: 다음의 3가지 키를 가진 JSON 객체
  1. summary: 'user_input'의 핵심 의도 (3개 이내)
  2. recommendations: 'user_input'을 기반으로 유추해볼 수 있는 대표 도서와 작가 등을 담은 배열 (4개 이내)
  3. related_concepts: 사용자 후속 질의로 확장될 가능성이 높은 개념 배열 (3개 이내)

#### [Strong Rules]
1. 출력은 오직 JSON 문법에 맞는 객체 하나만 있어야 하며, 어떠한 추가 설명, 주석, 마크다운도 포함하지 마세요.
2. 키 순서는 위 목록과 동일해야 합니다.
3. JSON에 대한 value 값은 '한국어'로 출력되어야 합니다.

##### [Example]
user_input = "덴마크 왕자가 주인공인 소설을 찾아줘."

{
  "concept_tags": ["덴마크 왕자", "소설"],
  "user_intents": {
    "summary": "덴마크 왕자를 주인공으로 하는 소설을 추천받고 싶어함",
    "recommendations": ["햄릿", "세익스피어"],
    "related_concepts": ["고전 문학", "비극", "4대 비극"]
  }
}

"""
