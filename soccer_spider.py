import yt_dlp
import datetime

CHANNELS = {
    'Premier League': {'url': 'https://www.youtube.com/c/NBCSports/videos', 'match': 'PREMIER LEAGUE HIGHLIGHTS'},
    'La Liga': {'url': 'https://www.youtube.com/c/ESPNFC/videos', 'match': 'LALIGA Highlights'},
    'Champions League': {'url': 'https://www.youtube.com/c/CBSSportsGolazo/videos', 'match': 'Extended Highlights', 'must_contain': 'UCL'}
}

def fetch_videos():
    categorized = {k: [] for k in CHANNELS}
    ydl_opts = {'quiet': True, 'extract_flat': True, 'playlist_items': '1-10'}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for league, config in CHANNELS.items():
            try:
                info = ydl.extract_info(config['url'], download=False)
                for entry in info.get('entries', []):
                    title = entry.get('title', '')
                    if config['match'].lower() in title.lower():
                        if config.get('must_contain', '').lower() in title.lower():
                            categorized[league].append({
                                'title': title.split('|')[0].strip().replace('v.', 'vs.'),
                                'url': f"https://www.youtube.com/watch?v={entry['id']}",
                                'thumb': entry['thumbnails'][-1]['url']
                            })
            except Exception as e: print(f"Error {league}: {e}")
    return categorized

def generate_html(data):
    # 1. Build the dynamic content string
    sections_html = ""
    for league, videos in data.items():
        sections_html += f'<div class="section"><div class="league-label">{league}</div><div class="grid">'
        if not videos:
            sections_html += '<p style="color:#555">No matches found.</p>'
        for v in videos:
            sections_html += f'''
                <a href="{v['url']}" target="_blank" class="card">
                    <img src="{v['thumb']}">
                    <div class="card-body"><div class="card-title">{v['title']}</div></div>
                </a>'''
        sections_html += '</div></div>'

    # 2. Load the template and swap placeholders
    with open("template.html", "r", encoding="utf-8") as f:
        template = f.read()

    now = datetime.datetime.now().strftime('%b %d, %I:%M %p')
    final_html = template.replace("{{ last_updated }}", now).replace("{{ content }}", sections_html)

    # 3. Save as index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)

if __name__ == "__main__":
    results = fetch_videos()
    generate_html(results)
    print("Dashboard updated successfully.")