<div align="center">

# 📊 GitHub Stats API

### Beautiful SVG badges showcasing GitHub user statistics

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/python-3.8+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![Vercel](https://img.shields.io/badge/vercel-%23000000.svg?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=for-the-badge)](LICENSE)

---

</div>

## ✨ Features

<table>
<tr>
<td>

- 🎨 **Beautiful Gradient Design** - Eye-catching SVG badges with smooth gradients
- 📈 **Real-time Stats** - Live data from GitHub API
- 🏆 **Grade System** - Rankings from S+ to C based on activity
- 💻 **Top Languages** - Visual breakdown of your most-used languages
- 🌍 **Profile Info** - Name, location, join date, and bio
- ⚡ **Fast & Lightweight** - Built with FastAPI for optimal performance
- 🚀 **Deploy Anywhere** - Ready for Vercel, Heroku, or local hosting
- 🔐 **Secure** - Uses GitHub Personal Access Token for authentication

</td>
</tr>
</table>

## 📸 Demo
<p align = "center">
   <img src = "./Screenshot 2026-01-15 140427.png" alt="GitHub Stat Demo" width=500>
</p>
```
https://your-domain.vercel.app/stats/svg?username=octocat
```

The API generates a beautiful SVG card showing:
- ⭐ Total contributions (current year)
- 📦 Public repositories count  
- 👥 Followers & following
- 🏅 Grade badge (S+, S, A+, A, B+, B, C)
- 💬 Programming languages breakdown
- 📍 Location & join date

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- GitHub account
- GitHub Personal Access Token

### Installation

1️⃣ **Clone the repository**
```bash
git clone https://github.com/yourusername/github-stats.git
cd github-stats
```

2️⃣ **Install dependencies**
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install fastapi uvicorn httpx python-dotenv
```

3️⃣ **Get your GitHub Personal Access Token**

- Go to [GitHub Settings → Tokens](https://github.com/settings/tokens)
- Click **"Generate new token (classic)"**
- Select scope: `read:user`
- Copy the generated token

4️⃣ **Configure environment variables**

Create a `.env` file in the root directory:
```bash
GITHUB_TOKEN=ghp_your_token_here
```

5️⃣ **Run the development server**
```bash
cd app
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000` 🎉

## 📖 API Reference

### Base URL
```
Local: http://127.0.0.1:8000
Production: https://your-domain.vercel.app
```

### Endpoints

#### 1. Root Endpoint
```http
GET /
```

Returns a welcome message.

**Response:**
```json
{
  "message": "Welcome to the GitHub User Stats API"
}
```

---

#### 2. Get User Stats (JSON)
```http
GET /stats?username={username}
```

Returns detailed GitHub statistics in JSON format.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| username | string | Yes | GitHub username |

**Example Request:**
```bash
curl http://127.0.0.1:8000/stats?username=octocat
```

**Example Response:**
```json
{
  "username": "octocat",
  "name": "The Octocat",
  "public_repos": 8,
  "followers": 4000,
  "following": 9,
  "bio": "A great octopus",
  "location": "San Francisco",
  "created_at": "2011-01-25T18:44:36Z",
  "commits_this_year": 1250,
  "grade": "S+",
  "avatar_url": "https://avatars.githubusercontent.com/u/583231",
  "languages": [
    {"name": "JavaScript", "percentage": 45.2},
    {"name": "Python", "percentage": 30.1},
    {"name": "TypeScript", "percentage": 15.7},
    {"name": "HTML", "percentage": 5.8},
    {"name": "CSS", "percentage": 3.2}
  ]
}
```

---

#### 3. Get User Stats (SVG Badge)
```http
GET /stats/svg?username={username}
```

Returns a beautiful SVG badge with user statistics.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| username | string | Yes | GitHub username |

**Example Usage:**

In Markdown:
```markdown
![GitHub Stats](http://127.0.0.1:8000/stats/svg?username=octocat)
```

In HTML:
```html
<img src="http://127.0.0.1:8000/stats/svg?username=octocat" alt="GitHub Stats" />
```

**Error Responses:**
```json
Status 404: "User not found"
```

## 🏆 Grade System

The API calculates a grade based on user activity:

| Grade | Requirements |
|-------|-------------|
| **S+** | 1000+ contributions OR 100+ repos OR 500+ followers |
| **S** | 500+ contributions OR 50+ repos OR 200+ followers |
| **A+** | 300+ contributions OR 30+ repos OR 100+ followers |
| **A** | 200+ contributions OR 20+ repos OR 50+ followers |
| **B+** | 100+ contributions OR 10+ repos OR 20+ followers |
| **B** | 50+ contributions OR 5+ repos OR 10+ followers |
| **C** | Below B requirements |

## 🌐 Deploy to Vercel

1️⃣ **Install Vercel CLI**
```bash
npm i -g vercel
```

2️⃣ **Deploy**
```bash
vercel
```

3️⃣ **Add Environment Variable**
- Go to your Vercel dashboard
- Navigate to Settings → Environment Variables
- Add `GITHUB_TOKEN` with your token value

4️⃣ **Redeploy**
```bash
vercel --prod
```

Your API will be live at `https://your-project.vercel.app`! 🚀

## 🛠️ Development

### Project Structure
```
github-stats/
├── api/
│   └── index.py          # Vercel serverless function
├── app/
│   ├── main.py           # FastAPI application
│   ├── github.py         # GitHub API integration
│   └── svg.py            # SVG generation (if exists)
├── .env                  # Environment variables (create this)
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel configuration
└── README.md
```

### Running Tests

```bash
# Install dev dependencies
pip install pytest httpx

# Run tests
pytest
```

### Local Development

```bash
# Run with auto-reload
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
python -m uvicorn app.main:app --reload
```

## 🎨 Customization

### Language Colors

The API uses GitHub's official language colors. To customize colors, edit the `lang_colors` dictionary in:
- [app/main.py](app/main.py) (lines 58-75)
- [api/index.py](api/index.py)

### Grade Thresholds

Modify grade calculation in the `calculate_grade()` function in:
- [app/github.py](app/github.py)
- [api/index.py](api/index.py)

### SVG Styling

Customize the SVG design by editing the SVG generation code in:
- [app/main.py](app/main.py) - `stats_svg()` endpoint

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Data from [GitHub REST API](https://docs.github.com/en/rest)
- Deployed on [Vercel](https://vercel.com)

## 📬 Contact

Have questions or suggestions? Feel free to open an issue!

---

<div align="center">

Made with ❤️ and Python

⭐ Star this repo if you find it useful!

</div>
