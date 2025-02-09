import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
from threading import Thread
import sys
import os
import signal
import json
from tkinter import BooleanVar

class PagesDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Gestione Pagine Instagram")
        self.dialog.geometry("600x400")
        
        # Area di testo per le pagine
        self.text_area = scrolledtext.ScrolledText(self.dialog, width=70, height=20)
        self.text_area.pack(padx=10, pady=10)
        
        # Carica le pagine esistenti
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                pages = config.get('instagram_pages', [])
                self.text_area.insert('1.0', '\n'.join(pages))
        except FileNotFoundError:
            pass
        
        # Pulsanti
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Salva", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Annulla", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Istruzioni
        ttk.Label(self.dialog, text="Inserisci un URL per riga").pack(pady=5)
    
    def save(self):
        pages = [page.strip() for page in self.text_area.get('1.0', tk.END).splitlines() if page.strip()]
        try:
            with open('config.json', 'w') as f:
                json.dump({'instagram_pages': pages}, f, indent=4)
            messagebox.showinfo("Successo", "Pagine salvate correttamente!")
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel salvare le pagine: {str(e)}")

class InstagramScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Event Scraper")
        self.root.geometry("510x470")  # Aumentata l'altezza per il nuovo checkbox
        
        # Variabili di stato
        self.process = None
        self.is_running = False
        self.credentials_file = "credentials.json"
        
        # Stile
        self.style = ttk.Style()
        self.style.configure('TButton', padding=5)
        self.style.configure('TLabel', padding=5)
        
        # Frame principale
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Credenziali
        ttk.Label(main_frame, text="Username Instagram:").grid(row=0, column=0, sticky=tk.W)
        self.username = ttk.Entry(main_frame, width=40)
        self.username.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(main_frame, text="Password Instagram:").grid(row=1, column=0, sticky=tk.W)
        self.password = ttk.Entry(main_frame, width=40, show="*")
        self.password.grid(row=1, column=1, padx=5, pady=5)

        # Checkbox per modalità headless
        self.headless_mode = BooleanVar(value=False)
        self.headless_checkbox = ttk.Checkbutton(
            main_frame, 
            text="Modalità headless (Chrome nascosto)",
            variable=self.headless_mode
        )
        self.headless_checkbox.grid(row=2, column=0, pady=5)
        
        # Checkbox per ricordare le credenziali
        self.remember_credentials = BooleanVar(value=False)
        self.remember_checkbox = ttk.Checkbutton(
            main_frame, 
            text="Ricorda credenziali",
            variable=self.remember_credentials,
            command=self.handle_remember_credentials
        )
        self.remember_checkbox.grid(row=2, column=1, pady=5)
        
        # Frame per i pulsanti
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        # Pulsante per avviare lo scraping
        self.scrape_button = ttk.Button(button_frame, text="Avvia Scraping", 
                                      command=self.start_scraping)
        self.scrape_button.pack(side=tk.LEFT, padx=5)
        
        # Pulsante per fermare lo scraping
        self.stop_button = ttk.Button(button_frame, text="Ferma Scraping", 
                                    command=self.stop_scraping, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Pulsante per aprire il file dei risultati
        self.view_results_button = ttk.Button(button_frame, text="Visualizza Risultati", 
                                            command=self.open_results, state='disabled')
        self.view_results_button.pack(side=tk.LEFT, padx=5)

        # Aggiungi pulsante per gestire le pagine nel menu
        ttk.Button(button_frame, text="Gestisci Pagine", 
                  command=self.open_pages_dialog).pack(side=tk.LEFT,pady=5)
        
        # Area di log
        ttk.Label(main_frame, text="Log:").grid(row=5, column=0, sticky=tk.W)
        self.log_area = scrolledtext.ScrolledText(main_frame, width=60, height=15)
        self.log_area.grid(row=6, column=0, columnspan=2, pady=5)
        
        # # Barra di progresso
        # self.progress = ttk.Progressbar(main_frame, length=400, mode='indeterminate')
        # self.progress.grid(row=7, column=0, columnspan=2, pady=10)

        # Carica le credenziali salvate all'avvio
        self.load_credentials()

    def handle_remember_credentials(self):
        if self.remember_credentials.get():
            self.save_credentials()
        else:
            self.delete_credentials()

    def save_credentials(self):
        credentials = {
            "username": self.username.get(),
            "password": self.password.get()
        }
        try:
            with open(self.credentials_file, 'w') as f:
                json.dump(credentials, f)
            self.log_area.insert(tk.END, "Credenziali salvate con successo\n")
        except Exception as e:
            self.log_area.insert(tk.END, f"Errore nel salvare le credenziali: {str(e)}\n")

    def load_credentials(self):
        try:
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, 'r') as f:
                    credentials = json.load(f)
                self.username.insert(0, credentials.get("username", ""))
                self.password.insert(0, credentials.get("password", ""))
                self.remember_credentials.set(True)
                self.log_area.insert(tk.END, "Credenziali caricate con successo\n")
        except Exception as e:
            self.log_area.insert(tk.END, f"Errore nel caricare le credenziali: {str(e)}\n")

    def delete_credentials(self):
        try:
            if os.path.exists(self.credentials_file):
                os.remove(self.credentials_file)
                self.log_area.insert(tk.END, "Credenziali rimosse con successo\n")
        except Exception as e:
            self.log_area.insert(tk.END, f"Errore nella rimozione delle credenziali: {str(e)}\n")

    def start_scraping(self):
        if not self.username.get() or not self.password.get():
            self.log_area.insert(tk.END, "Errore: Inserisci username e password\n")
            return
        
        # Salva le credenziali se l'opzione è selezionata
        if self.remember_credentials.get():
            self.save_credentials()
        
        self.scrape_button.configure(state='disabled')
        self.stop_button.configure(state='normal')
        self.progress.start()
        self.log_area.insert(tk.END, "Avvio scraping...\n")
        self.is_running = True
        
        Thread(target=self.run_scraper).start()

    def stop_scraping(self):
        if self.process:
            self.is_running = False
            if sys.platform == "win32":
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.process.pid)])
            else:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            
            self.log_area.insert(tk.END, "\nProcesso interrotto dall'utente\n")
            self.progress.stop()
            self.scrape_button.configure(state='normal')
            self.stop_button.configure(state='disabled')
            self.process = None

    def run_scraper(self):
        try:
            command = [
                sys.executable,
                '-u',  # Aggiunge modalità unbuffered per Python
                'ig_event_scraper.py',
                '-u', self.username.get(),
                '-p', self.password.get()
            ]
            
            if self.headless_mode.get():
                command.extend(['--headless'])
            
            # Imposta l'ambiente per forzare l'output unbuffered
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            
            if sys.platform == "win32":
                self.process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                    bufsize=1,
                    universal_newlines=True,
                    env=env
                )
            else:
                self.process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    preexec_fn=os.setsid,
                    bufsize=1,
                    universal_newlines=True,
                    env=env
                )
            
            # Leggi l'output in tempo reale
            while self.is_running:
                output = self.process.stdout.readline()
                if output:
                    self.log_area.insert(tk.END, output)
                    self.log_area.see(tk.END)
                    self.root.update()
                
                if self.process.poll() is not None:
                    break
            
            if self.is_running:  # Se il processo è terminato naturalmente
                # Leggi eventuali output rimanenti
                remaining_output, stderr = self.process.communicate()
                if remaining_output:
                    self.log_area.insert(tk.END, remaining_output)
                if stderr:
                    self.log_area.insert(tk.END, "Errori:\n" + stderr + "\n")
                
                if self.process.returncode == 0:
                    self.log_area.insert(tk.END, "Scraping completato con successo!\n")
                    self.view_results_button.configure(state='normal')
                else:
                    self.log_area.insert(tk.END, "Errore durante lo scraping\n")
                
                # Forza l'aggiornamento finale dell'interfaccia
                self.log_area.see(tk.END)
                self.root.update()
        
        except Exception as e:
            self.log_area.insert(tk.END, f"Errore: {str(e)}\n")
            self.log_area.see(tk.END)
            self.root.update()
        
        finally:
            self.progress.stop()
            self.scrape_button.configure(state='normal')
            self.stop_button.configure(state='disabled')
            self.is_running = False

    def open_results(self):
        if os.path.exists("instagram_posts.txt"):
            if sys.platform == "win32":
                os.startfile("instagram_posts.txt")
            else:
                subprocess.call(["xdg-open", "instagram_posts.txt"])
        else:
            self.log_area.insert(tk.END, "File dei risultati non trovato\n")

    def open_pages_dialog(self):
        PagesDialog(self.root)

def main():
    root = tk.Tk()
    app = InstagramScraperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 