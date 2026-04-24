// ─── Configuration API Cloudflare Workers ───────────────────────────────────
// L'URL de votre API Cloudflare Workers qui génère les signatures SHA-256.
//
// ARCHITECTURE SÉCURISÉE:
// - Le script.js génère le deck JSON et l'envoie à cette API
// - L'API (Cloudflare Workers) possède le secret caché dans ses variables d'environnement
// - L'API calcule la signature SHA-256 avec le secret et la renvoie
// - Le script.js reçoit la signature officielle et télécharge le fichier
// - Résultat: Impossible de tricher, le secret est invisible côté client
//
// DÉPLOIEMENT:
// 1. Suivez les instructions dans cloudflare-worker.js
// 2. Remplacez cette URL par l'URL de votre Worker déployé
const SIGNATURE_API_URL = "https://wargame-api.gougele222.workers.dev";

// ─── Helper XSS ─────────────────────────────────────────────────────────────
function escapeHtml(str) {
    if (str == null) return '';
    const div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
}

let currentDoctrine = null;
let currentDeck = [];
let vehicleData = {};

// Load data on start
window.addEventListener('DOMContentLoaded', () => {
    if (window.VEHICLES_DATA) {
        vehicleData = window.VEHICLES_DATA;
        renderCountryList();
    } else {
        console.error("VEHICLES_DATA not found.");
        document.getElementById('country-list').innerHTML = "<p style='color: var(--danger)'>Erreur: Données d'unités introuvables.</p>";
    }
});

function selectDoctrine(key) {
    currentDoctrine = key;
    document.getElementById('step-1').style.display = 'none';
    document.getElementById('builder-ui').style.display = 'grid';
    document.getElementById('current-doctrine-label').innerText = DOCTRINES[key].name;
    updateCreditsDisplay();
}

function renderCountryList() {
    const list = document.getElementById('country-list');
    list.innerHTML = '';
    
    let totalCountries = 0;
    for (const [country, vehicles] of Object.entries(vehicleData)) {
        totalCountries++;
        const item = document.createElement('div');
        item.className = 'country-item';
        
        const header = document.createElement('div');
        header.className = 'country-header';
        header.innerHTML = `<span>${escapeHtml(country)}</span> <span style="font-size: 0.8rem; opacity: 0.5;">${vehicles.length} unités</span>`;
        header.onclick = () => item.classList.toggle('active');
        
        const container = document.createElement('div');
        container.className = 'country-vehicles';
        
        vehicles.forEach(v => {
            const card = document.createElement('div');
            card.className = 'vehicle-card';
            card.onclick = () => addVehicleToDeck(country, v);
            
            const costStr = Object.entries(v.baseCredits)
                .filter(([key, val]) => val > 0 && !key.startsWith('_'))
                .map(([type, val]) => `${val} ${translateType(type)}`)
                .join(' + ') || 'Gratuit';

            const thumbUrl = getVehicleImage(v);

            card.innerHTML = `
                <img src="${escapeHtml(thumbUrl)}" alt="${escapeHtml(v.name)}" style="object-fit: cover;">
                <div class="vehicle-info">
                    <span class="vehicle-name">${escapeHtml(v.name)}</span>
                    <span class="vehicle-cost">${escapeHtml(costStr)}</span>
                </div>
            `;
            container.appendChild(card);
        });
        
        item.appendChild(header);
        item.appendChild(container);
        list.appendChild(item);
    }
    document.getElementById('country-count').innerText = `${totalCountries} pays chargés`;
}

function translateType(type) {
    const map = {
        infantry: 'INF',
        armor: 'ARM',
        mechanized: 'MEC',
        motorized: 'MOT',
        support: 'SUP',
        plane: 'AIR',
        invitation: 'INV'
    };
    return map[type] || type;
}

let pendingVehicle = null;
let editingInstanceId = null;

function addVehicleToDeck(country, vehicle) {
    if (vehicle.emportOptions && vehicle.emportOptions.length > 0) {
        showCreditModal(country, vehicle);
    } else {
        const emptyEmport = { infantry: 0, armor: 0, mechanized: 0, motorized: 0, support: 0, plane: 0, invitation: 0, _text: '' };
        confirmAddVehicle(country, vehicle, emptyEmport);
    }
}

