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

# ---------------------------------------------------------------------------
# EINZIGE STELLE FÜR DIE DOMAIN.
# Ändert sich der Hosting-Ort — Repository-Umzug, eigene Domain — genügt eine
# Änderung hier. Sitemap, robots.txt und die og:url/canonical-Angaben
# jeder Seite werden daraus abgeleitet.
#
# Aktuell: das Repository heißt "Syntaxisbuch.github.io" (umbenannt von
# "Syntaxis"), GitHub Pages liefert es deshalb an der Wurzel aus, ohne
# Unterordner. Für eine eigene Domain später: SITE_URL hier ändern und eine
# Datei "CNAME" mit genau der Domain (ohne https://, ohne Pfad) ins
# Wurzelverzeichnis legen — siehe README, Abschnitt "Domain".
# ---------------------------------------------------------------------------
SITE_URL = "https://syntaxisbuch.github.io"

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


def rendere_lr_buch2():
    r = reihe("lr")
    b2 = r["buch2"]
    zeilen = []
    for t in b2["teile"]:
        marke = f'TEIL {t["teil"]}' if t["teil"] else "—"
        hinweis = f'<p class="kennung" style="margin-top:.3rem">{t["hinweis"]}</p>' if t.get("hinweis") else ""
        zeilen.append(f'''<div class="werk">
        <span class="band">{marke}</span>
        <div><h3 style="font-size:1.3rem">{t["titel"]}</h3>{hinweis}</div>
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
        meta = " · ".join(t for t in [
            f'{b["kapitel"]} Kapitel' if b.get("kapitel", 0) > 0 else "", tags] if t)

        zeilen.append(f'''<article class="werk" id="nc-{b["nr"].lower()}">
        <span class="band">BAND {b["nr"]}<br>{b["jahr"]}</span>
        {cover}
        <div>
          <h3>{b["titel"]}</h3>
          <p style="color:var(--bone);margin-bottom:.6rem"><strong>{b["fall"]}</strong> — {b["ort"]}</p>
          <p>{b["text"]}</p>
          {f'<p class="kennung" style="margin-top:.7rem">{meta}</p>' if meta else ""}
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
                   f'<span class="ki-hinweis">KI-generiert</span></a>')
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


def rendere_neuigkeiten():
    D = json.loads((WURZEL / "data" / "neuigkeiten.json").read_text(encoding="utf-8"))
    zeilen = []
    for e in D["eintraege"]:
        datum = e["datum"]
        anzeige = f"{datum[8:10]}.{datum[5:7]}.{datum[0:4]}"
        zeilen.append(f'''<article class="neuigkeit">
          <span class="kennung">{anzeige}</span>
          <div><h3><a href="{e["link"]}">{e["titel"]}</a></h3><p>{e["text"]}</p></div>
        </article>''')
    return "".join(zeilen)


