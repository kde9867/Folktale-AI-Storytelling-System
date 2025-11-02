"""
한국 전래동화 AI 스토리텔링 시스템 - Streamlit Web App
"""

import json
import random
import xml.etree.ElementTree as ET
from io import BytesIO
from typing import Dict, List, Optional

import requests
import streamlit as st
from google import genai
from PIL import Image

# 페이지 설정
st.set_page_config(
    page_title="한국 전래동화 AI 스토리텔링",
    page_icon="📚",
    layout="wide"
)

# CSS 스타일링
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .story-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .stButton>button {
        background-color: #FF6B6B;
        color: white;
        border-radius: 10px;
        padding: 10px 30px;
        font-size: 1.1rem;
    }
    </style>
""", unsafe_allow_html=True)

# FolktaleAPIClient 클래스
class FolktaleAPIClient:
    """전래동화 API 클라이언트"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # 실제 엔드포인트
        self.base_url = "https://api.kcisa.kr/openapi/service/rest/meta14/getNLCF031801"
        
    def get_folktales(self, page_no: int = 1, num_of_rows: int = 50) -> Dict:
        """전래동화 목록 조회"""
        if not self.api_key:
            return {"error": "no_api_key", "message": "API 키가 없습니다"}
        
        params = {
            'serviceKey': self.api_key,
            'pageNo': str(page_no),
            'numOfRows': str(num_of_rows)
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            
            if response.status_code != 200:
                return {"error": f"HTTP {response.status_code}", "message": "API 요청 실패"}
            
            # XML 응답 파싱
            return self._parse_xml(response.text)
                
        except Exception as e:
            return {"error": "exception", "message": str(e)}
    
    def _parse_xml(self, xml_text: str) -> Dict:
        """XML 응답 파싱"""
        try:
            root = ET.fromstring(xml_text)
            
            # resultCode 확인
            result_code = root.find('.//resultCode')
            result_msg = root.find('.//resultMsg')
            
            code = result_code.text if result_code is not None else '00'
            msg = result_msg.text if result_msg is not None else 'SUCCESS'
            
            # 0000 또는 00은 정상
            if code not in ['00', '0000']:
                return {
                    "error": f"API_ERROR_{code}",
                    "message": msg,
                    "response": {
                        "header": {
                            "resultCode": code,
                            "resultMsg": msg
                        }
                    }
                }
            
            # items 파싱
            items = []
            for item in root.findall('.//item'):
                item_dict = {}
                for child in item:
                    item_dict[child.tag] = child.text
                items.append(item_dict)
           
            return {
                'response': {
                    'header': {
                        'resultCode': '00',
                        'resultMsg': 'NORMAL SERVICE.'
                    },
                    'body': {
                        'items': items,
                        'totalCount': len(items)
                    }
                }
            }
        except Exception as e:
            return {"error": "xml_parse", "message": str(e)}
    
    def get_item_details(self, item: Dict) -> Dict:
        """API 응답을 표준 형식으로 변환"""
        return {
            'title': item.get('title', '제목 없음'),
            'author': item.get('creator', '저자 미상'),
            'content': item.get('description', item.get('title', '')),
            'keyword': item.get('subjectKeyword', ''),
            'language': item.get('language', '한국어'),
            'url': item.get('url', ''),
            'thumbnail': item.get('referenceIdentifier', '')
        }

# StorytellingAI 클래스
class StorytellingAI:
    """Gemini AI를 활용한 스토리텔링 시스템"""
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        
    def summarize_story(self, title: str, content: str) -> str:
        """전래동화 줄거리 요약"""
        prompt = f"""
        다음 한국 전래동화를 어린이가 이해하기 쉽게 3-5문장으로 요약해주세요.
        
        제목: {title}
        내용: {content}
        
        요약은 재미있고 교훈적인 내용을 포함해야 합니다.
        """
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"요약 생성 실패: {str(e)}"
    
    def create_image_prompt(self, title: str, summary: str) -> str:
        """이미지 생성을 위한 프롬프트 생성"""
        prompt = f"""
        다음 한국 전래동화의 핵심 장면을 그림으로 표현하기 위한 영문 프롬프트를 생성해주세요.
        
        제목: {title}
        줄거리: {summary}
        
        요구사항:
        - 동화적이고 따뜻한 느낌
        - 한국 전통 요소 포함
        - 어린이 친화적
        - 영어로 작성
        - 50 단어 이내
        
        프롬프트만 출력해주세요.
        """
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            return f"A warm and friendly Korean folktale illustration about {title}"
    
    def generate_image(self, prompt: str) -> Optional[Image.Image]:
        """Gemini로 이미지 생성"""
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[prompt],
            )
            
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image = Image.open(BytesIO(part.inline_data.data))
                    return image
            
            return None
        except Exception as e:
            st.error(f"이미지 생성 실패: {str(e)}")
            return None

