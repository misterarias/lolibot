test: 
	@poetry run coverage run -m pytest -v 
	@poetry run coverage report --fail-under 70 -m

style:
	@poetry run black .
	@poetry run flake8

pre-commit: style test
	@echo "Pre-commit checks passed."

clean:
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -delete
	@echo "Cleaned up temporary files."
