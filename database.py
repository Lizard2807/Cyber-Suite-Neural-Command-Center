import sqlite3

def init_db():
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titolo TEXT,
            data_ora TEXT,
            descrizione TEXT,
            priorita TEXT DEFAULT 'Ordinario',
            completato INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS spesa_documenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titolo_documento TEXT,
            negozi_articoli TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS misure (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prodotto TEXT,
            m1_tipo TEXT,
            m1_val TEXT,
            m2_tipo TEXT,
            m2_val TEXT,
            m3_tipo TEXT,
            m3_val TEXT,
            note_extra TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intrattenimento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titolo TEXT,
            tipo TEXT,
            genere TEXT,
            stato TEXT,
            voto TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pomodoro_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            compito TEXT,
            categoria TEXT DEFAULT 'Generale',
            completato INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS armadio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            capo TEXT,
            categoria TEXT,
            colore TEXT,
            stagione TEXT,
            posizione TEXT
        )
    """)
    # --- Nuove tabelle Allenamento & Cucina ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS record_personali (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            esercizio TEXT,
            peso_tempo TEXT,
            data_record TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS allenamento_scheda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            giorno TEXT,
            dettagli_esercizi TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS allenamento_sessione_oggi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            tipo_allenamento TEXT,
            durata TEXT,
            note TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ricette (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titolo TEXT,
            categoria TEXT,
            utensili TEXT,
            ingredienti TEXT,
            procedimento TEXT
        )
    """)
    conn.commit()
    conn.close()

# --- Agenda ---
def aggiungi_evento(titolo, data_ora, descrizione, priorita):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO eventi (titolo, data_ora, descrizione, priorita, completato) VALUES (?, ?, ?, ?, 0)", (titolo, data_ora, descrizione, priorita))
    conn.commit()
    conn.close()

def modifica_evento(evento_id, titolo, data_ora, descrizione, priorita):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE eventi SET titolo = ?, data_ora = ?, descrizione = ?, priorita = ? WHERE id = ?", (titolo, data_ora, descrizione, priorita, evento_id))
    conn.commit()
    conn.close()

def ottieni_eventi():
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, titolo, data_ora, descrizione, priorita, completato FROM eventi ORDER BY data_ora ASC")
    eventi = cursor.fetchall()
    conn.close()
    return eventi

def elimina_evento(evento_id):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM eventi WHERE id = ?", (evento_id,))
    conn.commit()
    conn.close()

def toggle_completato(evento_id):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("SELECT completato FROM eventi WHERE id = ?", (evento_id,))
    res = cursor.fetchone()
    if res:
        nuovo_stato = 0 if res[0] == 1 else 1
        cursor.execute("UPDATE eventi SET completato = ? WHERE id = ?", (nuovo_stato, evento_id))
        conn.commit()
    conn.close()

# --- Spesa ---
def aggiungi_documento_spesa(titolo_documento, negozi_articoli):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO spesa_documenti (titolo_documento, negozi_articoli) VALUES (?, ?)", (titolo_documento, negozi_articoli))
    conn.commit()
    conn.close()

def modifica_documento_spesa(spesa_id, titolo_documento, negozi_articoli):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE spesa_documenti SET titolo_documento = ?, negozi_articoli = ? WHERE id = ?", (titolo_documento, negozi_articoli, spesa_id))
    conn.commit()
    conn.close()

def ottieni_documenti_spesa():
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, titolo_documento, negozi_articoli FROM spesa_documenti ORDER BY id DESC")
    items = cursor.fetchall()
    conn.close()
    return items

def elimina_documento_spesa(spesa_id):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM spesa_documenti WHERE id = ?", (spesa_id,))
    conn.commit()
    conn.close()

# --- Misure ---
def aggiungi_misura(prodotto, m1_tipo, m1_val, m2_tipo, m2_val, m3_tipo, m3_val, note_extra):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO misure (prodotto, m1_tipo, m1_val, m2_tipo, m2_val, m3_tipo, m3_val, note_extra) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (prodotto, m1_tipo, m1_val, m2_tipo, m2_val, m3_tipo, m3_val, note_extra))
    conn.commit()
    conn.close()

