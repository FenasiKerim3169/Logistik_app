from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import (Benutzer, Transport, Zeitfenster, Schicht, Logbuch, 
                   Distanz, ArchivTransport, Fahrzeugtyp, Mehrfachtransport, 
                   MehrfachtransportRoute)
import schemas
from datetime import datetime

app = FastAPI()

# CORS-Freigabe für Frontend (Port 3000-3005)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003",
        "http://127.0.0.1:3004",
        "http://127.0.0.1:3005"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tabellen erstellen
Base.metadata.create_all(bind=engine)

# DB-Session bereitstellen
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root - EINFACHER TEST
@app.get("/")
def read_root():
    return {"message": "Logistiksoftware-Backend läuft "}

# -------------------- FAHRZEUGTYPEN --------------------
@app.post("/fahrzeugtypen", response_model=schemas.FahrzeugtypOut)
def fahrzeugtyp_erstellen(fahrzeugtyp: schemas.FahrzeugtypCreate, db: Session = Depends(get_db)):
    db_fahrzeugtyp = Fahrzeugtyp(**fahrzeugtyp.dict())
    db.add(db_fahrzeugtyp)
    db.commit()
    db.refresh(db_fahrzeugtyp)
    return db_fahrzeugtyp

@app.get("/fahrzeugtypen", response_model=list[schemas.FahrzeugtypOut])
def alle_fahrzeugtypen(db: Session = Depends(get_db)):
    return db.query(Fahrzeugtyp).all()

