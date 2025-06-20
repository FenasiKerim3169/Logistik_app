import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Datenbankverbindung (Stand 10.6.)
engine = create_engine("postgresql://postgres:Sercanserkan1905@localhost/logistikdb")
Session = sessionmaker(bind=engine)
session = Session()

def meter_to_minutes(meter, durchschnittsgeschwindigkeit_kmh=10, zusaetzliche_minuten=5, mindest_minuten=8):
    """
    Konvertiert Meter in Minuten basierend auf durchschnittlicher Geschwindigkeit
    Standard: 10 km/h (sehr langsam für innerbetrieblichen Verkehr)
    Zusätzlich: 5 Minuten für Ein-/Ausladen, Wenden, etc.
    Mindestzeit: 8 Minuten (auch für sehr kurze Strecken)
    """
    # Meter zu km
    km = meter / 1000
    # Zeit in Stunden
    stunden = km / durchschnittsgeschwindigkeit_kmh
    # Zeit in Minuten
    fahrzeit_minuten = stunden * 60
    # Gesamtzeit = Fahrzeit + zusätzliche Zeit
    gesamt_minuten = fahrzeit_minuten + zusaetzliche_minuten
    # Mindestzeit anwenden
    if gesamt_minuten < mindest_minuten:
        gesamt_minuten = mindest_minuten
    return round(gesamt_minuten, 1)  # Auf 1 Dezimalstelle runden

def import_excel_matrix_to_distanzmatrix(excel_file):
    """
    Importiert Excel-Matrix in die distanzmatrix-Tabelle
    Matrix-Format: Zeilen = Von-Orte, Spalten = Nach-Orte
    Konvertiert Meter zu Minuten
    """
    try:
        # Excel-Datei laden
        df = pd.read_excel(excel_file, index_col=0)  # Erste Spalte als Index verwenden
        print(f"Excel-Matrix geladen: {len(df)} Zeilen, {len(df.columns)} Spalten")
        
        print("Von-Orte (Zeilen):", list(df.index))
        print("Nach-Orte (Spalten):", list(df.columns))
        
        # Daten in Datenbank einfügen
        imported_count = 0
        
        for von_ort in df.index:
            for nach_ort in df.columns:
                # Distanzwert aus der Matrix holen
                distanz_value = df.loc[von_ort, nach_ort]
                
                # Nur wenn ein gültiger Wert vorhanden ist
                if pd.notna(distanz_value) and distanz_value != 0:
                    von = str(von_ort).strip()
                    nach = str(nach_ort).strip()
                    distanz_meter = float(distanz_value)
                    weg_minuten = meter_to_minutes(distanz_meter)
                    
                    # Überprüfen ob Eintrag bereits existiert
                    exists = session.execute(
                        text("SELECT 1 FROM distanzmatrix WHERE von=:von AND nach=:nach"), 
                        {"von": von, "nach": nach}
                    ).fetchone()
                    
                    if not exists:
                        # Neuen Eintrag hinzufügen
                        session.execute(
                            text("INSERT INTO distanzmatrix (von, nach, weg_min) VALUES (:von, :nach, :weg_min)"), 
                            {"von": von, "nach": nach, "weg_min": weg_minuten}
                        )
                        imported_count += 1
                        print(f"Importiert: {von} -> {nach}: {distanz_meter}m = {weg_minuten}min")
        
        session.commit()
        print(f"\nImport abgeschlossen! {imported_count} neue Einträge hinzugefügt.")
        
    except Exception as e:
        print(f"Fehler beim Import: {e}")
        session.rollback()
    finally:
        session.close()

def show_current_data():
    """
    Zeigt die aktuellen Daten in der distanzmatrix-Tabelle
    """
    try:
        result = session.execute(text("SELECT * FROM distanzmatrix LIMIT 10")).fetchall()
        print(f"\nAktuelle Daten in distanzmatrix ({len(list(session.execute(text('SELECT * FROM distanzmatrix'))))} Einträge total):")
        for row in result:
            print(f"ID: {row.id}, Von: {row.von}, Nach: {row.nach}, Weg: {row.weg_min}min")
    except Exception as e:
        print(f"Fehler beim Anzeigen: {e}")

if __name__ == "__main__":
    # Excel-Dateien im Verzeichnis suchen
    import os
    excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and not f.startswith('~$')]
    
    if excel_files:
        print("Gefundene Excel-Dateien:")
        for i, file in enumerate(excel_files):
            print(f"{i+1}. {file}")
        
        # Erste Excel-Datei automatisch verwenden
        excel_file = excel_files[0]
        print(f"\nVerwende: {excel_file}")
        import_excel_matrix_to_distanzmatrix(excel_file)
        
        # Ergebnis anzeigen
        show_current_data()
    else:
        print("Keine Excel-Dateien (.xlsx) im aktuellen Verzeichnis gefunden")
        show_current_data()
