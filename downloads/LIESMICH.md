# Downloadordner

Hier liegen die PDF- und EPUB-Dateien. Welche Datei zu welchem Werk gehört, steht
in `../data/werke.json` im Feld `dateien`.

## Erwartete Dateinamen

| Werk | Dateien |
|---|---|
| Landkarte der Realität | `landkarte-der-realitaet.pdf` · `landkarte-der-realitaet.epub` |
| Chroniken I — Der Schatten über Dreamland | `chroniken-1-schatten-ueber-dreamland.pdf` · `.epub` |
| Chroniken II — Der König des dichten Unterholzes | `chroniken-2-koenig-des-dichten-unterholzes.pdf` · `.epub` |
| Chroniken III — Das Tier im Menschen | `chroniken-3-das-tier-im-menschen.pdf` · `.epub` |
| Chroniken IV — Was das Licht verspricht | noch keine Datei hinterlegt |
| Chroniken V — Der Nullpunkt | noch keine Datei hinterlegt |
| Autopsien der Schatten, Sektion A | `autopsien-der-schatten-sektion-a.pdf` · `.epub` |

Andere Namen sind kein Problem — dann einfach den Pfad in `data/werke.json`
anpassen und `python3 _build/build.py` laufen lassen.

## Solange eine Datei fehlt

Der Downloadknopf erscheint ausgegraut, mit dem Hinweis, dass das Format noch
nicht abgelegt ist. Die Seite funktioniert normal weiter. Sobald die Datei hier
liegt und neu gebaut wurde, wird der Knopf aktiv.

## Hinweis zu GitHub

Für Dateien über 50 MB warnt GitHub, ab 100 MB lehnt es sie ab. Falls ein PDF so
groß wird: entweder mit `gs` oder `qpdf` verkleinern, oder die Datei über GitHub
Releases bereitstellen und in `data/werke.json` die vollständige URL eintragen —
das Feld `datei` akzeptiert auch `https://…`.
