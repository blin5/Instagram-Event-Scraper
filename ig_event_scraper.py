from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import os
from dotenv import load_dotenv
import argparse
import sys
import json

def parse_arguments():
    parser = argparse.ArgumentParser(description='Scraper Instagram per eventi')
    parser.add_argument('--username', '-u', help='Username Instagram', required=True)
    parser.add_argument('--password', '-p', help='Password Instagram', required=True)
    parser.add_argument('--headless', action='store_true', help='Avvia Chrome in modalità headless')
    return parser.parse_args()

# Funzione per rifiutare i cookie se viene visualizzata la finestra dei cookie
def refuse_cookies(driver):
    try:
        refuse_button = driver.find_element(By.XPATH, '//button[text()="Rifiuta cookie facoltativi"]')
        refuse_button.click()
        time.sleep(2)  # Attendi il rifiuto dei cookie
    except:
        pass  # Se non appare il bottone dei cookie, non fare nulla


# Funzione per eseguire il login su Instagram (modifica username e password con i tuoi credenziali)
def instagram_login(driver, username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(2)

    # Rifiuta i cookie
    refuse_cookies(driver)
    
    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")
    
    username_input.send_keys(username)
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    
    time.sleep(10)  # Attendi il caricamento della pagina dopo il login

    # non attivare notifiche
    try:
        notify_button = driver.find_element(By.XPATH, '//button[@class="_a9-- _ap36 _a9_1"]')
        notify_button.click()
        time.sleep(2)  # Attendi il rifiuto delle notifiche
    except:
        pass  # Se non appare il bottone, non fare nulla


# Funzione per estrarre i testi degli ultimi 3 post di una pagina Instagram e scriverli su un file
def get_last_three_posts_text(driver, page_url, file):
    driver.get(page_url)
    time.sleep(3)  # Attendi il caricamento della pagina

    # Rifiuta i cookie
    refuse_cookies(driver)

    # Trova i primi 3 post
    posts = driver.find_elements(By.XPATH, '//a[@class="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz _a6hd"]')[:3]
    
    post_texts = []
    for post in posts:
        post_url = post.get_attribute("href")
        post.click()
        time.sleep(3)
        
        # Estrai il testo del post
        try:
            post_text = driver.find_element(By.XPATH, '//h1[@class="_ap3a _aaco _aacu _aacx _aad7 _aade"]').text
        except:
            post_text = "Testo non disponibile"

         # Scrivi il testo e l'URL del post nel file
        file.write(f"Post URL: {post_url}\n")
        file.write(f"Post Text: {post_text}\n")
        file.write("-" * 40 + "\n")  # Separatore per i post
        
        driver.find_element(By.XPATH, '//div[@class="x160vmok x10l6tqk x1eu8d0j x1vjfegm"]').click()
        time.sleep(3)  # Chiudi il dialogo del post

    return post_texts

def main():
    args = parse_arguments()
    sys.stdout.reconfigure(line_buffering=True)
    
    print("\nAvvio Instagram Event Scraper...")
    
    # Carica la configurazione
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            instagram_pages = config.get('instagram_pages', [])
            if not instagram_pages:
                raise ValueError("Nessuna pagina configurata in config.json")
    except FileNotFoundError:
        print("File config.json non trovato!")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Errore nel parsing del file config.json!")
        sys.exit(1)
    except Exception as e:
        print(f"Errore nel caricamento della configurazione: {str(e)}")
        sys.exit(1)

    print(f"Caricate {len(instagram_pages)} pagine da analizzare")
    
    print("Configurazione del browser Chrome...")
    chrome_options = Options()
    chrome_options.add_argument("--disable-search-engine-choice-screen")
    
    if args.headless:
        print("Avvio in modalità headless...")
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)

    try:
        print("\nEffettuo il login su Instagram...")
        instagram_login(driver, args.username, args.password)
        print("Login completato!")

        # Apri un file per scrivere i risultati
        with open("instagram_posts.txt", "w", encoding="utf-8") as file:
            # Estrai i post da ogni pagina
            for i, page in enumerate(instagram_pages, 1):
                print(f"\nAnalisi pagina {i}/{len(instagram_pages)}: {page}")
                sys.stdout.flush()  # Forza il flush dopo ogni messaggio importante
                posts_texts = get_last_three_posts_text(driver, page, file)

    except Exception as e:
        print(f"\nErrore durante l'esecuzione: {str(e)}")
        sys.stdout.flush()
        raise e
    finally:
        print("\nChiusura del browser...")
        driver.quit()
        print("Browser chiuso correttamente")
        sys.stdout.flush()

    print("\nScraping completato! I risultati sono stati salvati in 'instagram_posts.txt'")
    sys.stdout.flush()

if __name__ == "__main__":
    main()