function showCreditModal(country, vehicle, instanceId = null) {
    pendingVehicle = { country, vehicle };
    editingInstanceId = instanceId;
    document.getElementById('modal-vehicle-name').innerText = vehicle.name;
    const list = document.getElementById('credit-options-list');
    list.innerHTML = '';
    
    // Add "Sans emport" option
    const noneBtn = document.createElement('button');
    noneBtn.className = 'credit-option-btn';
    noneBtn.innerHTML = `<span class="opt-text">Pas d'emport supplémentaire</span> <span class="opt-cost">Gratuit</span>`;
    noneBtn.onclick = () => {
        const emptyEmport = { infantry: 0, armor: 0, mechanized: 0, motorized: 0, support: 0, plane: 0, invitation: 0, _text: '' };
        if (editingInstanceId) {
            updateVehicleEmport(editingInstanceId, emptyEmport);
        } else {
            confirmAddVehicle(country, vehicle, emptyEmport);
        }
        closeCreditModal();
    };
    list.appendChild(noneBtn);

    vehicle.emportOptions.forEach((opt, idx) => {
        const btn = document.createElement('button');
        btn.className = 'credit-option-btn';
        
        const costStr = Object.entries(opt)
            .filter(([key, val]) => val > 0 && !key.startsWith('_'))
            .map(([type, val]) => `<b>${val}</b> ${translateType(type)}`)
            .join(', ');
            
        const optTitle = opt._text || `Option ${idx + 1}`;
        btn.innerHTML = `<span class="opt-text">${optTitle}</span> <span class="opt-cost">${costStr}</span>`;
        btn.onclick = () => {
            if (editingInstanceId) {
                updateVehicleEmport(editingInstanceId, opt);
            } else {
                confirmAddVehicle(country, vehicle, opt);
            }
            closeCreditModal();
        };
        list.appendChild(btn);
    });
    
    document.getElementById('credit-modal').style.display = 'flex';
}

function updateVehicleEmport(instanceId, emport) {
    const idx = currentDeck.findIndex(v => v.instanceId === instanceId);
    if (idx !== -1) {
        currentDeck[idx].selectedEmport = emport;
        updateDeckUI();
        updateCreditsDisplay();
    }
}

function closeCreditModal() {
    document.getElementById('credit-modal').style.display = 'none';
    pendingVehicle = null;
    editingInstanceId = null;
}

function confirmAddVehicle(country, vehicle, emport) {
    currentDeck.push({ 
        ...vehicle, 
        country, 
        selectedEmport: emport,
        instanceId: crypto.randomUUID()
    });
    updateDeckUI();
    updateCreditsDisplay();
}

function removeVehicle(instanceId) {
    currentDeck = currentDeck.filter(v => v.instanceId !== instanceId);
    updateDeckUI();
    updateCreditsDisplay();
}

function getVehicleImage(v) {
    if (!v) return '../Assets/Other/img/Logo_Ranked.png';
    
    // Use local image if available and it's not an imgur link
    // or if thumbnail is missing
    let path = v.image_path || v.thumbnail || '';
    
    if (path && !path.startsWith('http') && !path.startsWith('../')) {
        path = '../Assets/' + path;
    }
    
    // If we have both, and thumbnail is imgur, prefer local path
    if (v.thumbnail && v.thumbnail.includes('imgur.com') && v.image_path) {
        path = '../Assets/' + v.image_path;
    }
    
    return path || '../Assets/Other/img/Logo_Ranked.png';
}

function updateDeckUI() {
    const sections = document.querySelectorAll('.deck-section .section-items');
    sections.forEach(s => s.innerHTML = '');
    
    currentDeck.forEach(v => {
        // Calculate total credits
        const totalCredits = {};
        for (const type in v.baseCredits) {
            totalCredits[type] = (v.baseCredits[type] || 0) + (v.selectedEmport[type] || 0);
        }

        // Find primary section
        let primaryType = null;
        for (const [type, val] of Object.entries(totalCredits)) {
            if (val > 0 && type !== 'invitation') {
                primaryType = type;
                break;
            }
        }
        
        if (!primaryType && totalCredits.invitation > 0) primaryType = 'motorized';
        if (!primaryType) primaryType = 'infantry';
        
        const section = document.querySelector(`.deck-section[data-type="${primaryType}"] .section-items`);
        if (section) {
            const div = document.createElement('div');
            div.className = 'selected-vehicle animate-in';
            div.onclick = (e) => {
                if (e.target.className !== 'remove-btn') {
                    showCreditModal(v.country, v, v.instanceId);
                }
            };

            const thumbUrl = getVehicleImage(v);
            const totalCostStr = Object.entries(totalCredits)
                .filter(([key, val]) => val > 0 && !key.startsWith('_'))
                .map(([type, val]) => `${val} ${translateType(type)}`)
                .join(' + ');

            const emportText = v.selectedEmport._text ? `<span class="emport-label" title="${escapeHtml(v.selectedEmport._text)}">${escapeHtml(v.selectedEmport._text)}</span>` : '';

            div.innerHTML = `
                <div class="selected-vehicle-info">
                    <img src="${escapeHtml(thumbUrl)}" alt="${escapeHtml(v.name)}" style="width: 40px; height: 25px; border-radius: 4px; object-fit: cover;">
                    <div style="flex: 1;">
                        <span style="font-weight: 600; display: block; font-size: 0.9rem;">${escapeHtml(v.name)}</span>
                        <div style="display: flex; gap: 5px; align-items: center;">
                            <span class="total-cost-badge">${escapeHtml(totalCostStr)}</span>
                            ${emportText}
                        </div>
                    </div>
                </div>
                <button class="remove-btn" onclick="removeVehicle('${escapeHtml(v.instanceId)}')">×</button>
            `;
            section.appendChild(div);
        }
    });
}

