export default function Home() {
  const features = [
    { title: "Transportplanung & Verwaltung", desc: "Erstellung & Steuerung von Transporten", icon: "🚛" },
    { title: "Rundtouren & Mehrfachtransporte", desc: "Kombination ähnlicher Transporte", icon: "🔁" },
    { title: "Transportstatus aktualisieren", desc: "Fahrer-Updates zu Transporten & Fehlererkennung integriert", icon: "📦" },
    { title: "Logbuch & Historie", desc: "Änderungen & Aktivitäten verfolgen", icon: "📘" },
    { title: "Auswertung & Statistik", desc: "Analyse & Berichte zu Transporten", icon: "📊" },
    { title: "Administration", desc: "Benutzerrollen, Schichtplanung & Transportmatrix", icon: "🛠️" }
  ];

  return (
    <div className="min-h-screen p-8 bg-gray-100">
      <h1 className="text-4xl font-bold mb-10 text-center">Logistiksoftware Dashboard</h1>
      <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 max-w-screen-xl mx-auto">
        {features.map((feature, index) => (
          <button
            key={index}
            onClick={() => alert(`${feature.title} wird bald verfügbar sein.`)}
            className="bg-white h-full text-left p-6 rounded-2xl shadow hover:shadow-xl transition border border-gray-200 hover:bg-blue-50 flex flex-col justify-between"
          >
            <div className="text-4xl mb-3">{feature.icon}</div>
            <div>
              <h2 className="text-lg font-bold mb-1">{feature.title}</h2>
              <p className="text-sm text-gray-600">{feature.desc}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}


