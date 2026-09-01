/* SYNTAXIS — Grundfunktionen: Höhenmesser, Menü, Suche */
(() => {
  "use strict";

  /* Die Ebenen der Stadt sind zugleich die Ebenen der Website.
     z = Meter über dem Stadt-Basisdatum. */
  const EBENEN = [
    { z:  520, slug: "index",       titel: "Turmspitze",              unter: "Start und Übersicht",             href: "index.html" },
    { z:  500, slug: "landkarte",   titel: "Landkarte der Realität",  unter: "Oberste Terrasse — Vernunft",     href: "landkarte.html", c: "lr" },
    { z:  400, slug: "licht",       titel: "Licht der Realität",      unter: "Obere-Mittlere — Messung",        href: "licht.html",     c: "ld" },
    { z:  280, slug: "downloads",   titel: "Ausgabestelle",           unter: "Mittlere Terrasse — Verwaltung",  href: "downloads.html" },
    { z:  180, slug: "atlas",       titel: "Kartographischer Atlas",  unter: "Mittlere-Untere — Gedächtnis",    href: "atlas.html" },
    { z:   80, slug: "chroniken",   titel: "Chroniken von Neocortex City", unter: "Untere Terrasse — Trieb",    href: "chroniken.html", c: "nc" },
    { z:   20, slug: "gegenfragen", titel: "Gegenfragen-Kartei",      unter: "Thalamus Central Station",        href: "gegenfragen.html" },
    { z:    0, slug: "werkzeuge",   titel: "Das Rüstzeug",            unter: "Unterste Terrasse — Grundfunktionen", href: "werkzeuge.html" },
    { z:  -60, slug: "autopsien",   titel: "Autopsien der Schatten",  unter: "Sub-Unterste — Seziersaal",       href: "autopsien.html", c: "au" }
  ];

  const seite = document.body.dataset.seite || "";
  const ZMAX = 520, ZMIN = -60;

  /* ---------- Höhenmesser ---------- */
  const skala = document.getElementById("hmSkala");
  if (skala) {
    EBENEN.forEach(e => {
      const p = (ZMAX - e.z) / (ZMAX - ZMIN);
      const a = document.createElement("a");
      a.className = "hm-stop";
      a.href = e.href;
      a.style.top = (p * 100) + "%";
      if (e.c) a.dataset.c = e.c;
      if (e.slug === seite) a.setAttribute("aria-current", "page");
      a.innerHTML = `<span class="pkt"></span><span class="tip"><b>${e.titel}</b><span class="z">${e.z} m</span></span>`;
      a.setAttribute("aria-label", `${e.titel}, ${e.z} Meter`);
      skala.appendChild(a);
    });
  }

  /* ---------- Mobilnavigation ---------- */
  const liste = document.getElementById("mobilnavListe");
  if (liste) {
    EBENEN.forEach(e => {
      const li = document.createElement("li");
      li.innerHTML = `<a href="${e.href}"${e.slug === seite ? ' aria-current="page"' : ""}><span>${e.titel}</span><span class="z">${e.z} m</span></a>`;
      liste.appendChild(li);
    });
    ["lizenz.html|Lizenz und Nutzung", "impressum.html|Impressum"].forEach(s => {
      const [href, t] = s.split("|");
      const li = document.createElement("li");
      li.innerHTML = `<a href="${href}"><span>${t}</span><span class="z">—</span></a>`;
      liste.appendChild(li);
    });
  }
  const menuAuf = document.getElementById("menuAuf"), mobilnav = document.getElementById("mobilnav");
  menuAuf?.addEventListener("click", () => {
    const offen = mobilnav.classList.toggle("offen");
    menuAuf.setAttribute("aria-expanded", String(offen));
  });

  /* Aktiver Punkt in der Kopfleiste */
  document.querySelectorAll(".hauptnav a").forEach(a => {
    if (a.dataset.s === seite) a.setAttribute("aria-current", "page");
  });

  /* ---------- Suche ---------- */
  const fenster = document.getElementById("suchfenster");
  const eingabe = document.getElementById("suchEingabe");
  const trefferListe = document.getElementById("suchTreffer");
  let index = null, ladend = null, cursor = 0;

  async function ladeIndex() {
    if (index) return index;
    if (ladend) return ladend;
    ladend = (async () => {
      const eintraege = [];
      EBENEN.forEach(e => eintraege.push({ art: "Ebene", titel: e.titel, unter: `${e.unter} · ${e.z} m`, href: e.href, gew: 3 }));
      eintraege.push(
        { art: "Seite", titel: "Lizenz und Nutzung", unter: "Was erlaubt ist, was nicht", href: "lizenz.html", gew: 2 },
        { art: "Seite", titel: "Impressum und Haftungsausschluss", unter: "Kontakt, Urheber, neurale Assistenz", href: "impressum.html", gew: 2 }
      );
      try {
        const [werke, stadt, wz, gf] = await Promise.all([
          fetch("data/werke.json").then(r => r.json()).catch(() => null),
          fetch("data/stadt.json").then(r => r.json()).catch(() => null),
          fetch("data/werkzeuge.json").then(r => r.json()).catch(() => null),
          fetch("data/gegenfragen.json").then(r => r.json()).catch(() => null)
        ]);
        werke?.reihen.forEach(r => {
          eintraege.push({ art: "Reihe", titel: r.titel, unter: r.claim, href: r.seite, gew: 3 });
          (r.baende || []).forEach(b => eintraege.push({
            art: r.kennung + "-" + (b.nr || ""), titel: b.titel,
            unter: (b.fall || b.inhalt || "").slice(0, 96), href: r.seite, gew: 2
          }));
          (r.faelle || []).forEach(f => eintraege.push({
            art: "AU-" + String(f.nr).padStart(2, "0"), titel: f.titel,
            unter: f.unter, href: "autopsien.html#au-" + f.nr, gew: 2
          }));
        });
        stadt?.sektoren.forEach(s => eintraege.push({
          art: s.id, titel: s.name, unter: `${s.hirn} · Z ${s.z} m`, href: "atlas.html#" + s.id, gew: 2
        }));
        wz?.ruestzeug.forEach(k => eintraege.push({
          art: k.sig, titel: k.name, unter: k.kern, href: "werkzeuge.html#kartei", gew: 1
        }));
        wz?.redflags.punkte.forEach(p => eintraege.push({
          art: "Red Flag " + p.nr, titel: p.name, unter: p.frage, href: "werkzeuge.html#redflags", gew: 1
        }));
        gf?.forEach(g => eintraege.push({
          art: g.id, titel: g.behauptung, unter: "Gegenfrage aus Autopsie #" + String(g.au).padStart(2, "0"),
          href: "gegenfragen.html#" + g.id, gew: 1
        }));
      } catch (e) { /* Index bleibt auf den Grundeinträgen */ }
      index = eintraege;
      return index;
    })();
    return ladend;
  }

  function norm(s) {
    return (s || "").toLowerCase()
      .replace(/ä/g, "ae").replace(/ö/g, "oe").replace(/ü/g, "ue").replace(/ß/g, "ss")
      .replace(/[„“”"‚‘’']/g, "");
  }

  function suche(q) {
    const n = norm(q).trim();
    if (!n) return index.filter(e => e.gew >= 3).slice(0, 9);
    const worte = n.split(/\s+/);
    return index
      .map(e => {
        const heu = norm(e.art + " " + e.titel + " " + e.unter);
        let p = 0;
        for (const w of worte) {
          const i = heu.indexOf(w);
          if (i < 0) return null;
          p += (i === 0 ? 6 : 3) + e.gew;
          if (norm(e.titel).startsWith(w)) p += 5;
          if (norm(e.art) === w) p += 12;
        }
        return { e, p };
      })
      .filter(Boolean)
      .sort((a, b) => b.p - a.p)
      .slice(0, 14)
      .map(x => x.e);
  }

  function hervor(text, q) {
    const n = norm(q).trim().split(/\s+/).filter(Boolean);
    let t = text;
    if (!n.length) return t;
    const nt = norm(t);
    const i = nt.indexOf(n[0]);
    if (i < 0) return t;
    return t.slice(0, i) + "<mark>" + t.slice(i, i + n[0].length) + "</mark>" + t.slice(i + n[0].length);
  }

  function zeichne(q) {
    const treffer = suche(q);
    cursor = 0;
    trefferListe.innerHTML = treffer.length
      ? treffer.map((e, i) => `<li><a href="${e.href}" class="${i === 0 ? "aktiv" : ""}">
          <span class="art">${e.art}</span>
          <span class="txt">${hervor(e.titel, q)}<small>${e.unter || ""}</small></span></a></li>`).join("")
      : `<li><a href="gegenfragen.html"><span class="art">—</span><span class="txt">Kein Treffer<small>Versuch es mit einem Sektor-Kürzel wie NK-01, einer Signatur wie LR-I-1.2.3 oder einem Stichwort.</small></span></a></li>`;
  }

  async function oeffne() {
    await ladeIndex();
    fenster.classList.add("offen");
    zeichne("");
    eingabe.value = "";
    eingabe.focus();
  }
  function schliesse() { fenster.classList.remove("offen"); }

  document.getElementById("suchAuf")?.addEventListener("click", oeffne);
  fenster?.querySelector("[data-schliessen]")?.addEventListener("click", schliesse);
  eingabe?.addEventListener("input", () => zeichne(eingabe.value));

  document.addEventListener("keydown", ev => {
    const tippt = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName || "");
    if (ev.key === "/" && !tippt && !fenster.classList.contains("offen")) { ev.preventDefault(); oeffne(); return; }
    if ((ev.key === "k" || ev.key === "K") && (ev.metaKey || ev.ctrlKey)) { ev.preventDefault(); oeffne(); return; }
    if (!fenster.classList.contains("offen")) return;
    if (ev.key === "Escape") { schliesse(); return; }
    const links = [...trefferListe.querySelectorAll("a")];
    if (!links.length) return;
    if (ev.key === "ArrowDown" || ev.key === "ArrowUp") {
      ev.preventDefault();
      links[cursor]?.classList.remove("aktiv");
      cursor = (cursor + (ev.key === "ArrowDown" ? 1 : -1) + links.length) % links.length;
      links[cursor].classList.add("aktiv");
      links[cursor].scrollIntoView({ block: "nearest" });
    }
    if (ev.key === "Enter") { ev.preventDefault(); links[cursor]?.click(); }
  });
})();
