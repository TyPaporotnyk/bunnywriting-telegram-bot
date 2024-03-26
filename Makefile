test:
	pytest -v tests -W ignore

lint:
	pre-commit run --all-files
