import sqlite3
import os

Se siamo su Render usa il disco persistente /data, altrimenti il file locale sul Mac
DB_PATH = "/data/agenda.db" if os.path.exists("/data") else "agenda.db"

def ottieni_connessione():
return sqlite3.connect(DB_PATH)

def init_db():
conn = ottieni_connessione()
cursor = conn.cursor()

# --- Tabella Agenda ---
cursor.execute('''

CREATE TABLE IF NOT EXISTS eventi (
id INTEGER PRIMARY KEY AUTOINCREMENT,
titolo TEXT NOT NULL,
data_ora TEXT NOT NULL,
descrizione TEXT,
priorita TEXT,
completato INTEGER DEFAULT 0
)
''')

# --- Tabella Spesa ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS spesa_docs (
id INTEGER PRIMARY KEY AUTOINCREMENT,
titolo TEXT NOT NULL,
raw_data TEXT NOT NULL
)
''')

# --- Tabella Misure ---

cursor.execute('''
CREATE TABLE IF NOT EXISTS misure (
id INTEGER PRIMARY KEY AUTOINCREMENT,
prodotto TEXT NOT NULL,
m1_tipo TEXT, m1_val TEXT,
m2_tipo TEXT, m2_val TEXT,
m3_tipo TEXT, m3_val TEXT,
note_extra TEXT
)
''')

# --- Tabella Intrattenimento (Media) ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS intrattenimento (
id INTEGER PRIMARY KEY AUTOINCREMENT,
titolo TEXT NOT NULL,
tipo TEXT NOT NULL,
genere TEXT NOT NULL,
stato TEXT NOT NULL,
voto TEXT

)
''')

# --- Tabella Pomodoro ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS pomodoro_tasks (
id INTEGER PRIMARY KEY AUTOINCREMENT,
compito TEXT NOT NULL,
categoria TEXT NOT NULL,
completato INTEGER DEFAULT 0
)
''')

# --- Tabella Armadio ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS armadio (
id INTEGER PRIMARY KEY AUTOINCREMENT,
capo TEXT NOT NULL,
categoria TEXT NOT NULL,

colore TEXT NOT NULL,
stagione TEXT NOT NULL,
posizione TEXT NOT NULL
)
''')

# --- Tabella Record Allenamento ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS record (
id INTEGER PRIMARY KEY AUTOINCREMENT,
esercizio TEXT NOT NULL,
peso_tempo TEXT NOT NULL,
data TEXT NOT NULL
)
''')

# --- Tabella Schede Allenamento ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS schede (
id INTEGER PRIMARY KEY AUTOINCREMENT,

giorno TEXT NOT NULL,
dettagli_esercizi TEXT NOT NULL
)
''')

# --- Tabella Ricette Cucina ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS ricette (
id INTEGER PRIMARY KEY AUTOINCREMENT,
titolo TEXT NOT NULL,
categoria TEXT NOT NULL,
utensili TEXT NOT NULL,
ingredienti TEXT NOT NULL,
procedimento TEXT NOT NULL
)
''')

conn.commit()
conn.close()

(Assicurati che tutte le funzioni di lettura/scrittura nel tuo database.py utilizzino ottieni_connessione())
