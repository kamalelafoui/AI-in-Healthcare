const pptxgen = require("pptxgenjs");
const { applyTheme } = require("/mnt/skills/public/pptx/scripts/apply_theme.js");
const THEME = { name: "Healthcare", headFontFace: "Georgia", bodyFontFace: "Calibri",
  colors: { dk1: "14292F", lt1: "FFFFFF", dk2: "0F4C5C", lt2: "F4F7F8", accent1: "0F4C5C", accent2: "E36414", accent3: "2A9D8F", accent4: "E9A100", accent5: "C0392B", accent6: "5B6F75", hlink: "0F4C5C", folHlink: "5B6F75" } };

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "AI in Healthcare - mini-projet final";
const C = pres.SchemeColor;

pres.defineSlideMaster({ title: "TITRE", background: { color: "0F4C5C" },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.7, y: 1.5, w: 8.6, h: 1.4, fontSize: 40, bold: true, color: "FFFFFF", valign: "bottom", align: "left" }, text: "" } },
            { placeholder: { options: { name: "body", type: "body", x: 0.7, y: 3.1, w: 8.6, h: 1.2, fontSize: 18, color: "C9E3EA" }, text: "" } }] });
pres.defineSlideMaster({ title: "CONTENU", background: { color: "FFFFFF" }, slideNumber: { x: 9.2, y: 5.25, fontSize: 10, color: "5B6F75" },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 9, h: 0.7, fontSize: 24, bold: true, color: "0F4C5C", valign: "middle", align: "left" }, text: "" } },
            { text: { text: "AI in Healthcare · 1.0.0", options: { x: 0.5, y: 5.25, w: 4, h: 0.25, fontSize: 9, color: "5B6F75", isTextBox: true, margin: 0 } } }] });