# 세션 스테이트 초기화
if 'api_keys_set' not in st.session_state:
    st.session_state.api_keys_set = False
if 'selected_story' not in st.session_state:
    st.session_state.selected_story = None
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None

# 메인 UI
st.markdown('<h1 class="main-header">📚 한국 전래동화 AI 스토리텔링</h1>', unsafe_allow_html=True)
st.markdown("---")

# 사이드바 - API 키 설정
with st.sidebar:
    st.header("⚙️ 설정")
    
    google_api_key = st.text_input(
        "Google API Key",
        type="password",
        help="Gemini API 키를 입력하세요"
    )
    
    data_gov_api_key = st.text_input(
        "공공데이터 API Key",
        type="password",
        help="없으면 샘플 데이터를 사용합니다"
    )
    
    if st.button("API 키 저장"):
        if google_api_key:
            st.session_state.google_api_key = google_api_key
            st.session_state.data_gov_api_key = data_gov_api_key
            st.session_state.api_keys_set = True
            st.success("✅ API 키가 저장되었습니다!")
        else:
            st.error("❌ Google API 키는 필수입니다!")
    
    st.markdown("---")
    st.markdown("### 📖 사용 방법")
    st.markdown("""
    1. API 키 입력 및 저장
    2. 전래동화 선택
    3. AI 요약 생성
    4. 이미지 생성
    """)
    
    st.markdown("---")
    st.markdown("### 🔗 참고 링크")
    st.markdown("[Google AI Studio](https://aistudio.google.com/)")
    st.markdown("[공공데이터 포털](https://www.data.go.kr/)")

# 메인 컨텐츠
if not st.session_state.api_keys_set:
    st.info("👈 먼저 사이드바에서 API 키를 설정해주세요!")
