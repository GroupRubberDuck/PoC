# PoC

Per avviare l'applicazione è sufficiente aver docker e docker compose installati ed eseguire:
```bash
docker compose up --build -d
```
L'applicazione sarà quindi accessibile attraverso il browser all'indirizzo [http://localhost:8080](http://localhost:8080).

## Sviluppo
Per lo sviluppo è necessario avere un'istanza di MongoDB installata e in esecuzione, ed aver impostato le seguenti variabili di ambiente per permettere all'applicazione di collegarsi al database:
- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`

Per avviare il server in modalità debug eseguire:
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
