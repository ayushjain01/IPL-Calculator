# IPL Calculator - Will my team qualify?

Explore how different match results could change the IPL points table. Let the computer try possible endings to a season, or pick the winners yourself.

The app uses Python, HTML and CSS.

## Getting started

Requires **Python 3.11 or newer** and Git to clone the repository.

```sh
git clone https://github.com/ayushjain01/IPL-Calculator.git
cd IPL-Calculator
python server.py --open-browser
```

The app opens at [http://127.0.0.1:8000](http://127.0.0.1:8000). Keep the terminal open while using it, and press **Ctrl+C** to stop the server. On systems where Python is named `python3`, use `python3` in the commands instead.

On Windows, you can also double-click `run.bat` after cloning. This launcher selects Python 3.11 through the Windows Python launcher. If you have a newer version, run `python server.py --open-browser` with that version instead.

The match data needed to run the app is included. An internet connection is only needed to download new data or open external links.

## Choose a mode

### Computer predictions

1. Choose your team. Its row will be highlighted.
2. Choose how many possible season endings to try. The default, 2,000, is a good starting point.
3. Click **Calculate chances**.

A result of **70%** means the team finished in the top four in about 70 out of every 100 endings the computer tried. More endings make the estimate steadier; they do not guarantee a better prediction.

The NRR range shows where the team's net run rate landed in the middle 80% of those endings. Actual results can fall outside it.

### Manual predictions

1. Click either team’s win button, or **No result** to try a washout.
2. The points table updates after every pick.
3. Click another option to change the result, or click the selected option again to undo it.

Use **Reset all picks** to start again. Picks last up to eight hours in your browser session. Restarting the app clears them. Computer predictions run separately and do not use these picks.

## Which season am I looking at?

IPL 2026 has finished, and RCB won back to back. The homepage has a link to relive the celebrations.

For now, the calculator lets you go back to **28 April 2026, after match 40**. It starts with the actual points table and scores from then. You can explore different results for the **30 league matches still to come at that point**.

This is a historical replay, not a live forecast. Although the season has finished, those later scores and results are kept out of the prediction model.

## How do the predictions work?

The computer gives each team a strength rating based on past results. Wins raise the rating; losses lower it. This simple method is called **Elo**. Higher-rated teams get a better chance of winning, but upsets can still happen.

It then plays out the remaining fixtures many times and counts how often each team reaches the top four.

**The model is still experimental.** In testing on 142 decided matches from 2024–2025, it picked the winner correctly **49.3%** of the time. Its probability estimates did no better than giving each team an equal chance. Use the tool to explore possibilities, rather than as a reliable forecast. It does not know about injuries, playing elevens, the toss or weather.

## What is NRR?

**Net run rate** compares how quickly a team scores with how quickly its opponents score against it. A higher number is better. For example, scoring at 9 runs per over and conceding 8 gives an NRR of **+1.000**.

- For completed matches, the app uses actual runs and balls.
- For predicted matches, the scores are unknown. The app uses examples from past IPL matches to estimate NRR. These are possible scores, not exact score predictions.
- A win earns 2 points. A no result gives both teams 1 point and does not change their NRR.

In the table, **P** means played, **W** wins, **L** losses, **NR** no results, **T** unresolved ties, and **PTS** points. Teams are ranked by points, then wins, then NRR.

## How much data is included?

The download from [Cricsheet](https://cricsheet.org/downloads/) contains **1,243 IPL match records**.

The saved team ratings use **1,209 available records across 19 seasons, 2008–2026**, from 18 April 2008 through 28 April 2026. Of those, **1,200 decided matches update the ratings**. Only the first 40 matches of 2026 are included. Coverage depends on which records Cricsheet provides.

The example scores used for future NRR come from suitable matches from **2018 onward**, up to the same cutoff date.

## Where is the model?

| File | What it does |
| --- | --- |
| `model.py` | Calculates team ratings, possible results and NRR |
| `data/replay.json` | Stores the learned team ratings and the historical data used by the app |
| `data/model-report.json` | Records how the model performed in testing |
| `prepare_data.py` | Rebuilds the model from the downloaded match data |
| `server.py` | Runs the website on your computer |

There is no separate `.pkl` model file. The learned part is the **team ratings saved in `data/replay.json`**. Starting the website loads them; it does not train the model again.

## Troubleshooting

- **Python is not found:** install Python 3.11 or newer and check that `python --version` (or `python3 --version`) works in your terminal.
- **An environment points to a missing Python installation:** deactivate it and use an installed Python 3.11+ interpreter, or recreate the environment.
- **Port 8000 is already in use:** choose another port with `python server.py --port 8001 --open-browser`.
- **Opening an HTML file does not run the calculator:** start `server.py` and visit the local address above. The calculations require the Python server.

## Optional: rebuild the model

You do not need to do this to use the app. From the project folder, run:

```sh
python prepare_data.py
```

This reuses the local archive at `data/raw/ipl_male_json.zip`, or downloads it if missing. To use a newer download, save it separately and pass its path with `--archive`. Rebuilding still uses the same 2026 match-40 starting point. Restart the app afterwards to load the rebuilt model.

## When the next IPL season starts

TODO: pull official fixtures **and match results every day**, check them against the official points table, and update the app's data. Show when it was last updated and warn if it is out of date. Keep each season's manual picks separate.

Automation will be added later. The old collection workflow is manual-only, and its scraper needs updating before use.

## Technical details and checks

See [the technical notes](docs/technical-details.md) for the full model settings, test scores, NRR edge cases and hosting notes. The website's **How it works** page also explains the calculations.

To run the checks:

```sh
python -m unittest discover -s tests -p "test_*.py" -v
```

For deployment, use hosting that can run Python. The local server is intended for running the project on your own computer; a public deployment needs an appropriate production server setup.

## Sources and license

Match data comes from [Cricsheet](https://cricsheet.org/) under [ODC-BY 1.0](https://cricsheet.org/licensing/). See [data/SOURCE.md](data/SOURCE.md) for the download details. The local DM Sans font includes its OFL license.

The application is MIT licensed; see [LICENSE.txt](LICENSE.txt). Created by [Ayush Jain](https://github.com/ayushjain01). Not affiliated with the IPL.
