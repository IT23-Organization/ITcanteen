# ITCanteen

Run frontend:
```sh
cd frontend
npm install # install dependencies
npm run dev
```

Run backend:
```sh
cd backend
# Initialize database with mock data (for testing)
sqlite3 data.sqlite ".read mock.sql"

# Run backend
go mod download # install dependencies
go run main.go # or go build && ./main
```

Run Discord bot:
```sh
cd Discord-Bot
python -m pip install -r requirements.txt
python main.py
```

## สำหรับอาจาร์ยโชติพัชร์

พวกเราได้ทำการ deploy ไปยังเซิฟเวอร์คณะที่
```sh
http://10.30.32.31:5173 #website
http://10.30.32.31:8080 #backend
```
จะสามารถเข้าถึงได้ถ้าต่อ Wifi คณะหรือ VPN คณะนะครับ

ส่วน Discord สามารถเข้าได้ผ่าน https://discord.gg/mqcAXdCyxM
