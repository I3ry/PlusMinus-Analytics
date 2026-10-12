# Recruiter launch kit

## What to share

Primary artifact: the static portfolio homepage. It links to the NBA explorer, training prototype and recruiter documents. Supporting artifact: the GitHub repository with README and case study. Add a two-minute screen recording after reviewing the material yourself. A document draft alone does not establish a working MVP; lead with the demo.

## Run locally

From the repository root with Node 20 or later:

```sh
node scripts/package.mjs
node scripts/serve.mjs
```

Open `http://127.0.0.1:4173`. The server exposes only the `public` directory and binds to local loopback. No npm install is needed. Run `node --test tests/prototype.test.mjs` for the mock model and API checks. Use `python -m unittest discover -s tests -p test_eras.py` in an environment containing Pandas and NumPy for era regression tests.

## Deployable artifact and hosting

Deploy the entire `public/` directory, keeping nested paths. Run `node scripts/package.mjs` whenever the recruiter documents change. Existing `vercel.json` points its output directory to `public`.

For Vercel's dashboard, import this GitHub repository, choose the **Other** framework preset, set the output directory to **public**, and leave the build command empty (disable any auto-detected build override). The committed public folder already contains the documents. Verify project-level settings match the repository. No secrets are needed for the static site. The Python Streamlit app is an alternative local app, not the entry point for this deployment.

These instructions follow [Vercel build configuration](https://vercel.com/docs/builds/configure-a-build) and [static project configuration](https://vercel.com/docs/project-configuration/vercel-json), reviewed October 10, 2026. A repository configuration is not proof of a successful deployment. The live deployment URL has not been established by this delivery.

After deployment, verify `/`, `/prototype/`, `/explorer.html`, `/prototype/db.json`, and `/deliverables/CASE_STUDY.md`; check the site signed out and on a phone. Test player changes, all three dashboards, a 45-minute plan and a JSON download. If NBA charts fail, check Plotly CDN and CSV requests. If the prototype fails, check `.mjs` JavaScript MIME handling and db.json.

## Three-day plan

| Day | Work | Definition of done |
|---|---|---|
| 1: October 10 | Review artifacts and calculations; run checks; publish static site; add actual demo URL to README | Public URL works signed out, no broken navigation, claims match functionality |
| 2: October 11 | Capture desktop/mobile screenshots and record the demo; rehearse the data-quality explanation | Two-minute recording shows player → evidence → plan; owner can explain every résumé claim |
| 3: October 12 | Ask two peers for usability feedback; fix consequential issues; update résumé and portfolio links | Shareable case study, recording, GitHub link, and tested live URL |

If starting later, shift the days rather than rushing the verification. Avoid spending these three days on auth, video ingestion or a new LLM integration.

## Two-minute demo script

**0:00–0:20 — Problem.** “I built PlusMinus to explore how basketball data can lead to a clear next practice. This portfolio pairs an NBA analytics pipeline with a separate training-product prototype.”

**0:20–0:50 — Evidence.** Open Training Lab, select Jordan Ellis and show zone accuracy. “These sessions are synthetic, which keeps the demo repeatable. Every summary traces back to a shot event.” Open chart values.

**0:50–1:15 — Product decision.** Open Training Plan and select 45 minutes. “The rule chooses the lowest-accuracy zone with enough attempts, then explains the evidence and divides the available time. It is rules-based; I have not integrated a live AI model.” Download JSON.

**1:15–1:35 — Technical feasibility.** Open Coach Overview, then inspect a simulated API response. “The same seven-entity fixture supports three dashboards and five simulated route contracts. A real backend would add ownership, persistence and observability.”

**1:35–2:00 — Judgment.** Open the case study. “I found that the original era analysis grouped by home-team code, corrected the season logic and added regressions. The next product step is user validation; the roadmap gates AI behind evidence and evaluation.”

## Evidence-safe résumé bullets

- Built an interactive basketball analytics portfolio with player, coach, and training dashboards; authored the PRD, feature blueprint, UX flows, and a six-month roadmap for shot tracking, ratings, and future AI-assisted explanations.
- Developed a seven-entity synthetic data model containing 1,440 shot events across 24 sessions, powering 15 analytics charts and five simulated API contracts with automated integrity and behavior checks.
- Created a recruiter-ready case study covering architecture, competitive analysis, KPI definitions, and GTM hypotheses; corrected an era-classification defect in a 79,763-shot NBA dataset.

Use “published” and “deployed” only once the GitHub artifacts and live URL exist. Do not claim “AI-powered,” validated skill improvements, a production database/backend, or “3× recruiter engagement” for this version.

## Interview preparation

Be ready to explain: why a mock came before a backend; why the shooting index is not a validated skill rating; how foreign keys prevent cross-player mistakes; why weighted aggregates use total makes/attempts; what the 20-attempt threshold does and does not prove; how the era bug was detected; and what evidence would justify adding AI. Describe AI assistance honestly and demonstrate that you understand the resulting code.
