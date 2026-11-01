import sqlite3
import os

Configurazione del percorso sul disco persistente di Render o in locale sul Mac
DB_PATH = "/data/agenda.db" if os.path.exists("/data") else "agenda.db"

def ottieni_connessione():
return sqlite3.connect(DB_PATH)

def init_db():
conn = ottieni_connessione()
cursor = conn.cursor()

# Agenda
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

# Spesa
cursor.execute('''
CREATE TABLE IF NOT EXISTS spesa_docs (
id INTEGER PRIMARY KEY AUTOINCREMENT,

titolo TEXT NOT NULL,
raw_data TEXT NOT NULL
)
''')

# Misure
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

# Intrattenimento / Media (Film e Serie TV) - Senza limiti di inserimento
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

# Pomodoro
cursor.execute('''
CREATE TABLE IF NOT EXISTS pomodoro_tasks (
id INTEGER PRIMARY KEY AUTOINCREMENT,
compito TEXT NOT NULL,
categoria TEXT NOT NULL,
completato INTEGER DEFAULT 0
)
''')


# Armadio
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

# Record Allenamento
cursor.execute('''
CREATE TABLE IF NOT EXISTS record (
id INTEGER PRIMARY KEY AUTOINCREMENT,
esercizio TEXT NOT NULL,
peso_tempo TEXT NOT NULL,
data TEXT NOT NULL

)
''')

# Schede Allenamento
cursor.execute('''
CREATE TABLE IF NOT EXISTS schede (
id INTEGER PRIMARY KEY AUTOINCREMENT,
giorno TEXT NOT NULL,
dettagli_esercizi TEXT NOT NULL
)
''')

# Ricette Cucina
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

--- Funzioni di Gestione Intrattenimento (Media) ---
def aggiungi_intrattenimento(titolo, tipo, genere, stato, voto):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("INSERT INTO intrattenimento (titolo, tipo, genere, stato, voto) VALUES (?, ?, ?, ?, ?)",
(titolo, tipo, genere, stato, voto))
conn.commit()

conn.close()

def ottieni_intrattenimento():
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("SELECT * FROM intrattenimento ORDER BY id DESC")
data = cursor.fetchall()
conn.close()
return data

def modifica_intrattenimento(item_id, titolo, tipo, genere, stato, voto):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("UPDATE intrattenimento SET titolo=?, tipo=?, genere=?, stato=?, voto=? WHERE id=?",
(titolo, tipo, genere, stato, voto, item_id))
conn.commit()

conn.close()

def elimina_intrattenimento(item_id):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("DELETE FROM intrattenimento WHERE id=?", (item_id,))
conn.commit()
conn.close()

(Funzioni di utilità per le altre tabelle)
def ottieni_eventi():
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("SELECT * FROM eventi ORDER BY id DESC")
d = cursor.fetchall()

conn.close()
return d

def aggiungi_evento(titolo, data_ora, descrizione, priorita):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("INSERT INTO eventi (titolo, data_ora, descrizione, priorita) VALUES (?, ?, ?, ?)", (titolo, data_ora, descrizione, priorita))
conn.commit()
conn.close()

def modifica_evento(evento_id, titolo, data_ora, descrizione, priorita):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("UPDATE eventi SET titolo=?, data_ora=?, descrizione=?, priorita=? WHERE id=?", (titolo, data_ora, descrizione, priorita, 

evento_id))
conn.commit()
conn.close()

def elimina_evento(evento_id):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("DELETE FROM eventi WHERE id=?", (evento_id,))
conn.commit()
conn.close()

def toggle_completato(evento_id):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("UPDATE eventi T SET completato = CASE WHEN completato = 1 THEN 0 ELSE 1 END WHERE id=?", (evento_id,))
conn.commit()
conn.close()


def ottieni_documenti_spesa():
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("SELECT * FROM spesa_docs ORDER BY id DESC")
d = cursor.fetchall()
conn.close()
return d

def aggiungi_documento_spesa(titolo, raw):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("INSERT INTO spesa_docs (titolo, raw_data) VALUES (?, ?)", (titolo, raw))
conn.commit()
conn.close()

def modifica_documento_spesa(sid, titolo, raw):
conn = ottieni_connessione()

cursor = conn.cursor()
cursor.execute("UPDATE spesa_docs SET titolo=?, raw_data=? WHERE id=?", (titolo, raw, sid))
conn.commit()
conn.close()

def elimina_documento_spesa(sid):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("DELETE FROM spesa_docs WHERE id=?", (sid,))
conn.commit()
conn.close()

