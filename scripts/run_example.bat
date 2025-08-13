@echo off
echo Running example smoke test...
poetry run python -c "import pysme.sample; print(pysme.sample.hello())"

