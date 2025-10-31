package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strconv"

	"github.com/gorilla/mux"
	_ "github.com/mattn/go-sqlite3"
)

// --- Types ------------------------------

// For simplicity, the store ID will be from 0 to 1000 and products will have
// IDs from storeID * 1000 + 1 to storeID * 1000 + 999.
// So there will be a maximum of 1000 stores and 999 products per store.

type Store struct {
	StoreID  int       `json:"store_id"`
	Name     string    `json:"name"`
	Products []Product `json:"products"`
}

// nextProductID returns the next available product ID for the store.
// You can't assign product IDs manually by doing len(products) + 1 because if
// (non-last) products are deleted, their IDs could be reused and cause
// conflicts.
func (s *Store) nextProductID() int {
	if len(s.Products) == 0 {
		return s.StoreID*1000 + 1
	}
	// Find empty slots
	usedIDs := make(map[int]bool)
	for _, product := range s.Products {
		usedIDs[product.ProductID] = true
	}
	for i := 1; i <= len(s.Products)+1; i++ {
		candidateID := s.StoreID*1000 + i
		if !usedIDs[candidateID] {
			return candidateID
		}
	}
	// Should not reach here
	return s.StoreID*1000 + len(s.Products) + 1
}

type Product struct {
	ProductID int `json:"product_id"`
	// The ID of the store that sells this product.
	// In theory, we could get the store ID by floor(productID / 1000),
	// but let's store it explicitly for clarity.
	StoreID int     `json:"store_id"`
	Name    string  `json:"name"`
	Price   float64 `json:"price"`
}

type Order struct {
	OrderID int `json:"order_id"`
	// The ID of the student who made the order.
	// Not a foreign key to anything.
	StudentID int `json:"student_id"`
	// The ID of the store from which the order was made.
	// Used to look up product prices.
	StoreID    int     `json:"store_id"`
	ProductID  int     `json:"product_id"`
	TotalPrice float64 `json:"total_price"`
	Paid       bool    `json:"paid"`
	Done       bool    `json:"done"`
}

// CreateProductRequest is used when adding a new product to a store.
// It lacks fields that are set by the server.
type CreateProductRequest struct {
	StoreID int     `json:"store_id"`
	Name    string  `json:"name"`
	Price   float64 `json:"price"`
}

// CreateOrderRequest is used when creating a new order.
// It lacks fields that are set by the server.
type CreateOrderRequest struct {
	StudentID int `json:"student_id"`
	StoreID   int `json:"store_id"`
	ProductID int `json:"product_id"`
}

func (cor *CreateOrderRequest) toOrder(order *Order, orderID int) {
	order.StudentID = cor.StudentID
	order.StoreID = cor.StoreID
	order.ProductID = cor.ProductID

	order.OrderID = orderID
	order.TotalPrice = 0.0
	order.Paid = false
	order.Done = false
}

// UpdateOrderRequest is used to update an existing order.
// Only the fields that are not null will be updated.
type UpdateOrderRequest struct {
	OrderID int   `json:"order_id"`
	Paid    *bool `json:"paid,omitempty"`
	Done    *bool `json:"done,omitempty"`
}

func (uor *UpdateOrderRequest) applyToOrder(order *Order) {
	if uor.Paid != nil {
		order.Paid = *uor.Paid
	}
	if uor.Done != nil {
		order.Done = *uor.Done
	}
}

// --- State ------------------------------

var stores []Store

// Flat list of all products across all stores, for faster querying.
var products []Product

var orders []Order

