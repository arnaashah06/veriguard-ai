const pptxgen = require('pptxgenjs');
const path = require('path');

const pptx = new pptxgen();
pptx.defineLayout({ name: 'STANDARD', width: 10, height: 7.5 });
pptx.layout = 'STANDARD';
pptx.author = 'Abstract_Minds';
pptx.subject = 'VeriGuard AI technical presentation';
pptx.title = 'VeriGuard AI - SIH 2026';
pptx.company = 'Abstract_Minds';
pptx.lang = 'en-US';
pptx.theme = {
  headFontFace: 'Aptos Display',
  bodyFontFace: 'Aptos',
  lang: 'en-US'
};
pptx.defineSlideMaster({
  title: 'MASTER',
  background: { color: 'F3F6F8' },
  objects: [
    { rect: { x: 0, y: 0, w: 10, h: 0.36, fill: { color: '263B55' }, line: { color: '263B55' } } },
    { text: { text: 'Abstract_Minds  |  SIH2026-T2851  |  VeriGuard AI', options: { x: 0.42, y: 7.18, w: 8.8, h: 0.16, fontFace: 'Aptos', fontSize: 7, color: '5B6675', margin: 0 } } }
  ],
  slideNumber: { x: 9.15, y: 0.09, color: 'FFFFFF', fontFace: 'Aptos', fontSize: 8 }
});

const C = { navy: '263B55', teal: '2C7A7B', blue: '2B6CB0', gold: 'C9972B', ink: '1F2937', muted: '5B6675', white: 'FFFFFF', light: 'F3F6F8', green: '2E7D32', paleBlue: 'E7F0F5', paleGreen: 'E8F2EC', paleGold: 'FFF4D6' };
const bullet = (items) => items.map((item) => ({ text: item, options: { bullet: { indent: 14 }, hanging: 3, breakLine: true } }));

function header(slide, kicker, title) {
  slide.addText(kicker.toUpperCase(), { x: 0.42, y: 0.10, w: 5.8, h: 0.16, fontSize: 8, bold: true, color: C.white, margin: 0 });
  slide.addText(title, { x: 0.42, y: 0.68, w: 9.0, h: 0.42, fontSize: 23, bold: true, color: C.navy, margin: 0 });
}
function bullets(slide, items, x, y, w, h, size = 14) {
  slide.addText(bullet(items), { x, y, w, h, fontSize: size, color: C.ink, breakLine: false, paraSpaceAfterPt: 8, margin: 0.05, valign: 'top', fit: 'shrink' });
}
function panel(slide, x, y, w, h, fill, line = fill) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.05, fill: { color: fill }, line: { color: line, width: 1 } });
}
function footerNote(slide, text) { slide.addText(text, { x: 0.58, y: 6.76, w: 8.8, h: 0.2, fontSize: 9, color: C.muted, margin: 0 }); }

// 1 Title
{
  const s = pptx.addSlide('MASTER');
  s.background = { color: C.light };
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 10, h: 1.52, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText('SMART INDIA HACKATHON 2026', { x: 0.48, y: 0.33, w: 8.5, h: 0.24, fontSize: 15, bold: true, color: C.white, margin: 0 });
  s.addText('VeriGuard AI', { x: 0.48, y: 2.05, w: 8.7, h: 0.6, fontSize: 36, bold: true, color: C.navy, margin: 0 });
  s.addText('AI-Based Fake Identity & Document Screening System', { x: 0.5, y: 2.75, w: 8.5, h: 0.3, fontSize: 16, bold: true, color: C.teal, margin: 0 });
  s.addText('Problem Statement ID: SIH26188\nTeam ID: SIH2026-T2851\nTeam: Abstract_Minds', { x: 0.5, y: 3.55, w: 5.5, h: 1.05, fontSize: 14, color: C.ink, breakLine: false, margin: 0, paraSpaceAfterPt: 8 });
  s.addText('Team members: Arnaa Shah (Team Leader), Rushabh Khatri, Krutika Barewadia,\nMeet Jariwala, Yashvi Parmar, Jay Petigara', { x: 0.5, y: 4.85, w: 8.8, h: 0.5, fontSize: 11, color: C.ink, breakLine: false, margin: 0, fit: 'shrink' });
  s.addText('Repository: https://github.com/arnaashah06/veriguard-ai', { x: 0.5, y: 6.48, w: 8.7, h: 0.2, fontSize: 10, color: C.blue, margin: 0 });
}

// 2 Scope
{
  const s = pptx.addSlide('MASTER'); header(s, '01 | Verified Project Scope', 'What the prototype does');
  bullets(s, [
    'Screens identity-document images and an optional selfie.',
    'Supports Aadhaar, PAN, Voter ID / EPIC, Driving Licence, and Passport workflows.',
    'Processes one document or a multi-document submission.',
    'Returns structured findings, risk assessment, explanations, and audit events.',
    'Uses synthetic local demo assets for repeatable demonstrations.'
  ], 0.58, 1.55, 8.8, 3.6, 16);
  panel(s, 0.58, 5.55, 8.85, 0.68, 'E6F0F2', C.teal);
  s.addText('Scope note: this is a prototype screening workflow, not an issuing-authority verification service.', { x: 0.83, y: 5.78, w: 8.3, h: 0.2, fontSize: 12, bold: true, color: C.teal, margin: 0 });
}

