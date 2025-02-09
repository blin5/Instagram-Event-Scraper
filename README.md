# Instagram Event Scraper

Uno strumento per estrarre automaticamente i post da pagine Instagram di locali ed eventi.

## 📋 Prerequisiti

- Python 3.8 o superiore
- Google Chrome installato
- Un account Instagram valido

## 🚀 Installazione

1. Clona il repository:
```bash
git clone https://github.com/blin5/Instagram-Event-Scraper.git
cd instagram-event-scraper
```
2. Installa le dipendenze necessarie:
```bash
pip install -r requirements.txt
```

## 💻 Utilizzo

### Interfaccia Grafica

1. Avvia l'interfaccia grafica:
```bash
python frontend.py
```

2. Inserisci le tue credenziali Instagram
3. (Opzionale) Seleziona "Ricorda credenziali" per salvare le tue credenziali
4. (Opzionale) Seleziona "Modalità headless" per eseguire Chrome in background
5. Usa il pulsante "Gestisci Pagine" per configurare le pagine Instagram da monitorare
6. Clicca "Avvia Scraping" per iniziare

### Linea di Comando

Lo script può essere eseguito da riga di comando:

```bash
python ig_event_scraper.py -u <username> -p <password> [--headless]
```

### Parametri
- `-u` o `--username`: Il tuo username Instagram
- `-p` o `--password`: La tua password Instagram
- `--headless`: (Opzionale) Avvia Chrome in modalità headless

## ⚙️ Configurazione

Le pagine Instagram da monitorare possono essere configurate in due modi:
1. Attraverso l'interfaccia grafica usando il pulsante "Gestisci Pagine"
2. Modificando direttamente il file `config.json`

Formato del file `config.json`:
```json
{
    "instagram_pages": [
        "https://www.instagram.com/pagina1/",
        "https://www.instagram.com/pagina2/",
        "..."
    ]
}
```

## 📄 Output

Lo script genererà un file `instagram_posts.txt` contenente:
- URL dei post
- Testo dei post
- Separatori tra i diversi post

## ⚠️ Note
- Lo script potrebbe richiedere alcuni secondi per elaborare ogni pagina
- Assicurati di avere una connessione internet stabile
- Non chiudere il browser Chrome durante l'esecuzione

## 🔒 Privacy e Sicurezza
- Le credenziali vengono utilizzate solo per l'autenticazione su Instagram
- Se si utilizza l'opzione "Ricorda credenziali", queste vengono salvate localmente