# Endpunkt für verfügbare Zeiten
@app.get("/verfuegbare-zeiten/{fahrzeugtyp}/{datum}")
def verfuegbare_zeiten(fahrzeugtyp: str, datum: str, db: Session = Depends(get_db)):
    # Alle bereits gebuchten Zeiten für dieses Fahrzeug an diesem Tag
    gebuchte_zeiten = db.query(Transport.startzeit).filter(
        Transport.fahrzeugtyp == fahrzeugtyp,
        Transport.datum == datum
    ).all()
    
    # Auch Mehrfachtransporte berücksichtigen
    gebuchte_zeiten_mehrfach = db.query(Mehrfachtransport.startzeit).filter(
        Mehrfachtransport.fahrzeugtyp == fahrzeugtyp,
        Mehrfachtransport.datum == datum
    ).all()
    
    alle_gebuchten = [zeit[0] for zeit in gebuchte_zeiten] + [zeit[0] for zeit in gebuchte_zeiten_mehrfach]
    
    # Alle möglichen Zeitslots (48 pro Tag)
    alle_zeiten = []
    for i in range(48):
        h = str(i // 2).zfill(2)
        m = "00" if i % 2 == 0 else "30"
        alle_zeiten.append(f"{h}:{m}")
    
    # Verfügbare Zeiten zurückgeben
    verfuegbare = [zeit for zeit in alle_zeiten if zeit not in alle_gebuchten]
    return {"verfuegbare_zeiten": verfuegbare}

# -------------------- BENUTZER --------------------
@app.post("/benutzer", response_model=schemas.BenutzerOut)
def benutzer_erstellen(benutzer: schemas.BenutzerCreate, db: Session = Depends(get_db)):
    db_benutzer = Benutzer(**benutzer.dict())
    db.add(db_benutzer)
    db.commit()
    db.refresh(db_benutzer)
    return db_benutzer

@app.get("/benutzer", response_model=list[schemas.BenutzerOut])
def alle_benutzer(db: Session = Depends(get_db)):
    return db.query(Benutzer).all()

@app.put("/benutzer/{id}", response_model=schemas.BenutzerOut)
def benutzer_updaten(id: int, daten: schemas.BenutzerCreate, db: Session = Depends(get_db)):
    benutzer = db.query(Benutzer).filter(Benutzer.id == id).first()
    if not benutzer:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    for k, v in daten.dict().items():
        setattr(benutzer, k, v)
    db.commit()
    db.refresh(benutzer)
    return benutzer

@app.delete("/benutzer/{id}")
def benutzer_loeschen(id: int, db: Session = Depends(get_db)):
    benutzer = db.query(Benutzer).filter(Benutzer.id == id).first()
    if not benutzer:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    db.delete(benutzer)
    db.commit()
    return {"message": f"Benutzer {id} gelöscht "}

# -------------------- TRANSPORTE --------------------
@app.post("/transporte", response_model=schemas.TransportOut)
def transport_erstellen(transport: schemas.TransportCreate, db: Session = Depends(get_db)):
    distanz = db.query(Distanz.weg_min).filter(
        (Distanz.von == transport.von) & (Distanz.nach == transport.nach)
    ).first()

    if not distanz:
        distanz = db.query(Distanz.weg_min).filter(
            (Distanz.von == transport.nach) & (Distanz.nach == transport.von)
        ).first()

    weg_min = float(distanz[0]) if distanz else None

    t = Transport(
        von=transport.von,
        nach=transport.nach,
        fahrzeugtyp=transport.fahrzeugtyp,
        datum=transport.datum,
        startzeit=transport.startzeit,
        weg_min=weg_min,
        zeitfenster=transport.zeitfenster,
        status=transport.status,
        begruendung=transport.begruendung,
        fahrer_id=transport.fahrer_id,
        mehrfachtransport_id=transport.mehrfachtransport_id,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t

@app.get("/transporte", response_model=list[schemas.TransportOut])
def alle_transporte(db: Session = Depends(get_db)):
    return db.query(Transport).all()

@app.put("/transporte/{id}", response_model=schemas.TransportOut)
def transport_updaten(id: int, daten: schemas.TransportCreate, db: Session = Depends(get_db)):
    transport = db.query(Transport).filter(Transport.id == id).first()
    if not transport:
        raise HTTPException(status_code=404, detail="Transport nicht gefunden")
    for k, v in daten.dict().items():
        setattr(transport, k, v)
    db.commit()
    db.refresh(transport)
    return transport

@app.delete("/transporte/{id}")
def transport_loeschen(id: int, db: Session = Depends(get_db)):
    transport = db.query(Transport).filter(Transport.id == id).first()
    if not transport:
        raise HTTPException(status_code=404, detail="Transport nicht gefunden")
    db.delete(transport)
    db.commit()
    return {"message": f"Transport {id} gelöscht "}

# -------------------- MEHRFACHTRANSPORTE --------------------
@app.post("/mehrfachtransporte", response_model=schemas.MehrfachtransportOut)
def mehrfachtransport_erstellen(mehrfach: schemas.MehrfachtransportCreate, db: Session = Depends(get_db)):
    # Gesamtdistanz berechnen
    gesamt_weg = 0
    for route in mehrfach.routen:
        distanz = db.query(Distanz.weg_min).filter(
            (Distanz.von == route.von) & (Distanz.nach == route.nach)
        ).first()
        if not distanz:
            distanz = db.query(Distanz.weg_min).filter(
                (Distanz.von == route.nach) & (Distanz.nach == route.von)
            ).first()
        if distanz:
            gesamt_weg += float(distanz[0])
    
    # Mehrfachtransport erstellen
    mt = Mehrfachtransport(
        name=mehrfach.name,
        fahrzeugtyp=mehrfach.fahrzeugtyp,
        datum=mehrfach.datum,
        startzeit=mehrfach.startzeit,
        gesamt_weg_min=gesamt_weg,
        fahrer_id=mehrfach.fahrer_id,
        erstellt_am=datetime.now()
    )
    db.add(mt)
    db.commit()
    db.refresh(mt)
    
    # Routen hinzufügen
    for route in mehrfach.routen:
        distanz = db.query(Distanz.weg_min).filter(
            (Distanz.von == route.von) & (Distanz.nach == route.nach)
        ).first()
        if not distanz:
            distanz = db.query(Distanz.weg_min).filter(
                (Distanz.von == route.nach) & (Distanz.nach == route.von)
            ).first()
        weg_min = float(distanz[0]) if distanz else 0
        
        route_obj = MehrfachtransportRoute(
            mehrfachtransport_id=mt.id,
            reihenfolge=route.reihenfolge,
            von=route.von,
            nach=route.nach,
            weg_min=weg_min
        )
        db.add(route_obj)
    
    db.commit()
    return mt

@app.get("/mehrfachtransporte", response_model=list[schemas.MehrfachtransportOut])
def alle_mehrfachtransporte(db: Session = Depends(get_db)):
    return db.query(Mehrfachtransport).all()

# -------------------- ZEITFENSTER --------------------
@app.post("/zeitfenster", response_model=schemas.ZeitfensterOut)
def zeitfenster_erstellen(data: schemas.ZeitfensterCreate, db: Session = Depends(get_db)):
    z = Zeitfenster(**data.dict())
    db.add(z)
    db.commit()
    db.refresh(z)
    return z

@app.get("/zeitfenster", response_model=list[schemas.ZeitfensterOut])
def alle_zeitfenster(db: Session = Depends(get_db)):
    return db.query(Zeitfenster).all()

@app.put("/zeitfenster/{id}", response_model=schemas.ZeitfensterOut)
def zeitfenster_updaten(id: int, daten: schemas.ZeitfensterCreate, db: Session = Depends(get_db)):
    eintrag = db.query(Zeitfenster).filter(Zeitfenster.id == id).first()
    if not eintrag:
        raise HTTPException(status_code=404, detail="Zeitfenster nicht gefunden")
    for k, v in daten.dict().items():
        setattr(eintrag, k, v)
    db.commit()
    db.refresh(eintrag)
    return eintrag

@app.delete("/zeitfenster/{id}")
def zeitfenster_loeschen(id: int, db: Session = Depends(get_db)):
    eintrag = db.query(Zeitfenster).filter(Zeitfenster.id == id).first()
    if not eintrag:
        raise HTTPException(status_code=404, detail="Zeitfenster nicht gefunden")
    db.delete(eintrag)
    db.commit()
    return {"message": f"Zeitfenster {id} gelöscht "}

# -------------------- SCHICHTEN --------------------
@app.post("/schichten", response_model=schemas.SchichtOut)
def schicht_erstellen(data: schemas.SchichtCreate, db: Session = Depends(get_db)):
    s = Schicht(**data.dict())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

@app.get("/schichten", response_model=list[schemas.SchichtOut])
def alle_schichten(db: Session = Depends(get_db)):
    return db.query(Schicht).all()

@app.put("/schichten/{id}", response_model=schemas.SchichtOut)
def schicht_updaten(id: int, daten: schemas.SchichtCreate, db: Session = Depends(get_db)):
    eintrag = db.query(Schicht).filter(Schicht.id == id).first()
    if not eintrag:
        raise HTTPException(status_code=404, detail="Schicht nicht gefunden")
    for k, v in daten.dict().items():
        setattr(eintrag, k, v)
    db.commit()
    db.refresh(eintrag)
    return eintrag

@app.delete("/schichten/{id}")
def schicht_loeschen(id: int, db: Session = Depends(get_db)):
    eintrag = db.query(Schicht).filter(Schicht.id == id).first()
    if not eintrag:
        raise HTTPException(status_code=404, detail="Schicht nicht gefunden")
    db.delete(eintrag)
    db.commit()
    return {"message": f"Schicht {id} gelöscht "}

# -------------------- LOGBUCH --------------------
@app.post("/logbuch", response_model=schemas.LogbuchOut)
def logbuch_eintrag(data: schemas.LogbuchCreate, db: Session = Depends(get_db)):
    l = Logbuch(**data.dict())
    db.add(l)
    db.commit()
    db.refresh(l)
    return l

@app.get("/logbuch", response_model=list[schemas.LogbuchOut])
def alle_logs(db: Session = Depends(get_db)):
    return db.query(Logbuch).all()

@app.delete("/logbuch/{id}")
def log_loeschen(id: int, db: Session = Depends(get_db)):
    eintrag = db.query(Logbuch).filter(Logbuch.id == id).first()
    if not eintrag:
        raise HTTPException(status_code=404, detail="Logbuch-Eintrag nicht gefunden")
    db.delete(eintrag)
    db.commit()
    return {"message": f"Logbuch-Eintrag {id} gelöscht "}

# -------------------- DISTANZMATRIX --------------------
@app.post("/distanzmatrix", response_model=schemas.DistanzOut)
def distanz_eintrag(data: schemas.DistanzCreate, db: Session = Depends(get_db)):
    d = Distanz(**data.dict())
    db.add(d)
    db.commit()
    db.refresh(d)
    return d

@app.get("/distanzmatrix", response_model=list[schemas.DistanzOut])
def alle_distanzen(db: Session = Depends(get_db)):
    return db.query(Distanz).all()

@app.put("/distanzmatrix/{id}", response_model=schemas.DistanzOut)
def distanz_updaten(id: int, daten: schemas.DistanzCreate, db: Session = Depends(get_db)):
    eintrag = db.query(Distanz).filter(Distanz.id == id).first()
    if not eintrag:
        raise HTTPException(status_code=404, detail="Distanz nicht gefunden")
    for k, v in daten.dict().items():
        setattr(eintrag, k, v)
    db.commit()
    db.refresh(eintrag)
    return eintrag

@app.delete("/distanzmatrix/{id}")
def distanz_loeschen(id: int, db: Session = Depends(get_db)):
    eintrag = db.query(Distanz).filter(Distanz.id == id).first()
    if not eintrag:
        raise HTTPException(status_code=404, detail="Distanz nicht gefunden")
    db.delete(eintrag)
    db.commit()
    return {"message": f"Distanz {id} gelöscht "}

# -------------------- ARCHIV TRANSPORTE --------------------
@app.post("/archiv_transporte", response_model=schemas.ArchivTransportOut)
def archiv_transport_erstellen(data: schemas.ArchivTransportCreate, db: Session = Depends(get_db)):
    a = ArchivTransport(**data.dict())
    db.add(a)
    db.commit()
    db.refresh(a)
    return a

@app.get("/archiv_transporte", response_model=list[schemas.ArchivTransportOut])
def alle_archiv_transporte(db: Session = Depends(get_db)):
    return db.query(ArchivTransport).all()

@app.delete("/archiv_transporte/{id}")
def archiv_loeschen(id: int, db: Session = Depends(get_db)):
    eintrag = db.query(ArchivTransport).filter(ArchivTransport.id == id).first()
    if not eintrag:
        raise HTTPException(status_code=404, detail="Archiv-Transport nicht gefunden")
    db.delete(eintrag)
    db.commit()
    return {"message": f"Archiv-Transport {id} gelöscht "} 