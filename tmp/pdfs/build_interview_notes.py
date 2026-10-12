from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.colors import HexColor
import pdfplumber

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/pdf/PlusMinus_Analytics_Interview_Notes.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)

# Note-style consolidation of all substantive PlusMinus interview discussion.
# Each page retains the reference's plain headings and short, indented notes.
pages = [
('PlusMinus Analytics:', [
('What "I" Did', [
'Developed a basketball analytics prototype and the product documentation around it.',
'Organized the concept around 3 capabilities:',
'> Understanding shooting results.',
'> Reviewing session performance.',
'> Turning those results into a practice plan.',
'Connected data definitions, transformations, validation, and documentation to a specific user decision.',
'Interview theme: I worked on making data trustworthy, understandable, and useful.']),
('How I introduce the project', [
'PlusMinus has 2 separate experiences: a historical NBA explorer and a training-product prototype.',
'The historical component uses 79,763 exported shots across 10 selected players, with observed game dates spanning 1996-2026.',
'Python transformations clean shot records, calculate shooting metrics, and aggregate results for visual analysis.',
'Training Lab uses synthetic data and explicit rules to demonstrate a practice-planning workflow.',
'The strongest work to discuss: correcting era classification, defining metrics, testing relationships and calculations, and documenting a focused next release.',
'A data product needs clear definitions and reliable transformations in addition to a dashboard.']),
('Why this relates to Vanguard', [
'Target role: Data Product Analyst, Personal Wealth Data Strategy & Management.',
'Data discovery: understand the grain, source, coverage, and intended use of a dataset.',
'Data quality: identify problems, trace their causes, and validate the correction.',
'Requirements: document business rules, definitions, acceptance criteria, and success measures.',
'Communication: explain decisions and limitations clearly to product, engineering, and business partners.',
'Use the project as evidence of relevant preparation; do not claim enterprise, cloud, or cross-functional delivery experience that did not occur.']),
('How to use these notes', [
'These notes consolidate the substantive interview and resume discussion from this chat in the reference PDF\'s note style.',
'First-person wording is a rehearsal draft. Use built, reviewed, helped develop, or validated according to my actual contribution.',
'The project used AI coding assistance. Be ready to explain the decisions and validation I personally owned.',
'STAR = Situation, Task, Action, Result. Practice stories 1, 3, and 6 first.'])
]),
('STAR 1: Correcting a data-quality issue', [
('When I use this answer', ['Tell me about a difficult problem, your attention to detail, or how you validate data.']),
('Situation', [
'The NBA explorer grouped shots into eras to compare shooting patterns over time.',
'The existing transformation could put a home-team abbreviation into the era field under some conditions.',
'It also mishandled compact season identifiers such as 22023.',
'A populated field and plausible chart could therefore communicate the wrong meaning.']),
('Task', ['Make era classification represent the correct basketball season and carry the correction through exported data and dashboard labels.']),
('Action', [
'Traced the era field back to the transformation that created it.',
'Defined source precedence: use explicit season metadata first; infer from game date only when needed.',
'Normalized supported season formats so 22023 represents the season beginning in 2023.',
'Accounted for calendar year versus season year. January games generally belong to a season that started the previous year.',
'Included a specific exception for the 2020 bubble when using date inference.',
'Updated era values in the exported shot records while preserving other fields and row order.',
'Rebuilt era-level aggregates in both export locations.',
'Added regression cases for metadata precedence, compact identifiers, invalid dates, mixed formats, and frontend label coverage.']),
('Result', [
'The corrected implementation produces season-based era classifications and includes coverage for known failure cases.',
'The grouping now matches the meaning intended by the dashboard comparison.',
'Lesson: structurally valid data can still be semantically wrong.',
'Describe the discovery as my own only if I personally found it; otherwise explain how I reviewed, understood, or validated the repair.']),
('Concepts I can explain', [
'Semantic quality: a team abbreviation is valid text, but not a valid era.',
'Source precedence: authoritative metadata takes priority over a date approximation.',
'Lineage: follow a value from source records through transformations, exports, and charts.',
'Regression testing: turn known failures into repeatable checks.',
'Vanguard connection: business decisions depend on fields having consistent, correct meaning.'])
]),
('STAR 2: Understanding the data', [
('When I use this answer', ['How do you approach a new dataset? What data discovery or profiling have you done?']),
('Situation', [
'The project contained historical NBA exports and a separate training dataset.',
'Both involved basketball shooting, but their origins, structures, and intended uses differed.',
'Without those distinctions, the analysis could imply unsupported comparisons or representativeness.']),
('Task', ['Clarify what each dataset represents, how records relate, and which questions each source can reasonably answer.']),
('Action', [
'Documented the grain: one historical shot record represents one shot attempt.',
'Documented training relationships: events connect to sessions; sessions connect to players.',
'Recorded historical coverage: 79,763 shots, 10 selected players, observed game dates from November 1, 1996 to February 23, 2026.',
'Treated this as selected-player sample coverage, not a complete league dataset or proof of collection freshness.',
'Documented synthetic training data: 3 fictional players, 24 sessions, and 1,440 shot events.',
'Kept historical NBA records separate from fictional practice records; they are not joined to establish player performance.',
'Recorded assumptions: synthetic sessions use equal shot volume; historical era comparisons lack adjustments for pace, opponents, and rule changes.']),
('Result', [
'The documentation makes source, coverage, relationships, and limitations explicit.',
'That supports choosing an appropriate analysis and explaining what a result can support.',
'Lesson: establish what the data represents before looking for an interesting pattern.']),
('Concepts I can explain', [
'Grain: the unit represented by one record. Mixing grains can duplicate records or distort aggregates.',
'Provenance: where data came from and how it was generated.',
'Coverage versus completeness: a wide date range does not prove complete history.',
'Representativeness: a selected sample does not automatically support population-wide conclusions.',
'Synthetic data: useful for reproducible demonstrations and testing; not evidence of actual user behavior.',
'Vanguard connection: understand the dataset and business context before recommending how to use it.'])
]),
('STAR 3: Defining and validating metrics', [
('When I use this answer', ['How do you ensure reporting is accurate? Explain a technical concept to a business stakeholder.']),
('Situation', [
'Training Lab shows accuracy across players, sessions, and zones.',
'Different aggregation methods can produce different answers.',
'There was also a risk of describing a shooting percentage as a broader measure of skill.']),
('Task', ['Define metrics consistently and connect displayed values back to individual shot events.']),
('Action', [
'Defined overall accuracy as total makes divided by total attempts.',
'Weighted each attempt equally rather than taking an unweighted average of session percentages.',
'Kept an empty denominator unknown: no attempts is different from missing every shot.',
'Distinguished percentage-point change from relative percentage change.',
'Used tests to reconcile zone attempt totals to player events.',
'Recalculated stored session ratings from each session\'s shots.',
'Documented the shooting index as session shooting percentage on a 0-100 scale, not an independently validated skill score.']),
('Result', [
'The calculations have explicit definitions and automated reconciliation checks.',
'The dashboard is easier to explain because the same measure has a consistent meaning.',
'Lesson: explain the numerator, denominator, population, and time period before interpreting a number.']),
('Example I can say out loud', [
'Session 1: 1 make out of 2 attempts = 50%.',
'Session 2: 9 makes out of 10 attempts = 90%.',
'A simple average gives 70%, but total makes / total attempts = 10 / 12 = 83.3%.',
'For overall shot accuracy, I use total makes divided by total attempts.',
'A move from 40% to 50% is 10 percentage points, or a 25% relative increase.']),
('Concepts I can explain', [
'Reconciliation: check that a summary agrees with the records underneath it.',
'Missing versus zero: no evidence and poor performance are different states.',
'Metric definition: specify calculation, scope, unit, and treatment of missing data.',
'Vanguard connection: shared definitions help teams use the same metric consistently.'])
]),
('STAR 4: Modeling related records', [
('When I use this answer', ['What SQL or data-modeling experience do you have? How do you validate related datasets?']),
('Situation', [
'The training experience connects players, sessions, shot maps, events, ratings, and plans.',
'Records can reference existing IDs and still connect to the wrong player or session.']),
('Task', ['Make relationships explicit and validate both references and ownership consistency.']),
('Action', [
'Worked with 7 entities and documented primary keys and relationships.',
'Separated referential integrity from relationship consistency.',
'> An event\'s shot map must exist and belong to the same session as the event.',
'> A rating\'s player must be the player who owns the referenced session.',
'Used composite foreign keys in the SQL schema to express paired relationships.',
'Validated unique IDs, foreign-key references, event/session consistency, and rating ownership in fixture tests.',
'Documented 5 simulated API contracts with required inputs, success responses, and error behavior.',
'Kept architecture claims precise: browser JSON and an in-memory dispatcher power the prototype; SQLite is an inspectable artifact, not its runtime backend.']),
('Result', [
'The model and contracts can be inspected and tested independently of the interface.',
'The Node suite passed its 4 tests during this chat: relationships, metrics, plans, and route behavior.',
'Lesson: reliability includes how records connect, not just whether individual values look reasonable.']),
('Concepts I can explain', [
'Primary key: uniquely identifies a record.',
'Foreign key: requires a reference to an existing record.',
'Composite foreign key: validates a combination, such as session and player together.',
'Data contract: defines expected inputs, outputs, meanings, and failure behavior.',
'Relationship consistency is not access authorization. A production backend still needs authentication and server-side ownership checks.',
'Vanguard connection: useful preparation for documenting rules and supporting validation with engineers.'])
]),
('STAR 5: Explaining a recommendation', [
('When I use this answer', ['Tell me about a tradeoff. How do you turn analysis into action or evaluate an AI-enabled idea?']),
('Situation', ['Training Lab needed to connect shot results to a practice plan users could understand and inspect.']),
('Task', ['Demonstrate a transparent recommendation process with testable rules and clearly stated limits.']),
('Action', [
'Used a deterministic rule rather than a learned model.',
'Calculated accuracy by zone for the selected player.',
'Excluded zones with fewer than 20 attempts and selected the lowest-accuracy eligible zone.',
'Used a consistent alphabetical tie-breaker when accuracies match.',
'Included the selected zone, accuracy, and attempt count in the explanation.',
'Allocated approximately 20% of duration to warm-up, 60% to focus, and the remainder to review.',
'Handled integer rounding so allocated minutes sum exactly to the requested duration.',
'Tested focus selection and durations across the fixture\'s players, plus invalid durations and missing evidence.',
'Documented the limits: raw low accuracy may reflect a harder shot type, and 20 attempts is a heuristic rather than statistical confidence.']),
('Result', [
'The prototype demonstrates a traceable path from records to an action.',
'The limitation informed the proposed next release: let the player choose a focus and present the relevant evidence.',
'It does not demonstrate technique diagnosis or measured player improvement.']),
('Example I can demonstrate', [
'The documented fictional Jordan Ellis demo has 54.6% overall accuracy.',
'Above-break 3 is the selected focus: 40.0% across 120 attempts.',
'A 45-minute plan allocates 9 minutes to warm-up, 27 to focus, and 9 to review.',
'I can explain the evidence, rule, and allocation rather than treating the output as a black box.']),
('Concepts I can explain', [
'Deterministic: identical inputs produce the same result.',
'Explainable: the output exposes the records and logic behind it.',
'Personalized here means tailored to recorded results and chosen time, not learned understanding of technique.',
'Vanguard connection: assess whether an analytical output is explainable and appropriate for its decision; this is not a financial recommendation model.'])
]),
('STAR 6: Defining the next release', [
('When I use this answer', ['How do you prioritize, document requirements, or define success?']),
('Situation', [
'The broad vision covered historical analysis, player and coach dashboards, plans, and possible AI features.',
'The product question was which single workflow a real user should be able to complete.']),
('Task', ['Specify a focused next release with observable acceptance criteria and a way to evaluate usefulness.']),
('Action', [
'Narrowed the proposed MVP to an adult recreational player logging practice, reviewing results, choosing a plan, and recording a comparable follow-up.',
'Translated the workflow into acceptance criteria:',
'> Saved data survives refresh; retrying a save does not create duplicates.',
'> One user cannot access another user\'s records.',
'> Corrections update aggregates and mark affected plan evidence outdated.',
'Matched the model to actual input: store manually entered zone totals without inventing shot locations.',
'Specified evidence snapshots and rules versions so old plans retain their original rationale.',
'Defined proposed usability checks and pilot measures; deferred complexity until the core workflow can be evaluated.']),
('Result', [
'The deliverable is a focused PRD with scope, business rules, acceptance criteria, and proposed validation gates.',
'This is a planning result, not a launched application or completed user study.',
'Its value is converting an idea into work that can be implemented and checked.']),
('How I would measure success', [
'Proposed observed usability sessions: can at least 4 of 5 participants save a session, locate a plan, and explain the evidence unaided?',
'Proposed logging measure: median entry time of 90 seconds or less for prepared four-zone totals.',
'Proposed pilot: 5-10 adults over 4 weeks; measure saved plans followed by linked sessions within 7 days.',
'These are initial decision rules, not achieved results or statistically conclusive findings.']),
('Concepts I can explain', [
'Requirement = what must happen. Acceptance criterion = observable proof it happened.',
'Idempotency = retries do not create unintended duplicates.',
'Evidence versioning = preserve the information supporting an earlier decision.',
'Vanguard connection: help translate business needs into testable delivery work.'])
]),
('Resume 1: Product scope and roadmap', [
('Original bullet discussed', [
'Built an AI-powered basketball analytics MVP, producing the full PRD, feature blueprint, UX flows, and a 6-month roadmap covering shot tracking, skill ratings, and personalized training.']),
('What I actually show', [
'A basketball analytics prototype and supporting product documentation.',
'PRD means Product Requirements Document:',
'> Describes the problem and intended user.',
'> Defines requirements and acceptance criteria.',
'Feature blueprint: breaks the experience into specific capabilities, inputs, behavior, and outputs.',
'UX flows: show how a user moves from reviewing evidence to a next action.',
'Six-month roadmap: proposed sequencing, dependencies, and validation milestones, not six months of completed delivery.']),
('What makes it personalized?', [
'Uses the selected player\'s records and calculates accuracy by zone.',
'Considers zones with at least 20 attempts and selects the lowest-accuracy eligible zone.',
'Allocates the selected duration across warm-up, focus, and review.',
'This is rules-based tailoring, not a model that learns a player\'s technique.']),
('Why 6 months?', [
'Six months is the proposed planning horizon.',
'It shows a development sequence beyond the initial prototype.',
'It is an estimate, not a proven delivery timeline. Add a more specific rationale only if it reflects how I chose it.']),
('Terms I should use precisely', [
'AI-powered: not supported by current runtime behavior; AI explanations are proposed.',
'Shot tracking: synthetic shot records and visualizations, not automated video detection.',
'Skill ratings: descriptive session shooting percentage, not validated skill measurement.',
'MVP: current runnable prototype and proposed real-user next release are distinct.',
'Static delivery supports an inspectable demo; it does not establish authenticated writes, durable sessions, or backend scale.']),
('Revised resume wording', [
'Developed a basketball analytics prototype with rules-based practice recommendations; documented the PRD, feature blueprint, UX flows, and proposed six-month roadmap for session tracking, shooting metrics, and personalized practice plans.'])
]),
('Resume 2: How I got the numbers', [
('Original bullet discussed', [
'Developed a 7-entity mock database enabling 15+ analytics visuals, 5 simulated API endpoints, and 3 interactive dashboards showcasing technical feasibility.']),
('How I counted the entities', [
'Counted distinct entity types, not the number of records.',
'Coaches: 1. Players: 3. Sessions: 24. Shot maps: 24.',
'Events: 1,440. Ratings: 24. Initial example plans: 3.',
'The browser uses 7 JSON collections. A corresponding SQLite schema and populated artifact make the model inspectable.',
'Seven is the resulting model size, not a target. A simpler zone-total product may need a different model.']),
('How I counted the visuals', [
'3 dashboard views with 5 numbered visuals each = 15.',
'Player: session accuracy, attempts by session, zone accuracy, shot map, shooting index.',
'Coach: roster accuracy, practice volume, latest-versus-first change, time invested, player-by-zone matrix.',
'Training: target gap, practice distribution, cumulative accuracy, made-versus-missed totals, practice allocation.',
'Use 15 instead of 15+ unless additional visuals are explicitly inventoried in the same scope.',
'These are not 15 independent measures: session accuracy and shooting index share the same underlying metric.']),
('How I counted and tested the contracts', [
'GET /api/players; GET /api/sessions; GET /api/shot-maps; GET /api/ratings; POST /api/plans.',
'Five method/path contracts execute inside the browser; they are not hosted HTTP endpoints.',
'Tests cover all 5 contracts and missing IDs, unknown players, invalid duration, unsupported method, and unknown route.',
'Generated plans are transient outputs; downloading a plan does not persist a database write.']),
('What technical feasibility means', [
'Related records feed dashboard calculations and a traceable plan in a working browser experience.',
'It does not establish production scale, secure multi-user operation, adoption, or recommendation effectiveness.',
'These counts measure implementation scope. Tests check specific correctness properties.']),
('Revised resume wording', [
'Modeled seven related entities in a synthetic dataset supporting 15 analytics visuals across three interactive dashboards and five simulated API contracts; validated relationships, metric reconciliation, and recommendation behavior with automated tests.'])
]),
('Resume 3: Case study and engagement', [
('Original bullet discussed', [
'Produced a complete GitHub case study with architecture diagrams, competitive analysis, KPI framework, and GTM strategy, boosting project clarity and recruiter engagement by an estimated 3x.']),
('What I can substantiate', [
'The case study connects the problem, architecture, implementation, decisions, evidence, and limits.',
'Supporting documents cover competitive positioning, proposed KPIs, and go-to-market strategy.',
'Separating implemented work from future plans helps a reviewer assess the project.',
'Verify the files are committed and visible before describing the case study as published on GitHub. The earlier working-tree review showed untracked case-study files.']),
('If asked: How did you measure 3x?', [
'That was an informal estimate, and I do not have a measured baseline supporting a threefold increase.',
'The wording is too strong; I would remove it. I can substantiate the documentation, not the engagement uplift.',
'An estimate still needs a definition, baseline, and method. Do not invent views, feedback, or response rates.']),
('How I could measure engagement', [
'Define case-study engagement rate = unique visitors who open the case study / unique portfolio visitors.',
'Illustrative example only: before, 10 of 100 visitors = 10%; after, 30 of 100 = 30%.',
'30% / 10% = 3x the rate; the change is 20 percentage points or a 200% relative increase.',
'Use comparable windows, consistent tracking, and account for different traffic sources.',
'A before/after comparison alone does not prove the case study caused the difference.',
'Call it visitor engagement unless there is evidence the visitors are recruiters.']),
('How I could measure clarity', [
'Ask reviewers to identify the problem, distinguish built versus proposed features, and explain a limitation.',
'Record task completion and time to find supporting evidence.',
'That evaluates communication; it does not automatically establish hiring impact.']),
('Revised resume wording', [
'Created a portfolio case study documenting architecture, data provenance, validation results, competitive analysis, proposed KPIs, and go-to-market strategy, with clear distinctions between implemented capabilities and future work.'])
]),
('Follow-up answers and evidence', [
('What did I personally do?', [
'I personally owned [the components I actually owned]. I used AI coding assistance for [the tasks it supported].',
'My contribution was [specific decisions, analysis, implementation, review, or testing]. I can walk through [a function, rule, or test I understand].',
'Do not claim independent discovery or authorship if I reviewed assisted work. Describe reviewing, testing, modifying, and explaining accurately.']),
('How I explain the metrics to Vanguard', [
'I separate delivery measures from outcome measures.',
'Seven entities, 15 visuals, 5 contracts, and 3 dashboards are verifiable implementation counts.',
'Tests provide evidence about specific correctness properties.',
'Adoption, better decisions, player improvement, and recruiter engagement require separate measurement.',
'I want the evidence behind a claim to be as clear as the claim itself.']),
('Boundaries to remember', [
'Historical data is a selected-player sample, not the entire NBA.',
'Training Lab is synthetic and rules-based, not a trained AI product.',
'The API is simulated; the prototype does not prove a live backend or production deployment.',
'The next-release PRD, pilot, revenue, retention, and improvement outcomes are not completed achievements.',
'Do not claim stakeholder interviews, Agile teamwork, cloud operations, or enterprise scale unless I actually did them.',
'CSV export support does not prove a Tableau workbook was built; the reviewed repository had no committed workbook.']),
('Where the evidence lives', [
'src/data_cleaning.py: cleaning, season classification, and metric transformations.',
'scripts/repair_eras.py and tests/test_eras.py: export repair and era regressions.',
'public/prototype/model.mjs: calculations, plan rules, and simulated contracts.',
'tests/prototype.test.mjs: relationship, metric, plan, and contract checks.',
'docs/recruiter/DATA_API.md and schema.sql: definitions, counts, and relationships.',
'docs/recruiter/PRODUCT_SPEC.md, MVP_PRD.md, and STRATEGY.md: requirements and proposed strategy.',
'docs/recruiter/CASE_STUDY.md, AUDIT.md, LAUNCH_KIT.md, and VERIFICATION.md: narrative, claims, demo, and recorded checks.']),
('Verification context', [
'During this chat, all 4 Node tests passed. The earlier Python rerun could not start because the configured executable was unavailable.',
'The existing October 10, 2026 report records prior Python, SQLite, and browser checks; those were not all rerun for these notes.',
'Source: this chat and its repository review. Style reference: Plus Minus Evaluation.pdf. Prepared October 11, 2026.'])
])
]

