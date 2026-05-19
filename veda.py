import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import hashlib
import asyncio
import aiohttp
import trafilatura
import random
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode, quote
from huggingface_hub import HfApi, hf_hub_download

# ==========================================
# SECURE CONFIGURATION
# ==========================================
HF_REPO_ID = "ravikiranoffl/HEDA"
HF_TOKEN = os.environ.get("HF_TOKEN")
SCRAPERAPI_KEY = os.environ.get("SCRAPERAPI_KEY") # Optional: Add to GitHub Secrets for ultimate stealth

# Realistic Browser Camouflage (Fallback if ScraperAPI is off)
REAL_BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Upgrade-Insecure-Requests': '1'
}

TARGET_FEEDS = {
    # --- INDIA: NATIONAL CORE ---
    "Google_News_India": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "The_Hindu_National": "https://www.thehindu.com/news/national/feeder/default.rss",
    "Times_of_India_National": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "Indian_Express_National": "https://indianexpress.com/section/india/feed/",
    "NDTV_Latest": "https://feeds.feedburner.com/ndtvnews-latest",

    # --- INDIA: FINANCIAL MARKETS ---
    "Moneycontrol_Markets": "https://www.moneycontrol.com/rss/marketreports.xml",
    "Moneycontrol_Commodities": "https://www.moneycontrol.com/rss/commodities.xml",
    "LiveMint_Markets": "https://www.livemint.com/rss/markets",
    "Economic_Times_Markets": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",

    # --- TELUGU HEAVYWEIGHTS ---
    "Namasthe_Telangana": "https://www.ntnews.com/feed",
    "NTV_Telugu": "https://ntvtelugu.com/feed",
    "10TV_Telugu": "https://10tv.in/feed",
    "ABP_Desam_Telugu": "https://telugu.abplive.com/home/feed",
    "V6_Velugu_TS": "https://www.v6velugu.com/feed",

    # --- INDIA: REGIONAL ---
    "The_Hindu_Tamil_Nadu": "https://www.thehindu.com/news/national/tamil-nadu/feeder/default.rss",
    "The_Hindu_Telangana": "https://www.thehindu.com/news/national/telangana/feeder/default.rss",
    "The_Hindu_Andhra_Pradesh": "https://www.thehindu.com/news/national/andhra-pradesh/feeder/default.rss",
    "The_Hindu_Karnataka": "https://www.thehindu.com/news/national/karnataka/feeder/default.rss",
    "The_Hindu_Kerala": "https://www.thehindu.com/news/national/kerala/feeder/default.rss",
    "Indian_Express_Bangalore": "https://indianexpress.com/section/cities/bangalore/feed/",
    "Indian_Express_Hyderabad": "https://indianexpress.com/section/cities/hyderabad/feed/",
    "Indian_Express_Thiruvanthapuram":"https://indianexpress.com/section/cities/thiruvananthapuram/feed/",
    "Indian_Express_Jammu":"https://indianexpress.com/section/cities/jammu/feed/",
    "Indian_Express_Chennai": "https://indianexpress.com/section/cities/chennai/feed/",
    "The_Hindu_Delhi": "https://www.thehindu.com/news/cities/Delhi/feeder/default.rss",
    "Indian_Express_Lucknow": "https://indianexpress.com/section/cities/lucknow/feed/",
    "Indian_Express_Chandigarh": "https://indianexpress.com/section/cities/chandigarh/feed/",
    "Mid_Day_Mumbai": "https://www.mid-day.com/Resources/midday/rss/mumbai-news.xml",
    "Indian_Express_Mumbai": "https://indianexpress.com/section/cities/mumbai/feed/",
    "Indian_Express_Pune": "https://indianexpress.com/section/cities/pune/feed/",
    "Indian_Express_Ahmedabad": "https://indianexpress.com/section/cities/ahmedabad/feed/",
    "Indian_Express_Kolkata": "https://indianexpress.com/section/cities/kolkata/feed/",

    # --- SPECIALIZED ---
    "ESPN_Cricinfo_India": "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",
    "Economic_Times_Tech": "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",

    # --- GLOBAL ---
    "NYT_USA_Top": "https://rss.nytimes.com/services/xml/rss/nyt/US.xml",
    "NPR_News_USA": "https://feeds.npr.org/1001/rss.xml",
    "PBS_NewsHour": "https://www.pbs.org/newshour/feeds/rss/headlines",
    "Washington_Post_World": "https://feeds.washingtonpost.com/rss/world",
    "CBC_Canada_Top": "https://www.cbc.ca/cmlink/rss-topstories",
    "Los_Angeles_Times": "https://www.latimes.com/world-nation/rss2.0.xml",
    "MercoPress_LatAm": "https://en.mercopress.com/rss",
    "BBC_Latin_America": "https://feeds.bbci.co.uk/news/world/latin_america/rss.xml",
    "Rio_Times_Brazil": "https://riotimesonline.com/feed/",
    "BBC_Europe": "https://feeds.bbci.co.uk/news/world/europe/rss.xml",
    "The_Guardian_Europe": "https://www.theguardian.com/europe/rss",
    "France24_Europe": "https://www.france24.com/en/europe/rss",
    "Independent_UK": "https://www.independent.co.uk/news/world/europe/rss",
    "Sky_News_UK": "https://feeds.skynews.com/feeds/rss/home.xml",
    "RTE_Ireland": "https://www.rte.ie/news/rss/news-headlines.xml",
    "AllAfrica_Top": "https://allafrica.com/tools/headlines/rdf/africa/headlines.rdf",
    "BBC_Africa": "https://feeds.bbci.co.uk/news/world/africa/rss.xml",
    "Mail_and_Guardian_SA": "https://mg.co.za/feed/",
    "Africa_Report": "https://www.theafricareport.com/feed/",
    "Premium_Times_Nigeria": "https://www.premiumtimesng.com/feed",
    "SCMP_Hong_Kong": "https://www.scmp.com/rss/2/feed",
    "CNA_Singapore": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml",
    "Japan_Times": "https://www.japantimes.co.jp/feed/",
    "AlJazeera_MiddleEast": "https://www.aljazeera.com/xml/rss/all.xml",
    "Arab_News": "https://www.arabnews.com/cat/1/rss.xml",
    "Times_of_Israel": "https://www.timesofisrael.com/feed/",
    "ABC_News_Australia": "https://www.abc.net.au/news/feed/51120/rss.xml",
    "The_Age_Melbourne": "https://www.theage.com.au/rss/feed.xml",
    "RNZ_New_Zealand": "https://www.rnz.co.nz/rss/national.xml",
    "News_com_au": "https://www.news.com.au/content-feeds/latest-news-national/"
}