func initialize() {
	// Init db
	db, err := sql.Open("sqlite3", "./data.sqlite")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create tables if not exist
	_, err = db.Exec(`
	CREATE TABLE IF NOT EXISTS stores (
		store_id INTEGER PRIMARY KEY,
		name     TEXT NOT NULL,
		products TEXT NOT NULL
	);
	CREATE TABLE IF NOT EXISTS products (
		product_id INTEGER PRIMARY KEY,
		store_id   INTEGER NOT NULL,
		name       TEXT    NOT NULL,
		price      REAL    NOT NULL,
		FOREIGN KEY (store_id) REFERENCES stores(store_id)
	);
	CREATE TABLE IF NOT EXISTS orders (
		order_id    INTEGER PRIMARY KEY,
		student_id  INTEGER NOT NULL,
		store_id    INTEGER NOT NULL,
		product_id  INTEGER NOT NULL,
		total_price REAL    NOT NULL,
		paid        INTEGER NOT NULL,
		done        INTEGER NOT NULL,
		FOREIGN KEY (store_id) REFERENCES stores(store_id)
	);
	`)

	if err != nil {
		panic(err)
	}

	rows, err := db.Query("SELECT store_id, name, products FROM stores")
	if err != nil {
		panic(err)
	}
	defer rows.Close()
	for rows.Next() {
		var store Store
		var productsJSON string
		err := rows.Scan(&store.StoreID, &store.Name, &productsJSON)
		if err != nil {
			panic(err)
		}
		err = json.Unmarshal([]byte(productsJSON), &store.Products)
		if err != nil {
			panic(err)
		}
		stores = append(stores, store)
	}

	rows, err = db.Query("SELECT order_id, student_id, store_id, product_id, total_price, paid, done FROM orders")
	if err != nil {
		panic(err)
	}
	defer rows.Close()
	for rows.Next() {
		var order Order
		var paidInt, doneInt int
		err := rows.Scan(&order.OrderID, &order.StudentID, &order.StoreID, &order.ProductID, &order.TotalPrice, &paidInt, &doneInt)
		if err != nil {
			panic(err)
		}
		order.Paid = paidInt != 0
		order.Done = doneInt != 0
		orders = append(orders, order)
	}

	rows, err = db.Query("SELECT product_id, name, price FROM products")
	if err != nil {
		panic(err)
	}
	defer rows.Close()
	for rows.Next() {
		var product Product
		err := rows.Scan(&product.ProductID, &product.Name, &product.Price)
		if err != nil {
			panic(err)
		}
		products = append(products, product)
	}
}

func persist() {
	db, err := sql.Open("sqlite3", "./data.sqlite")
	if err != nil {
		panic(err)
	}
	defer db.Close()
	for _, store := range stores {
		productsJSON, err := json.Marshal(store.Products)
		if err != nil {
			panic(err)
		}
		_, err = db.Exec("REPLACE INTO stores (store_id, name, products) VALUES (?, ?, ?)", store.StoreID, store.Name, string(productsJSON))
		if err != nil {
			panic(err)
		}
	}

	for _, product := range products {
		_, err = db.Exec("REPLACE INTO products (product_id, store_id, name, price) VALUES (?, ?, ?, ?)", product.ProductID, product.StoreID, product.Name, product.Price)
		if err != nil {
			panic(err)
		}
	}

	for _, order := range orders {
		paidInt := 0
		if order.Paid {
			paidInt = 1
		}
		doneInt := 0
		if order.Done {
			doneInt = 1
		}

		_, err = db.Exec(
			"REPLACE INTO orders (order_id, student_id, store_id, product_id, total_price, paid, done) VALUES (?, ?, ?, ?, ?, ?, ?)",
			order.OrderID, order.StudentID, order.StoreID, order.ProductID, order.TotalPrice, paidInt, doneInt,
		)
		if err != nil {
			panic(err)
		}
	}
	db.Close()
}

func storeGetProducts(storeID int) (bool, []Product) {
	for _, store := range stores {
		if store.StoreID == storeID {
			return true, store.Products
		}
	}
	return false, []Product{}
}

func addOrder(order Order) {
	orders = append(orders, order)
	// TODO persist to db
}

// --- HTTP handlers ------------------------------

func jsonResponse(w http.ResponseWriter, status int, data any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)

	json, err := json.Marshal(data)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	w.Write(json)
}

func handleStoreCreate(w http.ResponseWriter, r *http.Request) {
	name := r.URL.Query().Get("name")
	if name == "" {
		jsonResponse(w, http.StatusBadRequest, "Missing store name")
		return
	}
	if len(stores) >= 1000 {
		jsonResponse(w, http.StatusBadRequest, "Store limit reached, have we reached that point?")
		return
	}
	newStore := Store{
		StoreID:  len(stores) + 1,
		Name:     name,
		Products: []Product{},
	}
	stores = append(stores, newStore)
	jsonResponse(w, http.StatusOK, map[string]any{
		"ok":       "true",
		"store_id": newStore.StoreID,
	})
}

