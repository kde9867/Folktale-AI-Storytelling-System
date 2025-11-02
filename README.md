# Folktale-AI-Storytelling-System

# 한국 전래동화 AI 스토리텔링 시스템

## 프로젝트 개요

공공데이터 포털의 **한국 전래동화 API**와 **Google AI (Gemini + Imagen)**를 활용하여 전래동화를 현대적으로 재해석하는 AI 시스템입니다.

### 핵심 기능

1. **전래동화 데이터 수집**: 공공데이터 포털 API로부터 한국 전래동화 데이터 수집
2. **AI 줄거리 요약**: Gemini 2.5 Flash로 다양한 스타일의 줄거리 요약
3. **교훈 분석**: 전래동화가 담고 있는 가치와 교훈 자동 추출
4. **이미지 프롬프트 생성**: Imagen(Nano Banana)으로 스토리 기반 이미지 생성을 위한 프롬프트 자동 생성

---

## 기술 스택

### AI 모델
- **Gemini 2.5 Flash**: 텍스트 분석, 요약, 프롬프트 생성
- **Imagen (Nano Banana)**: 이미지 생성 (프롬프트 생성까지 구현)

### 데이터 소스
- **문화체육관광부 다국어동화구연 한국전래동화 API**
  - 출처: 공공데이터 포털 (https://www.data.go.kr/data/15105185/openapi.do)
  - 제공: 국립어린이청소년도서관

### 개발 환경
- Python 3.8+
- Jupyter Notebook
- Google AI API

---

## 설치 및 실행

### 1. 필수 라이브러리 설치

```bash
pip install google-generativeai requests pillow ipywidgets matplotlib
```

### 2. API 키 발급

#### Google AI API Key
1. [Google AI Studio](https://aistudio.google.com/app/apikey) 접속
2. API 키 생성
3. 환경변수 설정 또는 노트북에 직접 입력

```bash
export GOOGLE_API_KEY='your-google-api-key'
```

#### 공공데이터 포털 API Key
1. [데이터 활용 신청](https://www.data.go.kr/data/15105185/openapi.do) 페이지 접속
2. 회원가입 및 로그인
3. 활용 신청 후 서비스 키 발급
4. 환경변수 설정 또는 노트북에 직접 입력

```bash
export DATA_GOV_API_KEY='your-data-gov-api-key'
```

### 3. 노트북 실행

```bash
jupyter notebook korean_folktale_ai_demo.ipynb
```

---

## 주요 기능 상세

### 1. 전래동화 API 연동

```python
client = FolktaleAPIClient(api_key)
folktales = client.get_folktales(page_no=1, num_of_rows=10)
```

- REST API를 통한 전래동화 데이터 조회
- 제목, 저자, 발행 정보 등 메타데이터 제공
- 검색 및 필터링 기능

### 2. 다양한 요약 스타일

```python
styles = ["어린이용", "교육용", "핵심요약", "상세분석"]
```

- **어린이용**: 5-7세 어린이가 이해할 수 있는 쉬운 표현
- **교육용**: 교사나 부모를 위한 교육 목적 요약
- **핵심요약**: 2-3문장의 간단한 핵심 내용
- **상세분석**: 스토리 구조, 상징, 문화적 의미 분석

### 3. 교훈 분석

```python
moral_analysis = summarizer.analyze_moral_lesson(story_data)
```

- 전래동화가 담고 있는 핵심 가치 추출
- 현대 사회에의 적용 방안 제시
- 어린이 교육 포인트 도출

### 4. 이미지 생성 프롬프트

```python
image_prompt = summarizer.generate_image_prompt(story_data, summary)
```

- 한국어 스토리를 영문 이미지 프롬프트로 변환
- 한국 전통 문화 요소 자동 포함
- 동화적이고 따뜻한 분위기 설정
- Imagen API에 바로 사용 가능

---



## 참고 자료

### 공식 문서
- [공공데이터 포털](https://www.data.go.kr/)
- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API 문서](https://ai.google.dev/docs)
- [Vertex AI Imagen](https://cloud.google.com/vertex-ai/docs/generative-ai/image/overview)

