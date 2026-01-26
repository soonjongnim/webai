import streamlit as st
import datetime
import os
from github_storage import get_storage
from news_collector import get_collector

# Page config
st.set_page_config(page_title="AI IT Newsroom", layout="wide")

# Initialize storage and collector
try:
    storage = get_storage()
    collector = get_collector()
except Exception as e:
    st.error(f"Initialization Error: {e}")
    st.stop()

# --- Sidebar ---
st.sidebar.title("🚀 IT Newsroom")
menu = st.sidebar.radio("메뉴", ["뉴스룸", "관리자 대시보드"])

# --- Helper Functions ---
def update_view_count():
    stats = storage.load_json("data/stats.json")
    stats["total_views"] += 1
    storage.save_json("data/stats.json", stats, message="Increment view count")
    return stats["total_views"]

# --- Main Newsroom ---
if menu == "뉴스룸":
    total_views = update_view_count()
    st.title("🗞️ 오늘의 AI IT 뉴스 브리핑")
    
    archive = storage.load_json("data/news_archive.json")
    
    if not archive:
        st.info("아직 생성된 리포트가 없습니다. 관리자 대시보드에서 분석을 실행해 주세요.")
    else:
        # Sort dates descending
        dates = sorted(archive.keys(), reverse=True)
        selected_date = st.sidebar.selectbox("과거 리포트 보기", dates)
        
        st.markdown(f"### 📅 {selected_date} 리포트")
        st.markdown(archive[selected_date])
    
    st.sidebar.markdown(f"**누적 방문자 수:** {total_views}")

# --- Admin Dashboard ---
elif menu == "관리자 대시보드":
    st.title("⚙️ 관리자 대시보드")
    
    admin_password = st.sidebar.text_input("관리자 암호", type="password")
    correct_password = st.secrets["ADMIN_PASSWORD"] if "ADMIN_PASSWORD" in st.secrets else os.getenv("ADMIN_PASSWORD", "admin123")
    
    if admin_password != correct_password:
        st.warning("비밀번호를 입력해 주세요.")
        st.stop()
    
    tab1, tab2, tab3 = st.tabs(["피드 관리", "분석 실행", "통계"])
    
    # Tab 1: Feed Management
    with tab1:
        st.subheader("RSS 피드 관리")
        feeds = storage.load_json("data/feeds.json")
        
        new_feed = st.text_input("새 RSS URL 추가")
        if st.button("추가"):
            if new_feed and new_feed not in feeds:
                feeds.append(new_feed)
                storage.save_json("data/feeds.json", feeds, message=f"Add feed: {new_feed}")
                st.success("피드가 추가되었습니다.")
                st.rerun()
        
        st.write("---")
        st.write("현재 등록된 피드:")
        for i, feed in enumerate(feeds):
            col1, col2 = st.columns([0.8, 0.2])
            col1.write(feed)
            if col2.button("삭제", key=f"del_{i}"):
                feeds.pop(i)
                storage.save_json("data/feeds.json", feeds, message=f"Delete feed: {feed}")
                st.success("피드가 삭제되었습니다.")
                st.rerun()

    # Tab 2: Run Analysis
    with tab2:
        st.subheader("뉴스 수집 및 AI 분석 실행")
        if st.button("🚀 분석 시작"):
            with st.spinner("뉴스를 수집하고 AI로 분석 중입니다..."):
                feeds = storage.load_json("data/feeds.json")
                if not feeds:
                    st.error("등록된 RSS 피드가 없습니다.")
                else:
                    news_items = collector.fetch_news(feeds)
                    report = collector.generate_report(news_items)
                    
                    # Save to archive
                    today_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    archive = storage.load_json("data/news_archive.json")
                    archive[today_str] = report
                    storage.save_json("data/news_archive.json", archive, message=f"New report for {today_str}")
                    
                    st.success(f"{today_str} 리포트 생성 완료!")
                    st.markdown(report)

    # Tab 3: Statistics
    with tab3:
        st.subheader("방문자 통계")
        stats = storage.load_json("data/stats.json")
        st.metric("누적 방문자 수", stats["total_views"])
