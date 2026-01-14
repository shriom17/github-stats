# GitHub Stats API

Beautiful SVG badges showing GitHub user statistics.

## Setup

1. Install dependencies:
```bash
pip install fastapi uvicorn httpx
```

2. Get a GitHub Personal Access Token:
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scope: `read:user`
   - Copy the token

3. Create a `.env` file (copy from `.env.example`):
```bash
GITHUB_TOKEN=your_token_here
```

4. Run the server:
```bash
cd app
uvicorn main:app --reload
```

## Usage

- **JSON Stats**: `http://127.0.0.1:8000/stats?username=octocat`
- **SVG Badge**: `http://127.0.0.1:8000/stats/svg?username=octocat`

## Features

- Total contributions (current year)
- Public repositories count
- Followers count
- Grade system (S+, S, A+, A, B+, B, C)
- Beautiful gradient design