// TODO add User type and check permissions
func handleStoreDelete(w http.ResponseWriter, r *http.Request) {
	storeIDStr := r.URL.Query().Get("store_id")
	storeID, err := strconv.Atoi(storeIDStr)
	if err != nil {
		jsonResponse(w, http.StatusBadRequest, "Invalid store_id")
		return
	}
	for i, store := range stores {
		if store.StoreID == storeID {
			// Remove store
			stores = append(stores[:i], stores[i+1:]...)
			jsonResponse(w, http.StatusOK, "bye")
			return
		}
	}
	jsonResponse(w, http.StatusBadRequest, "Store not found")
}

func handleStoreAddProduct(w http.ResponseWriter, r *http.Request) {
	var createProductRequest CreateProductRequest
	err := json.NewDecoder(r.Body).Decode(&createProductRequest)
	if err != nil {
		jsonResponse(w, http.StatusBadRequest, "Invalid product data")
		return
	}
	for i, store := range stores {
		if store.StoreID == createProductRequest.StoreID {
			newProduct := Product{
				ProductID: store.nextProductID(),
				StoreID:   createProductRequest.StoreID,
				Name:      createProductRequest.Name,
				Price:     createProductRequest.Price,
			}
			stores[i].Products = append(stores[i].Products, newProduct)
			products = append(products, newProduct)
			jsonResponse(w, http.StatusOK, map[string]any{
				"ok":         "true",
				"product_id": newProduct.ProductID,
			})
			return
		}
	}
	jsonResponse(w, http.StatusBadRequest, "Store not found")
}

func handleStoreRemoveProduct(w http.ResponseWriter, r *http.Request) {
	productIDStr := r.URL.Query().Get("product_id")
	productID, err := strconv.Atoi(productIDStr)
	if err != nil {
		jsonResponse(w, http.StatusBadRequest, "Invalid product_id")
		return
	}
	for i, store := range stores {
		for j, product := range store.Products {
			if product.ProductID == productID {
				// Remove product from store
				stores[i].Products = append(stores[i].Products[:j], stores[i].Products[j+1:]...)
				// Remove product from global list
				for k, p := range products {
					if p.ProductID == productID {
						products = append(products[:k], products[k+1:]...)
						break
					}
				}
				jsonResponse(w, http.StatusOK, map[string]any{
					"ok": "true",
				})
				return
			}
		}
	}
	jsonResponse(w, http.StatusBadRequest, "Product not found")
}

func handleGetStore(w http.ResponseWriter, r *http.Request) {
	storeIDStr := r.URL.Query().Get("store_id")
	storeID, err := strconv.Atoi(storeIDStr)
	if err != nil {
		jsonResponse(w, http.StatusBadRequest, "Invalid store_id")
		return
	}
	for _, store := range stores {
		if store.StoreID == storeID {
			jsonResponse(w, http.StatusOK, store)
			return
		}
	}
	jsonResponse(w, http.StatusBadRequest, "Store not found")
}

func handleGetProduct(w http.ResponseWriter, r *http.Request) {
	productIDStr := r.URL.Query().Get("product_id")
	productID, err := strconv.Atoi(productIDStr)
	if err != nil {
		jsonResponse(w, http.StatusBadRequest, "Invalid product_id")
		return
	}
	for _, store := range stores {
		for _, product := range store.Products {
			if product.ProductID == productID {
				jsonResponse(w, http.StatusOK, product)
				return
			}
		}
	}
	jsonResponse(w, http.StatusBadRequest, "Product not found")
}

func handleGetProductsFromStore(w http.ResponseWriter, r *http.Request) {
	storeIDStr := r.URL.Query().Get("store_id")
	storeID, err := strconv.Atoi(storeIDStr)
	if err != nil {
		http.Error(w, "Invalid store_id", http.StatusBadRequest)
		return
	}
	found, products := storeGetProducts(storeID)
	if !found {
		http.Error(w, "Store not found", http.StatusNotFound)
		return
	}
	jsonResponse(w, http.StatusOK, products)
}

