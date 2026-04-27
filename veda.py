import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import hashlib
from datetime import datetime, timezone, timedelta

# ==========================================
# VEDA ULTIMATE TARGET MATRIX 
# ==========================================
TARGET_FEEDS = {
    # --- INDIA: NATIONAL CORE ---
    "Google_News_India": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "The_Hindu_National": "https://www.thehindu.com/news/national/feeder/default.rss",
    "Times_of_India_National": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "Indian_Express_National": "https://indianexpress.com/section/india/feed/",
    "NDTV_Latest": "https://feeds.feedburner.com/ndtvnews-latest",
    "News18_National": "https://www.news18.com/commonfeeds/v1/eng/rss/india.xml",

    # --- INDIA: FINANCIAL MARKETS ---
    "Moneycontrol_Markets": "https://www.moneycontrol.com/rss/marketreports.xml",
    "Moneycontrol_Commodities": "https://www.moneycontrol.com/rss/commodities.xml",
    "LiveMint_Markets": "https://www.livemint.com/rss/markets",
    "Economic_Times_Markets": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "Financial_Express_Economy": "https://www.financialexpress.com/economy/feed/",

    # --- TELUGU HEAVYWEIGHTS ---
    "Namasthe_Telangana": "https://www.ntnews.com/feed",
    "NTV_Telugu": "https://ntvtelugu.com/feed",
    "10TV_Telugu": "https://10tv.in/feed",
    "ABP_Desam_Telugu": "https://telugu.abplive.com/home/feed",
    "V6_Velugu_TS": "https://www.v6velugu.com/feed",

    # --- INDIA: SOUTH ---
    "The_Hindu_Tamil_Nadu": "https://www.thehindu.com/news/national/tamil-nadu/feeder/default.rss",
    "The_Hindu_Karnataka": "https://www.thehindu.com/news/national/karnataka/feeder/default.rss",
    "The_Hindu_Kerala": "https://www.thehindu.com/news/national/kerala/feeder/default.rss",
    "Indian_Express_Bangalore": "https://indianexpress.com/section/cities/bangalore/feed/",
    "Indian_Express_Chennai": "https://indianexpress.com/section/cities/chennai/feed/",

    # --- INDIA: NORTH ---
    "The_Hindu_Delhi": "https://www.thehindu.com/news/cities/Delhi/feeder/default.rss",
    "Indian_Express_Lucknow": "https://indianexpress.com/section/cities/lucknow/feed/",
    "Indian_Express_Chandigarh": "https://indianexpress.com/section/cities/chandigarh/feed/",
    "Kashmir_Observer": "https://kashmirobserver.net/feed/",

    # --- INDIA: WEST & CENTRAL ---
    "Mid_Day_Mumbai": "https://www.mid-day.com/Resources/midday/rss/mumbai-news.xml",
    "Indian_Express_Mumbai": "https://indianexpress.com/section/cities/mumbai/feed/",
    "Indian_Express_Pune": "https://indianexpress.com/section/cities/pune/feed/",
    "Indian_Express_Ahmedabad": "https://indianexpress.com/section/cities/ahmedabad/feed/",

    # --- INDIA: EAST & NORTHEAST ---
    "Indian_Express_Kolkata": "https://indianexpress.com/section/cities/kolkata/feed/",

    # --- SPECIALIZED ---
    "ESPN_Cricinfo_India": "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",
    "Economic_Times_Tech": "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",

    # ==========================================
    # GLOBAL CONTINENTS
    # ==========================================
    "NYT_USA_Top": "https://rss.nytimes.com/services/xml/rss/nyt/US.xml",
    "NPR_News_USA": "https://feeds.npr.org/1001/rss.xml",
    "PBS_NewsHour": "https://www.pbs.org/newshour/feeds/rss/headlines",
    "Washington_Post_World": "https://feeds.washingtonpost.com/rss/world",
    "CBC_Canada_Top": "https://www.cbc.ca/cmlink/rss-topstories",
    "Los_Angeles_Times": "https://www.latimes.com/world-nation/rss2.0.xml",
    "MercoPress_LatAm": "https://en.mercopress.com/rss",
    "BBC_Latin_America": "https://feeds.bbci.co.uk/news/world/latin_america/rss.xml",
    "Rio_Times_Brazil": "https://riotimesonline.com/feed/",
    "Havana_Times": "https://havanatimes.org/feed/",
    "BBC_Europe": "https://feeds.bbci.co.uk/news/world/europe/rss.xml",
    "The_Guardian_Europe": "https://www.theguardian.com/europe/rss",
    "France24_Europe": "https://www.france24.com/en/europe/rss",
    "Independent_UK": "https://www.independent.co.uk/news/world/europe/rss",
    "Sky_News_UK": "https://feeds.skynews.com/feeds/rss/home.xml",
    "RTE_Ireland": "https://www.rte.ie/news/rss/news-headlines.xml",
    "AllAfrica_Top": "https://allafrica.com/tools/headlines/rdf/africa/headlines.rdf",
    "BBC_Africa": "https://feeds.bbci.co.uk/news/world/africa/rss.xml",
    "News24_South_Africa": "https://feeds.news24.com/articles/news24/TopStories/rss",
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
    "Sydney_Morning_Herald": "https://www.smh.com.au/rss/feed.xml",
    "The_Age_Melbourne": "https://www.theage.com.au/rss/feed.xml",
    "RNZ_New_Zealand": "https://www.rnz.co.nz/rss/national.xml",
    "News_com_au": "https://www.news.com.au/content-feeds/latest-news-national/"
}

