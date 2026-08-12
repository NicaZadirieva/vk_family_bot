set shell := ["powershell.exe", "-c"]

@a_default:
	just --list

@dev:
    $env:ENVIRONMENT="development"; uv run ./main.py
@prod:
    $env:ENVIRONMENT="production"; uv run ./main.py

@lint:
	uv run ruff check --fix

@format:
	uv run ruff format