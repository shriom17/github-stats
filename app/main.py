from fastapi import FastAPI
from fastapi.responses import Response
from github import get_user_stats
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# You can set GITHUB_TOKEN environment variable for accurate contribution data
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
    
    # Determine grade color
    grade = stats_data['grade']
    if grade.startswith('S'):
        grade_color = "#FFD700"
    elif grade.startswith('A'):
        grade_color = "#C0C0C0"
    elif grade.startswith('B'):
        grade_color = "#CD7F32"
    else:
        grade_color = "#808080"
    
    name_display = stats_data['name'] or stats_data['username']
    
    svg_content = f"""
    <svg width="495" height="195" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
            </linearGradient>
            <filter id="shadow">
                <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.3"/>
            </filter>
        </defs>
        
        <!-- Background -->
        <rect width="495" height="195" rx="10" fill="url(#grad)" filter="url(#shadow)"/>
        
        <!-- Title Section -->
        <text x="20" y="35" font-family="'Segoe UI', Arial, sans-serif" font-size="22" font-weight="bold" fill="#ffffff">{name_display}</text>
        <text x="20" y="55" font-family="'Segoe UI', Arial, sans-serif" font-size="14" fill="#e0e0e0">@{stats_data['username']}</text>
        
        <!-- Grade Badge -->
        <rect x="410" y="15" width="65" height="50" rx="8" fill="{grade_color}" opacity="0.9"/>
        <text x="442.5" y="48" font-family="'Segoe UI', Arial, sans-serif" font-size="24" font-weight="bold" fill="#ffffff" text-anchor="middle">{grade}</text>
        
        <!-- Stats Grid -->
        <g transform="translate(20, 80)">
            <!-- Public Repos -->
            <rect width="140" height="80" rx="8" fill="rgba(255,255,255,0.15)"/>
            <text x="70" y="30" font-family="'Segoe UI', Arial, sans-serif" font-size="28" font-weight="bold" fill="#ffffff" text-anchor="middle">{stats_data['public_repos']}</text>
            <text x="70" y="55" font-family="'Segoe UI', Arial, sans-serif" font-size="12" fill="#e0e0e0" text-anchor="middle">Public Repos</text>
        </g>
        
        <g transform="translate(175, 80)">
            <!-- Followers -->
            <rect width="140" height="80" rx="8" fill="rgba(255,255,255,0.15)"/>
            <text x="70" y="30" font-family="'Segoe UI', Arial, sans-serif" font-size="28" font-weight="bold" fill="#ffffff" text-anchor="middle">{stats_data['followers']}</text>
            <text x="70" y="55" font-family="'Segoe UI', Arial, sans-serif" font-size="12" fill="#e0e0e0" text-anchor="middle">Followers</text>
        </g>
        
        <g transform="translate(330, 80)">
            <!-- Commits This Year -->
            <rect width="140" height="80" rx="8" fill="rgba(255,255,255,0.15)"/>
            <text x="70" y="30" font-family="'Segoe UI', Arial, sans-serif" font-size="28" font-weight="bold" fill="#ffffff" text-anchor="middle">{stats_data['commits_this_year']}</text>
            <text x="70" y="55" font-family="'Segoe UI', Arial, sans-serif" font-size="12" fill="#e0e0e0" text-anchor="middle">Commits (2026)</text>
        </g>
    </svg>
    """
    return Response(content=svg_content, media_type="image/svg+xml")