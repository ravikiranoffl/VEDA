import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import hashlib
import asyncio
import aiohttp
import trafilatura
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from email.utils import parsedate_to_datetime
from huggingface_hub import HfApi, hf_hub_download

# CONFIGURATION
HF_REPO_ID = "ravikiranoffl/HEDA"
HF_TOKEN = os.environ.get("HF_TOKEN")

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
    return datetime.now(timezone(timedelta(hours=5, minutes=30)))

def clean_url(url):
    parsed = urlparse(url)
    qd = [q for q in parse_qsl(parsed.query) if not q[0].startswith('utm_')]
    return urlunparse(parsed._replace(query=urlencode(qd)))

async def fetch_full_text(session, url, art_id, sem):
    async with sem:
        try:
            async with session.get(url, timeout=15) as resp:
                html = await resp.text()
                content = trafilatura.extract(html)
                await asyncio.sleep(1) 
                return art_id, content
        except: return art_id, None

async def process_deep_archive(new_articles):
    sem = asyncio.Semaphore(5)
    async with aiohttp.ClientSession(headers={'User-Agent': 'VEDA-Bot/2.0'}) as session:
        tasks = [fetch_full_text(session, a['url'], a['id'], sem) for a in new_articles]
        return dict(await asyncio.gather(*tasks))

def veda_engine():
    now = get_ist_time()
    date_str = now.strftime("%Y-%m-%d")
    folder = now.strftime("%Y")
    os.makedirs(folder, exist_ok=True)
    
    idx_path = f"{folder}/{date_str}.json"
    archive = json.load(open(idx_path)) if os.path.exists(idx_path) else {"date":date_str, "feeds":{}}
    
    new_for_deep = []
    status = {}

    for name, url in TARGET_FEEDS.items():
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'VEDA-Bot'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                root = ET.fromstring(resp.read())
                items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
                if not items: status[name]=0; continue
                
                status[name]=1
                if name not in archive["feeds"]: archive["feeds"][name] = []
                uids = {a["id"] for a in archive["feeds"][name]}

                for it in items:
                    link = clean_url(it.find('link').text or it.find('link').get('href'))
                    aid = hashlib.md5(link.encode()).hexdigest()
                    if aid not in uids:
                        title = it.find('title').text
                        pdt = it.find('pubDate').text if it.find('pubDate') is not None else "N/A"
                        obj = {"id":aid, "title":title, "url":link, "published_at":pdt}
                        archive["feeds"][name].append(obj)
                        new_for_deep.append(obj)
                
                archive["feeds"][name].sort(key=lambda x: x.get('published_at'), reverse=True)
                archive["feeds"][name] = archive["feeds"][name][:250]
        except: status[name]=0

    # Save Grid Index (Minified)
    json.dump(archive, open(idx_path, 'w'), separators=(',', ':'))
    
    # Update Status
    st_path = "status.json"
    st_data = json.load(open(st_path)) if os.path.exists(st_path) else []
    st_data.append({"run_time_ist": now.strftime("%Y-%m-%d %H:%M:%S"), "status": status})
    json.dump(st_data[-100:], open(st_path, 'w'), indent=4)

    # DEEP ARCHIVE (HEDA)
    if new_for_deep and HF_TOKEN:
        deep_map = asyncio.run(process_deep_archive(new_for_deep))
        api = HfApi(token=HF_TOKEN)
        deep_fn = f"data/{date_str}-deep.json"
        
        try:
            d_path = hf_hub_download(repo_id=HF_REPO_ID, filename=deep_fn, repo_type="dataset")
            current_deep = json.load(open(d_path))
        except: current_deep = {}
        
        current_deep.update({k: v for k, v in deep_map.items() if v})
        tmp_p = f"/tmp/{date_str}.json"
        json.dump(current_deep, open(tmp_p, 'w'), separators=(',', ':'))
        api.upload_file(path_or_fileobj=tmp_p, path_in_repo=deep_fn, repo_id=HF_REPO_ID, repo_type="dataset")

if __name__ == "__main__":
    veda_engine()
