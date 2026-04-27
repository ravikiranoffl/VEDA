import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import hashlib
from datetime import datetime


TARGET_FEEDS = {
    # --- GLOBAL & GULF (MENA/USA) ---
    "AlJazeera_English": "https://www.aljazeera.com/xml/rss/all.xml",
    "Gulf_News_UAE": "https://gulfnews.com/rss",
    "CNN_USA_Top": "http://rss.cnn.com/rss/cnn_topstories.rss",
    "BBC_World_News": "https://feeds.bbci.co.uk/news/world/rss.xml",

    # --- NATIONAL TRUTH & ALGORITHMS ---
    "Google_News_India": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "The_Hindu_National": "https://www.thehindu.com/news/national/feeder/default.rss",
    "NDTV_Top_Stories": "https://feeds.feedburner.com/ndtvnews-top-stories",

    # --- FINANCIAL MARKETS (24/7 Monitoring) ---
    "Moneycontrol_Markets": "https://www.moneycontrol.com/rss/marketreports.xml",
    "Moneycontrol_Commodities": "https://www.moneycontrol.com/rss/commodities.xml", # Oil/Gold
    "LiveMint_Economy": "https://www.livemint.com/rss/economy",

    # --- SOUTH INDIA / TELUGU (High Uptime) ---
    "The_Hindu_Telangana": "https://www.thehindu.com/news/national/telangana/feeder/default.rss",
    "BBC_Telugu": "https://www.bbc.com/telugu/index.xml",
    "The_Hindu_Andhra": "https://www.thehindu.com/news/national/andhra-pradesh/feeder/default.rss",
    "News18_Telugu_Home": "https://telugu.news18.com/commonfeeds/v1/tel/rss/home.xml",

    # --- REGIONAL STABILITY ---
    "The_Hindu_Tamil_Nadu": "https://www.thehindu.com/news/national/tamil-nadu/feeder/default.rss",
    "Deccan_Herald_Karnataka": "https://www.deccanherald.com/feed/rss.xml",
    "Mathrubhumi_Kerala_English": "https://english.mathrubhumi.com/cmlink/mathrubhumi-kerala-1.3323049",
    "TOI_Mumbai": "https://timesofindia.indiatimes.com/rssfeeds/-2128838597.cms",
    "The_Telegraph_East": "https://www.telegraphindia.com/rss/frontpage"
}

def get_dynamic_filepath():
    now = datetime.utcnow()
    year_folder = now.strftime("%Y")
    date_file = now.strftime("%Y-%m-%d")
    os.makedirs(year_folder, exist_ok=True)
    return f"{year_folder}/{date_file}.json"

def fetch_feed(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response: # Increased timeout to 15s for International
            return response.read()
    except Exception as e:
        print(f"Skipping {url}: Server busy.")
        return None

def update_archive():
    filepath = get_dynamic_filepath()
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            archive = json.load(f)
    else:
        archive = {
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "total_headlines": 0,
            "feeds": {name: [] for name in TARGET_FEEDS.keys()}
        }
        
    new_items = 0
    
    for feed_name, url in TARGET_FEEDS.items():
        xml_data = fetch_feed(url)
        if not xml_data: continue 
            
        try:
            root = ET.fromstring(xml_data)
            if feed_name not in archive["feeds"]:
                archive["feeds"][feed_name] = []
                
            existing_ids = {art["id"] for art in archive["feeds"][feed_name]}
            
            for item in root.findall('./channel/item'):
                link = item.find('link').text if item.find('link') is not None else ""
                if not link: continue
                    
                article_id = hashlib.md5(link.encode('utf-8')).hexdigest()
                
                if article_id not in existing_ids:
                    title = item.find('title').text if item.find('title') is not None else "Untitled"
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else "N/A"
                    
                    archive["feeds"][feed_name].append({
                        "id": article_id,
                        "title": title,
                        "published_at": pub_date,
                        "url": link
                    })
                    new_items += 1
        except:
            continue

    archive["total_headlines"] += new_items
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(archive, f, indent=4, ensure_ascii=False)
    print(f"Sync Complete. Added {new_items} items.")

if __name__ == "__main__":
    update_archive()