// 3 Workflow
{
  const s = pptx.addSlide('MASTER'); header(s, '02 | Processing Workflow', 'From upload to evidence dossier');
  const steps = ['Upload', 'Quality check', 'OCR + parsing', 'Validation', 'Cross-document', 'Risk + audit'];
  steps.forEach((step, i) => {
    const x = 0.58 + i * 1.5;
    panel(s, x, 1.72, 1.25, 1.05, i % 2 === 0 ? C.paleBlue : C.paleGreen, i % 2 === 0 ? C.blue : C.green);
    s.addText(`0${i + 1}`, { x: x + 0.12, y: 1.85, w: 0.3, h: 0.15, fontSize: 10, bold: true, color: C.gold, margin: 0 });
    s.addText(step, { x: x + 0.12, y: 2.18, w: 1.02, h: 0.35, fontSize: 11, bold: true, color: C.ink, margin: 0, fit: 'shrink' });
    if (i < steps.length - 1) s.addText('>', { x: x + 1.29, y: 2.05, w: 0.18, h: 0.25, fontSize: 16, bold: true, color: C.gold, margin: 0 });
  });
  bullets(s, [
    'The frontend sends multipart document and selfie data to /verify or /verify-multiple.',
    'The backend validates file type, size, and image readability before analysis.',
    'The response is rendered in the ResultsPage dossier with evidence panels and officer actions.'
  ], 0.7, 3.45, 8.7, 2.0, 15);
}

// 4 Implementation
{
  const s = pptx.addSlide('MASTER'); header(s, '03 | Implementation', 'Engineering components');
  panel(s, 0.58, 1.55, 4.1, 4.3, 'FFFFFF', 'D1D9DE');
  panel(s, 5.0, 1.55, 4.42, 4.3, 'FFFFFF', 'D1D9DE');
  bullets(s, ['Frontend: React + Vite', 'Backend: FastAPI + Uvicorn', 'OCR: Tesseract with preprocessing and multiple page-segmentation paths', 'Validation: Verhoeff, PAN, EPIC, RTO, and MRZ-oriented checks'], 0.85, 1.9, 3.55, 3.5, 14);
  bullets(s, ['Biometrics: face detection, quality checks, and encoding comparison', 'Forensics: Error Level Analysis signal', 'Reconciliation: normalized names, dates, and document attributes', 'Explainability: identity story and four-domain risk decomposition'], 5.27, 1.9, 3.85, 3.5, 14);
}

// 5 Validation
{
  const s = pptx.addSlide('MASTER'); header(s, '04 | Validation Logic', 'What is checked');
  const rows = [
    ['Aadhaar', 'Length and Verhoeff checksum path'],
    ['PAN', 'Structure, entity character, surname initial'],
    ['Voter ID', 'EPIC-style format checks'],
    ['Driving Licence', 'State-code and expiry checks'],
    ['Passport', 'MRZ structure and weighted check digits'],
    ['Images', 'Blur, brightness, exposure, and tamper signals']
  ];
  rows.forEach((row, i) => {
    const y = 1.55 + i * 0.72;
    s.addShape(pptx.ShapeType.rect, { x: 0.58, y, w: 8.85, h: 0.58, fill: { color: i % 2 === 0 ? 'F0F4F6' : 'FFFFFF' }, line: { color: 'FFFFFF', transparency: 100 } });
    s.addText(row[0], { x: 0.82, y: y + 0.18, w: 1.65, h: 0.16, fontSize: 12, bold: true, color: C.navy, margin: 0 });
    s.addText(row[1], { x: 2.55, y: y + 0.18, w: 6.3, h: 0.16, fontSize: 12, color: C.ink, margin: 0 });
  });
}

// 6 Testing
{
  const s = pptx.addSlide('MASTER'); header(s, '05 | Test Evidence', 'Repository test coverage');
  bullets(s, [
    'The repository contains suites for document rules, cross-document comparison, advanced features, edge cases, face checks, forensics, and end-to-end flows.',
    'The walkthrough records 18 real-versus-fake scenarios and additional focused suites.',
    'The walkthrough also records frontend lint and production-build checks.',
    'These figures are repository-documented results and should be rerun before final submission.'
  ], 0.58, 1.55, 8.8, 3.5, 15);
  panel(s, 0.58, 5.45, 8.85, 0.7, C.paleGold, C.gold);
  s.addText('Evidence standard: report dated command output for the final submission.', { x: 0.85, y: 5.7, w: 8.2, h: 0.18, fontSize: 13, bold: true, color: C.ink, margin: 0 });
}

// 7 UI evidence
{
  const s = pptx.addSlide('MASTER'); header(s, '06 | Live Prototype Evidence', 'Results dossier from local demo flow');
  const imagePath = path.join(__dirname, 'results_capture.png');
  s.addImage({ path: imagePath, x: 0.58, y: 1.4, w: 8.85, h: 4.95 });
  s.addText('Captured from the local clean multi-document demonstration flow.', { x: 0.62, y: 6.55, w: 8.5, h: 0.18, fontSize: 9, color: C.muted, margin: 0 });
}

// 8 Limitations
{
  const s = pptx.addSlide('MASTER'); header(s, '07 | Responsible Use', 'Limitations and next validation steps');
  bullets(s, [
    'OCR and face results vary with image quality, lighting, layout, and model availability.',
    'ELA is a suspicious-signal tool and does not prove fraud by itself.',
    'Synthetic demo assets do not establish real-world accuracy.',
    'Production use requires independent security, privacy, access-control, and regulatory review.',
    'External statistics, costs, legal conclusions, and regulatory approvals are intentionally omitted.'
  ], 0.58, 1.55, 8.8, 3.65, 15);
  panel(s, 0.58, 5.55, 8.85, 0.68, C.paleGreen, C.green);
  s.addText('Next step: rerun the complete test set and attach only approved evidence.', { x: 0.85, y: 5.78, w: 8.2, h: 0.2, fontSize: 13, bold: true, color: C.green, margin: 0 });
}

pptx.writeFile({ fileName: path.join(__dirname, 'VeriGuard_AI_SIH2026.pptx') });
