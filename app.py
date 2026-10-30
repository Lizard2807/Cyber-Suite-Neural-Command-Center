from database import init_db, aggiungi_evento, ottieni_eventi
from datetime import datetime

# Inizializza il database se non esiste
init_db()

if __name__ == "__main__":
    print("--- Assistente Agenda Locale (Offline) ---")
    print("La tua agenda personale è pronta e sicura sul tuo Mac.\n")
    
    while True:
        print("Cosa vuoi fare?")
        print("1. Visualizza impegni salvati")
        print("2. Aggiungi un nuovo impegno")
        print("3. Esci")
        
        scelta = input("\nScegli un'opzione (1, 2 o 3): ").strip()
        
        if scelta == '1':
            eventi = ottieni_eventi()
            if not eventi:
                print("\n📭 Non ci sono impegni salvati nell'agenda.\n")
            else:
                print("\n📅 Ecco i tuoi impegni salvati:")
                for ev in eventi:
                    print(f" - [{ev[1]}] {ev[0]} ({ev[2]})")
                print()
                
        elif scelta == '2':
            titolo = input("Inserisci il titolo dell'impegno (es. Fare la spesa): ").strip()
            data_ora = input("Inserisci data e ora (formato: YYYY-MM-DD HH:MM:SS, es. 2026-10-27 15:00:00): ").strip()
            descrizione = input("Eventuali dettagli (opzionale, premi Invio per saltare): ").strip()
            
            if titolo and data_ora:
                aggiungi_evento(titolo, data_ora, descrizione)
                print(f"\n✅ Evento aggiunto con successo! [{data_ora}] {titolo}\n")
            else:
                print("\n❌ Attenzione: il titolo e la data/ora sono obbligatori.\n")
                
        elif scelta == '3':
            print("\n👋 Arrivederci! I tuoi dati sono al sicuro nel database locale.")
            break
        else:
            print("\n❌ Scelta non valida. Inserisci 1, 2 o 3.\n")
