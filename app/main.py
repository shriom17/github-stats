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
    
    # Generate contribution graph (smooth curve)
    contribution_days = stats_data.get('contribution_days', [])
    contrib_graph = ""
    contrib_path = ""
    contrib_area = ""
    x_labels = ""
    y_labels = ""
    
    if contribution_days:
        max_contributions = max([day['count'] for day in contribution_days] or [1])
        graph_width = 380
        graph_height = 60
        
        # Calculate points for the curve
        points = []
        num_days = len(contribution_days)
        
        for i, day in enumerate(contribution_days):
            count = day['count']
            x = (i / (num_days - 1)) * graph_width if num_days > 1 else 0
            y = graph_height - (count / max_contributions * graph_height) if max_contributions > 0 else graph_height
            points.append((x, y))
        
        # Create smooth curve path using quadratic bezier curves
        if len(points) >= 2:
            # Start the path
            path_d = f"M {points[0][0]},{points[0][1]}"
            
            for i in range(1, len(points)):
                # Calculate control point for smooth curve
                if i < len(points) - 1:
                    # Midpoint between current and next point for smooth curve
                    cp_x = (points[i][0] + points[i-1][0]) / 2
                    path_d += f" Q {points[i-1][0]},{points[i-1][1]} {cp_x},{points[i][1]}"
                else:
                    # Last point
                    path_d += f" L {points[i][0]},{points[i][1]}"
            
            contrib_path = path_d
            
            # Create area under curve with gradient
            area_d = path_d + f" L {graph_width},{graph_height} L 0,{graph_height} Z"
            contrib_area = area_d
            
            # Create dots on the curve for visual appeal
            contrib_dots = ""
            for i, (x, y) in enumerate(points):
                if i % 3 == 0:  # Show every 3rd dot to avoid clutter
                    count = contribution_days[i]['count']
                    contrib_dots += f'<circle cx="{x}" cy="{y}" r="2.5" fill="#39d353" opacity="0.9"><title>{count} contributions</title></circle>'
            
            contrib_graph = contrib_dots
            
            # Generate Y-axis labels (contribution counts)
            y_step = max_contributions / 3
            for i in range(4):
                y_value = int(max_contributions - (i * y_step))
                y_pos = (i * graph_height / 3)
                y_labels += f'<text x="-5" y="{y_pos + 4}" font-family="\'Segoe UI\', Arial, sans-serif" font-size="9" fill="#718096" text-anchor="end">{y_value}</text>'
            
            # Generate X-axis labels (dates)
            # Show start, middle, and end dates
            from datetime import datetime as dt
            if num_days >= 3:
                for idx in [0, num_days // 2, num_days - 1]:
                    if idx < len(contribution_days):
                        date_str = contribution_days[idx]['date']
                        date_obj = dt.strptime(date_str, "%Y-%m-%d")
                        label = date_obj.strftime("%b %d")
                        x_pos = (idx / (num_days - 1)) * graph_width if num_days > 1 else 0
                        x_labels += f'<text x="{x_pos}" y="75" font-family="\'Segoe UI\', Arial, sans-serif" font-size="9" fill="#718096" text-anchor="middle">{label}</text>'
    
    lang_section_height = len(languages) * 34 + 70 if languages else 0
    contrib_section_height = 145 if contribution_days else 0
    svg_height = 290 + lang_section_height + contrib_section_height
    
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
            <linearGradient id="areaGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:#39d353;stop-opacity:0.3" />
                <stop offset="100%" style="stop-color:#39d353;stop-opacity:0.05" />
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
            <rect width="135" height="100" rx="12" fill="url(#cardGrad)" stroke="rgba(255,255,255,0.1)" stroke-width="1" filter="url(#cardShadow)"/>
            <text x="67.5" y="50" font-family="'Segoe UI', Arial, sans-serif" font-size="38" font-weight="800" fill="#ffffff" text-anchor="middle">{stats_data['public_repos']}</text>
            <text x="67.5" y="73" font-family="'Segoe UI', Arial, sans-serif" font-size="11" fill="#cbd5e0" text-anchor="middle" font-weight="600">Public Repos</text>
        </g>
        
        <g transform="translate(180, 145)">
            <!-- Commits This Year -->
            <rect width="135" height="100" rx="12" fill="url(#cardGrad)" stroke="rgba(255,255,255,0.1)" stroke-width="1" filter="url(#cardShadow)"/>
            <text x="67.5" y="50" font-family="'Segoe UI', Arial, sans-serif" font-size="38" font-weight="800" fill="{grade_color}" text-anchor="middle" filter="url(#glow)">{stats_data['commits_this_year']}</text>
            <text x="67.5" y="73" font-family="'Segoe UI', Arial, sans-serif" font-size="11" fill="#cbd5e0" text-anchor="middle" font-weight="600">Contributions</text>
        </g>
        
        <g transform="translate(325, 145)">
            <!-- Max Streak -->
            <rect width="140" height="100" rx="12" fill="url(#cardGrad)" stroke="rgba(255,255,255,0.1)" stroke-width="1" filter="url(#cardShadow)"/>
            <text x="70" y="50" font-family="'Segoe UI', Arial, sans-serif" font-size="38" font-weight="800" fill="#ff6b6b" text-anchor="middle" filter="url(#glow)">{stats_data.get('max_streak', 0)}</text>
            <text x="70" y="73" font-family="'Segoe UI', Arial, sans-serif" font-size="11" fill="#cbd5e0" text-anchor="middle" font-weight="600">🔥 Max Streak</text>
        </g>
        
        <!-- Contribution Graph Section -->
        {f'''<g transform="translate(35, 265)">
            <text x="0" y="0" font-family="'Segoe UI', Arial, sans-serif" font-size="18" font-weight="700" fill="#ffffff">📊 Contribution Activity</text>
            <text x="0" y="18" font-family="'Segoe UI', Arial, sans-serif" font-size="11" fill="#a0aec0" font-weight="500">Last 90 days</text>
        </g>
        <g transform="translate(50, 310)">
            <rect x="-10" y="0" width="420" height="105" rx="10" fill="rgba(255,255,255,0.02)" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
            
            <!-- Y-axis labels -->
            <g transform="translate(0, 15)">
                {y_labels}
            </g>
            
            <!-- Graph area -->
            <g transform="translate(10, 15)">
                <!-- Grid lines -->
                <line x1="0" y1="15" x2="380" y2="15" stroke="rgba(255,255,255,0.05)" stroke-width="1" stroke-dasharray="4,4"/>
                <line x1="0" y1="30" x2="380" y2="30" stroke="rgba(255,255,255,0.05)" stroke-width="1" stroke-dasharray="4,4"/>
                <line x1="0" y1="45" x2="380" y2="45" stroke="rgba(255,255,255,0.05)" stroke-width="1" stroke-dasharray="4,4"/>
                <line x1="0" y1="60" x2="380" y2="60" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
                
                <!-- Y-axis line -->
                <line x1="0" y1="0" x2="0" y2="60" stroke="rgba(255,255,255,0.15)" stroke-width="1.5"/>
                <!-- X-axis line -->
                <line x1="0" y1="60" x2="380" y2="60" stroke="rgba(255,255,255,0.15)" stroke-width="1.5"/>
                
                <!-- Area under curve -->
                <path d="{contrib_area}" fill="url(#areaGrad)"/>
                
                <!-- Curve line -->
                <path d="{contrib_path}" fill="none" stroke="#39d353" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <animate attributeName="stroke-dashoffset" from="1000" to="0" dur="1.5s" fill="freeze"/>
                </path>
                
                <!-- Data points -->
                {contrib_graph}
                
                <!-- X-axis labels -->
                {x_labels}
            </g>
        </g>''' if contribution_days else ''}
        
        <!-- Languages Section -->
        {f'''<g transform="translate(35, {285 + contrib_section_height})">
            <text x="0" y="0" font-family="'Segoe UI', Arial, sans-serif" font-size="18" font-weight="700" fill="#ffffff">💻 Most Used Languages</text>
        </g>
        <g transform="translate(40, {315 + contrib_section_height})">
            {lang_bars}
        </g>''' if languages else ''}
    </svg>
    """
    return Response(content=svg_content, media_type="image/svg+xml")