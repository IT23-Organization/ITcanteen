# ITCanteen

Run frontend:
```sh
cd frontend
bun install
bun run dev
```

Run backend:
```sh
cd backend

# Set up environment variables
echo "DB_PATH=data.db" > .env
echo "PORT=3000" >> .env

bun install
bun run dev
```

Run Discord bot:
```sh
cd bot
python -m pip install -r requirements.txt
python main.py
```