def modifica_misura(misura_id, prodotto, m1_tipo, m1_val, m2_tipo, m2_val, m3_tipo, m3_val, note_extra):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE misure SET prodotto = ?, m1_tipo = ?, m1_val = ?, m2_tipo = ?, m2_val = ?, m3_tipo = ?, m3_val = ?, note_extra = ? 
        WHERE id = ?
    """, (prodotto, m1_tipo, m1_val, m2_tipo, m2_val, m3_tipo, m3_val, note_extra, misura_id))
    conn.commit()
    conn.close()

def ottieni_misure():
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, prodotto, m1_tipo, m1_val, m2_tipo, m2_val, m3_tipo, m3_val, note_extra FROM misure ORDER BY id DESC")
    misure = cursor.fetchall()
    conn.close()
    return misure

def elimina_misura(misura_id):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM misure WHERE id = ?", (misura_id,))
    conn.commit()
    conn.close()

# --- Film & Serie TV ---
def aggiungi_intrattenimento(titolo, tipo, genere, stato, voto):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO intrattenimento (titolo, tipo, genere, stato, voto) VALUES (?, ?, ?, ?, ?)", (titolo, tipo, genere, stato, voto))
    conn.commit()
    conn.close()

def modifica_intrattenimento(item_id, titolo, tipo, genere, stato, voto):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE intrattenimento SET titolo = ?, tipo = ?, genere = ?, stato = ?, voto = ? WHERE id = ?", (titolo, tipo, genere, stato, voto, item_id))
    conn.commit()
    conn.close()

def ottieni_intrattenimento():
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, titolo, tipo, genere, stato, voto FROM intrattenimento ORDER BY id DESC")
    items = cursor.fetchall()
    conn.close()
    return items

def elimina_intrattenimento(item_id):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM intrattenimento WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

# --- Pomodoro Focus ---
def aggiungi_pomodoro_task(compito, categoria):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pomodoro_tasks (compito, categoria, completato) VALUES (?, ?, 0)", (compito, categoria))
    conn.commit()
    conn.close()

def ottieni_pomodoro_tasks():
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, compito, categoria, completato FROM pomodoro_tasks ORDER BY id DESC")
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def toggle_pomodoro_task(task_id):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("SELECT completato FROM pomodoro_tasks WHERE id = ?", (task_id,))
    res = cursor.fetchone()
    if res:
        nuovo = 0 if res[0] == 1 else 1
        cursor.execute("UPDATE pomodoro_tasks SET completato = ? WHERE id = ?", (nuovo, task_id))
        conn.commit()
    conn.close()

def elimina_pomodoro_task(task_id):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pomodoro_tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def elimina_completati_pomodoro():
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pomodoro_tasks WHERE completato = 1")
    conn.commit()
    conn.close()

# --- Armadio ---
def aggiungi_capo(capo, categoria, colore, stagione, posizione):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO armadio (capo, categoria, colore, stagione, posizione) VALUES (?, ?, ?, ?, ?)", (capo, categoria, colore, stagione, posizione))
    conn.commit()
    conn.close()

def ottieni_armadio():
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, capo, categoria, colore, stagione, posizione FROM armadio ORDER BY id DESC")
    items = cursor.fetchall()
    conn.close()
    return items

def elimina_capo(capo_id):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM armadio WHERE id = ?", (capo_id,))
    conn.commit()
    conn.close()

# --- Allenamento & Record ---
def aggiungi_record(esercizio, peso_tempo, data_record):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO record_personali (esercizio, peso_tempo, data_record) VALUES (?, ?, ?)", (esercizio, peso_tempo, data_record))
    conn.commit()
    conn.close()

def ottieni_record():
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, esercizio, peso_tempo, data_record FROM record_personali ORDER BY id DESC")
    items = cursor.fetchall()
    conn.close()
    return items

def elimina_record(rec_id):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM record_personali WHERE id = ?", (rec_id,))
    conn.commit()
    conn.close()

def aggiungi_scheda_allenamento(giorno, dettagli_esercizi):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO allenamento_scheda (giorno, dettagli_esercizi) VALUES (?, ?)", (giorno, dettagli_esercizi))
    conn.commit()
    conn.close()

def modifica_scheda_allenamento(scheda_id, giorno, dettagli_esercizi):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE allenamento_scheda SET giorno = ?, dettagli_esercizi = ? WHERE id = ?", (giorno, dettagli_esercizi, scheda_id))
    conn.commit()
    conn.close()

def ottieni_schede_allenamento():
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, giorno, dettagli_esercizi FROM allenamento_scheda ORDER BY id DESC")
    items = cursor.fetchall()
    conn.close()
    return items

def elimina_scheda_allenamento(scheda_id):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM allenamento_scheda WHERE id = ?", (scheda_id,))
    conn.commit()
    conn.close()

# --- Cucina & Ricette ---
def aggiungi_ricetta(titolo, categoria, utensili, ingredienti, procedimento):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ricette (titolo, categoria, utensili, ingredienti, procedimento) VALUES (?, ?, ?, ?, ?)", (titolo, categoria, utensili, ingredienti, procedimento))
    conn.commit()
    conn.close()

def modifica_ricetta(ricetta_id, titolo, categoria, utensili, ingredienti, procedimento):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE ricette SET titolo = ?, categoria = ?, utensili = ?, ingredienti = ?, procedimento = ? WHERE id = ?", (titolo, categoria, utensili, ingredienti, procedimento, ricetta_id))
    conn.commit()
    conn.close()

def ottieni_ricette():
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, titolo, categoria, utensili, ingredienti, procedimento FROM ricette ORDER BY id DESC")
    items = cursor.fetchall()
    conn.close()
    return items

def elimina_ricetta(ricetta_id):
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ricette WHERE id = ?", (ricetta_id,))
    conn.commit()
    conn.close()