const tb = (s, t, o) => s.addText(t, { isTextBox: true, fontFace: "Calibri", color: "14292F", ...o });
function card(s, x, y, w, h, title, body, color) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: "F4F7F8" }, line: { color: "DCE5E8", width: 1 }, rectRadius: 0.08, objectName: "card " + title });
  s.addShape(pres.ShapeType.rect, { x, y: y + 0.12, w: 0.07, h: h - 0.24, fill: { color: color || "E36414" }, line: { color: color || "E36414", width: 0 } });
  tb(s, title, { x: x + 0.2, y: y + 0.08, w: w - 0.3, h: 0.35, fontSize: 14, bold: true, color: "0F4C5C", margin: 0 });
  tb(s, body, { x: x + 0.2, y: y + 0.45, w: w - 0.3, h: h - 0.55, fontSize: 11.5, valign: "top", margin: 0 });
}
const slide = t => { const s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Contenu" }); s.addText(t, { placeholder: "title" }); return s; };

pres.addSection({ title: "Introduction" });
let s = pres.addSlide({ masterName: "TITRE", sectionTitle: "Introduction" });
s.addText("AI in Healthcare", { placeholder: "title" });
s.addText("Architecture multi-agents par secteur · monitoring · tests · Docker · Render\nMini-projet final · 30 octobre 2026", { placeholder: "body" });
s.addNotes("Présenter le projet : 6 secteurs, un agent de monitoring, la santé en vedette. Données fictives.");

pres.addSection({ title: "Contenu" });
s = slide("Énoncé et objectifs");
card(s, 0.5, 1.2, 4.4, 1.55, "Ce qui est demandé", "Architecture multi-agents spécialisée par secteur (mines, santé, automobile, finance, énergie, e-Gov) avec un agent de monitoring.", "0F4C5C");
card(s, 5.1, 1.2, 4.4, 1.55, "Industrialisation", "Tests automatisés (GitHub Actions), conteneurisation Docker, déploiement sur Render.", "0F4C5C");
card(s, 0.5, 2.95, 4.4, 1.55, "Principe directeur", "L'agent aide à décider, il ne décide pas : un risque élevé est escaladé à un humain (HITL).", "E36414");
card(s, 5.1, 2.95, 4.4, 1.55, "Périmètre", "Données fictives, identifiants pseudonymisés, scores à base de règles à valider par un expert métier.", "E36414");
s.addNotes("Rappeler l'énoncé puis les garde-fous : aucune décision médicale finale.");

s = slide("Architecture multi-agents");
s.addImage({ path: "architecture.png", x: 0.9, y: 1.1, w: 8.2, h: 4.1, sizing: { type: "contain", w: 8.2, h: 4.1 }, altText: "Architecture : API, orchestrateur, 6 agents sectoriels, monitoring, gouvernance" });
s.addNotes("Parcours d'une demande : API, orchestrateur (Correlation ID), agent sectoriel, monitoring, escalade HITL.");

s = slide("Six agents sectoriels, un même socle");
const sec = [["Santé", "Triage patient : SpO2, température, fréquence cardiaque, douleur, comorbidités", "E36414"], ["Mines", "Sécurité : méthane, vibration, température galerie", "0F4C5C"], ["Automobile", "Maintenance : moteur, freins, pneus, airbag", "0F4C5C"],
  ["Finance", "Risque transaction : montant, fréquence, ancienneté, pays", "0F4C5C"], ["Énergie", "Stabilité réseau : charge, fréquence, transformateur", "0F4C5C"], ["e-Gov", "Dossier : anomalies, délai, similarité, cas sensible", "0F4C5C"]];
sec.forEach((c, i) => card(s, 0.5 + (i % 3) * 3.07, 1.2 + Math.floor(i / 3) * 1.9, 2.9, 1.7, c[0], c[1], c[2]));
tb(s, "Score 0-100 (poids = 100) · ≥ 70 risque élevé → escalade HITL · ≥ 35 modéré", { x: 0.5, y: 4.95, w: 9, h: 0.3, fontSize: 12, color: "5B6F75", margin: 0 });
s.addNotes("Même mécanique pour les six agents : indicateurs pondérés plus un drapeau oui/non.");

s = slide("Observabilité : un Correlation ID partout");
s.addShape(pres.ShapeType.roundRect, { x: 0.5, y: 1.2, w: 4.2, h: 3.7, fill: { color: "0F4C5C" }, line: { color: "0F4C5C", width: 0 }, rectRadius: 0.1, objectName: "stat card" });
tb(s, "27 / 27", { x: 0.7, y: 1.5, w: 3.8, h: 1.0, fontSize: 54, bold: true, color: "FFFFFF", fontFace: "Georgia", margin: 0 });
tb(s, "exécutions avec Correlation ID unique (format CID-xxxxxxxxxx), y compris échecs et kill switch", { x: 0.7, y: 2.6, w: 3.8, h: 1.2, fontSize: 15, color: "C9E3EA", margin: 0 });
tb(s, "Alertes : latence > 5 000 ms · échec > 20 %", { x: 0.7, y: 4.1, w: 3.8, h: 0.6, fontSize: 13, color: "FFFFFF", margin: 0 });
s.addText([{ text: "Même identifiant sur le résultat, chaque événement du journal et la réponse API", options: { bullet: true, breakLine: true } },
  { text: "Agent de monitoring : durée, tokens, coût, statut par étape", options: { bullet: true, breakLine: true } },
  { text: "KPI : succès 92,6 %, échec 7,4 %, latence moyenne 1 149 ms, p95 5 279 ms", options: { bullet: true, breakLine: true } },
  { text: "Tests : unicité et présence sur tous les événements", options: { bullet: true } }],
  { isTextBox: true, x: 5.0, y: 1.3, w: 4.5, h: 3.4, fontSize: 15, color: "14292F", paraSpaceAfter: 10, valign: "top" });
s.addNotes("Critère d'observabilité : montrer le résultat du lot et le dashboard avec les Correlation ID.");

s = slide("Gouvernance et garde-fous");
card(s, 0.5, 1.2, 4.4, 1.15, "8 Agent Cards", "Orchestrateur, monitoring, 6 agents : propriétaires, garde-fous, limites, revue.", "0F4C5C");
card(s, 5.1, 1.2, 4.4, 1.15, "SemVer + CHANGELOG", "Versions 1.0.0 (active) et 1.1.0 (retirée), demandes de changement CR-001/002.", "0F4C5C");
card(s, 0.5, 2.55, 4.4, 1.15, "Non-régression golden", "6 cas rejoués avant tout déploiement ; v1.1.0 refusée.", "E36414");
card(s, 5.1, 2.55, 4.4, 1.15, "Approbation à deux rôles", "Deux approbateurs distincts requis pour déployer.", "E36414");
card(s, 0.5, 3.9, 9.0, 1.0, "Kill switch · rollback · audit", "Endpoints protégés par jeton ; chaque action est tracée dans le journal d'audit.", "2A9D8F");

s = slide("Tests automatisés et chaîne CI/CD");
s.addImage({ path: "deploiement.png", x: 0.6, y: 1.1, w: 8.8, h: 2.9, sizing: { type: "contain", w: 8.8, h: 2.9 }, altText: "Chaîne GitHub Actions, Docker, Render" });
s.addText([{ text: "28 tests : scoring, pipeline, gouvernance, API", options: { bullet: true, breakLine: true } },
  { text: "CI : check + pytest + lot + simulation d'incident, puis build Docker et test de santé", options: { bullet: true, breakLine: true } },
  { text: "Docker : image slim, utilisateur non-root, HEALTHCHECK · Render : render.yaml, ADMIN_TOKEN hors dépôt", options: { bullet: true } }],
  { isTextBox: true, x: 0.6, y: 4.05, w: 8.8, h: 1.1, fontSize: 13, color: "14292F", paraSpaceAfter: 4, valign: "top" });
s.addNotes("Précision : les 6 tests d'API et la CI se lancent sur la machine de l'étudiant / GitHub ; le déploiement Render se fait avec son compte.");

s = slide("Dashboard — localhost:8001");
s.addImage({ path: "screens/dashboard_vue_ensemble.png", x: 0.5, y: 1.15, w: 4.5, h: 3.2, sizing: { type: "contain", w: 4.5, h: 3.2 }, altText: "Dashboard : KPI et graphiques" });
s.addImage({ path: "screens/dashboard_analyse.png", x: 5.1, y: 1.15, w: 4.4, h: 3.2, sizing: { type: "contain", w: 4.4, h: 3.2 }, altText: "Formulaire d'analyse et résultat" });
tb(s, "Logo, menu (5 vues), KPI, anneau des catégories, latences avec seuil, formulaire par secteur avec Correlation ID, Agent Cards et audit. Utilisable hors ligne.", { x: 0.5, y: 4.5, w: 9, h: 0.7, fontSize: 13, margin: 0 });

s = slide("Incident CR-002 : le runbook en action");
s.addImage({ path: "incident.png", x: 0.6, y: 1.1, w: 8.8, h: 2.7, sizing: { type: "contain", w: 8.8, h: 2.7 }, altText: "Détection, contention, remédiation, rétablissement" });
s.addText([{ text: "Cause : seuil HITL relevé de 70 à 90 → les patients au score 70-89 ne sont plus escaladés", options: { bullet: true, breakLine: true } },
  { text: "Rollback vers 1.0.0 : 1 anomalie avant, 0 après", options: { bullet: true, breakLine: true } },
  { text: "Redéploiement de 1.1.0 désormais refusé par la non-régression (cas G3, score 77)", options: { bullet: true } }],
  { isTextBox: true, x: 0.6, y: 3.9, w: 8.8, h: 1.2, fontSize: 14, color: "14292F", paraSpaceAfter: 5, valign: "top" });

s = slide("Critères de validation");
const hd = t => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: "0F4C5C" } } });
const rows = [[hd("Critère"), hd("Preuve"), hd("Statut")],
  ["Observabilité", "Correlation ID 27/27", "Validé en local"], ["Tests", "28 tests + GitHub Actions", "22 exécutés ici · CI à lancer"],
  ["Gouvernance", "8 Agent Cards complètes", "Validé en local"], ["Conteneurisation / déploiement", "Dockerfile, compose, render.yaml", "À déployer sur Render"],
  ["Incident", "Runbook simulé, rapport JSON", "Validé en local"], ["Documentation + vidéo", "docx, pptx, scénario vidéo", "Vidéo à enregistrer"]];
s.addTable(rows, { x: 0.5, y: 1.2, w: 9, colW: [2.9, 3.3, 2.8], fontSize: 13, fontFace: "Calibri", color: "14292F", border: { type: "solid", pt: 0.75, color: "DCE5E8" }, rowH: 0.5, valign: "middle" });

pres.addSection({ title: "Conclusion" });
s = pres.addSlide({ masterName: "TITRE", sectionTitle: "Conclusion" });
s.addText("Limites et suites", { placeholder: "title" });
s.addText("Latences et coûts simulés · règles à valider par un clinicien · Slack simulé · stockage fichiers\nSuites : modèle réel, base de données, alertes Slack/e-mail, métriques", { placeholder: "body" });

pres.writeFile({ fileName: "Presentation_AI_in_Healthcare.pptx" }).then(() => applyTheme("Presentation_AI_in_Healthcare.pptx", THEME)).then(() => console.log("pptx ok"));
