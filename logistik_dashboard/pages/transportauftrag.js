import React, { useState, useEffect } from "react";

const bauten = [
  "Bau 01-01", "Bau 01-02", "Bau 02-01", "Bau 02-02", "Bau 3", "Bau 4",
  "Bau 5", "Bau 7", "Bau 20", "Bau 22", "Bau 24-1", "Bau 24-2",
  "Bau 25-1", "Bau 25-2", "Bau 26", "Bau 28", "Bau 30", "Bau 40",
  "Bau 70", "Bau 78", "Bau 90", "Bau 91", "Bau 93"
];

const zeitslots = Array.from({ length: 48 }, (_, i) => {
  const h = String(Math.floor(i / 2)).padStart(2, '0');
  const m = i % 2 === 0 ? '00' : '30';
  return `${h}:${m}`;
});

export default function Transportauftrag() {
  const [fahrzeugtypen, setFahrzeugtypen] = useState([]);
  const [data, setData] = useState({
    fahrzeugtyp: "",
    abholort: "",
    zielort: "",
    datum: "",
    startzeit: ""
  });
  const [wegMin, setWegMin] = useState("");

  // Fahrzeugtypen laden
  useEffect(() => {
    fetch("http://127.0.0.1:8000/fahrzeugtypen")
      .then(res => res.json())
      .then(data => setFahrzeugtypen(data))
      .catch(err => console.error("Fehler beim Laden der Fahrzeugtypen", err));
  }, []);

  // Weg in Minuten laden
  useEffect(() => {
    if (data.abholort && data.zielort && data.abholort !== data.zielort) {
      fetch("http://127.0.0.1:8000/distanzmatrix")
        .then(res => res.json())
        .then(all => {
          const found = all.find(e =>
            (e.von === data.abholort && e.nach === data.zielort) ||
            (e.von === data.zielort && e.nach === data.abholort)
          );
          setWegMin(found ? found.weg_min : "");
        })
        .catch(() => setWegMin(""));
    } else {
      setWegMin("");
    }
  }, [data.abholort, data.zielort]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!data.fahrzeugtyp || !data.abholort || !data.zielort || !data.datum || !data.startzeit) {
      alert("Bitte füllen Sie alle Felder aus.");
      return;
    }

    const payload = {
      von: data.abholort,
      nach: data.zielort,
      fahrzeugtyp: data.fahrzeugtyp,
      datum: data.datum,
      startzeit: data.startzeit,
      zeitfenster: new Date(`${data.datum}T${data.startzeit}:00.000Z`).toISOString()
    };

    try {
      const res = await fetch("http://127.0.0.1:8000/transporte", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        alert("Transport wurde erfolgreich erstellt!");
        setData({ fahrzeugtyp: "", abholort: "", zielort: "", datum: "", startzeit: "" });
        setWegMin("");
      } else {
        const errorText = await res.text();
        alert(`Fehler ${res.status}: ${errorText}`);
      }
    } catch (error) {
      alert(`Netzwerkfehler: ${error.message}`);
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold text-center mb-8">Transportauftrag</h1>
      
      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
          
          {/* Fahrzeugtyp Kachel - ERSTE POSITION */}
          <div className="bg-white p-4 rounded-lg shadow border">
            <h3 className="font-semibold text-gray-700 mb-2">Fahrzeugtyp</h3>
            <select
              className="w-full p-2 border rounded"
              value={data.fahrzeugtyp}
              onChange={(e) => setData({ ...data, fahrzeugtyp: e.target.value })}
              required
            >
              <option value="">Fahrzeugtyp wählen</option>
              {fahrzeugtypen.map((typ) => (
                <option key={typ.id} value={typ.name}>{typ.name}</option>
              ))}
            </select>
          </div>

          {/* Bau von Kachel - ZWEITE POSITION */}
          <div className="bg-white p-4 rounded-lg shadow border">
            <h3 className="font-semibold text-gray-700 mb-2">Bau von</h3>
            <select
              className="w-full p-2 border rounded"
              value={data.abholort}
              onChange={(e) => setData({ ...data, abholort: e.target.value })}
              required
            >
              <option value="">Abholort wählen</option>
              {bauten.map((bau) => (
                <option key={bau} value={bau}>{bau}</option>
              ))}
            </select>
          </div>

          {/* Bau nach Kachel - DRITTE POSITION */}
          <div className="bg-white p-4 rounded-lg shadow border">
            <h3 className="font-semibold text-gray-700 mb-2">Bau nach</h3>
            <select
              className="w-full p-2 border rounded"
              value={data.zielort}
              onChange={(e) => setData({ ...data, zielort: e.target.value })}
              required
            >
              <option value="">Zielort wählen</option>
              {bauten.map((bau) => (
                <option key={bau} value={bau}>{bau}</option>
              ))}
            </select>
          </div>

          {/* Datum Kachel - VIERTE POSITION */}
          <div className="bg-white p-4 rounded-lg shadow border">
            <h3 className="font-semibold text-gray-700 mb-2">Datum</h3>
            <input
              type="date"
              className="w-full p-2 border rounded"
              value={data.datum}
              onChange={(e) => setData({ ...data, datum: e.target.value })}
              required
            />
          </div>

          {/* Startzeit Kachel - FÜNFTE POSITION */}
          <div className="bg-white p-4 rounded-lg shadow border">
            <h3 className="font-semibold text-gray-700 mb-2">Startzeit</h3>
            <select
              className="w-full p-2 border rounded"
              value={data.startzeit}
              onChange={(e) => setData({ ...data, startzeit: e.target.value })}
              required
            >
              <option value="">Startzeit wählen</option>
              {zeitslots.map((zeit) => (
                <option key={zeit} value={zeit}>{zeit}</option>
              ))}
            </select>
          </div>

          {/* Button Kachel - SECHSTE POSITION */}
          <div className="bg-white p-4 rounded-lg shadow border flex items-center justify-center">
            <button
              type="submit"
              className="w-full bg-blue-600 text-white p-3 rounded hover:bg-blue-700 font-semibold"
            >
              Transport speichern
            </button>
          </div>

        </div>

        {/* Weg in Minuten Anzeige */}
        {wegMin && (
          <div className="bg-white p-4 rounded-lg shadow border text-center">
            <p className="text-lg font-semibold text-gray-700">
              Fahrzeit: <span className="text-blue-600">{wegMin} Minuten</span>
            </p>
          </div>
        )}
      </form>
    </div>
  );
}


