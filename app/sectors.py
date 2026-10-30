"""Agents sectoriels : un scoreur de risque spécialisé par secteur.

Chaque indicateur : (champ, libellé, unité, sens, seuil_ok, seuil_critique, poids)
sens "haut" : plus la valeur est élevée, plus le risque augmente ; "bas" : l'inverse.
Les règles sont des hypothèses pédagogiques, à valider par un expert métier.
"""
SECTEURS = {
    "sante": {
        "nom": "Santé", "agent": "Agent Triage Patient", "id": "HC-SANTE-001",
        "indicateurs": [
            ("spo2", "Saturation en oxygène", "%", "bas", 95, 88, 35),
            ("temperature", "Température", "°C", "haut", 37.5, 39.5, 20),
            ("frequence_cardiaque", "Fréquence cardiaque", "bpm", "haut", 100, 140, 20),
            ("douleur", "Douleur (0-10)", "/10", "haut", 3, 8, 15),
        ],
        "drapeau": ("comorbidites", "Comorbidités", 10),
    },
    "mines": {
        "nom": "Mines", "agent": "Agent Sécurité Minière", "id": "HC-MINES-001",
        "indicateurs": [
            ("methane", "Méthane", "% vol", "haut", 0.5, 1.5, 40),
            ("vibration", "Vibration", "mm/s", "haut", 5, 15, 30),
            ("temperature", "Température galerie", "°C", "haut", 30, 45, 20),
        ],
        "drapeau": ("zone_confinee", "Zone confinée", 10),
    },
    "automobile": {
        "nom": "Automobile", "agent": "Agent Maintenance Véhicule", "id": "HC-AUTO-001",
        "indicateurs": [
            ("temp_moteur", "Température moteur", "°C", "haut", 100, 125, 35),
            ("usure_freins", "Usure des freins", "%", "haut", 60, 90, 40),
            ("pression_pneus", "Pression des pneus", "bar", "bas", 2.0, 1.4, 15),
        ],
        "drapeau": ("alerte_airbag", "Alerte airbag", 10),
    },
    "finance": {
        "nom": "Finance", "agent": "Agent Risque Transaction", "id": "HC-FIN-001",
        "indicateurs": [
            ("montant_ratio", "Montant / moyenne client", "x", "haut", 2, 10, 40),
            ("transactions_24h", "Transactions sur 24 h", "nb", "haut", 5, 25, 30),
            ("anciennete_compte", "Ancienneté du compte", "mois", "bas", 12, 1, 20),
        ],
        "drapeau": ("pays_a_risque", "Pays à risque", 10),
    },
    "energie": {
        "nom": "Énergie", "agent": "Agent Stabilité Réseau", "id": "HC-NRG-001",
        "indicateurs": [
            ("charge_reseau", "Charge du réseau", "%", "haut", 70, 95, 40),
            ("ecart_frequence", "Écart de fréquence", "Hz", "haut", 0.1, 0.5, 30),
            ("temp_transfo", "Température transformateur", "°C", "haut", 70, 110, 20),
        ],
        "drapeau": ("maintenance_en_cours", "Maintenance en cours", 10),
    },
    "egov": {
        "nom": "e-Gov", "agent": "Agent Dossier Administratif", "id": "HC-EGOV-001",
        "indicateurs": [
            ("anomalies_pieces", "Anomalies sur les pièces", "nb", "haut", 1, 4, 40),
            ("delai_traitement", "Délai de traitement", "jours", "haut", 15, 45, 30),
            ("similarite_demandes", "Similarité avec d'autres demandes", "%", "haut", 40, 85, 20),
        ],
        "drapeau": ("cas_sensible", "Cas sensible", 10),
    },
}


def _points(valeur, sens, ok, crit, poids):
    if sens == "haut":
        ratio = (valeur - ok) / (crit - ok)
    else:
        ratio = (ok - valeur) / (ok - crit)
    return poids * max(0.0, min(1.0, ratio))


def calculer_score(secteur, entree):
    """Retourne (score 0-100, détail par indicateur). Lève ValueError si l'entrée est invalide."""
    if secteur not in SECTEURS:
        raise ValueError(f"secteur inconnu : {secteur}")
    cfg = SECTEURS[secteur]
    detail, total = [], 0.0
    for champ, libelle, unite, sens, ok, crit, poids in cfg["indicateurs"]:
        if champ not in entree:
            raise ValueError(f"indicateur manquant : {champ}")
        try:
            valeur = float(entree[champ])
        except (TypeError, ValueError):
            raise ValueError(f"indicateur non numérique : {champ}")
        pts = _points(valeur, sens, ok, crit, poids)
        total += pts
        detail.append({"indicateur": libelle, "valeur": valeur, "unite": unite, "points": round(pts, 1)})
    champ_drapeau, libelle_drapeau, poids_drapeau = cfg["drapeau"]
    drapeau = str(entree.get(champ_drapeau, "non")).lower()
    if drapeau not in ("oui", "non"):
        raise ValueError(f"{champ_drapeau} doit valoir oui ou non")
    pts = poids_drapeau if drapeau == "oui" else 0
    total += pts
    detail.append({"indicateur": libelle_drapeau, "valeur": drapeau, "unite": "", "points": pts})
    return round(total), detail


def categoriser(score, seuil_hitl):
    if score >= seuil_hitl:
        return "Risque élevé"
    if score >= seuil_hitl * 0.5:
        return "Risque modéré"
    return "Risque faible"
