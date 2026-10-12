# Strategy — six-month roadmap, competitors, KPIs and GTM

Planning date: October 10, 2026. All targets, channels and customer segments below are hypotheses. The prototype has no measured traction.

## Competitive context

Official product materials reviewed October 10, 2026; features can change. This is a focused positioning scan, not a hands-on product benchmark or exhaustive market study.

| Alternative | Documented offering | Implication for PlusMinus |
|---|---|---|
| [HomeCourt](https://www.homecourt.ai/) | Camera-based basketball training and shot tracking; training content and interactive drills | Tracking alone is not a differentiated proposition. Test whether simpler evidence-to-plan explanations solve an unmet workflow need. |
| [HomeCourt shot analysis](https://www.homecourt.ai/faq/shotanalysis) | Real-time shot-analysis feedback | Avoid claiming novel AI shot analysis without a measured technical advantage. |
| [Noah Pro](https://www.noahbasketball.com/products/noah-pro) | Ball tracking with feedback on arc, depth and left-right deviation, plus analytics | The current prototype does not measure shot mechanics and cannot compete on that capability. |
| Manual notebook or spreadsheet | User-entered records and flexible calculations; conceptual baseline, not a specific researched vendor | The product must reduce effort or improve decisions relative to this low-tech alternative. Validate that in interviews. |

Proposed positioning: **a lightweight practice review that connects a visible shooting pattern to an understandable next session.** This is a testable positioning hypothesis, not an established market gap. No competitor pricing, market size or revenue estimates are assumed.

## Six-month roadmap

Month 1 starts when work resumes after this portfolio release; the dates are not commitments.

| Month | Outcome | Scope / dependency | Exit gate and decision |
|---|---|---|---|
| 1 | Validate the core task | Publish portfolio, observe five adult players/coaches, record confusion and completion; depends on recruitment | At least 4/5 explain the recommendation unaided within two minutes. Otherwise revise UX. |
| 2 | Capture a real practice | Manual event entry, relational persistence, authentication and ownership; depends on validated flow | Five consenting testers can save, reopen and correct a session; no cross-account access in authorization tests. |
| 3 | Validate useful feedback | Session history, coach review, sample-size rules and baseline comparisons; depends on real data | Coaches review at least 30 plans; at least 80% judged usable without substantial correction. Otherwise refine rules. |
| 4 | Evaluate optional AI explanations | Structured evidence, constrained output, numeric validation, fallback; depends on stable rules | Pass 50-case evaluation: numeric fidelity and schema validity 100%, relevance ≥90%; no unsupported guarantees. Otherwise retain rules. |
| 5 | Test camera feasibility | Small consented labeled dataset across devices and lighting; correction UI; depends on rights and labeling capacity | Report attempt precision/recall, outcome accuracy and failures by condition. Set release thresholds with coaches before evaluation; no public CV claim yet. |
| 6 | Decide whether to launch a pilot | Onboarding, retention instrumentation, support and accessibility; depends on useful repeated practice | Evaluate four-week repeat usage and interviews against preset targets; launch, narrow scope or stop based on evidence. |

Solo-project prioritization: a robust manual workflow is more valuable than simultaneously attempting computer vision, model training, mobile capture and social features. If Month 2 ownership or persistence is incomplete, defer AI and video work.

## KPI framework

Proposed events are not currently collected. The mock `events` table records basketball attempts; product telemetry is a different future dataset.

| Metric | Definition / denominator | Instrumentation | Initial decision target |
|---|---|---|---|
| Activation | New consenting players who save a valid session and view a plan within seven days / all new consenting players | `account_created`, `session_saved`, `plan_viewed`, stable pseudonymous ID | 60% pilot hypothesis; review after 20 signups |
| Weekly practice loop | Players saving a follow-up session after viewing a plan within seven days / players viewing a plan | `plan_viewed`, subsequent `session_saved` | 40% hypothesis; do not infer adherence from views alone |
| Four-week retention | Activated cohort with a valid session in days 22–28 / activated cohort with 28 days of observation | Session timestamps and cohort table | 30% hypothesis; report sample size |
| Recommendation usefulness | Coach-reviewed plans rated usable / all reviewed plans | Rubric and review record | 80% before broader pilot |
| Data integrity | Saved sessions passing ownership, count and reference validation / all attempted saves | Server validation results | 100% accepted records valid |
| Model numeric fidelity | AI explanations with every number matching supplied evidence / all evaluated explanations | Offline case set | 100% release gate, not measured now |
| Recruiter engagement | Unique case-study visitors taking a defined action / eligible unique visitors | Consented link analytics and manual response log | Establish baseline first; no claimed lift |

North-star candidate: weekly players completing a session → plan → follow-up session loop. It is a proxy for repeated use, not proof of skill improvement. Skill change needs a consistent shooting protocol, repeated measurements and an appropriate comparison design.

To support any future “3× engagement” statement, define the action and observation window in advance, compare like audiences and channels, deduplicate visitors, report sample sizes and uncertainty, and calculate new rate / baseline rate. An estimate without observations is not a result.

## GTM experiment

1. **Beachhead hypothesis:** independent coaches working with adult recreational players. Recruit through existing relationships and relevant basketball communities; no outreach has been sent.
2. **Offer:** a small, consented practice-review pilot with manual entry and an explainable plan. Avoid an AI accuracy promise.
3. **Discovery:** interview five coaches about current logging, review frequency, trust and willingness to change workflows. Test the notebook/spreadsheet alternative explicitly.
4. **Pilot:** invite up to ten adults for four weeks after persistence and access controls are ready. Collect task success, repeated use and interview feedback.
5. **Pricing:** ask about value and current alternatives before choosing a price. No revenue forecast is justified yet.
6. **Decision:** expand only if participants repeatedly use and understand the recommendations. If capture friction dominates, simplify entry before investing in acquisition.

Recruiter distribution is separate: GitHub case study → two-minute demo → live static site. Track replies and interview discussion qualitatively until there is a meaningful sample.
