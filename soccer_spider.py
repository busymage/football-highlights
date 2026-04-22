import yt_dlp
import datetime

# Configuration with refined search terms
CHANNELS = {
    'Premier League': {
        'url': 'https://www.youtube.com/c/NBCSports/videos',
        'match': 'PREMIER LEAGUE HIGHLIGHTS',
        'exclude': []
    },
    'La Liga': {
        'url': 'https://www.youtube.com/c/ESPNFC/videos',
        'match': 'LALIGA Highlights',
        'exclude': []
    },
    'Champions League': {
        'url': 'https://www.youtube.com/c/CBSSportsGolazo/videos',
        'match': 'Extended Highlights',
        'must_contain': 'UCL' # Specific check for UCL to avoid EPL/Serie A noise
    }
}

def fetch_videos():
    # Structured dictionary to keep leagues separate
    categorized_videos = { 'Premier League': [], 'La Liga': [], 'Champions League': [] }
    
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'playlist_items': '1-15',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for league, config in CHANNELS.items():
            print(f"Fetching {league}...")
            try:
                info = ydl.extract_info(config['url'], download=False)
                if 'entries' in info:
                    for entry in info['entries']:
                        title = entry.get('title', '')
                        
                        # Logic Check
                        is_match = config['match'].lower() in title.lower()
                        # Extra check for UCL channel specifically
                        if 'must_contain' in config:
                            if config['must_contain'].lower() not in title.lower():
                                is_match = False

                        if is_match:
                            categorized_videos[league].append({
                                'title': title,
                                'url': f"https://www.youtube.com/watch?v={entry['id']}",
                                'thumbnail': entry.get('thumbnails')[-1]['url']
                            })
            except Exception as e:
                print(f"Error {league}: {e}")
    return categorized_videos

def build_page(data):
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Football Daily Feed</title>
        <style>
            :root {{ --bg: #0a0a0a; --card: #161616; --text: #eee; --accent: #00ff87; }}
            body {{ font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); padding: 40px; margin: 0; }}
            .section {{ margin-bottom: 60px; }}
            .league-label {{ 
                font-size: 24px; font-weight: 800; text-transform: uppercase; 
                border-left: 5px solid var(--accent); padding-left: 15px; margin-bottom: 25px; 
                letter-spacing: 1px; color: #fff;
            }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 25px; }}
            .card {{ background: var(--card); border-radius: 12px; overflow: hidden; text-decoration: none; color: inherit; transition: 0.3s; }}
            .card:hover {{ transform: translateY(-5px); background: #222; }}
            .card img {{ width: 100%; aspect-ratio: 16/9; object-fit: cover; }}
            .card-body {{ padding: 15px; }}
            .card-title {{ font-size: 14px; font-weight: 500; line-height: 1.4; color: #ccc; }}
            .no-videos {{ color: #555; font-style: italic; }}
            header {{ margin-bottom: 50px; border-bottom: 1px solid #222; padding-bottom: 20px; }}
        </style>
    </head>
    <body>
        <header>
            <h1>Matchday Central</h1>
            <p style="color: #666;">Generated on {datetime.datetime.now().strftime('%b %d, %Y')}</p>
        </header>
    """

    for league, items in data.items():
        html_template += f"""
        <div class="section">
            <div class="league-label">{league}</div>
            <div class="grid">
        """
        
        if not items:
            html_template += '<p class="no-videos">No new highlights found in the last 24h.</p>'
        else:
            for v in items:
                html_content = f"""
                <a href="{v['url']}" target="_blank" class="card">
                    <img src="{v['thumbnail']}">
                    <div class="card-body">
                        <div class="card-title">{v['title']}</div>
                    </div>
                </a>
                """
                html_template += html_content
        
        html_template += "</div></div>"

    html_template += "</body></html>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)
    print("Done! Check highlights.html")

if __name__ == "__main__":
    vids = fetch_videos()
    build_page(vids)
