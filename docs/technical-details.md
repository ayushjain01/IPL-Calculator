# Technical reference

For installation and usage, see the [README](../README.md).

## Training coverage and where the model lives

The saved winner model processes **1,209 available match records across 19 IPL seasons (2008–2026)**, from **18 April 2008 through 28 April 2026**. Of these, **1,200 decided matches update the Elo ratings**; no results and unresolved ties do not transfer rating points. The archive contains 1,243 records overall, but the final 34 matches of 2026 are excluded from this replay's training history. Historical coverage reflects the records available from Cricsheet, not a guarantee that every scheduled match has a scorecard.

The model includes the first 40 matches of 2026 only. Future fixtures are retained without their actual winners or scores. Historical scoring samples for projected NRR use eligible matches from **2018 onward**, up to the same cutoff; this is a separate input from the full Elo history.

| File | Purpose |
| --- | --- |
| `model.py` | Model implementation: Elo updates, winner probabilities, NRR rules, historical score sampling and simulations |
| `data/replay.json` | Saved learned team ratings under `model.ratings`, selected parameters under `model.report.parameters`, and the replay's historical inputs |
| `data/model-report.json` | Parameter selection details and chronological evaluation results |
| `prepare_data.py` | Rebuilds the saved ratings and replay from the downloaded archive |
| `data/raw/ipl_male_json.zip` | Original downloaded Cricsheet archive; kept locally and ignored by Git |
| `server.py` | Loads the saved model and renders the browser app using Python and HTML forms |

There is no `.pkl` or neural-network weights file: **Elo's learned state is the team ratings stored in `data/replay.json`**. The server loads those ratings at startup; opening a page or running a simulation does not retrain the model. After rebuilding the data, restart the server to load the updated model.

## Model and honest evaluation

Dependency-free Elo starts teams at 1500 and transfers rating points after wins. Season boundaries regress ratings toward 1500. Update rate and carry-over were selected on 2022–2023. A separate walk-forward evaluation on 2024–2025 predicts each match before updating from that result. Bangalore/Bengaluru, Delhi and Punjab renames are combined; separate franchises are not merged.

The selected model scored **0.2536 Brier**, **0.7004 log loss**, and **49.3% winner accuracy** across 142 decided evaluation matches. A 50/50 baseline scores 0.2500 Brier and 0.6931 log loss, so **this version has not demonstrated predictive improvement over chance**. These results are shown in the app. Evaluation results were not used to retune parameters. See `data/model-report.json` and `/model.html`.

Qualification estimates combine these modest team ratings with the actual starting table and real fixtures. Ratings stay fixed during simulated future matches. There are no squad, injury, toss, home-advantage or weather inputs. Simulations assume decided matches; manual mode supports no results. Sampling error shown is approximate Monte Carlo error only, not a confidence interval for real-world qualification chances.

Future scores sample a pair of actual historical innings, conditional on the selected winner and loser. Ordinary 20-over matches from 2018 onward are eligible. Matches from 2023 onward receive three times the weight, with another three-times factor for matching venue names. This preserves realistic winning margins and chase lengths without fixed 180–160 scores. It does not model player/team-specific scoring distributions, and forecast NRR accuracy has not been validated. The displayed range is a simulated 10th–90th percentile range.

## NRR rules

Completed-match NRR comes from total runs and legal balls, not an average of match-level NRRs. All-out innings use the full allotted quota. Wides/no-balls count as runs but not legal balls. No-result games affect points but not NRR. Super Over scores are excluded; the Super Over winner still receives the match points.

Completed revised-target DLS chases use target minus one and the revised allocation for the first innings. Early-terminated DLS games without a verified par score are flagged as unsupported rather than silently estimated. No unsupported NRR games occur in the first 40 replay matches. Standings use points, wins, NRR, then alphabetical fallback for exact ties. Playoffs are excluded from league standings. Reference: [IPL playing conditions](https://documents.iplt20.com/bcci/documents/1742707993986_Match_Playing_Conditions.pdf).

## Refresh data / rebuild model

The app never downloads data on startup. An intentional rebuild is:

```text
python prepare_data.py --archive data/raw/ipl_male_json.zip
```

To obtain a fresh source snapshot, download the archive from Cricsheet to a new path, then pass that path with `--archive`. If no archive path is passed, the script reuses `data/raw/ipl_male_json.zip` if present, or downloads it once. Rebuilding preserves the explicit 2026 match-40 cutoff and refuses an incomplete replay schedule. Restart the server after rebuilding. The full raw archive is ignored by Git; compact derived replay/model files are included so a checkout runs without re-downloading.

## Validation

```text
python -m unittest discover -s tests -p "test_*.py" -v
```

Checks cover actual fixtures and results, future-data exclusion, legal balls, all-out quotas, NRR totals, Super Over exclusion, DLS handling, deterministic simulations, manual picks/reset, session isolation between modes, script-free HTML, and HTTP form protections.

## TODO: daily fixtures/results refresh when IPL starts

- Pull official fixtures **and match results every day**, including reschedules, abandoned matches and corrected scorecards.
- Reconcile reconstructed standings with the official table and add verified NRR overrides where source details are incomplete, especially early DLS terminations.
- Validate unique IDs, team names, season, innings totals and bowling allocations before publishing refreshed data.
- Add an explicit live-season dataset with source, last-successful-update time, stale-data notice and season-specific manual sessions.
- Add automation later; no scheduled data refresh is currently configured.

## Files and deployment

`server.py`: local HTML-form app; `model.py`: cricket rules, Elo, sampling and simulations; `prepare_data.py`: deliberate download/build step; `templates/base.html`: HTML shell; `app.css`: page styles; `data/replay.json`: offline replay and model inputs.

The active application uses `server.py`, `model.py`, `templates/`, `app.css` and the saved data. Deployment requires a Python-capable host; static-only hosting cannot execute the calculations.

MIT — see [LICENSE.txt](LICENSE.txt). Created by [Ayush Jain](https://github.com/ayushjain01). Not affiliated with the IPL.

## Render hosting

`app.py` exposes the shared pages and model through Flask. `render.yaml` starts Gunicorn on `0.0.0.0:$PORT` and configures `/healthz`. The local entry point remains `server.py`. See the README for deployment steps.

Hosted manual picks are saved in a signed, HTTP-only browser cookie with an eight-hour lifetime. On Render the cookie is marked Secure. `SECRET_KEY` is required on Render, and must be shared across workers and preserved across deploys. Sessions are scoped to the replay dataset. Posted forms require a session-specific CSRF token; pick submissions redirect to avoid duplicate changes on refresh. Render hostnames and optional `ALLOWED_HOSTS` entries are trusted explicitly. No database is needed for these small per-browser picks.
