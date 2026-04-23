const fs = require('fs');
const path = require('path');

const assetsPath = 'e:/Travaille/CodageAutres/Projets Web/Wargame/WGD/WargameRanked/WarGameDeck/Assets';
const jsonOutputPath = 'e:/Travaille/CodageAutres/Projets Web/Wargame/WGD/WargameRanked/WarGameDeck/Assets/vehicles.json';
const jsOutputPath = 'e:/Travaille/CodageAutres/Projets Web/Wargame/WGD/WargameRanked/WarGameDeck/Assets/vehicles.js';

const files = fs.readdirSync(assetsPath).filter(f => f.endsWith('.html') && f !== 'index.html');

let allVehicles = {};

function decodeHtml(html) {
    if (!html) return '';
    return html.replace(/&eacute;/g, 'é')
               .replace(/&egrave;/g, 'è')
               .replace(/&agrave;/g, 'à')
               .replace(/&icirc;/g, 'î')
               .replace(/&ocirc;/g, 'ô')
               .replace(/&ucirc;/g, 'û')
               .replace(/&ccedil;/g, 'ç')
               .replace(/&nbsp;/g, ' ')
               .replace(/<[^>]*>/g, ' ');
}

function sanitizeFilename(name) {
    return name.replace(/[<>:"/\\|?*]/g, '_').replace(/ /g, '_').replace(/[^a-zA-Z0-9_-]/g, '') + '.png';
}

function parseCreditType(type, typeName) {
    type = (type || '').toLowerCase();
    typeName = (typeName || '').toLowerCase();
    
    if (type.includes('infant') || typeName.includes('infant')) return 'infantry';
    if (type.includes('blind') || typeName.includes('blind')) return 'armor';
    if (type.includes('meca') || typeName.includes('meca')) return 'mechanized';
    if (type.includes('moto') || typeName.includes('moto')) return 'motorized';
    if (type.includes('support') || typeName.includes('support')) return 'support';
    if (type.includes('aérien') || type.includes('plane') || type.includes('aeriens') || typeName.includes('aérien') || typeName.includes('aeriens')) return 'plane';
    if (type.includes('invit') || typeName.includes('invit')) return 'invitation';
    return null;
}

function extractCredits(vehicle) {
    let emports = [];
    let baseCredits = { infantry: 0, armor: 0, mechanized: 0, motorized: 0, support: 0, plane: 0, invitation: 0 };
    let foundBase = false;

    // Check "credits" array (if it exists in future formats)
    if (Array.isArray(vehicle.credits)) {
        vehicle.credits.forEach(c => {
            const type = parseCreditType(c.type, c.typeName);
            if (type) {
                baseCredits[type] += parseInt(c.value) || 0;
                foundBase = true;
            }
        });
    }

    // Check blocks for credit types
    if (vehicle.description && typeof vehicle.description === 'object' && vehicle.description.blocks) {
        vehicle.description.blocks.forEach(block => {
            if (block.type === 'credit') {
                const creditType = parseCreditType(block.data.type, block.data.typeName);
                if (creditType) {
                    if (!foundBase) {
                        // First credit is the base
                        baseCredits[creditType] = parseInt(block.data.value) || 0;
                        foundBase = true;
                    } else {
                        // Subsequent are emports
                        const emport = { infantry: 0, armor: 0, mechanized: 0, motorized: 0, support: 0, plane: 0, invitation: 0 };
                        emport[creditType] = parseInt(block.data.value) || 0;
                        emport._text = block.data.text || block.data.typeName || 'Option';
                        emports.push(emport);
                    }
                }
            }
        });
    }

    // Check string description for legacy formats
    if (typeof vehicle.description === 'string') {
        const text = decodeHtml(vehicle.description);
        
        // Match the base credit which is usually at the top like "- Crédits : 3 - Crédits Aériens"
        const regex = /(\d+)\s*-\s*Crédits\s*([^<\s\n]+)/gi;
        let match;
        while ((match = regex.exec(text)) !== null) {
            const val = parseInt(match[1]);
            const typeText = match[2];
            const creditType = parseCreditType(typeText, typeText);
            
            if (creditType) {
                if (!foundBase) {
                    // First one is base cost
                    baseCredits[creditType] = val;
                    foundBase = true;
                } else {
                    // Subsequent are emports
                    // Try to find the emport name by looking backwards from the match
                    let emportName = `Option ${emports.length + 1}`;
                    const beforeText = text.substring(0, match.index);
                    const tdMatch = beforeText.match(/<td>([^<]+)<\/td>\s*<td>$/i);
                    if (tdMatch) {
                        emportName = tdMatch[1].trim();
                    } else {
                        emportName = `${val} - Crédits ${typeText}`;
                    }
                    
                    const emport = { infantry: 0, armor: 0, mechanized: 0, motorized: 0, support: 0, plane: 0, invitation: 0 };
                    emport[creditType] = val;
                    emport._text = emportName;
                    emports.push(emport);
                }
            }
        }
    }

    return { base: baseCredits, emports: emports };
}

files.forEach(file => {
    const filePath = path.join(assetsPath, file);
    if (fs.lstatSync(filePath).isDirectory()) return;

    const content = fs.readFileSync(filePath, 'utf8');
    const startIdx = content.indexOf('const vehicleList = [');
    if (startIdx === -1) return;
    
    let bracketCount = 0;
    let endIdx = -1;
    for (let i = startIdx + 'const vehicleList = '.length; i < content.length; i++) {
        if (content[i] === '[') bracketCount++;
        if (content[i] === ']') {
            bracketCount--;
            if (bracketCount === 0) {
                endIdx = i + 1;
                break;
            }
        }
    }

    if (endIdx !== -1) {
        const jsonStr = content.substring(startIdx + 'const vehicleList = '.length, endIdx);
        try {
            const list = JSON.parse(jsonStr);
            const countryFolderName = file.replace('.html', '').toLowerCase().replace(/ /g, '_').replace(/-/g, '_');
            const countryName = file.replace('.html', '').replace(/_/g, ' ');
            
            allVehicles[countryName] = list.map(v => {
                const creditInfo = extractCredits(v);
                
                // Determine image_path for Python script compatibility
                let image_path = v.thumbnail || "";
                if (image_path.includes('i.imgur.com') || image_path === "") {
                    image_path = `Image/${countryFolderName}/${sanitizeFilename(v.name)}`.replace(/\\/g, '/');
                }

                return {
                    id: v.id,
                    name: v.name,
                    thumbnail: v.thumbnail,
                    image_path: image_path.replace(/\\/g, '/'),
                    rank: v.rank,
                    br: v.br,
                    type: v.type,
                    baseCredits: creditInfo.base,
                    emportOptions: creditInfo.emports
                };
            });
            
            console.log(`Extracted ${list.length} vehicles from ${file}`);
        } catch (e) {
            console.error(`Failed to parse vehicleList from ${file}:`, e.message);
        }
    }
});

// Save both JSON and JS
fs.writeFileSync(jsonOutputPath, JSON.stringify(allVehicles, null, 2));
fs.writeFileSync(jsOutputPath, "window.VEHICLES_DATA = " + JSON.stringify(allVehicles, null, 2) + ";");
console.log(`Saved ${Object.keys(allVehicles).length} countries to ${jsonOutputPath} and ${jsOutputPath}`);
