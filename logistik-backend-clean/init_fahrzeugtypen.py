from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from database import engine
from models import Fahrzeugtyp

Session = sessionmaker(bind=engine)
session = Session()

def init_fahrzeugtypen():
    """
    Initialisiert die Fahrzeugtypen-Datenbank mit Dummy-Daten
    """
    fahrzeugtypen_data = [
        {"name": "Traileryard", "anzahl_verfuegbar": 8},
        {"name": "Jumbo", "anzahl_verfuegbar": 12},
        {"name": "Bonsai", "anzahl_verfuegbar": 5},
        {"name": "Touren LKW PCC", "anzahl_verfuegbar": 6},
    ]
    
    for fahrzeug_data in fahrzeugtypen_data:
        # Prüfen ob bereits vorhanden
        existing = session.query(Fahrzeugtyp).filter(
            Fahrzeugtyp.name == fahrzeug_data["name"]
        ).first()
        
        if not existing:
            fahrzeugtyp = Fahrzeugtyp(
                name=fahrzeug_data["name"],
                anzahl_verfuegbar=fahrzeug_data["anzahl_verfuegbar"]
            )
            session.add(fahrzeugtyp)
            print(f"Fahrzeugtyp hinzugefügt: {fahrzeug_data['name']} (Anzahl: {fahrzeug_data['anzahl_verfuegbar']})")
        else:
            print(f"Fahrzeugtyp bereits vorhanden: {fahrzeug_data['name']}")
    
    session.commit()
    print("Fahrzeugtypen-Initialisierung abgeschlossen!")

if __name__ == "__main__":
    init_fahrzeugtypen()
    session.close() 