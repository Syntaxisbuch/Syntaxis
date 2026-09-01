#!/usr/bin/env python3
"""
Syntaxis — Seitengenerator.

Setzt die fertigen HTML-Dateien im Wurzelverzeichnis aus
_build/layout.html und den Fragmenten in _build/pages/ zusammen.

Aufruf:  python3 _build/build.py
"""
import json
import re
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
LAYOUT = (WURZEL / "_build" / "layout.html").read_text(encoding="utf-8")
PAGES = WURZEL / "_build" / "pages"
WERKE = json.loads((WURZEL / "data" / "werke.json").read_text(encoding="utf-8"))

ROEM = {"1": "I", "2": "II", "3": "III", "4": "IV"}


def reihe(rid):
    return next(r for r in WERKE["reihen"] if r["id"] == rid)


def dateiliste(dateien, prefix=""):
    """Downloadknöpfe. Fehlende Dateien werden sichtbar, aber inaktiv gesetzt."""
    if not dateien:
        return ('<p class="kennung" style="margin-top:.9rem">Noch keine Datei hinterlegt — '
                'dieser Band ist in Arbeit.</p>')
    teile = []
    for d in dateien:
        extern = d["datei"].startswith(("http://", "https://"))
        da = extern or (WURZEL / d["datei"]).exists()
        label = d.get("label", prefix + " " + d["format"])
        aus = "" if da else ' aria-disabled="true"'
        teile.append(
            f'<a href="{d["datei"]}"{aus} download>'
            f'<span class="f">{d["format"]}</span>{label}</a>')
    def vorhanden(d):
        return d["datei"].startswith(("http://", "https://")) or (WURZEL / d["datei"]).exists()
    hinweis = "" if all(vorhanden(d) for d in dateien) else (
        '<p class="kennung" style="margin-top:.6rem">Grau hinterlegte Formate sind noch nicht abgelegt.</p>')
    return f'<div class="dl">{"".join(teile)}</div>{hinweis}'


def rendere_baende_lr():
    r = reihe("lr")
    zeilen = []
    for b in r["baende"]:
        zeilen.append(f'''<div class="werk">
        <span class="band">BAND {b["nr"]}</span>
        <div><h3>{b["titel"]}</h3><p>{b["inhalt"]}</p></div>
        <span class="status">LR-{b["nr"]}</span>
      </div>''')
    return '<div class="werkliste">' + "".join(zeilen) + "</div>"


def rendere_baende_nc():
    r = reihe("nc")
    zeilen = []
    for b in r["baende"]:
        tags = " · ".join(b.get("tags", []))
        st = b.get("status", "verfügbar")
        zeilen.append(f'''<article class="werk" id="nc-{b["nr"].lower()}">
        <span class="band">BAND {b["nr"]}<br>{b["jahr"]}</span>
        <div>
          <h3>{b["titel"]}</h3>
          <p style="color:var(--bone);margin-bottom:.6rem"><strong>{b["fall"]}</strong> — {b["ort"]}</p>
          <p>{b["text"]}</p>
          <p class="kennung" style="margin-top:.7rem">{b["kapitel"]} Kapitel · {tags}</p>
          {dateiliste(b.get("dateien"), b["titel"])}
        </div>
        <span class="status" data-s="{"verfuegbar" if st == "verfügbar" else ""}">{st}</span>
      </article>''')
    return '<div class="werkliste">' + "".join(zeilen) + "</div>"


def rendere_figuren():
    r = reihe("nc")
    zellen = "".join(
        f'<div class="zelle"><span class="kennung">{f["ort"]}</span>'
        f'<h4>{f["name"]}</h4><p style="color:var(--bone);margin-bottom:.4rem">{f["rolle"]}</p>'
        f'<p>{f["notiz"]}</p></div>' for f in r["figuren"])
    return f'<div class="raster drei">{zellen}</div>'


def rendere_faelle():
    r = reihe("au")
    zeilen = []
    for f in r["faelle"]:
        balken = "".join(f'<i class="{"an" if i < f["level"] else ""}"></i>' for i in range(5))
        stufe = next(s for s in r["gefahrenskala"] if s["level"] == f["level"])
        zeilen.append(f'''<article class="fall" id="au-{f["nr"]}">
        <span class="nr">{f["nr"]:02d}</span>
        <div>
          <h3>{f["titel"]}</h3>
          <p class="unter">{f["unter"]}</p>
          <p class="kern">{f["kern"]}</p>
          <p class="kennung" style="margin-top:.6rem">Ursprung: {f["ursprung"]} · Ton: {f["ton"]}</p>
        </div>
        <span class="stufe" data-l="{f["level"]}" title="{stufe["text"]}">
          <span class="balken">{balken}</span> L{f["level"]} {stufe["name"]}
        </span>
      </article>''')
    return "".join(zeilen)


def rendere_gefahrenskala():
    r = reihe("au")
    zeilen = "".join(
        f'<tr><td class="zahl">L{s["level"]}</td><td><strong>{s["name"]}</strong></td>'
        f'<td class="leise">{s["text"]}</td></tr>' for s in r["gefahrenskala"])
    return (f'<table class="daten"><thead><tr><th>Stufe</th><th>Bezeichnung</th>'
            f'<th>Bedeutung</th></tr></thead><tbody>{zeilen}</tbody></table>')


