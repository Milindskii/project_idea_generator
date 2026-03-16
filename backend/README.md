# Run Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

# Run Frontend (separate terminal)

```bash
cd ..
npm run dev
```

API docs available at: `http://localhost:8000/docs`

