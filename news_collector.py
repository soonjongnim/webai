import feedparser
from google import genai
import os
import datetime
import time
from typing import List, Dict
import streamlit as st

class NewsCollector:
    def __init__(self):
        self.api_key = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be set.")
        
        self.client = genai.Client(api_key=self.api_key)
        # Priority list based on your account's available models
        self.candidate_models = [
            'gemini-2.5-flash',
            'gemini-2.5-pro',
            'gemini-2.0-flash-lite-preview-02-05',
            'gemini-2.0-flash-lite',
            'gemini-2.0-flash-lite-001',
            'gemini-2.0-flash',
            'gemini-2.0-flash-exp'
        ]

    def fetch_news(self, rss_urls: List[str]) -> List[Dict]:
        """Fetches news from RSS feeds and filters for those within the last 72 hours."""
        all_news = []
        now = datetime.datetime.now()
        threshold = datetime.timedelta(hours=72)

        for url in rss_urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    published_time = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_time = datetime.datetime.fromtimestamp(time.mktime(entry.published_parsed))
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published_time = datetime.datetime.fromtimestamp(time.mktime(entry.updated_parsed))
                    
                    if published_time:
                        if now - published_time <= threshold:
                            all_news.append({
                                "title": entry.title,
                                "link": entry.link,
                                "summary": entry.get("summary", ""),
                                "source": feed.feed.get("title", "Unknown Source"),
                                "published": published_time.strftime("%Y-%m-%d %H:%M:%S")
                            })
            except Exception as e:
                print(f"Error parsing {url}: {e}")
        
        return all_news

    def generate_report(self, news_items: List[Dict]) -> str:
        """Generates a markdown report using Gemini AI."""
        if not news_items:
            return "최근 3일 이내에 발행된 새로운 뉴스가 없습니다."

        news_context = ""
        for item in news_items:
            news_context += f"제목: {item['title']}\n링크: {item['link']}\n요약: {item['summary']}\n---\n"

        prompt = f"""
Role: 전문 IT 테크 저널리스트
Task: 수집된 뉴스 기사들을 분석하여 한 장의 요약 보고서 작성

수집된 뉴스 데이터:
{news_context}

Format: 
1. ## [토픽명] 형태로 대분류 (3~5개 핵심 토픽으로 그룹화)
2. - [뉴스 제목](링크) : 한 줄 핵심 요약
3. 오늘 IT 업계의 주요 시사점 요약

중요: 각 뉴스 하단에 원문 피드 [링크]를 반드시 포함하세요. 한국어로 작성하세요.
"""
        # Get all available models from account to try as a last resort
        account_models = []
        try:
            models = self.client.models.list()
            account_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods or not m.supported_generation_methods]
        except:
            pass

        # Combine candidates with other account models (removing duplicates)
        trial_models = self.candidate_models.copy()
        for am in account_models:
            clean_name = am.replace('models/', '')
            if clean_name not in trial_models:
                trial_models.append(clean_name)

        last_error = None
        for model_id in trial_models:
            # Try both with and without 'models/' prefix
            for actual_id in [model_id, f"models/{model_id}"]:
                try:
                    response = self.client.models.generate_content(
                        model=actual_id,
                        contents=prompt
                    )
                    if response.text:
                        return response.text
                except Exception as e:
                    last_error = e
                    err_msg = str(e).lower()
                    # If it's 404 or 429, continue to next model/prefix
                    if "404" in err_msg or "429" in err_msg or "quota" in err_msg:
                        continue
                    else:
                        # For other fatal errors, return immediately
                        return f"AI 분석 중 치명적 오류 발생 ({actual_id}): {e}"
        
        return (f"모든 AI 모델 호출에 실패했습니다.\n"
                f"마지막 오류: {last_error}\n\n"
                f"계약된 할당량(Quota)이 0이거나 API 키가 활성화되는 중일 수 있습니다.\n"
                f"시도한 모델 목록: {', '.join(trial_models[:15])}")

# Singleton instance
@st.cache_resource
def get_collector():
    return NewsCollector()
