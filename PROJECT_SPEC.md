프로젝트 명세서: AI 기반 나만의 IT 뉴스룸 (My AI Newsroom)
1. 프로젝트 개요
목적: 국내 IT 뉴스 RSS를 수집하여 Gemini AI로 요약 분석하고, 날짜별 보고서 형태로 제공하는 웹 서비스.
핵심 가치: 데이터베이스 없이 GitHub 저장소를 저장소로 활용하며, 최신 AI 분석 기술을 활용한 1장 분량의 브리핑 제공.
2. 기술 스택 (Tech Stack)
Language: Python 3.10+
Frontend/Framework: Streamlit
AI Model: Google Gemini 1.5 Flash (API)
Data Fetching: feedparser
Storage/DB: GitHub Repository (JSON Files)
Integration: PyGithub (GitHub API wrapper)
Deployment: Streamlit Cloud
3. 데이터 구조 (Data Architecture)
모든 데이터는 /data 폴더 내의 JSON 파일로 관리하며, PyGithub를 통해 리포지토리에 직접 커밋/업데이트한다.
data/feeds.json: 등록된 RSS URL 리스트 (List[str])
data/news_archive.json: 날짜별 AI 분석 결과 리포트 (Dict[date_str, markdown_content])
data/stats.json: 접속자 통계 데이터 ({"total_views": int})
4. 핵심 기능 요구사항
4.1. 메인 뉴스룸 화면
최신성 우선: 접속 시 가장 최근에 생성된 분석 리포트를 메인 화면에 출력.
날짜별 조회: 사이드바 또는 상단 네비게이션을 통해 과거 날짜의 리포트를 선택하여 열람 가능.
UI 구성: 마크다운 형식을 지원하여 AI가 생성한 보고서(토픽별 분류, 링크 포함)가 깔끔하게 렌더링되어야 함.
4.2. 관리자 대시보드
인증: ADMIN_PASSWORD 환경 변수를 통한 간단한 비밀번호 보호.
RSS 관리: 피드 URL 추가 및 기존 피드 삭제 기능 (JSON 업데이트).
수집 및 분석 실행:
버튼 클릭 시 등록된 모든 RSS 피드 순회.
최근 3일 이내 발행된 기사만 추출.
Gemini 1.5 Flash API를 호출하여 아래 형식의 보고서 생성 지시:
뉴스들을 3~5개 핵심 토픽으로 그룹화.
각 뉴스별 핵심 요약 작성.
중요: 각 뉴스 하단에 원문 피드 [링크] 포함.
통계 확인: stats.json에 기록된 누적 방문자 수 표시.
4.3. GitHub 동기화 로직
Streamlit Cloud의 파일 시스템은 휘발성이므로, 데이터 변경(피드 추가, 분석 완료, 방문자 증가) 발생 시마다 PyGithub를 사용하여 리포지토리의 JSON 파일을 update_file 명령으로 갱신해야 함.
5. 상세 구현 가이드 (Logic Flow)
Step 1: 뉴스 데이터 수집
feedparser를 이용해 RSS 피드를 읽어옴.
published_parsed 값을 현재 시간과 비교하여 72시간(3일) 이내의 데이터만 필터링.
Step 2: AI 프롬프트 엔지니어링
code
Text
Role: 전문 IT 테크 저널리스트
Task: 수집된 뉴스 기사들을 분석하여 한 장의 요약 보고서 작성
Format: 
1. ## [토픽명] 형태로 대분류
2. - [뉴스 제목](링크) : 한 줄 핵심 요약
3. 오늘 IT 업계의 주요 시사점 요약
Step 3: Streamlit UI 레이아웃
st.sidebar: 메뉴 이동(메인/관리자) 및 날짜 선택기.
st.tabs: 관리자 화면 내 (피드관리/분석실행/통계) 탭 구분.
6. 환경 변수 설정 (Secrets)
앱 구동을 위해 다음 변수가 필요함:
GITHUB_TOKEN: GitHub Personal Access Token (repo 권한)
REPO_NAME: "계정명/저장소명"
GEMINI_API_KEY: Google AI Studio 발급 키
ADMIN_PASSWORD: 대시보드 진입용 암호
7. 초기 파일 구성 요구 (Pre-requisites)
리포지토리 내에 다음 파일이 초기화되어 있어야 함:
requirements.txt: streamlit, feedparser, google-generativeai, PyGithub, pandas 포함.
data/feeds.json: []
data/news_archive.json: {}
data/stats.json: {"total_views": 0}