else:
    # AI 클라이언트 초기화
    storytelling_ai = StorytellingAI(st.session_state.google_api_key)
    
    # 전래동화 데이터 가져오기
    st.header("1️⃣ 전래동화 선택")
    
    # API 키가 있는지 확인
    if not st.session_state.get('data_gov_api_key'):
        st.error("공공데이터 API 키를 입력해주세요!")
        st.stop()
    
    folktale_client = FolktaleAPIClient(st.session_state.data_gov_api_key)
    
    # 전래동화 데이터 수집
    collected_stories = []
    
    with st.spinner("전래동화 데이터를 불러오는 중..."):
        data = folktale_client.get_folktales(page_no=1, num_of_rows=50)
        
        if "error" not in data:
            try:
                items = data.get('response', {}).get('body', {}).get('items', [])
                
                if items:
                    for item in items:
                        story = folktale_client.get_item_details(item)
                        # 본문이 있는 것만 수집
                        if story['content'] and len(story['content']) > 50:
                            collected_stories.append(story)
                    
                    if collected_stories:
                        st.success(f"✅ {len(collected_stories)}개의 전래동화를 불러왔습니다!")
                    else:
                        st.warning("유효한 전래동화를 찾을 수 없습니다.")
                else:
                    st.warning("항목이 비어있습니다.")
            except Exception as e:
                st.error(f"데이터 처리 오류: {str(e)}")
        else:
            # API 오류 처리
            result_code = data.get('response', {}).get('header', {}).get('resultCode', '')
            result_msg = data.get('response', {}).get('header', {}).get('resultMsg', data.get('message', ''))
            
            if result_code == '12':
                st.error("활용 신청 승인 대기 중이거나 API 키가 잘못되었습니다.")
            else:
                st.error(f"API 오류: {result_msg}")
            st.stop()
    
    if not collected_stories:
        st.error("사용 가능한 전래동화가 없습니다.")
        st.stop()
    
    # 전래동화 목록 표시
    col1, col2 = st.columns([2, 1])
    
    with col1:
        story_titles = [story['title'] for story in collected_stories]
        selected_title = st.selectbox(
            "전래동화를 선택하세요",
            story_titles,
            key="story_selector"
        )
        
        # 선택된 이야기 찾기
        selected_story = next((s for s in collected_stories if s['title'] == selected_title), None)
        
        if selected_story:
            st.session_state.selected_story = selected_story
            
            with st.container():
                st.markdown('<div class="story-card">', unsafe_allow_html=True)
                st.subheader(f"📖 {selected_story['title']}")
                st.write(f"**저자:** {selected_story['author']}")
                
                # 내용을 적절히 잘라서 표시
                content = selected_story['content']
                if len(content) > 500:
                    content = content[:500] + "..."
                st.write(f"**내용:** {content}")
                
                if selected_story.get('keyword'):
                    st.write(f"**키워드:** {selected_story['keyword']}")
                st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.image("https://via.placeholder.com/300x400?text=Korean+Folktale", 
                 use_column_width=True)
    
    st.markdown("---")
    
    # AI 요약 생성
    st.header("2️⃣ AI 줄거리 요약")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button( " AI 요약 생성", use_container_width=True):
            if st.session_state.selected_story:
                with st.spinner("AI가 줄거리를 요약하고 있습니다..."):
                    summary = storytelling_ai.summarize_story(
                        st.session_state.selected_story['title'],
                        st.session_state.selected_story.get('content', '')
                    )
                    st.session_state.summary = summary
    
    with col2:
        if st.session_state.summary:
            st.success("AI 요약 완료!")
            st.write(st.session_state.summary)
    
    st.markdown("---")
    
    # 이미지 생성
    st.header("3️⃣ AI 이미지 생성")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("이미지 생성", use_container_width=True):
            if st.session_state.summary:
                with st.spinner("AI가 이미지를 생성하고 있습니다... (약 10-20초 소요)"):
                    # 이미지 프롬프트 생성
                    image_prompt = storytelling_ai.create_image_prompt(
                        st.session_state.selected_story['title'],
                        st.session_state.summary
                    )
                    
                    st.info(f"생성 프롬프트: {image_prompt}")
                    
                    # 이미지 생성
                    generated_image = storytelling_ai.generate_image(image_prompt)
                    
                    if generated_image:
                        st.session_state.generated_image = generated_image
                        st.success("이미지 생성 완료!")
                    else:
                        st.error("이미지 생성 실패")
            else:
                st.warning("먼저 AI 요약을 생성해주세요!")
    
    with col2:
        if st.session_state.generated_image:
            st.image(st.session_state.generated_image, 
                    caption=f"{st.session_state.selected_story['title']} - AI 생성 이미지",
                    use_column_width=True)
            
            # 이미지 다운로드 버튼
            buf = BytesIO()
            st.session_state.generated_image.save(buf, format="PNG")
            btn = st.download_button(
                label="이미지 다운로드",
                data=buf.getvalue(),
                file_name=f"{st.session_state.selected_story['title']}_ai_image.png",
                mime="image/png"
            )

# 푸터
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>🎓 한국 전래동화 AI 스토리텔링 시스템</p>
        <p>Powered by Google Gemini AI & Streamlit</p>
    </div>
""", unsafe_allow_html=True)