from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.styles import ParagraphStyle
from xml.sax.saxutils import escape
import pdfplumber

root=Path(__file__).resolve().parents[2]
out=root/'output/pdf/PlusMinus_Interview_Talking_Points.pdf'
title=ParagraphStyle('title',fontName='Times-Roman',fontSize=21,leading=25,spaceAfter=15)
head=ParagraphStyle('head',fontName='Times-Roman',fontSize=15,leading=18,spaceBefore=11,spaceAfter=6,keepWithNext=True)
bullet=ParagraphStyle('bullet',fontName='Helvetica',fontSize=11,leading=15,leftIndent=11,bulletIndent=0,spaceAfter=5)
sub=ParagraphStyle('sub',parent=bullet,leftIndent=25,bulletIndent=14)
pages=[('PlusMinus Analytics:',[
('What "I" Did',[
'I developed a basketball analytics prototype that connects shooting results to a suggested practice plan.',
'I used Python to clean historical shot data and aggregate it for comparisons.',
'I also produced the product requirements, feature blueprint, user flows, and roadmap.']),
('What the documents do',[
'The Product Requirements Document (PRD) defines the problem, intended user, requirements, and acceptance criteria.',
'The feature blueprint explains each capability, while the user flows show how someone moves from reviewing results to choosing a next action.',
'The six-month roadmap proposes the order of future development. It is a planning horizon, not six months of completed work.']),
('What makes it personalized?',[
'The plan uses the selected player\'s results to find the lowest-accuracy zone with at least 20 attempts.',
'It assigns approximately 20% of the chosen time to warm-up, 60% to focused practice, and the remainder to review.',
'The recommendation follows explicit rules. It does not use live AI or diagnose shooting technique.']),
('How did I get the numbers?',[
'I counted seven entities: players, sessions, shot maps, events, coaches, ratings, and plans.',
'The player, coach, and training dashboards each contain five visuals, giving 15 visuals across three dashboards.',
'Five simulated API contracts cover players, sessions, shot maps, ratings, and plans. They run in the browser rather than on a live backend.',
'The browser reads JSON collections, and a separate SQLite artifact shows the corresponding database structure.']),
('Case study + impact',[
'The case study includes architecture diagrams, competitive analysis, proposed KPIs, and a go-to-market strategy.',
'It explains the implementation and next steps. I have not measured a threefold increase in recruiter engagement.'])
]),('Interview examples:',[
('Data quality: fixing the era field',[
'The era classification could incorrectly use team names or misinterpret season identifiers.',
'The correction prioritizes explicit season information and uses game dates only as a fallback, including a 2020 bubble exception.',
'Rebuilt exports and regression tests support the corrected grouping. My takeaway is that a plausible chart can still rely on incorrect data.']),
('Data discovery: know the source',[
'The historical sample contains 79,763 shots across 10 selected NBA players; it does not represent the entire league.',
'The training prototype uses three fictional players, 24 sessions, and 1,440 synthetic shots.',
'I kept the sources separate and documented what each record represents and which conclusions the data can support.']),
('Validation: can I trust the metric?',[
'I calculate overall accuracy as total makes divided by total attempts, rather than averaging session percentages.',
'For example, sessions of 1/2 and 9/10 combine to 10/12, or 83.3%. With no attempts, accuracy stays unknown.',
'The tests check record relationships, metric totals, plan durations, and API responses. All four Node tests passed during the project review.']),
('Product thinking: what comes next?',[
'I narrowed the proposed next release to logging a session, reviewing results, choosing a plan, and recording a follow-up.',
'The requirements include reliable saving, duplicate prevention, and controls that keep each user\'s records private.',
'I would measure whether users complete the workflow unaided, understand the plan, and return. The pilot and production backend remain proposed work.']),
('Why this fits Vanguard',[
'This project connects data discovery, clear business rules, validation, and communication of limitations.',
'I used AI coding assistance and should distinguish what I personally built, reviewed, and validated when discussing these examples.'])
])]
story=[]
for i,(t,sections) in enumerate(pages):
 if i: story.append(PageBreak())
 story.append(Paragraph(escape(t),title))
 for h,items in sections:
  story.append(Paragraph(escape(h),head))
  for item in items:
   is_sub=item.startswith('> ')
   # Standard built-in fonts do not reliably support arrows.
   item=item.replace('→','>')
   story.append(Paragraph(escape(item[2:] if is_sub else item),sub if is_sub else bullet,bulletText='-' if is_sub else '\u2022'))
def footer(c,d):
 c.setFont('Helvetica',8)
 c.drawRightString(562,25,f'{d.page} / 2')
SimpleDocTemplate(str(out),pagesize=(612,792),leftMargin=50,rightMargin=50,topMargin=42,bottomMargin=40,title='PlusMinus Interview Talking Points').build(story,onFirstPage=footer,onLaterPages=footer)
with pdfplumber.open(out) as pdf:
 print('Pages:',len(pdf.pages))
 assert len(pdf.pages)==2
 for i,p in enumerate(pdf.pages):
  p.to_image(resolution=110).save(root/f'tmp/pdfs/talking-points-{i+1}.png')
 print('Words:',sum(len(p.extract_text().split()) for p in pdf.pages))
print(out)

