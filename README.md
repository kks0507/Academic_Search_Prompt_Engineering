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

## 5\. 사용 방법 (How to Use)

1.  사용자의 원본 질문을 `user_prompt` 변수에 할당합니다.
2.  `ANALYZE_GEMINI_PROMPT`를 호출하여 중간 결과인 `user_intent`를 생성합니다.
3.  `user_prompt`와 `user_intent`를 `EXTRACT_PARAMS_PROMPT`에 주입하여 완성된 프롬프트를 생성합니다.
4.  완성된 프롬프트를 Google Gemini API에 전송합니다. (권장 모델: `gemini-2.5-flash-lite-preview-06-17`)
5.  API로부터 받은 최종 JSON 응답 문자열을 파싱(Parsing)하여 애플리케이션에서 활용합니다.

## 6\. 작성자 (Author)
성균관대학교 언어AI대학원 영어공학과 김경수 
