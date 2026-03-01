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

### Documentazione
- [StrictDoc](https://strictdoc.readthedocs.io/en/stable/stable/docs/strictdoc_01_user_guide.html)
- [Flask](https://flask.palletsprojects.com/en/stable/)
- [mypy](https://mypy.readthedocs.io/en/stable/getting_started.html)
