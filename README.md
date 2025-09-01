# AI 기반 지능형 학술 검색 JSON 생성 프롬프트

## 1\. 개요 (Overview)

본 문서는 사용자의 자연어 도서 검색 질문(Query)을 2단계에 걸쳐 분석하여, 데이터베이스 검색 및 애플리케이션 로직에 최적화된 구조화된 JSON 객체를 생성하는 Google Gemini 프롬프트 시스템에 대해 설명합니다.

이 시스템은 단순 키워드 매칭 방식의 한계를 넘어, 사용자의 숨은 의도를 먼저 파악한 후, 그 의도를 바탕으로 검색 파라미터를 지능적으로 추출하여 더 정확하고 풍부한 검색 경험을 제공하는 것을 목표로 합니다.

## 2\. 주요 기능 (Key Features)

  * **2단계 분석 파이프라인**: '의도 분석'과 '파라미터 추출'의 2단계 접근으로 분석의 정확도를 높입니다.
  * **7가지 검색 유형 분류**: 사용자의 질문을 '제목', '저자+장르', '컨셉+줄거리' 등 7가지의 구체적인 유형으로 자동 분류합니다.
  * **의도 기반 정보 처리**: 명확한 질문(단순 검색)에서는 정보를 **추출**하고, 모호한 질문(심층 검색)에서는 사전 분석된 의도를 기반으로 정보를 **추론**합니다.
  * **지능형 도서 추천**: 줄거리나 컨셉만으로 질문하는 '심층 검색' 시, 가장 가능성 높은 유명 도서(예: '안네의 일기')를 추론하여 추천합니다.
  * **표준화된 JSON 출력**: 항상 일관된 구조의 영문 Key를 가진 JSON을 생성하여 안정적인 시스템 연동을 보장합니다.
  * **최적 검색어 생성**: DB 검색 효율을 높이기 위한 핵심 키워드 조합(`optimizedQuery`)을 자동으로 생성합니다.

## 3\. 시스템 아키텍처 (System Architecture)

본 시스템은 2개의 프롬프트를 순차적으로 실행하는 체인 프롬프트(Chain Prompt) 구조를 가집니다.

```
[사용자 질문] -> [Prompt 1: ANALYZE_GEMINI_PROMPT] -> [Intermediate JSON] -> [Prompt 2: EXTRACT_PARAMS_PROMPT] -> [Final JSON]
```

1.  **1단계 (의도 분석)**: `ANALYZE_GEMINI_PROMPT`가 사용자의 원본 질문(`user_prompt`)을 받아 핵심 키워드와 포괄적인 의도(`user_intent`)를 먼저 추출합니다.
2.  **2단계 (파라미터 추출)**: `EXTRACT_PARAMS_PROMPT`가 1단계 결과와 원본 질문을 종합하여 최종 검색 파라미터가 담긴 JSON을 생성합니다.

## 4\. 프롬프트 명세 (Prompt Specification)

### 4.1. 1단계: 의도 분석 프롬프트 (`ANALYZE_INTENT_PROMPT`)

  * **역할**: 사용자의 원본 질문에서 핵심 개념과 잠재적 의도를 파악하여 2단계 프롬프트가 더 풍부한 맥락을 가지고 분석을 수행할 수 있도록 사전 처리하는 역할을 합니다.

  * **입력 데이터 (Input Schema)**
    | 변수명 | 타입 | 설명 |
    | :--- | :--- | :--- |
    | `user_input` | String | 사용자가 입력한 원본 자연어 질문 |

  * **출력 데이터 (Output Schema)**
    | Key | 타입 | 설명 |
    | :--- | :--- | :--- |
    | `concept_tags`| Array[String] | 질문에서 파악된 핵심 주제, 관심사, 키워드 배열 |
    | `user_intents`| Array[String] | 사용자의 핵심 의도와 확장될 가능성이 높은 후속 질문 배열 |

  * **전체 프롬프트**:

    ```
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
    ```

