#!/usr/bin/env python3
"""
Syntaxis - Ein Projekt &uuml;ber kritisches Denken — Seitengenerator.

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
        return '<p class="dateihinweis">Noch keine Datei hinterlegt — dieser Band ist in Arbeit.</p>'
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
        '<p class="dateihinweis">Grau hinterlegte Formate sind noch nicht abgelegt.</p>')
    return f'<div class="dl">{"".join(teile)}</div>{hinweis}'


def rendere_baende_ld():
    r = reihe("ld")
    zeilen = []
    for b in r["baende"]:
        zeilen.append(f'''<div class="werk">
        <span class="band">BAND {b["nr"]}</span>
        <div><h3>{b["titel"]}</h3><p>{b["inhalt"]}</p></div>
        <span class="status">geplant</span>
      </div>''')
    return '<div class="werkliste">' + "".join(zeilen) + "</div>"


def rendere_au_plan():
    plan = json.loads((WURZEL / "data" / "autopsie-plan.json").read_text(encoding="utf-8"))
    blöcke = []
    for s in plan["sektionen"]:
        fertig = s.get("status") == "abgeschlossen"
        eintraege = []
        for f in s["faelle"]:
            u = '<span class="u">— ' + f["unter"] + "</span>" if f["unter"] else ""
            h = '<span class="hw">' + f["notiz"] + "</span>" if f["notiz"] else ""
            eintraege.append(
                '<li><span class="n">%03d</span><span class="t">%s %s%s</span></li>'
                % (f["nr"], f["titel"], u, h))
        offen = " open" if fertig else ""
        stand = "abgeschlossen" if fertig else "geplant"
        blöcke.append(
            '<details class="sektion"%s><summary>'
            '<span class="mark">SEKTION %s</span><span class="nm">%s</span>'
            '<span class="zz">%d Fälle · %s</span></summary>'
            '<p class="unter-s">%s</p><ol class="planliste">%s</ol></details>'
            % (offen, s["id"], s["name"], len(s["faelle"]), stand,
               s.get("unter", ""), "".join(eintraege)))
    return "".join(blöcke)


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

        cover = ""
        if b.get("cover"):
            cover = f'''<figure class="chroniken-bandcover">
            <img src="{b["cover"]}"
                 alt="Band {b["nr"]} – {b["titel"]}"
                 loading="lazy">
          </figure>'''

        verfuegbar = "verfuegbar" if st == "verfügbar" else ""

        zeilen.append(f'''<article class="werk" id="nc-{b["nr"].lower()}">
        <span class="band">BAND {b["nr"]}<br>{b["jahr"]}</span>
        {cover}
        <div>
          <h3>{b["titel"]}</h3>
          <p style="color:var(--bone);margin-bottom:.6rem"><strong>{b["fall"]}</strong> — {b["ort"]}</p>
          <p>{b["text"]}</p>
          <p class="kennung" style="margin-top:.7rem">{b["kapitel"]} Kapitel · {tags}</p>
          {dateiliste(b.get("dateien"), b["titel"])}
        </div>
        <span class="status" data-s="{verfuegbar}">{st}</span>
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
        cov = ""
        if f.get("cover"):
            cov = (f'<a class="fallcover" href="{f["cover"]}" target="_blank" rel="noopener" '
                   f'aria-label="Cover vergrößern: {f["titel"]}">'
                   f'<img src="{f.get("cover_klein", f["cover"])}" alt="Cover der Autopsie {f["nr"]:02d} — {f["titel"]}" loading="lazy" decoding="async">'
                   f'</a>')
        zeilen.append(f'''<article class="fall{" mit-cover" if cov else ""}" id="au-{f["nr"]}">
        <span class="nr">{f["nr"]:02d}</span>
        {cov}
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
                eintraege.append((
                    f'Band {b["nr"]} — {b["titel"]}',
                    b.get("dateien"),
                    b["fall"],
                    None,
                    b.get("cover")
                ))

        elif r["id"] == "au":
            inhalt = "".join(
                f'<li><span class="n">{f["nr"]:02d}</span>'
                f'<span class="tt">{f["titel"]} '
                f'<span class="leise">— {f["unter"]}</span></span>'
                f'</li>'
                for f in r["faelle"]
            )
            inhalt = (
                f'<div class="enthalten">'
                f'<span class="kennung">ENTHÄLT ZEHN FALLAKTEN</span>'
                f'<ol class="inhaltsliste">{inhalt}</ol>'
                f'</div>'
            )

            eintraege.append((
                r["titel"] + ", Sektion A",
                r.get("dateien"),
                r["claim"],
                inhalt,
                r.get("cover")
            ))

        else:
            eintraege.append((
                r["titel"],
                r.get("dateien"),
                r["claim"],
                None,
                r.get("cover")
            ))

        rows = "".join(
            f'''<div class="werk karte-werk{" mit-cover" if cover else ""}">
              <span class="band">{r["kennung"]}</span>
              {f'<div class="download-cover"><img src="{cover}" alt="{t}" loading="lazy"></div>' if cover else ""}
              <div>
                <h3 style="font-size:1.25rem">{t}</h3>
                <p>{u}</p>
                {dateiliste(d, t)}
                {x or ""}
              </div>
              <span class="status">{liz["kurz"]}</span>
            </div>'''
            for t, d, u, x, cover in eintraege
        )

        blöcke.append(
            f'''<section class="stratum reihenblock"
                data-reihe="{r["id"]}"
                data-reihenname="{r["titel"]}"
                style="padding-block:2.75rem">
              <div class="wrap">
                <div class="stratum-kopf">
                  <span class="reihenmarke">{r["kennung"]}</span>
                  <h3 style="font-size:1.7rem;margin:0">{r["titel"]}</h3>
                  <span class="hoehe">{liz["kurz"]}</span>
                </div>
                <div class="werkliste">{rows}</div>
              </div>
            </section>'''
        )

    return "".join(blöcke)


def rendere_f404():
    D = json.loads((WURZEL / "data" / "frequenz404.json").read_text(encoding="utf-8"))
    aus = []
    for f in D["folgen"]:
        zeilen = []
        for s in f["transkript"]:
            werbung = s["sprecher"] == "WERBUNG"
            regie = f'<span class="regie">{s["regie"]}</span>' if s["regie"] else ""
            zeilen.append(
                '<div class="funkzeile%s"><span class="sprecher">%s</span>'
                '<div class="rede">%s<p>%s</p></div></div>'
                % (" werbeblock" if werbung else "", s["sprecher"], regie, s["text"]))
        au = next((x for x in reihe("au")["faelle"] if x["nr"] == f.get("autopsie")), None)
        shownote = ""
        if au:
            shownote = ('<div class="shownotes"><span class="kennung">SHOWNOTES</span>'
                        '<p>Die vollständige Akte zu dieser Sendung: '
                        f'<a href="autopsien.html#au-{au["nr"]}">Autopsie #{au["nr"]:02d} — {au["titel"]}</a>. '
                        'Dort stehen die Belege, die Cassidy im Studio nur behauptet.</p></div>')
        aus.append(f'''<article class="sendung" id="{f["id"]}">
          <header class="sendungskopf">
            <span class="kennung">SENDUNG {f["nummer"]} · {f["zeit"]} · {f["dauer"]}</span>
            <h3>{f["titel"]}</h3>
            <p class="setting">{f["setting"]}</p>
            <p class="signal">[{f["signal"]}]</p>
          </header>
          <div class="funkprotokoll">{"".join(zeilen)}</div>
          <p class="signal ende">[{f["ausklang"]}]</p>
          {shownote}
        </article>''')
    return "".join(aus)


def rendere_f404_stimmen():
    D = json.loads((WURZEL / "data" / "frequenz404.json").read_text(encoding="utf-8"))
    z = "".join(
        f'<div class="zelle"><span class="kennung">{s["rolle"].upper()}</span>'
        f'<h4>{s["name"]}</h4><p>{s["notiz"]}</p></div>' for s in D["reihe"]["stimmen"])
    return f'<div class="raster drei">{z}</div>'


def rendere_f404_baende():
    D = json.loads((WURZEL / "data" / "frequenz404.json").read_text(encoding="utf-8"))
    z = "".join(
        f'<div class="werk"><span class="band">BAND {e["band"]}</span>'
        f'<div><h3 style="font-size:1.2rem">{e["titel"]}</h3><p>{e["notiz"]}</p></div></div>'
        for e in D["aus_den_baenden"])
    return f'<div class="werkliste">{z}</div>'


BAUSTEINE = {
    "{{LR_BAENDE}}": rendere_baende_lr,
    "{{LD_BAENDE}}": rendere_baende_ld,
    "{{AU_PLAN}}": rendere_au_plan,
    "{{NC_BAENDE}}": rendere_baende_nc,
    "{{NC_FIGUREN}}": rendere_figuren,
    "{{AU_FAELLE}}": rendere_faelle,
    "{{AU_SKALA}}": rendere_gefahrenskala,
    "{{DOWNLOADS}}": rendere_downloads,
    "{{F404}}": rendere_f404,
    "{{F404_STIMMEN}}": rendere_f404_stimmen,
    "{{F404_BAENDE}}": rendere_f404_baende,
}

# slug: (Titel, Beschreibung, Reihenfarbe, zusätzliche Skripte)
SEITEN = {
    "index":       ("Syntaxis — Ein Projekt &uuml;ber kritisches Denken",
                    "Kostenlose Bücher über kritisches Denken, Mythen und eine Stadt, die gebaut ist wie ein Gehirn. PDF und EPUB unter Creative-Commons-Lizenz.", "", ""),
    "landkarte":   ("Die Landkarte der Realität — Syntaxis",
                    "Das Hauptwerk: neun Bände über das Handwerk des Prüfens, vom Rüstzeug des Denkens bis zur Anatomie der Chimäre.", "lr", ""),
    "chroniken":   ("Chroniken von Neocortex City — Syntaxis",
                    "Vier Kriminalromane in einer Stadt, die gebaut ist wie ein menschliches Gehirn. Noir mit belegtem Anhang.", "nc", ""),
    "autopsien":   ("Autopsien der Schatten — Syntaxis",
                    "Mythen, seziert nach einem festen Protokoll. Zehn Fallakten sind fertig, 105 in zehn Sektionen sind geplant.", "au", ""),
    "licht":       ("Licht der Realität — Syntaxis",
                    "Ein Mythos als Türöffner, dahinter die Wissenschaft, die ihn auflöst — ein Band je Fachgebiet. In Vorbereitung.", "ld", ""),
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
    "frequenz-404": ("Frequenz 404 — Der Piratensender aus Neocortex City",
                    "Cassidy Null, Kevin und Dr. Tacheles streiten sich um drei Uhr nachts durch die Mythen der Stadt. Bonus zu den Chroniken von Neocortex City.", "nc", ""),
    "bildband":    ("Die Asservatenkammer — Syntaxis",
                    "Akten aus dem Schrank ziehen, Belege an die Pinnwand heften, den roten Faden spannen. Bildarchiv zu Neocortex City und den Fallakten.", "",
                    '<script src="assets/js/bildband.js"></script>'),
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
