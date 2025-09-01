EXTRACT_PARAMS_PROMPT = """
# [Instruction]
You are an expert AI that analyzes a user's book search query and generates a structured JSON object for optimal database search. Follow the steps below precisely.

# [Input Data]
- user_prompt: {user_prompt}
- user_intent: {user_intent}

---
# [Step 1: Classify Search Type (3-Tier System)]
First, classify the `user_prompt` into one of the 3 types defined below. Then, find the corresponding number ID (1-7) for the query's specific pattern.

1. Keyword-based Search (키워드 기반 질의)
- Description: The user provides a single, specific keyword for a title or an author.
- Rule: {user_prompt} that are 6 characters or less, OR are judged to be a single noun (including proper nouns), MUST be classified as this type.
- Query IDs:
    - 1. Title: A specific book title. (e.g., "데미안")
    - 3. Author: Works by a specific author. (e.g., "한강")

2. Simple Search (단순 질의)
- Description: The user specifies a clear combination of two entities like title and author, or author and genre.
- Query IDs:
    - 2. Title + Author: A specific title and author. (e.g., "헤르만 헤세의 데미안 있어?")
    - 4. Author + Genre: An author and a genre. (e.g., "한강 작가의 소설 작품을 찾아보고 싶어")

3. In-depth Search (심층 질의)
- Description: The user describes a concept, plot, or target audience without naming a specific book. This requires inference.
- Query IDs:
    - 5. Concept + Target Audience: Books for a specific audience. (e.g., "초등학생이 읽을 만한 우주 관련 책")
    - 6. Concept + Genre: A concept combined with a genre. (e.g., "인공지능을 다루는 SF 소설 추천해줘")
    - 7. Concept + Synopsis: A description of the plot or concept. (e.g., "주인공이 갑자기 고양이로 변하는 소설 알아?")

---
# [Step 2: Generate JSON Output]
Based on the classification from Step 1, fill out the following JSON object.
- Keys MUST be in English as specified in the format below.
- If the type is "Keyword-based Search" or "Simple Search" (IDs 1-4): EXTRACT entities directly from the `user_prompt`.
- If the type is "In-depth Search" (IDs 5-7): INFER and SUGGEST entities based on the `user_intent`. If the `user_intent` strongly suggests a famous book (e.g., "안네의 일기"), you MUST fill in the `title` and `author` fields.
- If a value cannot be found, leave it as an empty string "".

# [Unified Output JSON Format]
Respond with ONLY the following JSON object. Do not include any other text or explanations.
{{
  "searchType": "",       // String: "Keyword-based Search", "Simple Search", or "In-depth Search".
  "queryType": 0,         // Integer: The number ID from 1 to 7 determined in Step 1.
  "title": "",            // Inferred or extracted title of the book.
  "author": "",           // Inferred or extracted author of the book.
  "genre": "",            // Inferred or extracted genre.
  "concept": "",          // Core concept keywords from the user's query.
  "optimizedQuery": ""    // A 3-4 word keyword query for database search.
}}

---
# [Examples]

# [Example 1: Keyword-based Search (Type 3)]
- user_prompt: "한강"
- user_intent: "'한강' 작가의 도서 정보 탐색"
- Expected Output:
{{
  "searchType": "Keyword-based Search",
  "queryType": 3,
  "title": "",
  "author": "한강",
  "genre": "",
  "concept": "한강",
  "optimizedQuery": "한강"
}}

# [Example 2: Simple Search (Type 2)]
- user_prompt: "헤르만 헤세의 데미안"
- user_intent: "저자 '헤르만 헤세', 제목 '데미안'으로 도서 검색"
- Expected Output:
{{
    "searchType": "Simple Search",
    "queryType": 2,
    "title": "데미안",
    "author": "헤르만 헤세",
    "genre": "",
    "concept": "헤르만 헤세, 데미안",
    "optimizedQuery": "헤르만 헤세 데미안"
}}

# [Example 3: In-depth Search (Type 7)]
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
"""
