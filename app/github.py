import httpx
from datetime import datetime
import os

def get_user_stats(username: str, github_token: str = None):
    """Fetch GitHub user statistics from the GitHub API."""
    user_url = f"https://api.github.com/users/{username}"
    
    # Use token from parameter or environment
    token = github_token or os.getenv("GITHUB_TOKEN")
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    
    try:
        # Get user info
        response = httpx.get(user_url, timeout=10.0, headers=headers)
        
        if response.status_code == 404:
            return None
        
        response.raise_for_status()
        data = response.json()
        
        # Get contributions using GraphQL API
        commits_this_year = 0
        current_year = datetime.now().year
        
        if token:
            # Use GraphQL to get accurate contribution count
            graphql_url = "https://api.github.com/graphql"
            query = """
            query($username: String!) {
              user(login: $username) {
                contributionsCollection {
                  contributionCalendar {
                    totalContributions
                  }
                }
              }
            }
            """
            
            graphql_response = httpx.post(
                graphql_url,
                json={"query": query, "variables": {"username": username}},
                headers=headers,
                timeout=10.0
            )
            
            if graphql_response.status_code == 200:
                graphql_data = graphql_response.json()
                if "data" in graphql_data and graphql_data["data"]["user"]:
                    commits_this_year = graphql_data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
        
        # Get language statistics from repositories
        languages = {}
        repos_url = f"https://api.github.com/users/{username}/repos?per_page=100"
        repos_response = httpx.get(repos_url, timeout=10.0, headers=headers)
        
        if repos_response.status_code == 200:
            repos = repos_response.json()
            for repo in repos:
                if not repo.get('fork'):  # Skip forked repos
                    lang_url = repo.get('languages_url')
                    if lang_url:
                        lang_response = httpx.get(lang_url, timeout=5.0, headers=headers)
                        if lang_response.status_code == 200:
                            repo_languages = lang_response.json()
                            for lang, bytes_count in repo_languages.items():
                                languages[lang] = languages.get(lang, 0) + bytes_count
        
        # Get top 5 languages
        top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
        total_bytes = sum(languages.values()) if languages else 1
        language_stats = [
            {"name": lang, "percentage": round((bytes_count / total_bytes) * 100, 1)}
            for lang, bytes_count in top_languages
        ]
        
        # Calculate grade
        public_repos = data.get("public_repos", 0)
        followers = data.get("followers", 0)
        grade = calculate_grade(public_repos, followers, commits_this_year)
        
        return {
            "username": data.get("login"),
            "name": data.get("name"),
            "public_repos": public_repos,
            "followers": followers,
            "following": data.get("following", 0),
            "bio": data.get("bio"),
            "location": data.get("location"),
            "created_at": data.get("created_at"),
            "commits_this_year": commits_this_year,
            "grade": grade,
            "avatar_url": data.get("avatar_url"),
            "languages": language_stats
        }
    except httpx.HTTPError:
        return None

def calculate_grade(repos: int, followers: int, commits: int) -> str:
    """Calculate a grade based on GitHub activity."""
    score = (repos * 2) + (followers * 1.5) + (commits * 0.5)
    
    if score >= 500:
        return "S+"
    elif score >= 300:
        return "S"
    elif score >= 150:
        return "A+"
    elif score >= 100:
        return "A"
    elif score >= 50:
        return "B+"
    elif score >= 25:
        return "B"
    else:
        return "C"
