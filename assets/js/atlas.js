/* SYNTAXIS — Kartographischer Atlas */
(async () => {
  "use strict";

  const karte = document.getElementById("atlasKarte");
  if (!karte) return;

  let D;
  try { D = await (await fetch("data/stadt.json")).json(); }
  catch (e) {
    document.getElementById("atlasInfo").innerHTML =
      '<p class="leise">Die Sektordaten konnten nicht geladen werden. Falls du die Seite lokal geöffnet hast: Browser laden JSON nur über einen Webserver. Starte im Ordner <span class="kennung">python3 -m http.server</span> und öffne dann <span class="kennung">localhost:8000</span>.</p>';
    return;
  }

  const info = document.getElementById("atlasInfo");
  const filterreihe = document.getElementById("terrassenFilter");
  const nachId = Object.fromEntries(D.sektoren.map(s => [s.id, s]));
  const zahl = n => n.toLocaleString("de-DE", { maximumFractionDigits: 3 });

  let aktiveTerrasse = "oberste";
  let aktiverSektor = null;

  /* ---------- Filterknöpfe je Terrasse ---------- */
  D.terrassen.forEach(t => {
    const n = D.sektoren.filter(s => s.terrasse === t.id).length;
    if (!n) return;
    const b = document.createElement("button");
    b.className = "filter";
    b.type = "button";
    b.textContent = `${t.name} · ${t.z} m`;
    b.setAttribute("aria-pressed", String(t.id === aktiveTerrasse));
    b.addEventListener("click", () => { aktiveTerrasse = t.id; aktiverSektor = null; zeichne(); });
    filterreihe.appendChild(b);
  });

  /* ---------- Grundriss zeichnen ---------- */
  function zeichne() {
    [...filterreihe.children].forEach((b, i) => {
      const t = D.terrassen.filter(t => D.sektoren.some(s => s.terrasse === t.id))[i];
      b.setAttribute("aria-pressed", String(t.id === aktiveTerrasse));
    });

    const t = D.terrassen.find(x => x.id === aktiveTerrasse);
    const sek = D.sektoren.filter(s => s.terrasse === aktiveTerrasse);

    const W = 700, H = 500, pad = 58;
    const xs = sek.map(s => s.x).concat(0), ys = sek.map(s => s.y).concat(0);
    let minX = Math.min(...xs) - 1.2, maxX = Math.max(...xs) + 1.6;
    let minY = Math.min(...ys) - 1.2, maxY = Math.max(...ys) + 1.2;
    if (maxX - minX < 4) { const c = (maxX + minX) / 2; minX = c - 2; maxX = c + 2; }
    if (maxY - minY < 3) { const c = (maxY + minY) / 2; minY = c - 1.5; maxY = c + 1.5; }

    const sx = (W - pad * 2) / (maxX - minX);
    const sy = (H - pad * 2 - 40) / (maxY - minY);
    const s = Math.min(sx, sy);
    const px = x => pad + (x - minX) * s + ((W - pad * 2) - (maxX - minX) * s) / 2;
    const py = y => H - pad - (y - minY) * s - ((H - pad * 2 - 40) - (maxY - minY) * s) / 2;

    let g = `<g class="gitter">`;
    for (let k = Math.ceil(minX); k <= Math.floor(maxX); k++) {
      g += `<line x1="${px(k)}" y1="${pad - 10}" x2="${px(k)}" y2="${H - pad + 6}"/>`;
      g += `<text x="${px(k)}" y="${H - pad + 18}" text-anchor="middle">${k}</text>`;
    }
    for (let k = Math.ceil(minY); k <= Math.floor(maxY); k++) {
      g += `<line x1="${pad - 12}" y1="${py(k)}" x2="${W - pad + 10}" y2="${py(k)}"/>`;
      g += `<text x="${pad - 18}" y="${py(k) + 3}" text-anchor="end">${k}</text>`;
    }
    g += `<text x="${W - pad + 10}" y="${H - pad + 18}" text-anchor="end">X in km</text>`;
    g += `<text x="${pad - 18}" y="${pad + 8}" text-anchor="end">Y in km</text></g>`;

    /* Lokaler Nullpunkt */
    g += `<g><circle cx="${px(0)}" cy="${py(0)}" r="12" fill="none" stroke="var(--line-hard)" stroke-dasharray="2 3"/>
          <line x1="${px(0) - 16}" y1="${py(0)}" x2="${px(0) + 16}" y2="${py(0)}" stroke="var(--line-hard)"/>
          <line x1="${px(0)}" y1="${py(0) - 16}" x2="${px(0)}" y2="${py(0) + 16}" stroke="var(--line-hard)"/></g>`;

    const knoten = sek.map(o => {
      const cx = px(o.x), cy = py(o.y);
      const rechts = cx < W * 0.62;
      return `<g class="sektor" role="button" tabindex="0" data-id="${o.id}" aria-selected="${o.id === aktiverSektor}" aria-label="${o.name}">
        <circle cx="${cx}" cy="${cy}" r="${o.id === "T-00" || o.x === 0 && o.y === 0 ? 8 : 6}"/>
        <text x="${rechts ? cx + 12 : cx - 12}" y="${cy + 3.5}" text-anchor="${rechts ? "start" : "end"}">${o.name}</text>
      </g>`;
    }).join("");

    karte.innerHTML = `
      <text x="${pad - 18}" y="30" style="font-family:var(--data);font-size:10px;fill:var(--fog)">${t.name.toUpperCase()}</text>
      <text x="${W - pad + 10}" y="30" text-anchor="end" style="font-family:var(--data);font-size:10px;fill:var(--fog-dim)">Z ${t.z} m · ${t.hirn}</text>
      <text x="${W - pad + 10}" y="46" text-anchor="end" style="font-family:var(--body);font-size:11px;fill:var(--fog-dim)">Lokaler Nullpunkt: ${t.nullpunkt}</text>
      ${g}${knoten}`;

    karte.querySelectorAll(".sektor").forEach(el => {
      const w = () => waehle(el.dataset.id);
      el.addEventListener("click", w);
      el.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); w(); } });
    });

    if (aktiverSektor) waehle(aktiverSektor, false);
    else info.innerHTML = `<p class="leise" style="margin:0 0 .8rem">${t.funktion}.</p><p class="leise" style="margin:0">Wähle einen Sektor auf der Karte.</p>`;
  }

  /* ---------- Sektordetails ---------- */
  function waehle(id, neuZeichnen = true) {
    aktiverSektor = id;
    const o = nachId[id];
    if (!o) return;
    if (neuZeichnen) karte.querySelectorAll(".sektor").forEach(el =>
      el.setAttribute("aria-selected", String(el.dataset.id === id)));

    const baende = (o.band || []).map(b => `<a href="chroniken.html">Band ${["", "I", "II", "III", "IV"][b] || b}</a>`).join(", ");
    info.innerHTML = `
      <h3>${o.name}</h3>
      <p class="meta">${o.id}${o.sektor ? " · Sektor " + o.sektor : ""}</p>
      <dl>
        <dt>X</dt><dd>${zahl(o.x)} km</dd>
        <dt>Y</dt><dd>${zahl(o.y)} km</dd>
        <dt>Z</dt><dd>${zahl(o.z)} m</dd>
        <dt>REAL</dt><dd>${o.hirn}</dd>
        ${baende ? `<dt>BAND</dt><dd>${baende}</dd>` : ""}
      </dl>
      <p class="notiz">${o.notiz}</p>
      ${o.flagge ? `<p class="flagge-hinweis">Anmerkung zur Quelle: ${o.flagge}</p>` : ""}`;
    if (history.replaceState) history.replaceState(null, "", "#" + id);
  }

  /* ---------- Rechner ---------- */
  const von = document.getElementById("vonSektor"), nach = document.getElementById("nachSektor");
  const erg = document.getElementById("rechnerErgebnis");
  const sortiert = [...D.sektoren].sort((a, b) => b.z - a.z || a.name.localeCompare(b.name, "de"));
  const optionen = sortiert.map(s => `<option value="${s.id}">${s.name} — ${s.id}</option>`).join("");
  von.innerHTML = optionen; nach.innerHTML = optionen;
  von.value = "T-00"; nach.value = "NK-01";

  const v = id => D.verkehr.find(x => x.id === id);

  function zeit(sek) {
    if (sek < 90) return `${Math.round(sek)} Sekunden`;
    if (sek < 5400) return `${(sek / 60).toFixed(1).replace(".", ",")} Minuten`;
    return `${(sek / 3600).toFixed(1).replace(".", ",")} Stunden`;
  }

  function rechne() {
    const a = nachId[von.value], b = nachId[nach.value];
    if (!a || !b) return;
    const dz = Math.abs(b.z - a.z);
    const gleicheEbene = a.terrasse === b.terrasse;
    const dxy = gleicheEbene ? Math.hypot(b.x - a.x, b.y - a.y) : null;

    const tiefer = Math.min(a.z, b.z) < 0;
    const aufzug = tiefer ? v("aufzug-b") : v("aufzug-a");
    const tAufzug = dz > 0 ? dz / aufzug.wert : 0;

    let zeilen = "";
    if (dxy !== null) {
      zeilen += `<tr><td>Waagerechte Entfernung</td><td class="w">${zahl(dxy)} km</td></tr>`;
      if (dxy > 0) {
        zeilen += `<tr><td>Fahrt mit dem Pontiac Catalina</td><td class="w">${zeit(dxy * 1000 / (v("pontiac").wert / 3.6))}</td></tr>`;
        zeilen += `<tr><td>Querung per Sky Bridge</td><td class="w">${zeit(dxy * 1000 / (v("skybridge").wert / 3.6))}</td></tr>`;
      }
    } else {
      zeilen += `<tr><td>Waagerechte Entfernung</td><td class="w">nicht bestimmbar</td></tr>`;
    }
    zeilen += `<tr><td>Höhendifferenz</td><td class="w">${zahl(dz)} m</td></tr>`;
    if (dz > 0) zeilen += `<tr><td>${aufzug.name}</td><td class="w">${zeit(tAufzug)}</td></tr>`;

    const gesamt = tAufzug + (dxy ? dxy * 1000 / (v("pontiac").wert / 3.6) : 0);
    if (gesamt > 0) zeilen += `<tr><td><strong>Gesamt, Aufzug und Fahrzeug</strong></td><td class="w"><strong>${zeit(gesamt)}</strong></td></tr>`;

    const hinweis = dxy === null
      ? `<p class="kennung" style="margin:.8rem 0 0">${a.terrasse === b.terrasse ? "" : "Beide Orte liegen auf verschiedenen Ebenen mit eigenen Nullpunkten. Nur die Höhendifferenz ist belastbar."}</p>`
      : (tiefer ? `<p class="kennung" style="margin:.8rem 0 0">Unter dem Basisdatum fährt nur der archaische Hebel-Aufzug. Die spürbar längere Fahrzeit ist gewollt.</p>` : "");

    erg.innerHTML = `<table><thead><tr><th>Strecke</th><th>${a.name} → ${b.name}</th></tr></thead><tbody>${zeilen}</tbody></table>${hinweis}`;
  }
  von.addEventListener("change", rechne);
  nach.addEventListener("change", rechne);

  /* ---------- Tabellen ---------- */
  document.querySelector("#turmTabelle tbody").innerHTML =
    D.turm.map(e => `<tr><td class="zahl">${e.etage}</td><td>${e.name}</td><td class="zahl">${e.z} m</td></tr>`).join("");
  document.querySelector("#brueckenTabelle tbody").innerHTML =
    D.bruecken.map(b => {
      const a = nachId[b.von];
      const z = nachId[b.nach];
      return `<tr><td>${b.name}</td><td>${a ? a.name : b.von} ↔ ${z ? z.name : b.nach}</td><td class="leise">${b.real}</td></tr>`;
    }).join("");

  /* ---------- Start ---------- */
  const ziel = decodeURIComponent(location.hash.slice(1));
  if (nachId[ziel]) { aktiveTerrasse = nachId[ziel].terrasse; aktiverSektor = ziel; }
  zeichne();
  rechne();
})();