def rendere_quellen():
    D = json.loads((WURZEL / "data" / "quellen.json").read_text(encoding="utf-8"))
    bloecke = []
    for g in D["gruppen"]:
        eintraege = []
        for e in g["eintraege"]:
            kopf = e["name"]
            if e.get("url"):
                kopf = f'<a href="{e["url"]}" target="_blank" rel="noopener">{e["name"]} <span class="ext">↗</span></a>'
            unter = e.get("autor", "")
            eintraege.append(f'''<div class="gleintrag quelle">
              <dt>{kopf}{f'<span class="autor">{unter}</span>' if unter else ""}
                  <span class="kurz">{e["kurz"]}</span></dt>
              <dd>{e["text"]}</dd>
            </div>''')
        bloecke.append(f'''<section class="glgruppe">
          <h3 class="glgruppe-kopf">{g["name"]}<span class="kennung">{len(g["eintraege"])}</span></h3>
          <dl class="glossar">{"".join(eintraege)}</dl>
        </section>''')
    return "".join(bloecke)


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

        elif r["id"] == "lr":
            eintraege.append((
                "Buch 1 — Die Reise", r.get("dateien_buch1"),
                "Acht Bände, der Reihe nach zu lesen — Stand: Etappe 75, 24.09.2026",
                None, r.get("cover")
            ))
            eintraege.append((
                "Buch 2 — Die Werkstatt", r.get("dateien_buch2"),
                "Nachschlagewerk mit Glossar, Modell-Bibliothek und taktischem Kompendium — Stand: Etappe 75, 24.09.2026",
                None, r.get("cover_buch2")
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
    "{{LR_BUCH2}}": rendere_lr_buch2,
    "{{LD_BAENDE}}": rendere_baende_ld,
    "{{AU_PLAN}}": rendere_au_plan,
    "{{NC_BAENDE}}": rendere_baende_nc,
    "{{NC_FIGUREN}}": rendere_figuren,
    "{{AU_FAELLE}}": rendere_faelle,
    "{{AU_SKALA}}": rendere_gefahrenskala,
    "{{DOWNLOADS}}": rendere_downloads,
    "{{F404_STIMMEN}}": rendere_f404_stimmen,
    "{{F404_BAENDE}}": rendere_f404_baende,
    "{{QUELLEN}}": rendere_quellen,
    "{{NEUIGKEITEN}}": rendere_neuigkeiten,
}

# slug: (Titel, Beschreibung, Reihenfarbe, zusätzliche Skripte)
SEITEN = {
    "index":       ("Syntaxis — Ein Projekt &uuml;ber kritisches Denken",
                    "Kostenlose Bücher über kritisches Denken, Mythen und eine Stadt, die gebaut ist wie ein Gehirn. PDF und EPUB unter Creative-Commons-Lizenz.", "", ""),
    "landkarte":   ("Die Landkarte der Realität — Syntaxis",
                    "Das Hauptwerk in zwei Büchern: Buch 1, Die Reise, in acht Bänden vom Rüstzeug des Denkens bis zur Anatomie der Chimäre, dazu Buch 2, Die Werkstatt, als Nachschlagewerk.", "lr", ""),
    "chroniken":   ("Chroniken von Neocortex City — Syntaxis",
                    "Fünf Kriminalromane (drei erschienen, zwei in Arbeit) in einer Stadt, die gebaut ist wie ein menschliches Gehirn. Noir mit belegtem Anhang.", "nc", ""),
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
                    "Was mit den Syntaxis-Werken erlaubt ist: CC BY-NC-ND 4.0 für die Chroniken, CC BY-NC 4.0 für Landkarte und Autopsien.", "", ""),
    "impressum":   ("Impressum und Haftungsausschluss — Syntaxis",
                    "Herausgeber, Kontakt, neurale Assistenz und Haftungsausschluss.", "", ""),
    "frequenz-404": ("Frequenz 404 — Der Piratensender aus Neocortex City",
                    "Cassidy Null, Kevin und Dr. Tacheles streiten sich um drei Uhr nachts durch die Mythen der Stadt. Wöchentlich wechselnde Sendung plus Archiv.", "nc",
                    '<script src="assets/js/frequenz404.js"></script>'),
    "bildband":    ("Das Bildarchiv — Syntaxis",
                    "Mnemosynes Bildarchiv: Stadtansichten und Schauplätze, an der Wand aufgereiht und mit rotem Faden verbunden.", "",
                    '<script src="assets/js/bildband.js"></script>'),
    "glossar":     ("Glossar — Syntaxis",
                    "Signatur, Terrasse, Asservat, Toleranz-Zone: 35 Begriffe aus den Werken und der Stadt, durchsuchbar.", "",
                    '<script src="assets/js/glossar.js"></script>'),
    "quellen":     ("Quellenverzeichnis — Syntaxis",
                    "GWUP, Mimikama, Psiram, Hoaxilla und weiterführende Bücher: die realen Institutionen und Werke hinter dem Ansatz von Syntaxis.", "lr", ""),
    "neuigkeiten": ("Neuigkeiten — Syntaxis",
                    "Was zuletzt dazukam: neue Folgen, neue Bereiche, neue Werke — chronologisch, mit RSS-Feed.", "", ""),
    "404":         ("Seite nicht gefunden — Syntaxis",
                    "Diese Adresse liegt außerhalb des Koordinatensystems.", "", ""),
}


def seiten_url(slug):
    """Kanonische Adresse einer Seite. index.html liegt an der Wurzel ohne Dateinamen."""
    return SITE_URL + "/" if slug == "index" else f"{SITE_URL}/{slug}.html"


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
                .replace("{{URL}}", seiten_url(slug))
                .replace("{{OGBILD}}", SITE_URL + "/assets/img/og.png")
                .replace("{{INHALT}}", inhalt))
        (WURZEL / f"{slug}.html").write_text(html, encoding="utf-8")
        gebaut += 1
        print(f"  {slug}.html")
    print(f"\n{gebaut} Seiten gebaut.")
    return gebaut


def schreibe_sitemap():
    """sitemap.xml aus SEITEN — nie mehr von Hand nachpflegen, nie mehr veraltet."""
    prio = {"index": "1.0", "downloads": "0.9", "atlas": "0.8",
            "werkzeuge": "0.8", "gegenfragen": "0.8", "glossar": "0.6"}
    zeilen = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for slug in SEITEN:
        if slug == "404":
            continue
        zeilen.append(
            f"  <url><loc>{seiten_url(slug)}</loc><changefreq>monthly</changefreq>"
            f"<priority>{prio.get(slug, '0.7')}</priority></url>")
    zeilen.append("</urlset>")
    (WURZEL / "sitemap.xml").write_text("\n".join(zeilen) + "\n", encoding="utf-8")
    print("  sitemap.xml")


