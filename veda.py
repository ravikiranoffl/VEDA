import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import hashlib
from datetime import datetime

TARGET_FEEDS = {
    # --- NATIONAL TRUTH ---
    "Google_News_India": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "The_Hindu_National": "https://www.thehindu.com/news/national/feeder/default.rss",
    "Times_of_India_National": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "Indian_Express_National": "https://indianexpress.com/section/india/feed/",
    "NDTV_Latest": "https://feeds.feedburner.com/ndtvnews-latest",
    "News18_National": "https://www.news18.com/commonfeeds/v1/eng/rss/india.xml",

    # --- FINANCIAL MARKETS ---
    "Moneycontrol_Markets": "https://www.moneycontrol.com/rss/marketreports.xml",
    "Moneycontrol_Commodities": "https://www.moneycontrol.com/rss/commodities.xml",
    "LiveMint_Markets": "https://www.livemint.com/rss/markets",
    "Economic_Times_Markets": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "Financial_Express_Economy": "https://www.financialexpress.com/economy/feed/",

    # --- THE SOUTH (Armor-Piercing Enabled) ---
    "Sakshi_Telugu_AP": "https://www.sakshi.com/rss/andhra-pradesh.xml",
    "Sakshi_Telugu_TS": "https://www.sakshi.com/rss/telangana.xml",
    "The_Hindu_Telangana": "https://www.thehindu.com/news/national/telangana/feeder/default.rss",
    "The_Hindu_Andhra": "https://www.thehindu.com/news/national/andhra-pradesh/feeder/default.rss",
    "The_Hindu_Tamil_Nadu": "https://www.thehindu.com/news/national/tamil-nadu/feeder/default.rss",
    "News18_Tamil_Nadu": "https://tamil.news18.com/commonfeeds/v1/tam/rss/tamil-nadu.xml",

    # --- REGIONAL METROS & STATES ---
    "TOI_Delhi": "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
    "TOI_Uttar_Pradesh": "https://timesofindia.indiatimes.com/rssfeeds/2581104.cms",
    "News18_Hindi_National": "https://hindi.news18.com/rss/khabar/nation/nation.xml",
    "TOI_Mumbai": "https://timesofindia.indiatimes.com/rssfeeds/-2128838597.cms",
    "Mid_Day_Mumbai": "https://www.mid-day.com/Resources/midday/rss/mumbai-news.xml",
    "TOI_Pune": "https://timesofindia.indiatimes.com/rssfeeds/-2128821991.cms",
    "TOI_Kolkata": "https://timesofindia.indiatimes.com/rssfeeds/-2128833038.cms",
    "TOI_Madhya_Pradesh": "https://timesofindia.indiatimes.com/rssfeeds/2988506.cms",
    "TOI_Assam_Northeast": "https://timesofindia.indiatimes.com/rssfeeds/3404555.cms",

    # --- SPECIALIZED (Sports, Entertainment, Tech) ---
    "ESPN_Cricinfo_India": "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",
    "TOI_Sports": "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms",
    "Indian_Express_Sports": "https://indianexpress.com/section/sports/feed/",
    "TOI_Entertainment": "https://timesofindia.indiatimes.com/rssfeeds/1081479906.cms",
    "Indian_Express_Entertainment": "https://indianexpress.com/section/entertainment/feed/",
    "NDTV_Movies": "https://feeds.feedburner.com/ndtvmovies-latest",
    "Economic_Times_Tech": "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",
    "Gadgets360_Tech": "https://feeds.feedburner.com/ndtvgadgets-latest",

    # --- GLOBAL & WESTERN ---
    "AlJazeera_English": "https://www.aljazeera.com/xml/rss/all.xml",
    "NYT_America": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "CNN_Top_Stories": "http://rss.cnn.com/rss/cnn_topstories.rss",
    "BBC_World": "https://feeds.bbci.co.uk/news/world/rss.xml"
}

def get_dynamic_filepath():
    """Routes data to the correct YYYY/YYYY-MM-DD.json file."""
    now = datetime.utcnow()
    year_folder = now.strftime("%Y")
    date_file = now.strftime("%Y-%m-%d")
    os.makedirs(year_folder, exist_ok=True)
    return f"{year_folder}/{date_file}.json"

def fetch_feed(url):
    """Fetches XML using Armor-Piercing Headers to bypass strict WAFs (Cloudflare)."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/rdf+xml, application/xml, text/xml;q=0.9, */*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,te;q=0.8',
            'Connection': 'keep-alive'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def update_archive():
    filepath = get_dynamic_filepath()
    
    # Load existing daily data or initialize a new schema
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
            
            # Ensure feed category exists
            if feed_name not in archive["feeds"]:
                archive["feeds"][feed_name] = []
            
            existing_ids = {art["id"] for art in archive["feeds"][feed_name]}
            
            # Find all <item> tags (or <entry> for Atom feeds)
            for item in root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                
                # --- AGGRESSIVE LINK HUNTING ---
                link_elem = item.find('link')
                guid_elem = item.find('guid')
                
                link = ""
                if link_elem is not None and link_elem.text:
                    link = link_elem.text.strip()
                elif link_elem is not None and link_elem.get('href'):
                    link = link_elem.get('href').strip()
                elif guid_elem is not None and guid_elem.text:
                    link = guid_elem.text.strip()
                    
                if not link or "http" not in link: 
                    continue 
                    
                # The MD5 Hash Deduplication
                article_id = hashlib.md5(link.encode('utf-8')).hexdigest()
                
                if article_id not in existing_ids:
                    title_elem = item.find('title')
                    title = title_elem.text if title_elem is not None else "Untitled"
                    
                    pub_date = item.find('pubDate')
                    if pub_date is None: pub_date = item.find('{http://www.w3.org/2005/Atom}published')
                    pub_date_text = pub_date.text if pub_date is not None else "N/A"
                    
                    archive["feeds"][feed_name].append({
                        "id": article_id,
                        "title": title.strip(),
                        "published_at": pub_date_text,
                        "url": link
                    })
                    new_items += 1
        except Exception as e:
            print(f"Error parsing {feed_name}: {e}")
            continue

    archive["total_headlines"] += new_items
    
    # Save cleanly with native UTF-8 support
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(archive, f, indent=4, ensure_ascii=False)
        
    print(f"VEDA Sync: {new_items} new records captured cleanly.")

if __name__ == "__main__":
    update_archive()
