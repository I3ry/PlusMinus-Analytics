from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.styles import ParagraphStyle
import pdfplumber

root = Path(__file__).resolve().parents[2]
out = root / 'output/pdf/PlusMinus_Interview_Story_Notes.pdf'
styles = {
 'title': ParagraphStyle('title', fontName='Times-Roman', fontSize=21, leading=25, spaceAfter=13),
 'head': ParagraphStyle('head', fontName='Times-Roman', fontSize=15, leading=18, spaceBefore=11, spaceAfter=6, keepWithNext=True),
 'bullet': ParagraphStyle('bullet', fontName='Helvetica', fontSize=11, leading=15, leftIndent=11, bulletIndent=0, spaceAfter=6),
}

pages = [
('PlusMinus Analytics', [
('What I set out to do', [
'I developed PlusMinus to connect basketball shooting results to a useful next step: deciding what to practice.',
'The project brought together a historical NBA explorer and a separate training prototype, supported by product documentation.'
]),
('How I organized the work', [
'I used a Product Requirements Document (PRD) to explain the problem, intended user, requirements, and acceptance criteria.',
'The feature blueprint described each capability, and the user flows connected reviewing results to choosing a practice plan.',
'The six-month roadmap outlined proposed development beyond the prototype. It was a planning horizon, not six months of completed delivery.'
]),
('How I approached the data', [
'The historical sample contained 79,763 shots across 10 selected NBA players. The Python pipeline cleaned and aggregated those records for analysis.',
'Training Lab used three fictional players, 24 sessions, and 1,440 synthetic shots so the demonstration could be repeated consistently.',
'I kept those sources separate and made their limits clear. The NBA sample was not league-wide, and synthetic practice data could not prove real player improvement.'
]),
('What the prototype demonstrated', [
'The model contained seven entities: players, sessions, shot maps, events, coaches, ratings, and plans.',
'The player, coach, and training dashboards each contained five visuals, giving 15 visuals across three dashboards.',
'Five simulated API contracts handled players, sessions, shot maps, ratings, and plans inside the browser. JSON powered the demo, with a separate SQLite artifact showing the database structure.'
]),
('How the results became a practice plan', [
'The recommendation used the selected player\'s lowest-accuracy zone with at least 20 attempts, then divided the chosen time among warm-up, focused practice, and review.',
'This made the plan specific to recorded results and available time. It remained a transparent rule, not live AI or a diagnosis of shooting technique.'
])
]),
('PlusMinus Analytics: Decisions and lessons', [
('Where data quality became important', [
'One concrete issue was the era classification, which could use a team abbreviation or misread a season identifier.',
'The correction prioritized explicit season information, used dates as a fallback, and accounted for the 2020 bubble. Rebuilt exports and regression tests supported the repair.',
'That example reinforced my main lesson: a chart can look reasonable while the underlying data means the wrong thing.'
]),
('How I checked the numbers', [
'I defined overall accuracy as total makes divided by total attempts. Sessions of 1/2 and 9/10 combine to 10/12, or 83.3%, rather than an average of 70%.',
'The validation checked record relationships, metric totals, plan durations, and simulated API responses. All four Node tests passed during the project review.',
'I also distinguished descriptive measures from stronger claims. The shooting index was a session percentage, and the 20-attempt rule was not a statistical confidence threshold.'
]),
('How I focused the next release', [
'I narrowed the proposed next release to logging a session, reviewing results, choosing a plan, and recording a comparable follow-up.',
'The requirements covered reliable saving, duplicate prevention, and record ownership. I would measure whether users could finish unaided, understand the plan, and return.',
'The production backend and user pilot remained proposed work. The goal was to evaluate the core workflow before adding more complex features.'
]),
('How I explain my contribution and results', [
'I used AI coding assistance, so I distinguish the decisions I made from implementation I reviewed or validated. My ownership discussion centers on scope, definitions, and evidence.',
'The case study brought together architecture, competitive analysis, proposed KPIs, and a go-to-market strategy. The implementation counts show scope; I cannot substantiate a threefold recruiter-engagement increase.'
]),
('What I would bring to Vanguard', [
'This project helped me connect data discovery, clear business rules, validation, and communication. I would bring that same care to understanding and supporting trusted data products.'
])
])]

story = []
for index, (title, sections) in enumerate(pages):
 if index:
  story.append(PageBreak())
 story.append(Paragraph(escape(title), styles['title']))
 for heading, bullets in sections:
  story.append(Paragraph(escape(heading), styles['head']))
  for text in bullets:
   story.append(Paragraph(escape(text), styles['bullet'], bulletText='\u2022'))

def footer(c, d):
 c.setFont('Helvetica', 8)
 c.setFillColorRGB(.4,.4,.4)
 c.drawString(50, 25, 'Interview draft: describe only the work and decisions you personally owned.')
 c.drawRightString(562, 25, f'{d.page} / 2')

SimpleDocTemplate(str(out), pagesize=(612,792), leftMargin=50, rightMargin=50,
 topMargin=40, bottomMargin=44, title='PlusMinus Analytics - My Interview Story').build(story, onFirstPage=footer, onLaterPages=footer)
with pdfplumber.open(out) as pdf:
 print('Pages:', len(pdf.pages))
 assert len(pdf.pages) == 2, 'Unexpected page overflow'
 print('Words:', sum(len(p.extract_text().split()) for p in pdf.pages))
 for i, p in enumerate(pdf.pages):
  p.to_image(resolution=110).save(root / f'tmp/pdfs/story-notes-{i+1}.png')
print(out)