function updateCreditsDisplay() {
    if (!currentDoctrine) return;
    
    const totals = { infantry: 0, armor: 0, mechanized: 0, motorized: 0, support: 0, plane: 0, invitation: 0 };
    currentDeck.forEach(v => {
        for (const type in totals) {
            totals[type] += (v.baseCredits[type] || 0) + (v.selectedEmport[type] || 0);
        }
    });
    
    const doctrine = DOCTRINES[currentDoctrine];
    for (const type in totals) {
        const el = document.getElementById(`val-${type}`);
        if (!el) continue;
        
        // Invitation credits are global, no limit (or logic handled elsewhere)
        const max = doctrine[type] !== undefined ? doctrine[type] : "∞";
        el.innerText = `${totals[type]} / ${max}`;
        
        if (max !== "∞" && totals[type] > max) {
            el.classList.add('overflow');
        } else {
            el.classList.remove('overflow');
        }
    }
}

function resetBuilder() {
    if (confirm("Voulez-vous vraiment effacer tout le deck ?")) {
        currentDeck = [];
        updateDeckUI();
        updateCreditsDisplay();
    }
}

function stableStringify(obj) {
    const allKeys = [];
    JSON.stringify(obj, (key, value) => {
        allKeys.push(key);
        return value;
    });
    allKeys.sort();
    return JSON.stringify(obj, allKeys);
}

async function exportDeck() {
    const deckName = document.getElementById('deck-name').value || "Sans Nom";

    const deckData = {
        name: deckName,
        doctrine: currentDoctrine,
        units: currentDeck.map(v => ({
            id: v.id,
            name: v.name,
            country: v.country,
            baseCredits: v.baseCredits,
            selectedEmport: v.selectedEmport,
            thumbnail: v.thumbnail || v.image_path
        })),
        timestamp: Date.now()
    };

    try {
        // Envoyer le deck JSON à l'API Cloudflare Workers pour obtenir la signature
        const response = await fetch(SIGNATURE_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(deckData)
        });

        if (!response.ok) {
            throw new Error(`Erreur API: ${response.status} ${response.statusText}`);
        }

        const { signature } = await response.json();

        if (!signature) {
            throw new Error("L'API n'a pas renvoyé de signature");
        }

        const finalFile = {
            ...deckData,
            signature: signature
        };

        const blob = new Blob([JSON.stringify(finalFile, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${deckName.replace(/\s+/g, '_')}_deck.json`;
        a.click();

    } catch (error) {
        console.error("Erreur lors de la signature:", error);

        // Fallback: proposer d'exporter sans signature
        if (confirm(`L'API de signature est inaccessible (${error.message}).\n\nVoulez-vous exporter le deck quand même sans signature ?\n\n⚠️ `)) {
            const finalFile = {
                ...deckData,
                signature: null
            };

            const blob = new Blob([JSON.stringify(finalFile, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${deckName.replace(/\s+/g, '_')}_deck.json`;
            a.click();
        }
    }
}

function importDeck(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const data = JSON.parse(e.target.result);
            if (!data.doctrine || !data.units) throw new Error("Format invalide");
            
            // Note: La vérification de signature n'est plus faite côté client
            // car le secret est maintenant stocké uniquement dans l'API Cloudflare Workers.
            // La vérification peut être faite par le bot Discord ou un autre système serveur.
            
            // Load it
            currentDoctrine = data.doctrine;
            
            // Re-map units to latest data if possible to fix images and credits
            currentDeck = data.units.map(u => {
                let latest = null;
                if (window.VEHICLES_DATA && window.VEHICLES_DATA[u.country]) {
                    latest = window.VEHICLES_DATA[u.country].find(v => v.name === u.name);
                }
                
                if (latest) {
                    return { 
                        ...latest, 
                        country: u.country, 
                        selectedEmport: u.selectedEmport || { infantry: 0, armor: 0, mechanized: 0, motorized: 0, support: 0, plane: 0, invitation: 0, _text: '' },
                        instanceId: crypto.randomUUID()
                    };
                }
                return { ...u, instanceId: crypto.randomUUID() };
            });
            
            // Switch to builder UI
            document.getElementById('step-1').style.display = 'none';
            document.getElementById('builder-ui').style.display = 'grid';
            document.getElementById('current-doctrine-label').innerText = DOCTRINES[currentDoctrine].name;
            document.getElementById('deck-name').value = data.name;
            
            updateDeckUI();
            updateCreditsDisplay();
            
        } catch (err) {
            alert("Erreur lors de l'import : " + err.message);
        }
    };
    reader.readAsText(file);
}
