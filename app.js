/* ==========================================================================
   SYNTAXIS APPLICATION ENGINE v2.1
   Verwaltet Audio-Player, Autopsien-Filterung und das Epistemische Dojo
   ========================================================================== */

const SYNTAXIS = {
    autopsien: [
        { id: "AUTOPSIE #01", sec: "A", title: "Die Flache Erde & Eiswand", l: "l1", core: "Naiver Empirismus. Warum das Auge am Horizont betrügt und trigonometrische Erdkrümmungsmessung siegt.", skalpell: "Sehen ist nicht Messen" },
        { id: "AUTOPSIE #02", sec: "A", title: "Die Apollo-Mondlandungslüge", l: "l1", core: "JAQing und mathematische Geheimhaltungs-Entropie (Grimes-Modell) & Moskaus Schweigen.", skalpell: "Der Zeuge der Gegenseite" },
        { id: "AUTOPSIE #03", sec: "A", title: "Chemtrails & Geoengineering", l: "l2", core: "Protective Vigilance. Das Schmidt-Appleman-Kriterium der Atmosphärenthermodynamik.", skalpell: "Machbarkeit vs. Vollzug" },
        { id: "AUTOPSIE #04", sec: "A", title: "Die Klimalüge & CO-Mythos", l: "l3", core: "Agnotologie und Lösungsabwehr. Arrhenius-Absorptionsspektren vs. industriell erzeugter Zweifel.", skalpell: "Trennung von Diagnose & Therapie" },
        { id: "AUTOPSIE #05", sec: "A", title: "Die Hohle Erde & Agartha", l: "l1", core: "Romantischer Eskapismus. Schalentheorem und Seismik-Laufzeitmessung von P- und S-Wellen.", skalpell: "Inge Lehmanns Seismik-Bleistift" },
        { id: "AUTOPSIE #06", sec: "A", title: "Astrologie & Sternzeichen", l: "l1", core: "Barnum-Effekt, Präzession der Tagundnachtgleichen und Gezeitenkräfte im Kreißsaal.", skalpell: "Der Forer-Spiegel-Test" },
        { id: "AUTOPSIE #07", sec: "A", title: "Prä-Astronautik (Ancient Aliens)", l: "l2", core: "Kulturelle Enteignung und Monument-Proportionalitätsfehler. Merers Papyrus-Logbuch.", skalpell: "Das unvollendete Werkstück" },
        { id: "AUTOPSIE #08", sec: "A", title: "Der Roswell-Zwischenfall", l: "l1", core: "Gedächtnisdrift und nachträgliche Verdichtung (Project Mogul Spionageballone).", skalpell: "Der Zeitstempel-Test" },
        { id: "AUTOPSIE #09", sec: "A", title: "Planet X / Nibiru", l: "l2", core: "Apokalyptische Countdown-Logik und die himmelsmechanische Unmöglichkeit eines Geisterplaneten.", skalpell: "Die Kalender-Frist" },
        { id: "AUTOPSIE #10", sec: "A", title: "Die Simulationshypothese", l: "l1", core: "Kategorienfehler zwischen Wahrscheinlichkeitslogik und physikalischem Realitätsfundament.", skalpell: "Die Karte ist nicht das Land" },
        { id: "AUTOPSIE #11", sec: "B", title: "Homöopathie & Wassergedächtnis", l: "l2", core: "Simile-Prinzip, Avogadro-Grenze ($6{,}022 \\cdot 10^{23}$) und Benvenistes entzauberte Verdünnungen.", skalpell: "Die Avogadro-Grenze" },
        { id: "AUTOPSIE #12", sec: "B", title: "Impfgegnerschaft & Wakefield-Betrug", l: "l4", core: "Lancet-Retraction 1998, manipulierte Datensätze und pathogene Resurgenz.", skalpell: "Der Interessenkonflikt-Audit" }
    ],

    playlist: [
        { id: "track-ambient", title: "Neocortex Rain (Soundscape)", meta: "CC BY 4.0 · Noir Ambient Atmos", src: "audio/ambient_rain.mp3" },
        { id: "track-nc-01", title: "Fallakte #088: Der Mann ohne Echo", meta: "CC BY-NC-ND 4.0 · Hörbuch TTS", src: "audio/fallakte_088.mp3" },
        { id: "track-landkarte-01", title: "Landkarte: Das Fundament des Zweifels", meta: "CC BY 4.0 · Kapitel 1 Audio", src: "audio/landkarte_kapitel_01.mp3" }
    ],

    dojo: [
        {
            quote: "„Nachdem ich Globuli genommen habe, ging meine Grippe nach 7 Tagen weg. Die Schulmedizin hätte 1 Woche gebraucht!“",
            category: "Kausalitäts-Fehlschluss",
            options: [
                { text: "Post hoc ergo propter hoc (Fehlende Trennung von Spontanverlauf & Wirkung)", correct: true },
                { text: "Ad Hominem (Angriff auf die Ärzte)", correct: false },
                { text: "Strohmann-Argument", correct: false }
            ],
            explanation: "Exakt. Zeitliche Abfolge beweist keine Ursache (Regression zur Mitte und natürlicher Krankheitsverlauf heilen grippale Infekte meist nach rund 7 Tagen)."
        },
        {
            quote: "„400.000 NASA-Mitarbeiter und Zulieferer haben geschwiegen, weil sie alle bedroht wurden.“",
            category: "Verschwörungs-Entropie",
            options: [
                { text: "Zirkelschluss", correct: false },
                { text: "Grimes-Entropie-Bruch (Mathematische Unmöglichkeit von Großgeheimnissen)", correct: true },
                { text: "Äquivokation", correct: false }
            ],
            explanation: "Richtig! Nach der Grimes-Gleichung zur Informationsentropie bricht eine Geheimhaltung mit 400.000 Beteiligten in unter vier Jahren unweigerlich zusammen."
        }
    ]
};

