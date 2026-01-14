def generate_svg(username: str, repos: int, followers: int):
    return f"""
<svg width="380" height="140" viewBox="0 0 380 140"
     xmlns="http://www.w3.org/2000/svg">

  <!-- Background -->
  <rect x="0" y="0" width="380" height="140" rx="12" fill="#0d1117"/>

  <!-- Header -->
  <text x="20" y="35"
        fill="#58a6ff"
        font-size="18"
        font-family="Segoe UI, Arial">
    GitHub Stats
  </text>

  <!-- Username -->
  <text x="20" y="60"
        fill="#c9d1d9"
        font-size="14"
        font-family="Segoe UI, Arial">
    @{username}
  </text>

  <!-- Repo Count -->
  <text x="20" y="90"
        fill="#7ee787"
        font-size="14"
        font-family="Segoe UI, Arial">
    📦 Repositories: {repos}
  </text>

  <!-- Followers -->
  <text x="20" y="115"
        fill="#ffa657"
        font-size="14"
        font-family="Segoe UI, Arial">
    👥 Followers: {followers}
  </text>

</svg>
"""
