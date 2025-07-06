# Contributing

Thanks for your interest in AI-Unity-Studio!

## Setup

1. Install requirements: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and adjust paths.
3. Run `pre-commit install` to enable hooks.

## Workflow

- Use `python -m agents.tech.orchestrator "Feature"` to trigger the pipeline.
- Validate project map with `python tools/mapctl.py validate`.
- Summaries via `python tools/mapctl.py summary`.

Please format Python code with `black` and `isort`.
