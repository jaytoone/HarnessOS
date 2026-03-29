.PHONY: test coverage lint

test:
	python3 -m pytest tests/ -v

coverage:
	python3 -m pytest tests/ --cov=experiments --cov=runner --cov-report=html --cov-report=term-missing

lint:
	python3 -m mypy runner.py experiments/ --ignore-missing-imports --no-error-summary 2>/dev/null || true
