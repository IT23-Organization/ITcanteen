package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
)

// --- Types ------------------------------

type Product struct {
	ProductID int     `json:"product_id"`
	Name      string  `json:"name"`
	Price     float64 `json:"price"`
}

type Store struct {
	StoreID  int       `json:"store_id"`
	Name     string    `json:"name"`
	Products []Product `json:"products"`
}

type Order struct {
	OrderID int `json:"order_id"`
	// The ID of the student who made the order.
	StudentID int `json:"student_id"`
	// The ID of the store from which the order was made.
	// Used to look up product prices.
	StoreID int `json:"store_id"`
	// List of product IDs in the order.
	ProductIDs []int   `json:"product_ids"`
	TotalPrice float64 `json:"total_price"`
	Paid       bool    `json:"paid"`
	Done       bool    `json:"done"`
}

// CreateOrderRequest is used when creating a new order.
// It lacks fields that are set by the server.
type CreateOrderRequest struct {
	StudentID  int   `json:"student_id"`
	StoreID    int   `json:"store_id"`
	ProductIDs []int `json:"product_ids"`
}

func (cor *CreateOrderRequest) toOrder(order *Order, orderID int) {
	order.StudentID = cor.StudentID
	order.StoreID = cor.StoreID
	order.ProductIDs = cor.ProductIDs

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

func init() {
	stores = []Store{
		{
			StoreID: 1,
			Name:    "Foo Store",
			Products: []Product{
				{ProductID: 101, Name: "Apple", Price: 1.00},
				{ProductID: 102, Name: "Banana", Price: 1.50},
			},
		},
		{
			StoreID: 2,
			Name:    "Bar Store",
			Products: []Product{
				{ProductID: 201, Name: "Orange", Price: 1.50},
				{ProductID: 202, Name: "Grapes", Price: 2.00},
			},
		},
	}
	products = []Product{}
	for _, store := range stores {
		products = append(products, store.Products...)
	}
	orders = []Order{}
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

// Returns an ok response with a given map of data.
func okResponse(w http.ResponseWriter, data map[string]any) {
	w.Header().Set("Content-Type", "application/json")
	response := map[string]interface{}{
		"ok": "true",
	}
	for k, v := range data {
		response[k] = v
	}
	json.NewEncoder(w).Encode(response)
}

// Returns an (flattened) ok response with a given data object.
func okResponseWith(w http.ResponseWriter, data any) {
	w.Header().Set("Content-Type", "application/json")

	raw, err := json.Marshal(data)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	var obj map[string]interface{}
	err = json.Unmarshal(raw, &obj)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	obj["ok"] = "true"

	final, err := json.Marshal(obj)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	w.Write(final)
}

func invalidRequestResponse(w http.ResponseWriter, message string) {
	w.Header().Set("Content-Type", "application/json")
	response := map[string]string{
		"ok":    "false",
		"error": message,
	}
	json.NewEncoder(w).Encode(response)
}

func handleGetProduct(w http.ResponseWriter, r *http.Request) {
	productIDStr := r.URL.Query().Get("product_id")
	productID, err := strconv.Atoi(productIDStr)
	if err != nil {
		invalidRequestResponse(w, "Invalid product_id")
		return
	}
	for _, store := range stores {
		for _, product := range store.Products {
			if product.ProductID == productID {
				okResponseWith(w, product)
				return
			}
		}
	}
	invalidRequestResponse(w, "Product not found")
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
	okResponseWith(w, products)
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

	// Calculate total price
	for _, productID := range order.ProductIDs {
		for _, product := range products {
			if product.ProductID == productID {
				order.TotalPrice += product.Price
			}
		}
	}

	addOrder(order)
	okResponse(w, map[string]any{
		"ok": "true",
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
			okResponse(w, map[string]any{})
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
			okResponseWith(w, order)
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
	okResponseWith(w, storeOrders)
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
	okResponseWith(w, studentOrders)
}

func main() {
	fmt.Println("hello")
	http.HandleFunc("/product", handleGetProduct)

	http.HandleFunc("/store/products", handleGetProductsFromStore)
	http.HandleFunc("/store/orders", handleGetOrdersForStore)

	http.HandleFunc("/orders/", handleGetOrder)
	http.HandleFunc("/orders/add", handleAddOrder)
	http.HandleFunc("/orders/update", handleUpdateOrder)
	http.HandleFunc("/orders/student", handleGetOrdersForStudent)

	http.ListenAndServe(":8080", nil)
}
