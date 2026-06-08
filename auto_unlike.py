from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import msvcrt 

# --- CONFIGURE YOUR SETTINGS HERE (Editable on the fly via notepad) ---
COOLDOWN_POSTS_COUNT = 50       
COOLDOWN_WAIT_TIME = 2         
POST_LOAD_MAX_WAIT = 4         
GRID_RETURN_WAIT = 4           # Post-navigation baseline recovery wait time
# -----------------------------------------------------------------------

options = Options()
options.add_experimental_option("detach", True)
options.add_argument("--start-maximized")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 5)

LIKES_PAGE_URL = "https://www.instagram.com/your_activity/interactions/likes/"
LAST_MODIFIED_TIME = os.path.getmtime(__file__)

driver.get("https://www.instagram.com/")
print(">>> Log in manually, go to Settings > Your Activity > Interactions > Likes, then press Enter...")
input()
time.sleep(3)

def check_for_notepad_updates():
    global LAST_MODIFIED_TIME, COOLDOWN_POSTS_COUNT, COOLDOWN_WAIT_TIME, POST_LOAD_MAX_WAIT, GRID_RETURN_WAIT
    try:
        current_mod_time = os.path.getmtime(__file__)
        if current_mod_time > LAST_MODIFIED_TIME:
            print("\n[+] Notepad change detected! Hot-swapping configuration dynamically...")
            LAST_MODIFIED_TIME = current_mod_time
            with open(__file__, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if "COOLDOWN_POSTS_COUNT =" in line and not line.startswith("def"):
                        COOLDOWN_POSTS_COUNT = int(line.split("=")[1].split("#")[0].strip())
                    if "COOLDOWN_WAIT_TIME =" in line and not line.startswith("def"):
                        COOLDOWN_WAIT_TIME = float(line.split("=")[1].split("#")[0].strip())
                    if "POST_LOAD_MAX_WAIT =" in line and not line.startswith("def"):
                        POST_LOAD_MAX_WAIT = float(line.split("=")[1].split("#")[0].strip())
                    if "GRID_RETURN_WAIT =" in line and not line.startswith("def"):
                        GRID_RETURN_WAIT = float(line.split("=")[1].split("#")[0].strip())
            print(f"[~] Updated Rules -> Break Every: {COOLDOWN_POSTS_COUNT} posts | Wait: {COOLDOWN_WAIT_TIME}s")
    except Exception:
        pass

def trigger_browser_reload():
    print("[!] Triggering browser reload (top-left refresh button)...")
    try:
        driver.refresh()
        time.sleep(5)  
    except Exception as e:
        print(f"Failed to refresh browser: {e}")

def check_and_close_messages():
    """Strict check to ensure it ONLY triggers if a real message container overlay is present."""
    try:
        # Targets the specific message/chat wrapper overlay element on Instagram desktop
        message_box_present = driver.find_elements(By.XPATH, "//div[contains(@style, 'bottom: 0') or contains(@class, 'x10l6tqk')]//div[@role='button']//*[local-name()='svg' and @aria-label='Close']")
        
        if message_box_present:
            print("[!] Verified message overlay window is open. Clicking the cross button to close it...")
            message_box_present[0].click()
            time.sleep(2)
            return True
    except Exception:
        pass
    return False

def check_for_failed_to_load():
    try:
        failed_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Failed to load') or contains(text(), 'failed to load')]")
        if failed_elements:
            print("[!] 'Failed to load' detected on the page grid. Reloading...")
            trigger_browser_reload()
            return True
    except Exception:
        pass
    return False

def navigate_from_homepage_to_likes():
    try:
        print("[*] Attempting UI navigation from Homepage to Likes...")
        more_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'More')] | //div[@role='button']//span[text()='More'] | //*[local-name()='svg' and @aria-label='Settings']")))
        more_btn.click()
        time.sleep(2)
        your_activity_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Your activity')]")))
        your_activity_btn.click()
        time.sleep(4)
        try:
            interactions_btn = driver.find_element(By.XPATH, "//span[contains(text(),'Interactions')]")
            interactions_btn.click()
            time.sleep(1.5)
        except Exception:
            pass
        likes_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Likes')]")))
        likes_btn.click()
        print("[+] Navigated back via sidebar!")
        time.sleep(3)
    except Exception as e:
        driver.get(LIKES_PAGE_URL)
        time.sleep(5)

