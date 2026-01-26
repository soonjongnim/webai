import json
import os
from github import Github
from github import GithubException
import streamlit as st

class GitHubStorage:
    def __init__(self):
        self.token = st.secrets["GITHUB_TOKEN"] if "GITHUB_TOKEN" in st.secrets else os.getenv("GITHUB_TOKEN")
        self.repo_name = st.secrets["REPO_NAME"] if "REPO_NAME" in st.secrets else os.getenv("REPO_NAME")
        if not self.token or not self.repo_name:
            raise ValueError("GITHUB_TOKEN and REPO_NAME must be set in secrets or environment variables.")
        
        self.g = Github(self.token)
        self.repo = self.g.get_repo(self.repo_name)

    def load_json(self, file_path):
        """Loads JSON from GitHub repository."""
        try:
            content = self.repo.get_contents(file_path)
            data = json.loads(content.decoded_content.decode('utf-8'))
            return data
        except GithubException as e:
            if e.status == 404:
                # File not found, return default empty structure based on file name
                if "feeds" in file_path:
                    return []
                elif "archive" in file_path:
                    return {}
                elif "stats" in file_path:
                    return {"total_views": 0}
                return {}
            else:
                raise e

    def save_json(self, file_path, data, message="Update data"):
        """Saves JSON to GitHub repository."""
        content_str = json.dumps(data, indent=2, ensure_ascii=False)
        try:
            content = self.repo.get_contents(file_path)
            self.repo.update_file(
                path=file_path,
                message=message,
                content=content_str,
                sha=content.sha
            )
        except GithubException as e:
            if e.status == 404:
                # Create file if it doesn't exist
                self.repo.create_file(
                    path=file_path,
                    message=message,
                    content=content_str
                )
            else:
                raise e

# Singleton instance for easy access
@st.cache_resource
def get_storage():
    return GitHubStorage()