### 4.2. 2단계: 파라미터 추출 프롬프트 (`EXTRACT_PARAMS_PROMPT`)

  * **역할**: 1단계에서 분석된 의도(`user_intent`)와 원본 질문(`user_prompt`)을 바탕으로, 실제 데이터베이스 검색에 사용될 최종 파라미터를 추출하고 구조화합니다.

  * **입력 데이터 (Input Schema)**
    | 변수명 | 타입 | 설명 |
    | :--- | :--- | :--- |
    | `user_prompt` | String | 사용자가 입력한 원본 자연어 질문 |
    | `user_intent` | String | 1단계 프롬프트에서 분석된 사용자의 핵심 의도 및 부가 정보 |

  * **핵심 로직**: `user_prompt`를 분석하여 7가지 유형 중 하나로 분류하고, 그 유형에 따라 정보를 추출하거나 추론합니다. (상세 유형은 프롬프트 코드 참고)

  * **출력 데이터 (Output Schema)**
    | Key | 타입 | 설명 |
    | :--- | :--- | :--- |
    | `searchType` | String | "Simple Search"(1-4) 또는 "In-depth Search"(5-7)의 상위 분류 |
    | `queryType` | Integer | 1\~7 사이의 상세 분류 ID |
    | `title` | String | 추출 또는 추론된 도서 제목 |
    | `author` | String | 추출 또는 추론된 저자명 |
    | `genre` | String | 추출 또는 추론된 장르 |
    | `concept` | String | 질문의 핵심 컨셉을 나타내는 키워드 (쉼표로 구분) |
    | `optimizedQuery` | String | 데이터베이스 검색에 직접 사용할 최적화된 3-4 단어 검색어 |

  * **전체 프롬프트**:

    ```
    # [Instruction]
    You are an expert AI that analyzes a user's book search query and generates a structured JSON object for optimal database search. Follow the steps below precisely.

    # [Input Data]
    - user_prompt: {user_prompt}
    - user_intent: {user_intent}

    ---
    # [Step 1: Classify Search Type]
    First, classify the `user_prompt` into one of the 7 types defined below and find its corresponding number ID.

    1.  **Title**: The user is looking for a specific book title. (e.g., "데미안 찾아줘")
    2.  **Title + Author**: The user specifies both title and author. (e.g., "헤르만 헤세의 데미안 있어?")
    3.  **Author**: The user is looking for works by a specific author. (e.g., "헤르만 헤세 작품 목록 보여줘")
    4.  **Author + Genre**: The user specifies an author and a genre. (e.g., "한강 작가의 소설 작품을 찾아보고 싶어")
    5.  **Concept + Target Audience**: The user is looking for books for a specific audience. (e.g., "초등학생이 읽을 만한 우주 관련 책")
    6.  **Concept + Genre**: The user combines a concept with a genre. (e.g., "인공지능을 다루는 SF 소설 추천해줘")
    7.  **Concept + Synopsis**: The user describes the plot or concept of a book. (e.g., "주인공이 갑자기 고양이로 변하는 소설 알아?")

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
      "searchType": "",         // String: "Simple Search" (for types 1-4) or "In-depth Search" (for types 5-7).
      "queryType": 0,           // Integer: The number ID from 1 to 7 determined in Step 1.
      "title": "",              // Inferred or extracted title of the book.
      "author": "",             // Inferred or extracted author of the book.
      "genre": "",              // Inferred or extracted genre.
      "concept": "",            // Core concept keywords from the user's query.
      "optimizedQuery": ""      // A 3-4 word keyword query for database search.
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
    ```

## 5\. 사용 방법 (How to Use)

1.  사용자의 원본 질문을 `user_prompt` 변수에 할당합니다.
2.  `ANALYZE_GEMINI_PROMPT`를 호출하여 중간 결과인 `user_intent`를 생성합니다.
3.  `user_prompt`와 `user_intent`를 `EXTRACT_PARAMS_PROMPT`에 주입하여 완성된 프롬프트를 생성합니다.
4.  완성된 프롬프트를 Google Gemini API에 전송합니다. (권장 모델: `gemini-2.5-flash-lite-preview-06-17`)
5.  API로부터 받은 최종 JSON 응답 문자열을 파싱(Parsing)하여 애플리케이션에서 활용합니다.

## 6\. 작성자 (Author)
성균관대학교 언어AI대학원 영어공학과 김경수 
