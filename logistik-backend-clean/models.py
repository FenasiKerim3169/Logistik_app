from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Benutzer(Base):
    __tablename__ = "benutzer"

    id = Column(Integer, primary_key=True, index=True)
    vorname = Column(String)
    nachname = Column(String)
    rolle = Column(String)
    email = Column(String)

class Fahrzeugtyp(Base):
    __tablename__ = "fahrzeugtypen"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    anzahl_verfuegbar = Column(Integer, default=0)

class Transport(Base):
    __tablename__ = "transporte"

    id = Column(Integer, primary_key=True, index=True)
    von = Column(String)
    nach = Column(String)
    fahrzeugtyp = Column(String)
    datum = Column(Date)
    startzeit = Column(String)
    weg_min = Column(Float, nullable=True)
    zeitfenster = Column(DateTime)
    status = Column(String, default="offen")
    begruendung = Column(Text)
    fahrer_id = Column(Integer)
    mehrfachtransport_id = Column(Integer, ForeignKey("mehrfachtransporte.id"), nullable=True)

class Mehrfachtransport(Base):
    __tablename__ = "mehrfachtransporte"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)  # z.B. "Route A-B-C"
    fahrzeugtyp = Column(String)
    datum = Column(Date)
    startzeit = Column(String)
    status = Column(String, default="offen")
    gesamt_weg_min = Column(Float)
    fahrer_id = Column(Integer)
    erstellt_am = Column(DateTime)
    
    # Relationship zu einzelnen Transporten
    transporte = relationship("Transport", foreign_keys="Transport.mehrfachtransport_id")

class MehrfachtransportRoute(Base):
    __tablename__ = "mehrfachtransport_routen"

    id = Column(Integer, primary_key=True, index=True)
    mehrfachtransport_id = Column(Integer, ForeignKey("mehrfachtransporte.id"))
    reihenfolge = Column(Integer)  # 1, 2, 3, etc.
    von = Column(String)
    nach = Column(String)
    weg_min = Column(Float)

class Zeitfenster(Base):
    __tablename__ = "zeitfenster"

    id = Column(Integer, primary_key=True, index=True)
    start = Column(DateTime)
    ende = Column(DateTime)
    verfuegbar = Column(String, default="true")

class Schicht(Base):
    __tablename__ = "schichten"

    id = Column(Integer, primary_key=True, index=True)
    von = Column(DateTime)
    bis = Column(DateTime)
    pause_min = Column(Integer, default=0)
    fahrer_id = Column(Integer)

class Logbuch(Base):
    __tablename__ = "logbuch"

    id = Column(Integer, primary_key=True, index=True)
    aktion = Column(String)
    zeitpunkt = Column(DateTime)
    benutzer_id = Column(Integer)

class Distanz(Base):
    __tablename__ = "distanzmatrix"

    id = Column(Integer, primary_key=True, index=True)
    von = Column(String)
    nach = Column(String)
    weg_min = Column(Float)

class ArchivTransport(Base):
    __tablename__ = "archiv_transporte"

    id = Column(Integer, primary_key=True, index=True)
    von = Column(String)
    nach = Column(String)
    fahrzeugtyp = Column(String)
    status = Column(String)
    abgeschlossen_am = Column(DateTime)
    begruendung = Column(Text)
