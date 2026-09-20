/* SYNTAXIS — Asservatenkammer: Aktenschrank, Pinnwand, Leuchtkasten */
(async () => {
  "use strict";
  const wand = document.getElementById("pinnwand");
  if (!wand) return;
  let D;
  try { D = await (await fetch("data/bildband.json")).json(); }
  catch (e) { wand.innerHTML = '<p class="leise" style="padding:2rem">Akten konnten nicht geladen werden.</p>'; return; }

  const schrank = document.getElementById("schrank");
  const kopf = document.getElementById("aktenKopf");
  let offen = D.akten[0].id;

  schrank.innerHTML = D.akten.map(a => `
    <button class="lade" role="tab" data-akte="${a.id}" aria-selected="${a.id === offen}">
      <span class="sig">${a.signatur}</span>
      <span class="tt">${a.titel}</span>
      <span class="st">${a.status}</span>
    </button>`).join("");

  function zeichne() {
    const a = D.akten.find(x => x.id === offen);
    [...schrank.children].forEach(b => b.setAttribute("aria-selected", String(b.dataset.akte === offen)));

    kopf.innerHTML = `<span class="kennung">${a.signatur} · ${a.status}</span>
      <h3>${a.titel}</h3><p class="unter">${a.untertitel}</p><p class="notiz">${a.notiz}</p>`;

    if (!a.bilder.length) {
      wand.innerHTML = '<p class="leer">Diese Akte ist noch leer.</p>';
      return;
    }

    const faeden = a.faeden.map(([v, n]) => {
      const A = a.bilder.find(b => b.id === v), B = a.bilder.find(b => b.id === n);
      if (!A || !B) return "";
      return `<line x1="${A.x}" y1="${A.y}" x2="${B.x}" y2="${B.y}" vector-effect="non-scaling-stroke"/>`;
    }).join("");

    wand.innerHTML = `
      <svg class="faeden" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">${faeden}</svg>
      ${a.bilder.map((b, i) => `
        <figure class="beleg" style="left:${b.x}%;top:${b.y}%;--dreh:${b.dreh}deg;--verzug:${i * 40}ms"
                tabindex="0" role="button" data-id="${b.id}" aria-label="${b.titel} vergrößern">
          <span class="nadel"></span>
          <img src="${b.bild}" alt="${b.titel}" loading="lazy" decoding="async">
          <figcaption>${b.titel}<small>${b.unterschrift}</small></figcaption>
        </figure>`).join("")}`;

    wand.querySelectorAll(".beleg").forEach(el => {
      const auf = () => zeige(a.bilder.find(x => x.id === el.dataset.id));
      el.addEventListener("click", auf);
      el.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); auf(); } });
    });
  }

  /* Leuchtkasten */
  const lk = document.getElementById("leuchtkasten");
  const lkBild = document.getElementById("lkBild"), lkTitel = document.getElementById("lkTitel");
  const lkText = document.getElementById("lkText"), lkLink = document.getElementById("lkLink");
  function zeige(b) {
    if (!b) return;
    lkBild.src = b.gross || b.bild; lkBild.alt = b.titel;
    lkTitel.textContent = b.titel;
    lkText.textContent = b.notiz || b.unterschrift || "";
    if (b.ziel) { lkLink.href = b.ziel; lkLink.hidden = false; } else lkLink.hidden = true;
    lk.classList.add("offen");
    document.getElementById("lkZu").focus();
  }
  function zu() { lk.classList.remove("offen"); }
  document.getElementById("lkZu").addEventListener("click", zu);
  lk.addEventListener("click", e => { if (e.target === lk) zu(); });
  addEventListener("keydown", e => { if (e.key === "Escape") zu(); });

  schrank.addEventListener("click", e => {
    const b = e.target.closest("[data-akte]");
    if (!b) return;
    offen = b.dataset.akte; zeichne();
  });
  zeichne();
})();
