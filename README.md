# PoC

## Sviluppo
```bash
poetry install
poetry run flask --app src.poc.app:create_app run --debug
```

### Validazione
```bash
poetry run mypy .
poetry run ruff check .
poetry run pytest
poetry run strictdoc export .
```

