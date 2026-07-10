# House Price Prediction API (FastAPI + Neon PostgreSQL)

FastAPI backend for the "Cloud-Based House Price Prediction Platform" project.
Serves a trained `RandomForestRegressor` model and logs every prediction to a
Neon PostgreSQL `prediction_history` table.

## Project structure

```
backend/
├── app/
│   ├── main.py          # FastAPI app, routes
│   ├── database.py       # SQLAlchemy engine/session (reads DATABASE_URL)
│   ├── models.py          # prediction_history ORM model
│   ├── schemas.py         # Pydantic request/response models
│   ├── ml_model.py        # loads model.pkl / label_encoder.pkl, runs predictions
│   └── ml/
│       ├── model.pkl
│       └── label_encoder.pkl
├── requirements.txt
├── .env.example
├── .gitignore
└── render.yaml
```

> Note: `model.pkl` was missing from the uploaded zip (only `label_encoder.pkl`
> was present). It was retrained here using the exact same steps as
> `train_model.ipynb` (drop `longitude`/`latitude`, label-encode
> `ocean_proximity`, `RandomForestRegressor`, `random_state=42`), so the
> label encoder classes match exactly: `<1H OCEAN, INLAND, ISLAND, NEAR BAY, NEAR OCEAN`.

## 1. Local setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt

cp .env.example .env
# Edit .env and paste your real Neon connection string, e.g.:
# DATABASE_URL=postgresql://user:pass@ep-xxxx.neon.tech/dbname?sslmode=require
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Visit:
- http://127.0.0.1:8000/ — home/health check
- http://127.0.0.1:8000/docs — Swagger UI (test `/predict` here)

## 2. API Endpoints

| Method | Path                 | Description                                   |
|--------|----------------------|------------------------------------------------|
| GET    | `/`                  | Health check                                    |
| POST   | `/predict`           | Predict price, store in `prediction_history`    |
| GET    | `/predictions`       | All stored predictions (newest first)           |
| GET    | `/predictions/recent`| Last 5 predictions (bonus)                      |
| GET    | `/predictions/count` | Total predictions stored (bonus)                |

Example `POST /predict` body:

```json
{
  "housing_median_age": 25,
  "total_rooms": 5,
  "total_bedrooms": 5,
  "population": 1200,
  "households": 5,
  "median_income": 4.5,
  "ocean_proximity": "NEAR BAY"
}
```

## 3. Database

The `prediction_history` table is created automatically on startup via
`Base.metadata.create_all(bind=engine)` — no manual migration needed.
Columns: `id`, the 7 input features, `predicted_price`, `created_at`.

## 4. Git & GitHub

```bash
git init
git add .
git commit -m "FastAPI backend with Neon PostgreSQL integration"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

`.env` is already excluded via `.gitignore` so credentials never get committed.

## 5. Deploy to Render

1. Push this `backend/` folder to GitHub.
2. On Render: **New → Web Service** → connect the repo.
3. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variable:** `DATABASE_URL` = your Neon connection string
4. Deploy. Your API will be live at `https://<your-service>.onrender.com`.

## 6. Frontend integration

The companion Streamlit app (in `../frontend/app.py`) no longer calls
`model.predict()` locally — it sends a POST request to `POST {API_URL}/predict`
on the deployed backend and displays the returned price. Set `API_URL` as an
environment variable (or in `frontend/.env`) to point at your Render backend URL.