def ottieni_misure():
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("SELECT * FROM misure ORDER BY id DESC")

d = cursor.fetchall()
conn.close()
return d

def aggiungi_misura(p, m1t, m1v, m2t, m2v, m3t, m3v, note):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("INSERT INTO misure (prodotto, m1_tipo, m1_val, m2_tipo, m2_val, m3_tipo, m3_val, note_extra) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (p, m1t, m1v, m2t, m2v, m3t, m3v, note))
conn.commit()
conn.close()

def modifica_misura(mid, p, m1t, m1v, m2t, m2v, m3t, m3v, note):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("UPDATE misure SET prodotto=?, 

m1_tipo=?, m1_val=?, m2_tipo=?, m2_val=?, m3_tipo=?, m3_val=?, note_extra=? WHERE id=?", (p, m1t, m1v, m2t, m2v, m3t, m3v, note, mid))
conn.commit()
conn.close()

def elimina_misura(mid):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("DELETE FROM misure WHERE id=?", (mid,))
conn.commit()
conn.close()

def ottieni_pomodoro_tasks():
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("SELECT * FROM pomodoro_tasks ORDER BY id DESC")
d = cursor.fetchall()

conn.close()
return d

def aggiungi_pomodoro_task(c, cat):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("INSERT INTO pomodoro_tasks (compito, categoria) VALUES (?, ?)", (c, cat))
conn.commit()
conn.close()

def toggle_pomodoro_task(tid):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("UPDATE pomodoro_tasks SET completato = CASE WHEN completato = 1 THEN 0 ELSE 1 END WHERE id=?", (tid,))
conn.commit()
conn.close()

def elimina_pomodoro_task(tid):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("DELETE FROM pomodoro_tasks WHERE id=?", (tid,))
conn.commit()
conn.close()

def elimina_completati_pomodoro():
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("DELETE FROM pomodoro_tasks WHERE completato = 1")
conn.commit()
conn.close()

def ottieni_armadio():
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("SELECT * FROM armadio 

ORDER BY id DESC")
d = cursor.fetchall()
conn.close()
return d

def aggiungi_capo(capo, cat, col, stag, pos):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("INSERT INTO armadio (capo, categoria, colore, stagione, posizione) VALUES (?, ?, ?, ?, ?)", (capo, cat, col, stag, pos))
conn.commit()
conn.close()

def elimina_capo(cid):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("DELETE FROM armadio WHERE id=?", (cid,))
conn.commit()

conn.close()

def ottieni_record():
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("SELECT * FROM record ORDER BY id DESC")
d = cursor.fetchall()
conn.close()
return d

def aggiungi_record(es, pt, data):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("INSERT INTO record (esercizio, peso_tempo, data) VALUES (?, ?, ?)", (es, pt, data))
conn.commit()
conn.close()

def elimina_record(rid):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("DELETE FROM record WHERE id=?", (rid,))
conn.commit()
conn.close()

def ottieni_schede_allenamento():
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("SELECT * FROM schede ORDER BY id DESC")
d = cursor.fetchall()
conn.close()
return d

def aggiungi_scheda_allenamento(giorno, det):
conn = ottieni_connessione()
cursor = conn.cursor()

cursor.execute("INSERT INTO schede (giorno, dettagli_esercizi) VALUES (?, ?)", (giorno, det))
conn.commit()
conn.close()

def modifica_scheda_allenamento(sid, giorno, det):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("UPDATE schede SET giorno=?, dettagli_esercizi=? WHERE id=?", (giorno, det, sid))
conn.commit()
conn.close()

def elimina_scheda_allenamento(sid):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("DELETE FROM schede WHERE id=?", (sid,))

conn.close()

def ottieni_ricette():
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("SELECT * FROM ricette ORDER BY id DESC")
d = cursor.fetchall()
conn.close()
return d

def aggiungi_ricetta(titolo, cat, ute, ing, proc):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("INSERT INTO ricette (titolo, categoria, utensili, ingredienti, procedimento) VALUES (?, ?, ?, ?, ?)", (titolo, cat, ute, ing, proc))
conn.commit()
conn.close()

def modifica_ricetta(rid, titolo, cat, ute, ing, proc):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("UPDATE ricette SET titolo=?, categoria=?, utensili=?, ingredienti=?, procedimento=? WHERE id=?", (titolo, cat, ute, ing, proc, conn.total_changes))
conn.commit()
conn.close()

def elimina_ricetta(rid):
conn = ottieni_connessione()
cursor = conn.cursor()
cursor.execute("DELETE FROM ricette WHERE id=?", (rid,))
conn.commit()
conn.close()