func handleAddOrder(w http.ResponseWriter, r *http.Request) {
	var createOrderRequest CreateOrderRequest
	err := json.NewDecoder(r.Body).Decode(&createOrderRequest)
	if err != nil {
		http.Error(w, "Invalid order data", http.StatusBadRequest)
		return
	}
	var order Order
	createOrderRequest.toOrder(&order, len(orders)+1)

	// Calculate total price
	found, products := storeGetProducts(order.StoreID)
	if !found {
		http.Error(w, "Store not found", http.StatusNotFound)
		return
	}

	priceFound := false
	for _, product := range products {
		if product.ProductID == order.ProductID {
			order.TotalPrice = product.Price
			priceFound = true
			break
		}
	}
	if !priceFound {
		http.Error(w, "Product not found in store", http.StatusNotFound)
		return
	}

	addOrder(order)
	jsonResponse(w, http.StatusOK, map[string]any{
		"id": order.OrderID,
	})
}

func handleUpdateOrder(w http.ResponseWriter, r *http.Request) {
	var updateReq UpdateOrderRequest
	err := json.NewDecoder(r.Body).Decode(&updateReq)
	if err != nil {
		http.Error(w, "Invalid update data", http.StatusBadRequest)
		return
	}
	for i, order := range orders {
		if order.OrderID == updateReq.OrderID {
			updateReq.applyToOrder(&orders[i])
			jsonResponse(w, http.StatusOK, map[string]any{
				"ok": "true",
			})
			return
		}
	}
	http.Error(w, "Order not found", http.StatusNotFound)
}

func handleGetOrder(w http.ResponseWriter, r *http.Request) {
	orderIDStr := r.URL.Query().Get("order_id")
	orderID, err := strconv.Atoi(orderIDStr)
	if err != nil {
		http.Error(w, "Invalid order_id", http.StatusBadRequest)
		return
	}
	for _, order := range orders {
		if order.OrderID == orderID {
			jsonResponse(w, http.StatusOK, order)
			return
		}
	}
	http.Error(w, "Order not found", http.StatusNotFound)
}

func handleGetOrdersForStore(w http.ResponseWriter, r *http.Request) {
	storeIDStr := r.URL.Query().Get("store_id")
	storeID, err := strconv.Atoi(storeIDStr)
	if err != nil {
		http.Error(w, "Invalid store_id", http.StatusBadRequest)
		return
	}
	var storeOrders []Order
	for _, order := range orders {
		if order.StoreID == storeID {
			storeOrders = append(storeOrders, order)
		}
	}
	jsonResponse(w, http.StatusOK, storeOrders)
}

func handleGetOrdersForStudent(w http.ResponseWriter, r *http.Request) {
	studentIDStr := r.URL.Query().Get("student_id")
	studentID, err := strconv.Atoi(studentIDStr)
	if err != nil {
		http.Error(w, "Invalid student_id", http.StatusBadRequest)
		return
	}
	var studentOrders []Order
	for _, order := range orders {
		if order.StudentID == studentID {
			studentOrders = append(studentOrders, order)
		}
	}
	jsonResponse(w, http.StatusOK, studentOrders)
}

func middleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		log.Printf("%s %s\n", r.Method, r.URL.Path)
		next.ServeHTTP(w, r)
	})
}

func main() {
	initialize()

	// capture ctrl+c to persist data
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt)
	go func() {
		<-c
		persist()
		log.Println("bye")
		os.Exit(0)
	}()

	log.Println("hello")
	router := mux.NewRouter()

	router.HandleFunc("/store", handleGetStore).Methods("GET")
	router.HandleFunc("/store/create", handleStoreCreate).Methods("POST")
	router.HandleFunc("/store/delete", handleStoreDelete)
	router.HandleFunc("/store/product", handleGetProductsFromStore)
	router.HandleFunc("/store/product/add", handleStoreAddProduct)
	router.HandleFunc("/store/product/remove", handleStoreRemoveProduct)
	router.HandleFunc("/store/orders", handleGetOrdersForStore)

	router.HandleFunc("/product", handleGetProduct)

	router.HandleFunc("/orders/", handleGetOrder)
	router.HandleFunc("/orders/add", handleAddOrder)
	router.HandleFunc("/orders/update", handleUpdateOrder)
	router.HandleFunc("/orders/student", handleGetOrdersForStudent)

	loggedRouter := middleware(router)
	http.ListenAndServe(":8080", loggedRouter)
}
