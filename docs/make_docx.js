const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun, HeadingLevel, AlignmentType,
  LevelFormat, WidthType, BorderStyle, ShadingType, PageBreak, Footer, PageNumber, TableOfContents } = require("docx");

const BR = "0F4C5C", W = 9638;
const bd = { style: BorderStyle.SINGLE, size: 4, color: "C9D6DA" };
const borders = { top: bd, bottom: bd, left: bd, right: bd };
const P = (t, o = {}) => new Paragraph({ spacing: { after: 120, line: 300 }, ...o, children: Array.isArray(t) ? t : [new TextRun(t)] });
const B = t => new TextRun({ text: t, bold: true });
const H1 = t => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] });
const H2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const bullet = t => new Paragraph({ numbering: { reference: "b", level: 0 }, spacing: { after: 60 }, children: Array.isArray(t) ? t : [new TextRun(t)] });
const code = t => t.split("\n").map(l => new Paragraph({ spacing: { after: 0 }, shading: { type: ShadingType.CLEAR, fill: "EEF3F4" },
  children: [new TextRun({ text: l || " ", font: "Consolas", size: 18 })] }));

function table(cols, rows) {
  const total = cols.reduce((a, b) => a + b, 0);
  const cell = (t, w, head) => new TableCell({ width: { size: w, type: WidthType.DXA }, borders,
    shading: head ? { type: ShadingType.CLEAR, fill: BR } : undefined,
    margins: { top: 70, bottom: 70, left: 100, right: 100 },
    children: [new Paragraph({ children: [new TextRun({ text: String(t), bold: head, color: head ? "FFFFFF" : "14292F", size: 19 })] })] });
  return new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: cols,
    rows: rows.map((r, i) => new TableRow({ tableHeader: i === 0, children: r.map((c, j) => cell(c, cols[j], i === 0)) })) });
}
const img = (path, w, h) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
  children: [new ImageRun({ type: "png", data: fs.readFileSync(path), transformation: { width: w, height: h }, altText: { title: path, description: "Schéma", name: path } })] });
const caption = t => P([new TextRun({ text: t, italics: true, color: "5B6F75", size: 18 })], { alignment: AlignmentType.CENTER });