def ensure_on_likes_grid():
    current_url = driver.current_url.rstrip('/')
    target_url = LIKES_PAGE_URL.rstrip('/')
    if current_url == "https://www.instagram.com" or current_url == "https://www.instagram.com/":
        navigate_from_homepage_to_likes()
    elif target_url not in current_url:
        driver.get(LIKES_PAGE_URL)
        time.sleep(5)

def check_for_interrupt_signal():
    if msvcrt.kbhit():
        key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
        if key == 'p':
            print("\n========================================================")
            print("[PAUSED] Loop interrupted safely by user keypress.")
            print(">>> You can now make deeper changes in Notepad and Save.")
            print(">>> Press '1' + Enter in this window to RESTART unliking.")
            print(">>> Press Enter (or any other key) to CLOSE entirely.")
            print("========================================================")
            choice = input("Your choice: ").strip()
            if choice == '1':
                print("[+] Clearing buffer and restarting loop sequence...")
                time.sleep(1)
                return "restart"
            else:
                return "exit"
    return "continue"

def unlike_all():
    print("Starting to unlike... (Press 'P' in this window at any time to pause/restart)")
    unliked = 0
    
    while True:
        try:
            status = check_for_interrupt_signal()
            if status == "restart":
                unliked = 0 
                continue
            elif status == "exit":
                break
                
            check_for_notepad_updates()
            
            # --- PHASE 1: SAFETY & NAVIGATION CHECKS ---
            ensure_on_likes_grid()
            check_and_close_messages()
            check_for_failed_to_load()
            
            try:
                grid_wait = WebDriverWait(driver, POST_LOAD_MAX_WAIT)
                posts = grid_wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@role='button']//img")))
            except Exception:
                posts = driver.find_elements(By.XPATH, "//div[@role='button']//img")
            
            if not posts:
                print("[~] Grid empty. Waiting 5 seconds safety buffer...")
                time.sleep(5)
                posts = driver.find_elements(By.XPATH, "//div[@role='button']//img")
                if not posts:
                    print("\n[!] No posts remaining. Loop cycle finished.")
                    break 
                
            print(f"Opening next post...")
            posts[0].click()  
            time.sleep(4)     
            
            # --- PHASE 2: UNLIKING THE POST ---
            try:
                unlike_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(@aria-label,'Unlike') or contains(@aria-label,'unlike')]")))
                unlike_btn.click()
                unliked += 1
                print(f"Unliked {unliked} posts so far...")
                
                if unliked > 0 and unliked % COOLDOWN_POSTS_COUNT == 0:
                    print(f"[!] Hit milestone. Resting for {COOLDOWN_WAIT_TIME} seconds...")
                    time.sleep(COOLDOWN_WAIT_TIME)
                else:
                    time.sleep(1)
            except Exception:
                print("Could not find 'Unlike' button (Skipping).")
            
            # --- PHASE 3: THE RETURN TRANSITION ---
            print("Going back to the Likes grid...")
            driver.back()
            
            print(f"[~] Waiting {GRID_RETURN_WAIT} seconds for the grid interface to render completely...")
            time.sleep(GRID_RETURN_WAIT) 
            
        except Exception as e:
            if "Max retries exceeded" in str(e) or "target machine actively refused it" in str(e):
                print("\n[CRITICAL] Browser disconnected.")
                break
            trigger_browser_reload()
            continue

unlike_all()
try:
    driver.quit()
except Exception:
    pass