import time
from sqlalchemy import create_engine, text, MetaData
from database import DATABASE_URL, Base
import models # Wichtig: Importiert die Modelle, damit Base sie kennt

# Warten, falls die DB noch nicht bereit ist
time.sleep(3) 

# Verbindung zur Datenbank herstellen
engine = create_engine(DATABASE_URL)
print("Verbindung zur Datenbank hergestellt.")

# Alle Tabellen löschen (ACHTUNG: Alle Daten gehen verloren!)
print("Lösche alle vorhandenen Tabellen...")
try:
    # Reflektiere die existierenden Tabellen
    meta = MetaData()
    meta.reflect(bind=engine)
    # Lösche alle Tabellen
    meta.drop_all(bind=engine)
    print("Alle Tabellen erfolgreich gelöscht.")
except Exception as e:
    print(f"Fehler beim Löschen der Tabellen: {e}")


# Alle Tabellen neu erstellen (basierend auf den Models)
print("Erstelle alle Tabellen neu...")
try:
    Base.metadata.create_all(bind=engine)
    print("Alle Tabellen erfolgreich neu erstellt.")
except Exception as e:
    print(f"Fehler beim Erstellen der Tabellen: {e}")

print("Datenbank-Reset abgeschlossen.") 