def schreibe_robots():
    (WURZEL / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    print("  robots.txt")


def umleitungsseite(ziel):
    """Eine einzelne Weiterleitungsseite. ziel ist der Pfad ab der Domain-Wurzel,
    leer für die Startseite. Leitet per JavaScript weiter (behält #Sprungmarken
    und ?Parameter der alten Adresse) und per <noscript>-Meta-Refresh als Rückfall."""
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Seite umgezogen — Syntaxis</title>
<meta name="robots" content="noindex,follow">
<noscript><meta http-equiv="refresh" content="0; url=/{ziel}"></noscript>
<script>location.replace("/{ziel}" + location.hash + location.search);</script>
<style>
  body{{background:#0C1519;color:#DDE2DC;font-family:Georgia,serif;display:flex;
       align-items:center;justify-content:center;min-height:100vh;margin:0;padding:2rem;
       text-align:center}}
  a{{color:#3FA8A0}}
  p{{max-width:32rem;line-height:1.6;font-size:1.05rem}}
</style>
</head>
<body>
<p>Diese Seite ist umgezogen.<br>Falls die Weiterleitung nicht von selbst startet:
<a href="/{ziel}">weiter zu syntaxisbuch.github.io/{ziel}</a></p>
</body>
</html>'''


def schreibe_umleitungen():
    """Alter Pfad /Syntaxis/… → neue Wurzeladresse, Seite für Seite.

    Nach der Repository-Umbenennung (siehe README, Abschnitt „Domain“) existiert
    der Projektordner /Syntaxis/ nicht mehr, unter dem die Seite bis dahin lief.
    Jede dort verlinkte oder mit Lesezeichen versehene Unterseite würde sonst auf
    eine 404 laufen — nicht nur die Startseite. Für jede reguläre Seite entsteht
    deshalb hier ein winziger Umleiter am alten Ort, der project- und dateiweit
    automatisch mitwächst: taucht ein neuer Eintrag in SEITEN auf, bekommt er
    beim nächsten Bauen seinen Umleiter dazu, ohne dass das hier angefasst wird.
    """
    ordner = WURZEL / "Syntaxis"
    ordner.mkdir(exist_ok=True)
    ziele = {slug: ("" if slug == "index" else f"{slug}.html")
             for slug in SEITEN if slug != "404"}
    for slug, ziel in ziele.items():
        datei = "index.html" if slug == "index" else f"{slug}.html"
        (ordner / datei).write_text(umleitungsseite(ziel), encoding="utf-8")
    print(f"  Syntaxis/ — {len(ziele)} Umleitungen")


def schreibe_feed():
    """RSS 2.0 aus data/neuigkeiten.json — dieselbe Datei speist auch die
    Neuigkeiten-Seite. Ein neuer Eintrag dort taucht hier automatisch auf,
    ohne dass die Feed-Datei je von Hand angefasst werden muss."""
    D = json.loads((WURZEL / "data" / "neuigkeiten.json").read_text(encoding="utf-8"))
    def rfc822(datum):
        j, m, t = int(datum[:4]), int(datum[5:7]), int(datum[8:10])
        MON = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        return f"{t:02d} {MON[m-1]} {j} 12:00:00 +0000"
    def esc(s):
        return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    items = []
    for e in D["eintraege"]:
        link = seiten_url(e["link"].replace(".html", "")) if e["link"] != "index.html" else SITE_URL + "/"
        items.append(f'''  <item>
    <title>{esc(e["titel"])}</title>
    <link>{link}</link>
    <guid isPermaLink="false">{e["datum"]}-{esc(e["titel"])}</guid>
    <pubDate>{rfc822(e["datum"])}</pubDate>
    <description>{esc(e["text"])}</description>
  </item>''')
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>Syntaxis — Neuigkeiten</title>
  <link>{SITE_URL}/neuigkeiten.html</link>
  <description>Neue Folgen, Bereiche und Werke bei Syntaxis — einem Projekt über kritisches Denken.</description>
  <language>de-de</language>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(items)}
</channel>
</rss>
'''
    (WURZEL / "feed.xml").write_text(xml, encoding="utf-8")
    print("  feed.xml")


if __name__ == "__main__":
    print("Syntaxis — Seiten werden gebaut:\n")
    baue()
    schreibe_sitemap()
    schreibe_robots()
    schreibe_umleitungen()
    schreibe_feed()
