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



# 🏗️ Integrazione Frontend (Vue.js) e Backend (Flask)

Questo progetto utilizza un'architettura ibrida (pattern a "Isole" o Micro-Frontends). 
Il server Flask gestisce il routing, l'autenticazione e il rendering principale delle pagine tramite Jinja2. Vue.js viene utilizzato esclusivamente per "iniettare" componenti altamente interattivi (come le interfacce per l'interazione coi Decision Tree) all'interno di specifiche pagine HTML, senza la necessità di creare una Single Page Application (SPA) separata.

## ⚙️ Architettura Docker e Hot-Reloading

L'ambiente di sviluppo è orchestrato tramite `docker-compose.yaml` e si basa su due anime principali:
1. **Container `app` (Flask):** Serve le pagine HTML e le API backend.
2. **Container `vue_builder` (Node.js):** Lavora silenziosamente in background. Grazie a un volume condiviso, osserva i file sorgente Vue e, a ogni salvataggio (`Ctrl+S`), compila istantaneamente il codice JavaScript rilasciandolo nella cartella pubblica di Flask.

## 📁 Struttura delle Cartelle Rilevanti

* `frontend/src/` 👉 **Sorgenti Vue.** Qui si scrivono i file `.vue` e i file di avvio `.js`. Questo è l'unico posto in cui modificare il frontend.
* `frontend/vite.config.js` 👉 Configurazione di Vite per mappare gli entry-point multipli (le diverse "isole" Vue).
* `src/poc/static/vue-assets/` 👉 **File Compilati (NON TOCCARE).** Vite sputa qui i file generati. Questi file vengono serviti staticamente da Flask.

## 🛠️ Come aggiungere una nuova "Isola" Vue

Se un membro del team deve creare un nuovo componente interattivo, i passaggi sono 3:

1. **Creare il sorgente:** Creare il componente (es. `Editor.vue`) e un file di mount (es. `main-editor.js`) in `frontend/src/`.
2. **Aggiornare Vite:** Aggiungere l'entry-point in `frontend/vite.config.js` nella sezione `rollupOptions -> input`. Al prossimo salvataggio, Vite creerà un nuovo file compilato (es. `dt-editor.js`).
3. **Iniettare in Flask:** Nel template Jinja desiderato, inserire il div bersaglio nel `block content` e lo script compilato nel `block scripts`:
   ```html
   {% block content %}
       <div id="bersaglio-vue"></div>
   {% endblock %}

   {% block scripts %}
       <script type="module" src="{{ url_for('static', filename='vue-assets/dt-editor.js') }}"></script>
   {% endblock %}

# Verificare l'integrazione con Vue
Prima di procedere allo sviluppo si consiglia di controllare la pagina [http://localhost:8080/test-vue](http://localhost:8080/test-vue)

Serve a verificare che Vue funzioni correttamente, in un'esecuzione normale ciò che è visibile è una pagina contente un box giallo e un contatore reattivo, aggiornabile premendo un pulsante