def get_ist_time():
    return datetime.now(timezone(timedelta(hours=5, minutes=30)))

def clean_url(url):
    parsed = urlparse(url)
    qd = [q for q in parse_qsl(parsed.query) if not q[0].startswith('utm_')]
    return urlunparse(parsed._replace(query=urlencode(qd)))

# ==========================================
# THE DEEP CLEANER (GARBAGE FILTER)
# ==========================================
def clean_text(raw_text):
    if not raw_text:
        return None
        
    junk_triggers = [
        "also read", "read more", "related articles", 
        "related news", "click here", "watch video",
        "advertisement", "subscribe to our newsletter",
        "for more updates", "download our app"
    ]
    
    cleaned_lines = []
    for line in raw_text.split('\n'):
        clean_line = line.strip()
        if not clean_line:
            continue
            
        line_lower = clean_line.lower()
        is_junk = any(line_lower.startswith(trigger) or line_lower == trigger for trigger in junk_triggers)
        
        if not is_junk:
            cleaned_lines.append(clean_line)
            
    return '\n\n'.join(cleaned_lines)

# ==========================================
# ASYMMETRIC STEALTH EXTRACTION
# ==========================================
async def fetch_full_text(session, url, art_id, sem):
    async with sem:
        target_url = url
        
        # Deploy ScraperAPI if Key exists
        if SCRAPERAPI_KEY:
            target_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={quote(url)}"

        try:
            async with session.get(target_url, timeout=20) as resp:
                html = await resp.text()
                raw_text = trafilatura.extract(html)
                
                # Apply Deep Cleaner
                clean_content = clean_text(raw_text)
                
                # WAF Catch & Release
                if clean_content:
                    forbidden_phrases = ["Error 403 Forbidden", "Varnish cache server", "Cloudflare", "Enable JavaScript and cookies"]
                    if any(phrase in clean_content for phrase in forbidden_phrases):
                        return art_id, None
                
                # Human Mimicry Jitter (Random sleep 1.5s to 4.5s)
                await asyncio.sleep(random.uniform(1.5, 4.5))
                return art_id, clean_content
        except Exception:
            return art_id, None

