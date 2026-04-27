import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import hashlib
from datetime import datetime

TARGET_FEEDS = {
    # 1. NATIONAL TRUTH, ALGORITHMS & POLICY
    "Google_News_India": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "The_Hindu_National": "https://www.thehindu.com/news/national/feeder/default.rss",
    "Times_of_India_National": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "Indian_Express_National": "https://indianexpress.com/section/india/feed/",
    "NDTV_Top_Stories": "https://feeds.feedburner.com/ndtvnews-top-stories",

    # 2. FINANCIAL MARKETS (Stocks, Gold, Oil, NSE/BSE)
    "Moneycontrol_Markets": "https://www.moneycontrol.com/rss/marketreports.xml", 
    "Moneycontrol_Commodities": "https://www.moneycontrol.com/rss/commodities.xml", 
    "LiveMint_Markets": "https://www.livemint.com/rss/markets",
    "Economic_Times_Markets": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "Business_Standard_Top": "https://www.business-standard.com/rss/home_page_top_stories.rss",
    "Financial_Express_Economy": "https://www.financialexpress.com/economy/feed/",

    # 3. THE SOUTH (Authentic Regional Context)
    "Sakshi_Telugu_AP": "https://www.sakshi.com/rss/andhra-pradesh.xml",
    "Sakshi_Telugu_TS": "https://www.sakshi.com/rss/telangana.xml",
    "The_Hans_India_Hyderabad": "https://www.thehansindia.com/rss/hyderabad.xml", 
    "News18_Telugu_Politics": "https://telugu.news18.com/commonfeeds/v1/tel/rss/politics.xml",
    "The_Hindu_Tamil_Nadu": "https://www.thehindu.com/news/national/tamil-nadu/feeder/default.rss",
    "Daily_Thanthi_Tamil": "https://www.dailythanthi.com/rss/tamilnadu-news.xml",
    "News18_Tamil_Nadu": "https://tamil.news18.com/commonfeeds/v1/tam/rss/tamil-nadu.xml",
    "Deccan_Herald_Karnataka": "https://www.deccanherald.com/feed/rss.xml", 
    "Prajavani_Kannada": "https://www.prajavani.net/feed/rss.xml",
    "Mathrubhumi_Kerala_English": "https://english.mathrubhumi.com/cmlink/mathrubhumi-kerala-1.3323049",
    "OnManorama_Kerala": "https://www.onmanorama.com/news/kerala.rss",
    "Asianet_News_Malayalam": "https://malayalam.asianetnews.com/rss/kerala",

    # 4. THE NORTH, WEST & CENTRAL
    "The_Tribune_Punjab_Haryana": "https://www.tribuneindia.com/rss/feed.aspx?cat_id=27",
    "TOI_Delhi": "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
    "TOI_Uttar_Pradesh": "https://timesofindia.indiatimes.com/rssfeeds/2581104.cms",
    "Mid_Day_Mumbai": "https://www.mid-day.com/Resources/midday/rss/mumbai-news.xml",
    "Divya_Bhaskar_Gujarat": "https://www.divyabhaskar.co.in/rss-feed/1061/",
    "TOI_Pune": "https://timesofindia.indiatimes.com/rssfeeds/-2128821991.cms",
    "The_Telegraph_Kolkata": "https://www.telegraphindia.com/rss/frontpage",
    "TOI_Madhya_Pradesh": "https://timesofindia.indiatimes.com/rssfeeds/2988506.cms",
    "TOI_Assam_Northeast": "https://timesofindia.indiatimes.com/rssfeeds/3404555.cms",

    # 5. SPORTS & ENTERTAINMENT
    "ESPN_Cricinfo_India": "https://www.espncricinfo.com/rss/content/story/feeds/0.xml", 
    "TOI_Sports": "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms",
    "Indian_Express_Sports": "https://indianexpress.com/section/sports/feed/",
    "TOI_Entertainment": "https://timesofindia.indiatimes.com/rssfeeds/1081479906.cms",
    "Indian_Express_Entertainment": "https://indianexpress.com/section/entertainment/feed/",
    "NDTV_Movies": "https://feeds.feedburner.com/ndtvmovies-latest",

    # 6. TECHNOLOGY & STARTUPS
    "Economic_Times_Tech": "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",
    "Gadgets360_Tech": "https://feeds.feedburner.com/ndtvgadgets-latest"
}

def get_dynamic_filepath():
    """Routes data to the correct YYYY/YYYY-MM-DD.json file."""
    now = datetime.utcnow()
    year_folder = now.strftime("%Y")
    date_file = now.strftime("%Y-%m-%d")
    
    # Auto-create the year folder
    os.makedirs(year_folder, exist_ok=True)
    return f"{year_folder}/{date_file}.json"

def fetch_feed(url):
    """Fetches XML with a strict 10-second timeout to prevent stalling."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read()
    except Exception as e:
        print(f"Bypassed {url}: Server timeout or error.")
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
            "total_headlines_captured": 0,
            "feeds": {feed_name: [] for feed_name in TARGET_FEEDS.keys()}
        }
        
    new_additions = 0
    
    for feed_name, url in TARGET_FEEDS.items():
        xml_data = fetch_feed(url)
        if not xml_data:
            continue 
            
        try:
            root = ET.fromstring(xml_data)
            
            # Ensure feed category exists (if added later)
            if feed_name not in archive["feeds"]:
                archive["feeds"][feed_name] = []
                
            existing_ids = [article["id"] for article in archive["feeds"][feed_name]]
            
            for item in root.findall('./channel/item'):
                link = item.find('link').text if item.find('link') is not None else ""
                if not link:
                    continue
                    
                # Cryptographic deduplication
                article_id = hashlib.md5(link.encode('utf-8')).hexdigest()
                
                if article_id not in existing_ids:
                    title = item.find('title').text if item.find('title') is not None else "No Title"
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else "Timestamp Missing"
                    
                    archive["feeds"][feed_name].append({
                        "id": article_id,
                        "title": title,
                        "published_at": pub_date,
                        "url": link
                    })
                    new_additions += 1
        except Exception as e:
            print(f"Parse error on {feed_name}: XML malformed.")

    archive["total_headlines_captured"] += new_additions
    
    # Save cleanly with native UTF-8 support
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(archive, f, indent=4, ensure_ascii=False)
        
    print(f"VEDA Sync Complete: {new_additions} new items appended to {filepath}.")

if __name__ == "__main__":
    update_archive()