def rendere_downloads():
    blöcke = []
    for r in WERKE["reihen"]:
        liz = WERKE["lizenzen"][r["lizenz"]]
        eintraege = []
        if r["id"] == "nc":
            for b in r["baende"]:
                eintraege.append((f'Band {b["nr"]} — {b["titel"]}', b.get("dateien"), b["fall"]))
        else:
            eintraege.append((r["titel"], r.get("dateien"), r["claim"]))
        rows = "".join(f'''<div class="werk">
          <span class="band">{r["kennung"]}</span>
          <div><h3 style="font-size:1.25rem">{t}</h3><p>{u}</p>{dateiliste(d, t)}</div>
          <span class="status">{liz["kurz"]}</span>
        </div>''' for t, d, u in eintraege)
        blöcke.append(f'''<section class="stratum" style="padding-block:2.5rem"><div class="wrap">
          <div class="stratum-kopf"><h3 style="font-size:1.6rem">{r["titel"]}</h3>
          <span class="hoehe">{liz["kurz"]}</span></div>
          <div class="werkliste">{rows}</div></div></section>''')
    return "".join(blöcke)


BAUSTEINE = {
    "{{LR_BAENDE}}": rendere_baende_lr,
    "{{NC_BAENDE}}": rendere_baende_nc,
    "{{NC_FIGUREN}}": rendere_figuren,
    "{{AU_FAELLE}}": rendere_faelle,
    "{{AU_SKALA}}": rendere_gefahrenskala,
    "{{DOWNLOADS}}": rendere_downloads,
}

# slug: (Titel, Beschreibung, Reihenfarbe, zusätzliche Skripte)
SEITEN = {
    "index":       ("Syntaxis — Vier Reihen über das Prüfen von Behauptungen",
                    "Kostenlose Bücher über kritisches Denken, Mythen und eine Stadt, die gebaut ist wie ein Gehirn. PDF und EPUB unter Creative-Commons-Lizenz.", "", ""),
    "landkarte":   ("Die Landkarte der Realität — Syntaxis",
                    "Das Hauptwerk: neun Bände über das Handwerk des Prüfens, vom Rüstzeug des Denkens bis zur Anatomie der Chimäre.", "lr", ""),
    "chroniken":   ("Chroniken von Neocortex City — Syntaxis",
                    "Vier Kriminalromane in einer Stadt, die gebaut ist wie ein menschliches Gehirn. Noir mit belegtem Anhang.", "nc", ""),
    "autopsien":   ("Autopsien der Schatten — Syntaxis",
                    "Zehn Mythen, seziert nach einem festen Protokoll. Von der flachen Erde bis zur Simulationshypothese.", "au", ""),
    "licht":       ("Licht der Realität — Syntaxis",
                    "Die naturwissenschaftliche und experimentelle Reihe. In Vorbereitung.", "ld", ""),
    "atlas":       ("Kartographischer Atlas von Neocortex City — Syntaxis",
                    "Die Stadt als begehbares Gehirn: 27 Sektoren mit echten Koordinaten, Höhenschnitt, Wegzeiten und neuroanatomischer Entsprechung.", "",
                    '<script src="assets/js/atlas.js"></script>'),
    "werkzeuge":   ("Das Rüstzeug — Syntaxis",
                    "Red-Flag-Prüfung, Autopsie-Protokoll und ein Kartenkasten mit den Werkzeugen aus der Landkarte der Realität.", "lr",
                    '<script src="assets/js/werkzeuge.js"></script>'),
    "gegenfragen": ("Gegenfragen-Kartei — Syntaxis",
                    "115 verbreitete Behauptungen, die Falle dahinter und je eine Gegenfrage, die weiterführt statt zu belehren.", "au",
                    '<script src="assets/js/gegenfragen.js"></script>'),
    "downloads":   ("Downloads — Syntaxis",
                    "Alle Syntaxis-Werke als PDF und EPUB, kostenlos und unter Creative-Commons-Lizenz.", "", ""),
    "lizenz":      ("Lizenz und Nutzung — Syntaxis",
                    "Was mit den Syntaxis-Werken erlaubt ist: CC BY-NC-ND 4.0 für die Chroniken, CC BY-NC-SA 4.0 für Landkarte und Autopsien.", "", ""),
    "impressum":   ("Impressum und Haftungsausschluss — Syntaxis",
                    "Herausgeber, Kontakt, neurale Assistenz und Haftungsausschluss.", "", ""),
    "404":         ("Seite nicht gefunden — Syntaxis",
                    "Diese Adresse liegt außerhalb des Koordinatensystems.", "", ""),
}


def baue():
    gebaut = 0
    for slug, (titel, beschr, reihenfarbe, skripte) in SEITEN.items():
        frag = PAGES / f"{slug}.html"
        if not frag.exists():
            print(f"  fehlt: {frag.name}", file=sys.stderr)
            continue
        inhalt = frag.read_text(encoding="utf-8")
        for marke, fn in BAUSTEINE.items():
            if marke in inhalt:
                inhalt = inhalt.replace(marke, fn())
        html = (LAYOUT
                .replace("{{TITEL}}", titel)
                .replace("{{BESCHREIBUNG}}", beschr)
                .replace("{{REIHE}}", reihenfarbe)
                .replace("{{SLUG}}", slug)
                .replace("{{SKRIPTE}}", skripte)
                .replace("{{INHALT}}", inhalt))
        (WURZEL / f"{slug}.html").write_text(html, encoding="utf-8")
        gebaut += 1
        print(f"  {slug}.html")
    print(f"\n{gebaut} Seiten gebaut.")


if __name__ == "__main__":
    print("Syntaxis — Seiten werden gebaut:\n")
    baue()
