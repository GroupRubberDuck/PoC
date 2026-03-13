# PoC


## Sviluppo
```bash
# Impostare le variabili di ambiente per la connessione al database:
# - DB_HOST
# - DB_PORT
# - DB_USER
# - DB_PASSWORD
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

## Deploy
```bash
docker build -t grouprubberduck/poc .
docker run --rm -d -p 8080:8080 grouprubberduck/poc
```

### Documentazione
- [StrictDoc](https://strictdoc.readthedocs.io/en/stable/stable/docs/strictdoc_01_user_guide.html)
- [Flask](https://flask.palletsprojects.com/en/stable/)
- [mypy](https://mypy.readthedocs.io/en/stable/getting_started.html)