async def process_deep_archive(new_articles):
    sem = asyncio.Semaphore(4) # Polite concurrency limit
    headers = None if SCRAPERAPI_KEY else REAL_BROWSER_HEADERS
    
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = [fetch_full_text(session, a['url'], a['id'], sem) for a in new_articles]
        return dict(await asyncio.gather(*tasks))

# ==========================================
# MASTER ENGINE
# ==========================================
def veda_engine():
    now = get_ist_time()
    date_str = now.strftime("%Y-%m-%d")
    folder = now.strftime("%Y")
    os.makedirs(folder, exist_ok=True)
    
    idx_path = f"{folder}/{date_str}.json"
    archive = json.load(open(idx_path)) if os.path.exists(idx_path) else {"date": date_str, "feeds": {}}
    
    new_for_deep = []
    status = {}

    print(f"[{now.strftime('%H:%M:%S')}] Commencing Matrix Sweep...")

    # Phase 1: Lightweight RSS Ingestion
    for name, url in TARGET_FEEDS.items():
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                root = ET.fromstring(resp.read())
                items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
                if not items: 
                    status[name] = 0
                    continue
                
                status[name] = 1
                if name not in archive["feeds"]: archive["feeds"][name] = []
                uids = {a["id"] for a in archive["feeds"][name]}

                for it in items:
                    link = clean_url(it.find('link').text or it.find('link').get('href'))
                    aid = hashlib.md5(link.encode()).hexdigest()
                    if aid not in uids:
                        title = it.find('title').text
                        pdt = it.find('pubDate').text if it.find('pubDate') is not None else "N/A"
                        obj = {"id": aid, "title": title, "url": link, "published_at": pdt}
                        archive["feeds"][name].append(obj)
                        new_for_deep.append(obj)
                
                archive["feeds"][name].sort(key=lambda x: x.get('published_at', ''), reverse=True)
                archive["feeds"][name] = archive["feeds"][name][:250]
        except Exception as e:
            status[name] = 0

    # Save Lightweight Grid Index to GitHub
    json.dump(archive, open(idx_path, 'w'), separators=(',', ':'))
    
    # Save Status Telemetry
    st_path = "status.json"
    st_data = json.load(open(st_path)) if os.path.exists(st_path) else []
    st_data.append({"run_time_ist": now.strftime("%Y-%m-%d %H:%M:%S"), "status": status})
    json.dump(st_data[-150:], open(st_path, 'w'), indent=4) # Keep last 150 sweeps

    # Phase 2: HEDA Deep Archive (Hugging Face)
    if new_for_deep and HF_TOKEN:
        print(f"[{now.strftime('%H:%M:%S')}] Executing Deep Extraction on {len(new_for_deep)} new nodes...")
        deep_map = asyncio.run(process_deep_archive(new_for_deep))
        
        api = HfApi(token=HF_TOKEN)
        deep_fn = f"data/{date_str}.json"
        
        try:
            d_path = hf_hub_download(repo_id=HF_REPO_ID, filename=deep_fn, repo_type="dataset")
            current_deep = json.load(open(d_path))
        except Exception:
            current_deep = {}
        
        current_deep.update({k: v for k, v in deep_map.items() if v})
        
        tmp_p = f"/tmp/{date_str}.json"
        json.dump(current_deep, open(tmp_p, 'w', encoding='utf-8'), separators=(',', ':'), ensure_ascii=False)
        
        print(f"[{now.strftime('%H:%M:%S')}] Beaming payload to Hugging Face Vault...")
        api.upload_file(path_or_fileobj=tmp_p, path_in_repo=deep_fn, repo_id=HF_REPO_ID, repo_type="dataset")
        print(f"[{now.strftime('%H:%M:%S')}] Matrix Sweep Complete.")

if __name__ == "__main__":
    veda_engine()
