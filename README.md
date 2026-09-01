# Syntaxis — Website

Die Projektseite zu **Syntaxis** von Gerald Glaser: vier Reihen über das Prüfen von Behauptungen, kostenfrei als PDF und EPUB, unter Creative-Commons-Lizenz.

Live: <https://syntaxisbuch.github.io/Syntaxis/>
Kontakt: <Syntaxis_Buch@pm.me>

---

## Die Grundidee

Die Seite **ist** die Stadt. Navigation ist Höhe.

Neocortex City ist eine terrassierte Hügelfestung, deren Ebenen realen Hirnregionen entsprechen. Die Website übernimmt dieses Raster: Links läuft ein Höhenmesser von +520 m bis −60 m, und jeder Bereich sitzt auf der Terrasse, deren Funktion zu ihm passt.

| Höhe | Terrasse | Hirnregion | Bereich |
|---:|---|---|---|
| 520 m | Turmspitze | Brodmann-Areal 10 | Startseite |
| 500 m | Oberste | Präfrontaler Kortex | Landkarte der Realität |
| 400 m | Obere-Mittlere | Parietallappen | Licht der Realität |
| 280 m | Mittlere | Verwaltung | Ausgabestelle (Downloads) |
| 180 m | Mittlere-Untere | Hippocampus | Kartographischer Atlas |
| 80 m | Untere | Limbisches System | Chroniken von Neocortex City |
| 20 m | Thalamus Central Station | Thalamus | Gegenfragen-Kartei |
| 0 m | Unterste | Hirnstamm | Das Rüstzeug |
| −60 m | Sub-Unterste | Sonderzugang | Autopsien der Schatten |

---

## Ein neues Werk eintragen

**Alles läuft über eine einzige Datei: `data/werke.json`.** Danach einmal neu bauen.

### Neuer Band einer bestehenden Reihe

In `data/werke.json` bei der passenden Reihe unter `baende` (oder bei den Autopsien unter `faelle`) einen Eintrag ergänzen:

```json
{
  "nr": "V",
  "titel": "Der Nullpunkt",
  "jahr": "2027",
  "kapitel": 40,
  "fall": "Worum es geht",
  "ort": "Sektoren, in denen der Band spielt",
  "text": "Klappentext.",
  "tags": ["Stichwort", "Stichwort"],
  "dateien": [
    { "format": "PDF",  "datei": "downloads/chroniken-5-der-nullpunkt.pdf" },
    { "format": "EPUB", "datei": "downloads/chroniken-5-der-nullpunkt.epub" }
  ]
}
```

Dann die Dateien nach `downloads/` legen und bauen:

```bash
python3 _build/build.py
```

Solange eine Datei fehlt, erscheint der Knopf ausgegraut mit einem Hinweis — die Seite bricht nicht. Sobald die Datei da ist, wird der Knopf beim nächsten Bauen automatisch aktiv.

### Ganz neue Reihe

Ein neues Objekt in `reihen` anlegen. Wichtig sind `id`, `kennung`, `titel`, `terrasse`, `z`, `lizenz` und `seite`. Dann:

1. Ein Fragment `_build/pages/<slug>.html` anlegen (am einfachsten `licht.html` kopieren).
2. In `_build/build.py` im Wörterbuch `SEITEN` eine Zeile mit Titel und Beschreibung ergänzen.
3. In `assets/js/core.js` die Reihe in `EBENEN` eintragen, damit sie im Höhenmesser erscheint.
4. In `assets/css/syntaxis.css` einen Akzent unter `body[data-reihe="…"]` definieren.
5. Bauen.

---

## Aufbau