def get_ist_time():
    """Helper function to always get the current time in IST (UTC+5:30)"""
    ist_timezone = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist_timezone)

def get_dynamic_filepath():
    now = get_ist_time()
    year_folder = now.strftime("%Y")
    date_file = now.strftime("%Y-%m-%d")
    os.makedirs(year_folder, exist_ok=True)
    return f"{year_folder}/{date_file}.json"

def fetch_feed(url):
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
    except Exception:
        return None

def update_archive():
    filepath = get_dynamic_filepath()

    # 1. Load Daily Archive
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            archive = json.load(f)
    else:
        archive = {
            "date": get_ist_time().strftime("%Y-%m-%d"),
            "total_headlines": 0,
            "feeds": {} # Start completely empty!
        }

    # 2. Load Telemetry File (status.json)
    status_filepath = "status.json"
    if os.path.exists(status_filepath):
        with open(status_filepath, 'r', encoding='utf-8') as f:
            telemetry = json.load(f)
    else:
        telemetry = []

    new_items_total = 0
    current_run_status = {} # Will hold 1 or 0 for each feed

    for feed_name, url in TARGET_FEEDS.items():
        xml_data = fetch_feed(url)

        if not xml_data: 
            current_run_status[feed_name] = 0 # 0 = Dead/Empty
            continue

        try:
            root = ET.fromstring(xml_data)

            # Check if feed actually has articles
            items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
            if len(items) == 0:
                current_run_status[feed_name] = 0 # 0 = Alive, but Zero News
                continue

            current_run_status[feed_name] = 1 # 1 = Success! News Found.

            if feed_name not in archive["feeds"]:
                archive["feeds"][feed_name] = []

            existing_ids = {art["id"] for art in archive["feeds"][feed_name]}

            for item in items:
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
                    new_items_total += 1

        except Exception:
            current_run_status[feed_name] = 0 # 0 = Fake HTML / XML Crash
            continue

    archive["total_headlines"] += new_items_total

    # ZERO-WASTE CLEANUP: Remove any feeds that still ended up with 0 items
    archive["feeds"] = {k: v for k, v in archive["feeds"].items() if len(v) > 0}

    # Save the clean Daily Data
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(archive, f, indent=4, ensure_ascii=False)

    # --- SAVE TELEMETRY (status.json) ---
    # Log this exact run with a timestamp
    telemetry_entry = {
        "run_time_ist": get_ist_time().strftime("%Y-%m-%d %H:%M:%S"),
        "status": current_run_status
    }
    telemetry.append(telemetry_entry)

    # Keep only the last 100 runs so the file doesn't crash your editor
    telemetry = telemetry[-100:] 

    with open(status_filepath, 'w', encoding='utf-8') as f:
        json.dump(telemetry, f, indent=4, ensure_ascii=False)

    print(f"\nVEDA Sync Complete: {new_items_total} new items.")
    print("Telemetry logged to status.json")

if __name__ == "__main__":
    update_archive()
