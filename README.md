# Mumbai Heat & Air Quality Risk Intelligence

A Streamlit dashboard for six Mumbai monitoring stations: latest PM2.5, PM10 and temperature with
freshness labels, charts, a station map, and an honest test of whether a simple model can forecast
next-day PM2.5.

**Live app:** TODO (added after deployment)
**Screenshot:** TODO

## Result in one line
No model beat the "tomorrow = today" baseline on the test period (1 Jul to early Nov 2026), so the app shows
the comparison table and no forecast. See the Forecast page.

## Data sources
- OpenAQ API v3 (latest readings and daily summaries). Station operators: MPCB, BMC, IITM.
- Licences: TODO (check OpenAQ and each operator's terms before publishing).

## How it works
Source (OpenAQ) -> raw files (never edited) -> cleaning (flag, never fill) -> models -> Streamlit app.
TODO: add the architecture diagram.

## Results
See `models_saved/model_comparison.csv` or the Forecast page.

## Limitations
- About 20 months of data, one winter, six stations.
- The test period has no winter.
- Thresholds (coverage, plausibility, freshness, split date) are my own choices.
- Map colors are indicative and are not an official AQI.

## Setup
1. `python -m venv venv` then activate it
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your own OpenAQ key (free at explore.openaq.org)
4. TODO: commands to download the data and rebuild the cleaned file
5. `streamlit run app/Home.py`

## Tests
`python -m pytest tests -v` (5 tests on the cleaned data and results)