```
├── index.html … 404.html      erzeugte Seiten — nicht direkt bearbeiten
├── _build/
│   ├── build.py               Generator: python3 _build/build.py
│   ├── layout.html            Rahmen (Kopf, Fuß, Höhenmesser, Suche)
│   └── pages/*.html           Seiteninhalte — hier wird bearbeitet
├── assets/
│   ├── css/syntaxis.css       gesamtes Gestaltungssystem
│   ├── js/core.js             Höhenmesser, Menü, Suche
│   ├── js/atlas.js            Karte, Sektordetails, Wegzeitrechner
│   ├── js/werkzeuge.js        Red-Flag-Prüfung, Protokoll, Kartenkasten
│   └── js/gegenfragen.js      Kartei mit Suche und Filter
├── data/
│   ├── werke.json             ► Werkregister, steuert die ganze Seite
│   ├── stadt.json             27 Sektoren, Brücken, Turm, Geschwindigkeiten
│   ├── werkzeuge.json         Red Flags, Autopsie-Protokoll, Kartenkasten
│   └── gegenfragen.json       115 Karten aus den Quick-Reference-Tabellen
└── downloads/                 hier kommen PDF und EPUB hinein
```

Bearbeitet werden nur `_build/pages/`, `data/`, `assets/`. Die HTML-Dateien im Wurzelverzeichnis werden vom Generator überschrieben.

---

## Lokal ansehen

JSON-Dateien lädt kein Browser aus dem Dateisystem. Deshalb ein kleiner Server:

```bash
cd Syntaxis
python3 -m http.server 8000
```

Dann <http://localhost:8000> öffnen.

## Veröffentlichen

GitHub Pages im Repository unter *Settings → Pages* auf Branch `main`, Ordner `/ (root)` stellen. Die Datei `.nojekyll` liegt bereits bei; sie verhindert, dass GitHub die Dateien durch Jekyll schickt.

---

## Was diese Seite kann

- **Höhenmesser-Navigation** — die Ebenen der Stadt als Seitenstruktur, mit Tastaturbedienung
- **Suche** — `/` oder `Strg`+`K`; findet Werke, Sektoren, Denkwerkzeuge und Signaturen wie `LR-I-1.2.3` oder `NK-01`
- **Kartographischer Atlas** — Grundriss je Terrasse aus den echten X/Y-Koordinaten, Sektordetails mit neuroanatomischer Entsprechung und körperlichen Kosten, Wegzeitrechner nach den Geschwindigkeiten aus dem Kanon
- **Red-Flag-Prüfung** — dreizehn Warnzeichen als Prüfliste mit Befund
- **Autopsie-Protokoll** — neunzehn Punkte als Arbeitsbogen, mit Textexport
- **Kartenkasten** — 32 Denkwerkzeuge mit Signatur, filterbar
- **Gegenfragen-Kartei** — 115 Karten, durchsuchbar und nach Fall filterbar
- **Einstiegs-Assistent** — zwei Fragen, ein Lesevorschlag

Ohne Konten, ohne Werbung, ohne Analysewerkzeuge, ohne Cookies. Die Eingaben in den Werkzeugen bleiben im Browser (`localStorage`) und werden nicht übertragen.

### Schriften lokal einbinden

Standardmäßig lädt die Seite Instrument Serif, Spectral und Azeret Mono von Google Fonts. Wer das vermeiden will, lädt die Dateien herunter, legt sie unter `assets/fonts/` ab und ersetzt in `_build/layout.html` den `<link>` auf `fonts.googleapis.com` durch eigene `@font-face`-Regeln. Danach den Datenschutzabschnitt in `_build/pages/impressum.html` anpassen und neu bauen.

---

## Lizenz

**Inhalte** (Texte, Werke, Daten): siehe [Lizenz und Nutzung](lizenz.html).
Landkarte der Realität und Autopsien der Schatten: CC BY-NC-SA 4.0.
Chroniken von Neocortex City: CC BY-NC-ND 4.0.

**Quelltext dieser Website** (HTML, CSS, JavaScript, Generator): MIT, siehe `LICENSE`.

Neurale Assistenz bei Werken und Website: Anthropic Claude und Google Gemini. Cover und Stadtkarte: ChatGPT.
