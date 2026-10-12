# PlusMinus portfolio audit

Audit date: October 10, 2026. Scope: the local PlusMinus-Analytics checkout, not unprovided files or remote branches.

## Why the project felt undeployable

There was already a static website in `public/`, a Vercel output configuration, a Streamlit app, a Python pipeline, and 18 CSV exports. The README described a Tableau workflow and did not explain either runnable web experience. Both `docs/` and `tableau/` contained only `.gitkeep`; there was no committed PRD, roadmap, workbook, or case study. The project had implementation, but lacked an obvious entry point and an evidence-backed product story.

The résumé describes a player-development product, while the repository implemented historical NBA analysis. Those are related but different use cases. A historical NBA shot chart does not establish personalized training, a skill model, or AI inference.

## Claim-to-evidence assessment

| Original claim | Evidence at audit | Deliverable now | Remaining limit |
|---|---|---|---|
| AI-powered basketball MVP | No inference integration or model evaluation found | Rules-based training prototype and staged AI requirements | Do not call the current demo AI-powered |
| Full PRD, feature blueprint, UX flows, six-month roadmap | Documentation folder empty | PRODUCT_SPEC.md and STRATEGY.md | Specifications are proposed, not customer-validated |
| Seven-entity mock database | CSV NBA exports, no matching training schema | Seeded JSON collections, SQL schema, reproducible generator | Browser mock store, not a production database service |
| 15+ visuals, five APIs, three dashboards | Seven NBA pages; no matching training API | Exactly 15 training charts, five simulated route contracts, three dashboards | Simulation runs in browser memory; no network API |
| GitHub case study, competitors, KPI and GTM | Basic pipeline README only | Six recruiter documents, diagrams and updated README | Local files must be committed/pushed before appearing on GitHub |
| Estimated 3× recruiter engagement | No baseline, tracking, or experiment found | Measurement plan and evidence-safe résumé language | Remove the 3× claim until measured |

## Data defect corrected

The original cleaner used `HTM` as a fallback for `ERA`, so era exports contained team codes such as BOS and ATL. It also tested for season IDs longer than five characters even though `22023` has five. The corrected cleaner prioritizes explicit season metadata and otherwise estimates season start from game date, with a July boundary and a 2020 bubble exception. Invalid dates become Unknown. Historical inference remains an approximation when season metadata is absent.

The offline repair script updates ERA values in both export directories, including comparison files, and rebuilds era aggregates. It preserves the other CSV fields and shot row order. The selected-player sample still cannot support claims about league-wide causal trends or who is objectively the best player across eras.

## What is deployable now

The whole `public/` directory is a static artifact: portfolio entry page, original NBA explorer, training lab, mock data, and documentation. The training lab requires HTTP serving, but no installation, secrets, model billing, or database provisioning. The NBA explorer requires access to the Plotly CDN. Local verification is separate from a confirmed production deployment.

## Priority after this delivery

1. Publish the static folder and verify the public URL in a signed-out browser.
2. Record a two-minute demo and add the URL and screenshots to GitHub.
3. Conduct five usability sessions before adding camera tracking or AI.
4. Build persistent session logging only if those sessions validate the core decision loop.