// Autopsien Renderer
function initAutopsien() {
    const container = document.getElementById('autopsien-render-target');
    if (!container) return;

    function render(filter) {
        container.innerHTML = '';
        const filtered = SYNTAXIS.autopsien.filter(a => filter === 'all' || a.sec === filter);
        filtered.forEach(item => {
            const el = document.createElement('div');
            el.className = 'content-card';
            el.innerHTML = `
                <div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                        <span style="font-family:var(--font-mono); font-size:0.8rem; color:var(--accent-blue);">${item.id}</span>
                        <span class="threat-badge ${item.l}">${item.l.toUpperCase()}</span>
                    </div>
                    <h3 style="color:#fff; font-size:1.15rem; margin-bottom:0.5rem;">${item.title}</h3>
                    <p style="color:var(--text-secondary); font-size:0.9rem;">${item.core}</p>
                </div>
                <div class="skalpell-tag">Skalpell: ${item.skalpell}</div>
            `;
            container.appendChild(el);
        });
    }

    render('all');

    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            render(e.target.getAttribute('data-filter'));
        });
    });
}

// Audio System Engine
let currentTrack = 0;
function initAudio() {
    const audio = document.getElementById('syntaxis-stream');
    const toggle = document.getElementById('audio-toggle');
    const prev = document.getElementById('audio-prev');
    const next = document.getElementById('audio-next');
    const progress = document.getElementById('audio-progress');
    const time = document.getElementById('audio-time-display');

    if (!audio || !toggle) return;

    function load(idx) {
        currentTrack = idx;
        const item = SYNTAXIS.playlist[idx];
        if (!item) return;
        document.getElementById('player-track-title').innerText = item.title;
        document.getElementById('player-track-meta').innerText = item.meta;
        audio.src = item.src;
    }

    toggle.addEventListener('click', () => {
        if (audio.paused) {
            audio.play().catch(() => console.log("Audio-Autoplay erfordert Benutzerinteraktion."));
            toggle.innerText = "";
        } else {
            audio.pause();
            toggle.innerText = "";
        }
    });

    if (prev) prev.addEventListener('click', () => {
        currentTrack = (currentTrack - 1 + SYNTAXIS.playlist.length) % SYNTAXIS.playlist.length;
        load(currentTrack);
        audio.play();
        toggle.innerText = "";
    });

    if (next) next.addEventListener('click', () => {
        currentTrack = (currentTrack + 1) % SYNTAXIS.playlist.length;
        load(currentTrack);
        audio.play();
        toggle.innerText = "";
    });

    audio.addEventListener('timeupdate', () => {
        if (audio.duration) {
            const pct = (audio.currentTime / audio.duration) * 100;
            if (progress) progress.style.width = pct + "%";
            const m = Math.floor(audio.currentTime / 60);
            const s = Math.floor(audio.currentTime % 60);
            if (time) time.innerText = `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
        }
    });

    load(0);
}

// Epistemisches Dojo Widget
function initDojo() {
    let dojoIdx = 0;
    const catEl = document.getElementById('dojo-cat');
    const quoteEl = document.getElementById('dojo-quote-text');
    const optEl = document.getElementById('dojo-options');
    const feedEl = document.getElementById('dojo-feedback-box');
    const nextBtn = document.getElementById('dojo-next');

    if (!catEl || !quoteEl || !optEl) return;

    function renderQuest(i) {
        const q = SYNTAXIS.dojo[i];
        if (!q) return;
        catEl.innerText = `Kategorie: ${q.category}`;
        quoteEl.innerText = q.quote;
        optEl.innerHTML = '';
        feedEl.style.display = 'none';

        q.options.forEach(opt => {
            const btn = document.createElement('button');
            btn.className = 'dojo-btn';
            btn.innerText = opt.text;
            btn.addEventListener('click', () => {
                feedEl.style.display = 'block';
                if (opt.correct) {
                    feedEl.style.background = 'rgba(16, 185, 129, 0.15)';
                    feedEl.style.color = 'var(--accent-green)';
                    feedEl.innerHTML = `<strong>Korrekt identifiziert:</strong> ${q.explanation}`;
                } else {
                    feedEl.style.background = 'rgba(239, 68, 68, 0.15)';
                    feedEl.style.color = 'var(--accent-red)';
                    feedEl.innerHTML = `<strong>Fehldiagnose:</strong> Dieser Denkfehler greift hier nicht. Prüfe die logische Struktur.`;
                }
            });
            optEl.appendChild(btn);
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            dojoIdx = (dojoIdx + 1) % SYNTAXIS.dojo.length;
            renderQuest(dojoIdx);
        });
    }

    renderQuest(0);
}

document.addEventListener('DOMContentLoaded', () => {
    initAudio();
    initAutopsien();
    initDojo();
});