styles = {
 'title': ParagraphStyle('title', fontName='Times-Roman', fontSize=22, leading=26, spaceAfter=12),
 'head': ParagraphStyle('head', fontName='Times-Roman', fontSize=15, leading=18, spaceBefore=9, spaceAfter=5, keepWithNext=True),
 'bullet': ParagraphStyle('bullet', fontName='Helvetica', fontSize=10, leading=13, leftIndent=10, firstLineIndent=0, bulletIndent=0, spaceAfter=3),
 'sub': ParagraphStyle('sub', fontName='Helvetica', fontSize=10, leading=13, leftIndent=26, bulletIndent=15, spaceAfter=3),
}

class NumberedCanvas(canvas.Canvas):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.saved=[]
    def showPage(self):
        self.saved.append(dict(self.__dict__))
        self._startPage()
    def save(self):
        n=len(self.saved)
        for state in self.saved:
            self.__dict__.update(state)
            self.setFont('Helvetica',8)
            self.setFillColor(HexColor('#666666'))
            self.drawString(48,27,'PlusMinus Analytics | Interview notes')
            self.drawRightString(564,27,f'{self._pageNumber} / {n}')
            super().showPage()
        super().save()

story=[]
for index,(title,sections) in enumerate(pages):
    if index: story.append(PageBreak())
    story.append(Paragraph(escape(title),styles['title']))
    for heading,bullets in sections:
        story.append(Paragraph(escape(heading),styles['head']))
        for text in bullets:
            sub=text.startswith('> ')
            story.append(Paragraph(escape(text[2:] if sub else text),styles['sub' if sub else 'bullet'],bulletText='-' if sub else '\u2022'))

doc=SimpleDocTemplate(str(OUT),pagesize=(612,792),rightMargin=48,leftMargin=48,topMargin=43,bottomMargin=45,
                     title='PlusMinus Analytics - Interview Notes',author='PlusMinus Analytics',
                     subject='STAR answers, resume metrics, and Vanguard interview preparation')
doc.build(story,canvasmaker=NumberedCanvas)
with pdfplumber.open(OUT) as pdf:
    print('PDF:',OUT)
    print('PAGES:',len(pdf.pages))
    for i,p in enumerate(pdf.pages):
        text=p.extract_text() or ''
        print(i+1, len(text), text.splitlines()[0])
        p.to_image(resolution=100).save(ROOT / f'tmp/pdfs/page-{i+1:02}.png')
    assert len(pdf.pages)==len(pages), 'Unexpected overflow: adjust layout before delivery'
    all_text='\n'.join(p.extract_text() or '' for p in pdf.pages)
    assert '\ufffd' not in all_text

