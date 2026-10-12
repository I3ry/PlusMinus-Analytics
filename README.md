# PlusMinus Analytics

A basketball analytics portfolio connecting shot-level evidence to a clear next step. Includes a historical NBA explorer, a separate training-product prototype, and a complete product case study.

**Status:** runnable static prototype; synthetic training data; rules-based recommendations. No live AI inference, computer vision, authenticated backend, or measured business outcomes. A production URL has not yet been recorded here.

## Run the portfolio

With Node 20+ installed, no dependency installation is needed:

```sh
node scripts/package.mjs
node scripts/serve.mjs
```

Open **http://127.0.0.1:4173**. The homepage links to both experiences and the documents. Do not open the HTML through `file://`; data loading uses HTTP fetch.

| Experience | Entry point | Evidence |
|---|---|---|
| Portfolio and case study | `public/index.html` | Problem, tradeoffs, capabilities and recruiter reading room |
| Training Lab | `public/prototype/index.html` | Three dashboards, 15 charts, seven mock entities, five simulated API contracts |
| NBA explorer | `public/explorer.html` | Seven views over exported historical NBA data; requires Plotly CDN |
| Streamlit alternative | `app.py` | Python implementation of NBA analytics |

## Read the case study

- [Focused next-release MVP and implementation PRD](docs/recruiter/MVP_PRD.md)
- [Case study and architecture diagrams](docs/recruiter/CASE_STUDY.md)
- [PRD, feature blueprint and UX flows](docs/recruiter/PRODUCT_SPEC.md)
- [Six-month roadmap, competitors, KPI framework and GTM](docs/recruiter/STRATEGY.md)
- [Data model, five API contracts and chart inventory](docs/recruiter/DATA_API.md)
- [Recruiter demo script, deployment guide and résumé bullets](docs/recruiter/LAUNCH_KIT.md)
- [Original gaps and claim-to-evidence audit](docs/recruiter/AUDIT.md)
- [Verification results](docs/recruiter/VERIFICATION.md)

## Technical structure

```text
public/                  Static deployable artifact
  index.html             Recruiter entry point
  explorer.html          Existing NBA explorer
  data/                  Historical NBA exports
  prototype/             Training UI, model, and seven-entity JSON fixture
  deliverables/          Packaged recruiter documents
src/                     NBA collection, cleaning and export pipeline
scripts/                 Static server, seed generator, packaging, era repair
tests/                   Mock API/data tests and era regressions
docs/recruiter/          Source product/case-study deliverables and SQL schema
app.py                   Streamlit alternative
```

The training prototype executes API-like method/path contracts in browser memory; it does not host `/api` HTTP endpoints. Downloaded plans are transient outputs, not persisted writes. Ratings are descriptive shooting percentages, not validated skill measurements.

## Validate

```sh
node --test tests/prototype.test.mjs
python -m unittest discover -s tests -p test_eras.py
```

Python tests require Pandas and NumPy. The seeded mock fixture can be regenerated with `node scripts/seed.mjs`. The era repair runs offline with `python -m scripts.repair_eras`, preserving non-era shot fields and rebuilding era aggregates in both export directories.

## Deploy

Publish the full **public/** folder on a static host. Existing `vercel.json` declares that output directory. See the [launch kit](docs/recruiter/LAUNCH_KIT.md) for exact settings and signed-out smoke checks. Run the packaging script after documentation edits. No API keys or database configuration are required for this prototype. Files here are local until committed/pushed; publishing is a separate step.

## NBA pipeline and alternative app

```sh
python -m venv .venv
# Activate .venv using your shell, then:
pip install -r requirements.txt
streamlit run app.py
```

Existing scripts under `src/` collect NBA data through `nba_api`, clean and aggregate shot locations, and export CSVs. Live collection depends on NBA API availability; the portfolio uses committed exports and does not need collection to run. The master export has 79,763 shots from ten selected players with observed game dates in 1996–2026. It is not a complete league dataset. Historical era comparisons are descriptive and not adjusted for pace, rules or opponent quality.

Independent portfolio project developed with AI coding assistance. No affiliation with the NBA. Data rights should be reviewed before commercial redistribution. No user research, revenue or recruiter-engagement uplift is claimed.
