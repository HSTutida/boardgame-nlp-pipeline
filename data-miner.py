import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ==========================================
# 1. SETUP STEALTH BROWSER
# ==========================================
def create_stealth_browser():
    """Initializes and returns a stealthy Chrome webdriver."""
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # UNCOMMENT THIS LINE IF RUNNING IN GOOGLE COLAB OR CLOUD JUPYTER
    # chrome_options.add_argument("--headless") 
    
    # Stealth mode flags to bypass basic bot protection
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    print("Launching master stealth browser...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver

# ==========================================
# 2. GATHER GAMES FROM BROWSE PAGES (PAGINATED)
# ==========================================
def get_games_from_browse_pages(driver, total_games_needed=300):
    """Scrapes the main BGG browse pages across multiple pages to find Game IDs."""
    games = []
    page_number = 1
    
    while len(games) < total_games_needed:
        browse_url = f"https://boardgamegeek.com/browse/boardgame/page/{page_number}"
        print(f"\nScanning browse page {page_number}: {browse_url}")
        driver.get(browse_url)
        
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".collection_table"))
            )
        except Exception:
            print(f"Failed to load page {page_number}. Stopping scan early.")
            break

        game_links = driver.find_elements(By.CSS_SELECTOR, ".collection_objectname a")
        games_added_this_page = 0 
        
        for link in game_links:
            href = link.get_attribute("href")
            if href and "/boardgame/" in href:
                parts = href.split("/")
                try:
                    bg_index = parts.index("boardgame")
                    game_id = parts[bg_index + 1]
                    game_slug = parts[bg_index + 2]
                    
                    game_info = {"id": game_id, "slug": game_slug}
                    if game_info not in games:
                        games.append(game_info)
                        games_added_this_page += 1
                        
                except Exception:
                    continue 
                    
            if len(games) >= total_games_needed:
                break
                
        if games_added_this_page == 0:
            print("No new games found on this page. Reached the end of available lists.")
            break
            
        print(f"Total games collected so far: {len(games)} / {total_games_needed}")
        
        page_number += 1
        time.sleep(2) #Polite delay before turning the page
            
    return games

# ==========================================
# 3. SCRAPE FORUM REVIEWS FOR A SINGLE GAME
# ==========================================
def scrape_game_forum(driver, game_id, game_slug, forum_id=63, max_threads=3):
    """Scrapes full-length reviews from a specific game's forum, sorted by 'Hot/Top'."""
    all_reviews = []
    
    # NEW LOGIC: Appended ?sort=hot to the URL to pull the most popular reviews
    forum_url = f"https://boardgamegeek.com/boardgame/{game_id}/{game_slug}/forums/{forum_id}?sort=hot"
    
    print(f"\n[TARGET: {game_slug.upper()}] Navigating to Top Forums: {forum_url}")
    driver.get(forum_url)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='/thread/']"))
        )
    except Exception:
        print(f"Could not find thread links for {game_slug}. Moving to next game.")
        return []

    link_elements = driver.find_elements(By.CSS_SELECTOR, "a[href^='/thread/']")
    thread_urls = []
    
    for el in link_elements:
        url = el.get_attribute("href")
        if url and "/thread/" in url and "/new" not in url and "#" not in url:
            if url not in thread_urls:
                thread_urls.append(url)
                
    print(f"Found {len(thread_urls)} Hot threads for {game_slug}. Scraping top {max_threads}...")

    for url in thread_urls[:max_threads]:
        driver.get(url)
        try:
            wait_selectors = "article, main, .thread-post, bgg-markdown"
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, wait_selectors))
            )
            time.sleep(2) 
            
            title = "Unknown Title"
            try:
                title = driver.find_element(By.TAG_NAME, "h1").text.strip()
            except Exception:
                pass 
            
            review_elem = driver.find_element(By.CSS_SELECTOR, wait_selectors)
            review_text = review_elem.text.strip()
            
            if review_text:
                all_reviews.append({
                    'Game': game_slug,
                    'Title': title,
                    'Review': review_text,
                    'URL': url
                })
                print(f"  -> Extracted top thread: {title[:30]}...")
                
        except Exception:
            print(f"  -> Failed to read text on thread: {url.split('/')[-1]}")
            
        time.sleep(2) #Polite delay between visiting individual threads

    return all_reviews

# ==========================================
# 4. SAVE DATA TO CSV
# ==========================================
def save_to_csv(reviews, filename):
    """Saves the extracted reviews to a CSV file."""
    if not reviews:
        print(f"No reviews to save for this game.")
        return

    keys = reviews[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(reviews)
        
    print(f"Saved {len(reviews)} top reviews to {filename}")

# ==========================================
# MAIN EXECUTION PIPELINE
# ==========================================
if __name__ == "__main__":
    # --- CONFIGURATION ---
    GAMES_TO_MINE = 5 
    THREADS_PER_GAME = 3 
    # ---------------------
    
    browser = None
    try:
        browser = create_stealth_browser()
        
        # 1. Gather all 300 target games
        target_games = get_games_from_browse_pages(browser, total_games_needed=GAMES_TO_MINE)
        
        # 2. Iterate through the games and mine their forums
        for game in target_games:
            game_id = game['id']
            game_slug = game['slug']
            
            reviews = scrape_game_forum(browser, game_id, game_slug, max_threads=THREADS_PER_GAME)
            
            # Save immediately to prevent data loss on crashes
            if reviews:
                file_name = f"reviews_{game_slug}.csv"
                save_to_csv(reviews, file_name)
                
            print(f"Finished {game_slug}. Resting for 5 seconds before the next game...")
            time.sleep(2)
            
    finally:
        if browser:
            browser.quit()
        print("\nAll tasks complete. Browser closed.")
