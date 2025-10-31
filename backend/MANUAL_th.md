# API

## Endpoints ร้านค้า `stores/`

### `POST /store/create` สร้างร้านใหม่
| | |
|-|-|
| Query Parameters | `name` (string, required) — ชื่อร้าน

**ตัวอย่าง:**
```
POST /store/create?name=โคเจ
```

**ผลลัพธ์:**
```json
{
  "ok": "true",
  "store_id": 1
}
```

---

### `GET /store` ดูข้อมูลร้าน
| | |
|-|-|
| Query Parameters | `store_id` (int, required) — ID ร้าน

**ตัวอย่าง:**
```
GET /store?store_id=1
```

**ผลลัพธ์:**
```json
{
  "store_id": 1,
  "name": "โคเจ",
  "products": [
    {
      "product_id": 1001,
      "store_id": 1,
      "name": "แกงกะหรี่ไก่ทอก",
      "price": 60.0
    },
    {
      "product_id": 1002,
      "store_id": 1,
      "name": "กิมจิ",
      "price": 100.0
    }
  ]
}
```

---

### `POST /store/delete` ลบร้าน

| | |
|-|-|
| Query Parameters | `store_id` (int, required) — ID ร้าน

**ตัวอย่าง:**
```
POST /store/delete?store_id=1
```

**ผลลัพธ์:** 
```json
"bye"
```

---

### `POST /store/product/add` เพิ่มสินค้าใหม่
| | |
|-|-|
| Body (JSON) | `store_id` (int, required) — ID ร้าน
| | `name` (string, required) — ชื่อสินค้า
| | `price` (float, required) — ราคาสินค้า

**ตัวอย่าง:**
```json
{
  "store_id": 1,
  "name": "ชาเย็น",
  "price": 25.0
}
```

**ผลลัพธ์:**  
```json
{
  "ok": "true",
  "product_id": 1001
}
```

---

### `POST /store/product/remove` ลบสินค้า
| | |
|-|-|
| Query Parameters | `product_id` (int, required) — ID สินค้า

**ตัวอย่าง:**
```
POST /store/product/remove?product_id=1001
```

**ผลลัพธ์:**
```json
{ "ok": "true" }
```

---

### `GET /store/product` ดูสินค้าทั้งร้าน
| | |
|-|-|
| Query Parameters | `store_id` (int, required) — ID ร้าน

**ตัวอย่าง:**
```
GET /store/product?store_id=1
```

**ผลลัพธ์:**
```json
[
  { "product_id": 1001, "store_id": 1, "name": "ชาเย็น", "price": 25.0 },
  { "product_id": 1002, "store_id": 1, "name": "กาแฟเย็น", "price": 30.0 }
]
```

---

## Endpoints รายการ `products/`

### `GET /product` ดูรายการตาม ID
**Endpoint:** `GET /product`
**Query:**  
- `product_id` (int)

**ตัวอย่าง:**
```
GET /product?product_id=1002
```

**ผลลัพธ์:**
```json
{
  "product_id": 1002,
  "store_id": 1,
  "name": "กาแฟเย็น",
  "price": 30.0
}
```

---

## Endpoints ออเดอร์ `orders/`

### `POST /orders/add` สร้างออเดอร์ใหม่
| | |   
|-|-|
| Body (JSON) | `student_id` (int, required) — รหัสนักเรียน
| | `store_id` (int, required) — รหัสร้าน
| | `product_id` (int, required) — รหัสสินค้า

**ตัวอย่าง:**  
```json
{
  "student_id": 101,
  "store_id": 1,
  "product_id": 1002
}
```

**ผลลัพธ์:**  
```json
{ "id": 12 }
```

---

### `POST /orders/update` อัปเดตสถานะออเดอร์
| | |   
|-|-|
| Body (JSON) | `order_id` (int, required) — รหัสออเดอร์
| | `paid` (bool, optional) — สถานะการชำระเงิน
| | `done` (bool, optional) — สถานะการทำออเดอร์เสร็จสิ้น

สามารถส่งแค่บาง field ได้ เช่น:
```json
{ "order_id": 12, "done": true }
```
ระบบจะอัปเดตเฉพาะ field ที่ส่งมา

**ผลลัพธ์:**  
```json
{"ok": "true"}
```

---

### `GET /orders/` ดูออเดอร์ตาม ID
| | |
|-|-|
| Query Parameters | `order_id` (int, required) — รหัสออเดอร์

**ตัวอย่าง:**  
```
GET /orders/?order_id=12
```

**ผลลัพธ์:**  
```json
{
  "order_id": 12,
  "student_id": 101,
  "store_id": 1,
  "product_id": 1002,
  "total_price": 30.0,
  "paid": true,
  "done": false
}
```

---

### `GET /store/orders` ดูออเดอร์ของร้านค้า
| | |
|-|-|
| Query Parameters | `store_id` (int, required) — รหัสร้าน

**ตัวอย่าง:**  
```
GET /store/orders?store_id=1
```

**ผลลัพธ์:**  
```json
[
  {
    "order_id": 12,
    "student_id": 101,
    "store_id": 1, // <-
    "product_id": 1002,
    "total_price": 30.0,
    "paid": true,
    "done": false
  },
  {
    "order_id": 13,
    "student_id": 102,
    "store_id": 1, // <-
    "product_id": 1001,
    "total_price": 60.0,
    "paid": false,
    "done": false
  }
]
```

---

### `GET /student/orders` ดูออเดอร์ของนักเรียน
| | |
|-|-|
| Query Parameters | `student_id` (int, required) — รหัสนักเรียน

**ตัวอย่าง:**  
```
GET /student/orders?student_id=101
```

**ผลลัพธ์:**  
```json
[
  {
    "order_id": 12,
    "student_id": 101, // <-
    "store_id": 1,
    "product_id": 1002,
    "total_price": 30.0,
    "paid": true,
    "done": false
  },
  {
    "order_id": 15,
    "student_id": 101, // <-
    "store_id": 2,
    "product_id": 2001,
    "total_price": 45.0,
    "paid": false,
    "done": true
  }
]
```
