// ─── Doctrines et crédits ───────────────────────────────────────────────────────
// Définition des doctrines avec leurs limites de crédits par type d'unité
const DOCTRINES = {
    infantry: { name: "Infanterie", infantry: 12, armor: 0, mechanized: 3, motorized: 3, support: 2, plane: 0 },
    armored: { name: "Blindée", infantry: 2, armor: 13, mechanized: 3, motorized: 0, support: 4, plane: 0 },
    mechanized: { name: "Mécanisée", infantry: 10, armor: 0, mechanized: 10, motorized: 0, support: 2, plane: 0 },
    support: { name: "Appui", infantry: 5, armor: 0, mechanized: 2, motorized: 0, support: 10, plane: 5 },
    cas: { name: "CAS", infantry: 5, armor: 2, mechanized: 2, motorized: 3, support: 0, plane: 10 },
    mixed: { name: "Mixte", infantry: 5, armor: 5, mechanized: 2, motorized: 3, support: 3, plane: 2 }
};
