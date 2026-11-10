# Sand from the Source: working rules

@../../shared/idiom/CORE.md

Voice, working rules and dataset terms follow Idiom (`CORE.md`, `DATASETS.md`, `house/`; private repo, normally linked at `../../shared/idiom`). The import is harmless when the file is absent (CI). Public repo: never copy anything from Idiom's `personal/` or `working/` folders here.

A SubScout story on present-day source-to-sink around the North Sea: catchments, bedrock budgets, sediment flux and sand quality. Owner: Adam McCarthy. The analysis lives in the private `source-to-sink` repo; this repo holds the narrative and small derived extracts only.

- Built with SubScout (github.com/AdmcCarthy/SubScout); follow its CLAUDE.md and styleguide. `uv run --project ../SubScout subscout build story --out _site`.
- Every number in `story/story.md` is a `{{ metric }}` from `story/story.py`; no digits typed into prose.
- Extracts come from `scripts/make_extracts.py`; rerun it after the source-to-sink pipeline changes, then rebuild. Only frames whose geology sources are open for public display are extracted (North Sea, Norwegian Sea).
- Data terms and attribution lines are in `DATA-LICENCE.md` and in the story's `sources:`; keep them in step with Idiom `DATASETS.md`.
- Before showing prose: `python ../../shared/idiom/scripts/check_banned.py story/story.md` and `check_voice.py --mode published`. Before publishing: SubScout's readability gate on `_site`.
- Confidence levels on the page: Observed, Derived, Interpreted. The budget and the quality proxy are Derived; the glauconite reading and the past are Interpreted.
- British English, metric.
