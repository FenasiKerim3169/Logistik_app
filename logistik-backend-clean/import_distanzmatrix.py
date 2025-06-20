import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Datenbankverbindung (Stand 10.6.)
engine = create_engine("postgresql://postgres:Sercanserkan1905@localhost/logistikdb")
Session = sessionmaker(bind=engine)
session = Session()

def import_excel_matrix_to_distanzmatrix(excel_file):
    """
    Importiert Excel-Matrix in die distanzmatrix-Tabelle
    Matrix-Format: Zeilen = Von-Orte, Spalten = Nach-Orte
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
                    distanz_m = float(distanz_value)
                    
                    # Überprüfen ob Eintrag bereits existiert
                    exists = session.execute(
                        text("SELECT 1 FROM distanzmatrix WHERE von=:von AND nach=:nach"), 
                        {"von": von, "nach": nach}
                    ).fetchone()
                    
                    if not exists:
                        # Neuen Eintrag hinzufügen
                        session.execute(
                            text("INSERT INTO distanzmatrix (von, nach, distanz_m) VALUES (:von, :nach, :distanz_m)"), 
                            {"von": von, "nach": nach, "distanz_m": distanz_m}
                        )
                        imported_count += 1
                        print(f"Importiert: {von} -> {nach}: {distanz_m}m")
        
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
            print(f"ID: {row.id}, Von: {row.von}, Nach: {row.nach}, Distanz: {row.distanz_m}m")
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
