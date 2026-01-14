from fastapi import FastAPI
from fastapi.responses import Response
from github import get_user_stats
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

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