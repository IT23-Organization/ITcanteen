# ITCanteen

Run frontend:
```sh
cd frontend
bun install
bun run dev
```

Run backend:
```sh
# Initialize (run once)
sqlite3 data.sqlite < init.sql
opam install . --deps-only

# Run backend
dune exec backend
```

Run Discord bot:
```sh
cd bot
python -m pip install -r requirements.txt
python main.py
```