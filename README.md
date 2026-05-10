# Studiu Comparativ de Performanță – Aplicație Flask MVC

Disertație: _Studiu comparativ al performanței aplicațiilor web dezvoltate în Flask în funcție de mediul de execuție (bare metal, VM, Docker) și de tipul bazei de date utilizate (SQL vs NoSQL)._

---

## Structura proiectului

```
disertatie/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory
│   │   ├── controllers/
│   │   │   └── main.py          # Rute API (submit, benchmark/cpu, benchmark/io, records)
│   │   └── models/
│   │       └── sql_model.py     # Model SQLAlchemy (PostgreSQL)
│   ├── config.py                # Configurare (DB_TYPE, DATABASE_URL, MONGO_URI)
│   ├── run.py                   # Entry-point Gunicorn/Flask
│   ├── gunicorn.conf.py         # Configurare Gunicorn producție
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html               # Formular HTML + tabel înregistrări
│   ├── static/
│   │   ├── style.css
│   │   └── app.js
│   ├── nginx.conf               # Nginx reverse-proxy → backend
│   └── Dockerfile
├── benchmark/
│   └── run_benchmark.sh         # Script ApacheBench (10/50/100/200 utilizatori)
├── docker-compose.sql.yml       # 3 containere: frontend + backend + PostgreSQL
└── docker-compose.nosql.yml     # 3 containere: frontend + backend + MongoDB
```

---

## Endpoint-uri API

| Metodă | Cale | Descriere |
|--------|------|-----------|
| GET  | `/health` | Status aplicație + tip DB activ |
| POST | `/api/submit` | Primește formular, execută sarcină CPU-bound, salvează în DB |
| GET  | `/api/benchmark/cpu?value=42` | Test CPU-bound (100 000 iterații aritmetice) |
| GET  | `/api/benchmark/io?count=10` | Test I/O-bound (inserări bulk în DB) |
| GET  | `/api/records` | Ultimele 50 de înregistrări din DB |

---

## 1. Rulare Docker (recomandat pentru studiu)

### Varianta SQL (PostgreSQL)

```bash
docker compose -f docker-compose.sql.yml up --build
```

### Varianta NoSQL (MongoDB)

```bash
docker compose -f docker-compose.nosql.yml up --build
```

Aplicația este disponibilă la **http://localhost**.

---

## 2. Rulare Bare Metal / VM

### Cerințe
- Python 3.12+
- PostgreSQL **sau** MongoDB instalat și pornit local

### Pași

```bash
cd backend

# Creează și activează mediu virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalează dependențele
pip install -r requirements.txt
```

**Varianta SQL (PostgreSQL)**

```bash
createdb -U postgres perfdb

export DB_TYPE=sql
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/perfdb"
gunicorn --config gunicorn.conf.py run:app
```

**Varianta NoSQL (MongoDB)**

```bash
export DB_TYPE=nosql
export MONGO_URI="mongodb://localhost:27017/"
export MONGO_DB_NAME=perfdb
gunicorn --config gunicorn.conf.py run:app
```

Servește frontend-ul:

```bash
cd frontend && python3 -m http.server 8080
```

> Ajustează `API_BASE` din `frontend/static/app.js` la `http://localhost:5000/api` pentru rulare bare-metal fără nginx.

---

## 3. Benchmark

Instalează ApacheBench:

```bash
sudo apt install apache2-utils
```

Rulează scriptul (cu aplicația pornită pe portul 80):

```bash
cd benchmark
./run_benchmark.sh               # localhost:80 (Docker)
./run_benchmark.sh 192.168.x.x 80  # VM sau altă gazdă
```

Scriptul testează:
- **CPU-bound**: 500 requesturi × 4 niveluri de concurență (10 / 50 / 100 / 200)
- **I/O-bound**: idem, cu 5 inserări în DB per request

Rezultatele sunt salvate automat în `benchmark/results/`.

### Monitorizare sistem

```bash
mpstat -P ALL 1   # CPU per core, refresh 1s
htop              # utilizare generală
```

---

## 4. Variabile de mediu

| Variabilă | Valoare implicită | Descriere |
|-----------|-------------------|-----------|
| `DB_TYPE` | `sql` | `sql` pentru PostgreSQL, `nosql` pentru MongoDB |
| `DATABASE_URL` | `postgresql://perfuser:perfpass@localhost:5432/perfdb` | URI conexiune PostgreSQL |
| `MONGO_URI` | `mongodb://localhost:27017/` | URI conexiune MongoDB |
| `MONGO_DB_NAME` | `perfdb` | Numele bazei de date MongoDB |
| `SECRET_KEY` | `dev-secret-key-change-in-prod` | Cheie secretă Flask |

---

## 5. Arhitectura aplicației

```
Browser
  │
  ▼
Frontend (Nginx :80)
  │  /api/*  →  proxy
  ▼
Backend Flask (Gunicorn :5000)
  │
  ├── DB_TYPE=sql   →  PostgreSQL :5432
  └── DB_TYPE=nosql →  MongoDB    :27017
```

### Flux submit
1. Utilizatorul completează formularul (nume, prenume, cod, valoare, descriere).
2. Frontend-ul trimite `POST /api/submit` cu JSON.
3. Backend-ul execută 100 000 de iterații aritmetice (**CPU-bound**).
4. Rezultatul este salvat în DB (**I/O**).
5. Răspunsul JSON este afișat utilizatorului.