const c = [];
// Page de titre
c.push(new Paragraph({ spacing: { before: 2400, after: 200 }, children: [new TextRun({ text: "AI in Healthcare", bold: true, size: 64, color: BR })] }));
c.push(new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "Architecture multi-agents par secteur avec agent de monitoring", size: 32 })] }));
c.push(new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Mini-projet final : tests automatisés, Docker, déploiement Render", size: 24, color: "5B6F75" })] }));
c.push(new Paragraph({ spacing: { before: 600 }, children: [new TextRun({ text: "Documentation technique · version 1.0.0 · 30 octobre 2026", size: 22 })] }));
c.push(new Paragraph({ children: [new PageBreak()] }));

c.push(H1("1. Contexte et objectifs"));
c.push(P("L'énoncé demande une architecture multi-agents spécialisée par secteur (mines, santé, automobile, finance, énergie et e-Gov) intégrant un agent de monitoring, avec des tests automatisés (GitHub Actions), une conteneurisation Docker et un déploiement sur une plateforme cloud telle que Render. Le projet met en avant le secteur de la santé (triage patient) et traite les cinq autres secteurs avec le même socle."));
c.push(P("Principe directeur : l'agent aide à la décision, il ne décide pas. Tout cas à risque élevé est escaladé à un humain (Human-in-the-Loop), et un échec technique conduit à une revue manuelle."));
c.push(H2("Périmètre et données"));
c.push(bullet("Données entièrement fictives ; aucune donnée nominative (identifiants pseudonymisés du type PAT-001)."));
c.push(bullet("Scores calculés par des règles déterministes et documentées, à valider par un expert métier avant tout usage réel."));
c.push(bullet("Latences, tokens et coûts sont simulés : aucun modèle de langage n'est appelé dans cette version."));

c.push(H1("2. Architecture"));
c.push(P("Une demande (formulaire du dashboard ou appel API) est validée, puis prise en charge par l'orchestrateur. Celui-ci génère le Correlation ID, route vers l'agent du secteur concerné, applique le seuil HITL et choisit la sortie. L'agent de monitoring trace chaque étape sous le même Correlation ID."));
c.push(img("architecture.png", 610, 356));
c.push(caption("Figure 1 : architecture multi-agents par secteur"));
c.push(table([2300, 7338], [["Composant", "Rôle"],
  ["API FastAPI (app/api.py)", "Validation Pydantic, endpoints, service du dashboard sur le port 8001."],
  ["Orchestrateur (app/pipeline.py)", "Correlation ID, routage par secteur, seuil HITL, garde-fou kill switch."],
  ["Agents sectoriels (app/sectors.py)", "Score de risque 0-100 par secteur, à partir d'indicateurs pondérés."],
  ["Agent de monitoring (AgentMonitoring)", "Trace durée, tokens, coût, statut ; alimente KPI et alertes (app/stats.py)."],
  ["Gouvernance (app/governance.py)", "Version active, kill switch, rollback, non-régression, approbation, audit."]]));

c.push(H1("3. Agents sectoriels"));
c.push(P("Chaque agent additionne des points pondérés (somme des poids = 100) selon l'écart de chaque indicateur entre son seuil normal et son seuil critique, plus un drapeau oui/non. Un score à partir de 70 est « Risque élevé » ; à partir de 35, « Risque modéré »."));
c.push(table([1500, 2500, 5638], [["Secteur", "Agent", "Indicateurs (poids)"],
  ["Santé", "Agent Triage Patient", "SpO2 (35), température (20), fréquence cardiaque (20), douleur (15), comorbidités (10)"],
  ["Mines", "Agent Sécurité Minière", "Méthane (40), vibration (30), température galerie (20), zone confinée (10)"],
  ["Automobile", "Agent Maintenance Véhicule", "Température moteur (35), usure freins (40), pression pneus (15), alerte airbag (10)"],
  ["Finance", "Agent Risque Transaction", "Montant / moyenne (40), transactions 24 h (30), ancienneté compte (20), pays à risque (10)"],
  ["Énergie", "Agent Stabilité Réseau", "Charge réseau (40), écart de fréquence (30), température transformateur (20), maintenance (10)"],
  ["e-Gov", "Agent Dossier Administratif", "Anomalies pièces (40), délai (30), similarité demandes (20), cas sensible (10)"]]));
c.push(H2("Exemple santé"));
c.push(P("Patient PAT-002 : SpO2 85 %, température 39,8 °C, fréquence cardiaque 145 bpm, douleur 9/10, comorbidités. Score 100, risque élevé, escalade HITL. Patient PAT-001 (SpO2 98 %, 36,8 °C, 72 bpm, douleur 1) : score 0, sortie automatique."));

c.push(H1("4. Observabilité : agent de monitoring et Correlation ID"));
c.push(P([B("Critère de validation : "), new TextRun("un Correlation ID est présent sur chaque exécution.")]));
c.push(bullet("Format CID- suivi de 10 caractères hexadécimaux (UUID tronqué), généré par l'orchestrateur."));
c.push(bullet("Le même identifiant figure sur le résultat, sur chaque événement de logs/execution_log.jsonl et dans la réponse de l'API : une exécution se reconstitue de bout en bout."));
c.push(bullet("Les exécutions en échec ou suspendues par le kill switch reçoivent aussi un Correlation ID."));
c.push(bullet("Alertes : latence > 5 000 ms, taux d'échec > 20 %. KPI : taux de succès, p95, tokens, coût, escalades."));
c.push(P("Contrôles automatisés : tests test_correlation_id_sur_chaque_execution_et_chaque_evenement et test_correlation_ids_uniques ; le lot de test affiche « Correlation ID présent sur 27/27 exécutions »."));

c.push(H1("5. Gouvernance"));
c.push(bullet([B("Agent Cards : "), new TextRun("8 cartes (orchestrateur, monitoring, 6 agents sectoriels) dans governance/agent_cards.json : identifiant, description, propriétaires, garde-fous, limites, version, dates de revue. Un test vérifie que tous les champs sont renseignés.")]));
c.push(bullet([B("Versionnement SemVer : "), new TextRun("versions dans governance/versions/, historique dans CHANGELOG.md, version active dans active_config.json.")]));
c.push(bullet([B("Non-régression : "), new TextRun("6 cas golden rejoués avant tout déploiement.")]));
c.push(bullet([B("Approbation à deux rôles : "), new TextRun("le déploiement exige deux approbateurs distincts.")]));
c.push(bullet([B("Kill switch et rollback : "), new TextRun("endpoints protégés par X-Admin-Token ; actions tracées dans logs/audit.jsonl.")]));

c.push(H1("6. Tests automatisés et GitHub Actions"));
c.push(P("28 tests (scoring, pipeline, gouvernance, API). Les 22 tests du cœur ont été exécutés avec succès pendant la préparation ; les 6 tests d'API nécessitent FastAPI et httpx et s'exécutent via pip install -r requirements-dev.txt (ils sont ignorés si FastAPI est absent)."));
c.push(table([3000, 6638], [["Test", "Vérifie"],
  ["Scoring", "Bornes 0-100 pour les 6 secteurs, poids = 100, entrées invalides refusées"],
  ["Pipeline", "Correlation ID, escalade HITL, sortie automatique, échec, kill switch, absence de donnée nominative, lot de 27 demandes"],
  ["Gouvernance", "Agent Cards complètes, SemVer, golden, refus de v1.1.0, deux rôles, rollback, audit"],
  ["API", "Santé, dashboard, analyse, validation, statistiques, endpoints protégés"]]));
c.push(P("Le workflow .github/workflows/ci.yml enchaîne : python main.py --check, pytest, lot de test, simulation d'incident, puis construction de l'image Docker et test de santé du conteneur. Un échec bloque la suite."));

c.push(H1("7. Conteneurisation et déploiement"));
c.push(P("L'image Docker (python:3.12-slim, utilisateur non-root, HEALTHCHECK sur /api/health) expose le port 8001. docker-compose.yml monte outputs, logs et governance ; un profil batch exécute le lot de test."));
c.push(...code("cp .env.example .env\ndocker compose up --build        # http://localhost:8001\ndocker compose --profile batch run batch"));
c.push(img("deploiement.png", 610, 200));
c.push(caption("Figure 2 : chaîne GitHub Actions, Docker, Render"));
c.push(P("Déploiement Render : le fichier render.yaml décrit un Web Service Docker avec healthCheckPath /api/health ; ADMIN_TOKEN est saisi dans Render. Le déploiement effectif sur Render doit être réalisé avec votre compte ; l'URL publique est à ajouter ici et dans la démo."));

c.push(H1("8. Tableau de bord (localhost:8001)"));
c.push(bullet("Logo et menu : Vue d'ensemble, Analyser, Exécutions, Gouvernance, Runbook."));
c.push(bullet("Vue d'ensemble : 8 KPI, répartition par catégorie (anneau), exécutions par secteur, latences avec seuil, alertes."));
c.push(bullet("Formulaire « Analyser » : choix du secteur, champs adaptés, résultat avec score, catégorie, route, Correlation ID et détail des points."));
c.push(bullet("Gouvernance : version active, seuil, état du kill switch, Agent Cards, journal d'audit."));
c.push(bullet("Mode hors ligne : ouvert sans l'API, il affiche l'instantané du dernier lot et calcule le score localement."));

c.push(H1("9. Incident et runbook"));
c.push(P([B("Scénario simulé (CR-002) : "), new TextRun("le seuil HITL passe de 70 à 90 pour réduire les escalades. Les patients au score 70-89 ne sont plus escaladés (ex. score 77).")]));
c.push(img("incident.png", 610, 200));
c.push(caption("Figure 3 : cycle de gestion d'incident"));
c.push(table([2200, 7438], [["Étape", "Résultat de la simulation (scripts/simulate_incident.py)"],
  ["1. Détection", "Version 1.1.0 active : 1 patient critique non escaladé"],
  ["2. Contention", "Kill switch actif : statut « Suspendu (kill switch) », revue manuelle"],
  ["3. Remédiation", "Rollback vers 1.0.0 : 0 anomalie"],
  ["4. Rétablissement", "Kill switch désactivé ; redéploiement de 1.1.0 refusé par la non-régression (cas G3)"]]));
c.push(P("Retour d'expérience : aucun cas golden ne couvrait la zone 70-89. Le cas G3 a été ajouté ; toute modification de seuil exige désormais validation clinique et passage de la non-régression. Procédure complète : docs/RUNBOOK.md."));

c.push(H1("10. Résultats du lot de test"));
c.push(table([4800, 4838], [["Indicateur", "Valeur (version 1.0.0)"],
  ["Exécutions", "27 (6 secteurs ; 11 en santé)"], ["Correlation ID présents", "27 / 27"],
  ["Taux de succès / d'échec", "92,6 % / 7,4 % (2 demandes volontairement invalides)"],
  ["Catégories", "11 faible · 10 modéré · 4 élevé · 2 en échec"],
  ["Escalades HITL", "4 (patients PAT-002, PAT-004, PAT-006, PAT-009)"],
  ["Latence moyenne / p95", "1 149 ms / 5 279 ms (simulées)"], ["Alertes", "4 alertes de latence > 5 000 ms"],
  ["Tokens / coût", "5 097 tokens / 0,0025 USD (simulés)"]]));

c.push(H1("11. Grille des critères de validation"));
c.push(table([2300, 4700, 2638], [["Critère", "Preuve", "Statut"],
  ["Observabilité", "Correlation ID sur 27/27 exécutions ; tests dédiés", "Validé en local"],
  ["Tests", "28 tests ; CI GitHub Actions", "22 exécutés ici ; CI à lancer sur GitHub"],
  ["Gouvernance", "8 Agent Cards complètes, testées", "Validé en local"],
  ["Conteneurisation et déploiement", "Dockerfile, compose, render.yaml, /api/health", "À construire et déployer sur votre compte"],
  ["Incident", "Runbook appliqué par simulation, rapport JSON", "Validé en local"],
  ["Documentation + démo vidéo", "Ce document, présentation, docs/SCENARIO_VIDEO.md", "Vidéo à enregistrer"]]));

c.push(H1("12. Limites et suites"));
c.push(bullet("Scores à base de règles pédagogiques : validation par un clinicien indispensable avant tout usage réel."));
c.push(bullet("Pas de modèle de langage branché : latences et coûts simulés ; une intégration réelle nécessiterait de nouveaux tests et une revue des données transmises."));
c.push(bullet("Slack simulé ; stockage sur fichiers (à remplacer par une base de données en production)."));
c.push(bullet("Le JSON de workflow est un schéma simplifié du flux, pas un export Langflow natif."));
c.push(bullet("Suites : alertes réelles (Slack/e-mail), base de données, métriques Prometheus, authentification des utilisateurs."));

c.push(H1("Annexe : commandes"));
c.push(...code("pip install -r requirements-dev.txt\npython main.py --check\npython main.py\npython -m pytest -q\npython scripts/simulate_incident.py\npython scripts/build_dashboard.py\npython -m uvicorn app.api:app --port 8001"));

const doc = new Document({
  creator: "Mini-projet AI in Healthcare", title: "AI in Healthcare - Documentation technique",
  styles: { default: { document: { run: { font: "Arial", size: 21 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 32, bold: true, color: BR, font: "Arial" }, paragraph: { spacing: { before: 320, after: 160 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 25, bold: true, color: "E36414", font: "Arial" }, paragraph: { spacing: { before: 220, after: 100 }, outlineLevel: 1 } }] },
  numbering: { config: [{ reference: "b", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] }] },
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "AI in Healthcare · documentation technique · page ", size: 16, color: "5B6F75" }), new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "5B6F75" })] })] }) },
    children: c }]
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync("Documentation_AI_in_Healthcare.docx", b); console.log("docx ok"); });
