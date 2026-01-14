from fastapi import FastAPI
from fastapi.responses import Response
import os
import httpx
from datetime import datetime

app = FastAPI()

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
            # Use GraphQL to get accurate contribution count from Jan 1st
            graphql_url = "https://api.github.com/graphql"
            from_date = f"{current_year}-01-01T00:00:00Z"
            to_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            
            query = """
            query($username: String!, $from: DateTime!, $to: DateTime!) {
              user(login: $username) {
                contributionsCollection(from: $from, to: $to) {
                  contributionCalendar {
                    totalContributions
                  }
                }
              }
            }
            """
            
            graphql_response = httpx.post(
                graphql_url,
                json={
                    "query": query, 
                    "variables": {
                        "username": username,
                        "from": from_date,
                        "to": to_date
                    }
                },
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

@app.get("/")
def root():
    return {"message": "Welcome to the GitHub User Stats API"}

@app.get("/stats")
def stats(username: str):
    stats_data = get_user_stats(username)
    if stats_data is None:
        return Response(content="User not found", status_code=404)
    return stats_data

@app.get("/stats/svg")
def stats_svg(username: str):
    stats_data = get_user_stats(username)
    if stats_data is None:
        return Response(content="User not found", status_code=404)
    
    # Determine grade color with better colors
    grade = stats_data['grade']
    if grade.startswith('S'):
        grade_color = "#FFD700"
        grade_glow = "#FFA500"
    elif grade.startswith('A'):
        grade_color = "#C0C0C0"
        grade_glow = "#A8A8A8"
    elif grade.startswith('B'):
        grade_color = "#CD7F32"
        grade_glow = "#B87333"
    else:
        grade_color = "#718096"
        grade_glow = "#4A5568"
    
    name_display = stats_data['name'] or stats_data['username']
    location = stats_data.get('location') or 'Not set'
    
    # Format joined date
    from datetime import datetime
    if stats_data.get('created_at'):
        joined_date = datetime.strptime(stats_data['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        joined = joined_date.strftime("%b %Y")
    else:
        joined = "Unknown"
    
    # Language colors
    lang_colors = {
        "Python": "#3572A5",
        "JavaScript": "#f1e05a",
        "TypeScript": "#2b7489",
        "Java": "#b07219",
        "C++": "#f34b7d",
        "C": "#555555",
        "C#": "#178600",
        "Go": "#00ADD8",
        "Rust": "#dea584",
        "Ruby": "#701516",
        "PHP": "#4F5D95",
        "HTML": "#e34c26",
        "CSS": "#563d7c",
        "Shell": "#89e051",
        "Dart": "#00B4AB",
        "Kotlin": "#A97BFF",
        "Swift": "#ffac45"
    }
    
    # Generate language bars with improved styling
    languages = stats_data.get('languages', [])
    lang_bars = ""
    y_offset = 0
    
    for lang_data in languages:
        lang = lang_data['name']
        percentage = lang_data['percentage']
        color = lang_colors.get(lang, "#858585")
        bar_width = (percentage / 100) * 420  # Max width 420px
        
        lang_bars += f'''
        <g transform="translate(0, {y_offset})">
            <rect x="0" y="0" width="420" height="28" rx="6" fill="rgba(255,255,255,0.05)"/>
            <rect x="2" y="2" width="{bar_width}" height="24" rx="5" fill="{color}" opacity="0.9">
                <animate attributeName="width" from="0" to="{bar_width}" dur="1s" fill="freeze"/>
            </rect>
            <text x="14" y="18" font-family="'Segoe UI', Arial, sans-serif" font-size="12" fill="#ffffff" font-weight="600">{lang}</text>
            <text x="408" y="18" font-family="'Segoe UI', Arial, sans-serif" font-size="11" fill="#e2e8f0" text-anchor="end" font-weight="500">{percentage}%</text>
        </g>
        '''
        y_offset += 34
    
    lang_section_height = len(languages) * 34 + 70 if languages else 0
    svg_height = 290 + lang_section_height
    
    svg_content = f"""
    <svg width="500" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#1a202c;stop-opacity:1" />
                <stop offset="50%" style="stop-color:#2d3748;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#1a202c;stop-opacity:1" />
            </linearGradient>
            <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:rgba(255,255,255,0.1);stop-opacity:1" />
                <stop offset="100%" style="stop-color:rgba(255,255,255,0.05);stop-opacity:1" />
            </linearGradient>
            <filter id="shadow">
                <feDropShadow dx="0" dy="6" stdDeviation="8" flood-opacity="0.3"/>
            </filter>
            <filter id="cardShadow">
                <feDropShadow dx="0" dy="2" stdDeviation="4" flood-opacity="0.2"/>
            </filter>
            <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>
        
        <!-- Background -->
        <rect width="500" height="{svg_height}" rx="16" fill="url(#grad)" filter="url(#shadow)"/>
        
        <!-- Decorative Elements -->
        <circle cx="50" cy="50" r="80" fill="{grade_color}" opacity="0.03"/>
        <circle cx="450" cy="{svg_height - 50}" r="100" fill="{grade_color}" opacity="0.02"/>
        
        <!-- Header Section -->
        <text x="35" y="48" font-family="'Segoe UI', Arial, sans-serif" font-size="28" font-weight="800" fill="#ffffff" letter-spacing="-0.5">{name_display}</text>
        <text x="35" y="73" font-family="'Segoe UI', Arial, sans-serif" font-size="15" fill="#a0aec0" font-weight="500">@{stats_data['username']}</text>
        
        <!-- Grade Badge -->
        <g transform="translate(445, 40)">
            <circle cx="0" cy="0" r="32" fill="{grade_glow}" opacity="0.15"/>
            <circle cx="0" cy="0" r="28" fill="url(#cardGrad)" stroke="{grade_color}" stroke-width="2.5"/>
            <text x="0" y="9" font-family="'Segoe UI', Arial, sans-serif" font-size="20" font-weight="800" fill="{grade_color}" text-anchor="middle">{grade}</text>
        </g>
        
        <!-- Info Row -->
        <g transform="translate(35, 95)">
            <rect x="0" y="0" width="155" height="30" rx="15" fill="url(#cardGrad)" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
            <text x="15" y="19" font-family="'Segoe UI', Arial, sans-serif" font-size="12" fill="#e2e8f0" font-weight="500">📍 {location}</text>
        </g>
        <g transform="translate(200, 95)">
            <rect x="0" y="0" width="145" height="30" rx="15" fill="url(#cardGrad)" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
            <text x="15" y="19" font-family="'Segoe UI', Arial, sans-serif" font-size="12" fill="#e2e8f0" font-weight="500">📅 {joined}</text>
        </g>
        
        <!-- Stats Grid -->
        <g transform="translate(35, 145)">
            <!-- Public Repos -->
            <rect width="210" height="100" rx="12" fill="url(#cardGrad)" stroke="rgba(255,255,255,0.1)" stroke-width="1" filter="url(#cardShadow)"/>
            <text x="105" y="50" font-family="'Segoe UI', Arial, sans-serif" font-size="42" font-weight="800" fill="#ffffff" text-anchor="middle">{stats_data['public_repos']}</text>
            <text x="105" y="73" font-family="'Segoe UI', Arial, sans-serif" font-size="13" fill="#cbd5e0" text-anchor="middle" font-weight="600">Public Repositories</text>
        </g>
        
        <g transform="translate(255, 145)">
            <!-- Commits This Year -->
            <rect width="210" height="100" rx="12" fill="url(#cardGrad)" stroke="rgba(255,255,255,0.1)" stroke-width="1" filter="url(#cardShadow)"/>
            <text x="105" y="50" font-family="'Segoe UI', Arial, sans-serif" font-size="42" font-weight="800" fill="{grade_color}" text-anchor="middle" filter="url(#glow)">{stats_data['commits_this_year']}</text>
            <text x="105" y="73" font-family="'Segoe UI', Arial, sans-serif" font-size="13" fill="#cbd5e0" text-anchor="middle" font-weight="600">Contributions 2026</text>
        </g>
        
        <!-- Languages Section -->
        {f'''<g transform="translate(35, 285)">
            <text x="0" y="0" font-family="'Segoe UI', Arial, sans-serif" font-size="18" font-weight="700" fill="#ffffff">💻 Most Used Languages</text>
        </g>
        <g transform="translate(40, 315)">
            {lang_bars}
        </g>''' if languages else ''}
    </svg>
    """
    return Response(content=svg_content, media_type="image/svg+xml")

# Vercel requires the app to be exported
app = app
