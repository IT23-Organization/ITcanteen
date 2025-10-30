package main

import (
	"encoding/json"
	"fmt"
	"log"
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
	OrderID    int     `json:"order_id"`
	StudentID  int     `json:"student_id"`
	StoreID    int     `json:"store_id"`
	ProductIDs []int   `json:"product_ids"`
	TotalPrice float64 `json:"total_price"`
	Paid       bool    `json:"paid"`
	Done       bool    `json:"done"`
}

type PartialOrder struct {
	StudentID  int   `json:"student_id"`
	StoreID    int   `json:"store_id"`
	ProductIDs []int `json:"product_ids"`
}

func (po *PartialOrder) toOrder(order *Order, orderID int) {
	order.StudentID = po.StudentID
	order.StoreID = po.StoreID
	order.ProductIDs = po.ProductIDs

	order.OrderID = orderID
	order.TotalPrice = 0.0
	order.Paid = false
	order.Done = false
}

// --- State ------------------------------

var stores []Store
var orders []Order

func init() {
	stores = []Store{
		{
			StoreID: 1,
			Name:    "Foo Store",
			Products: []Product{
				{ProductID: 1, Name: "Apple", Price: 1.00},
				{ProductID: 2, Name: "Banana", Price: 1.50},
			},
		},
		{
			StoreID: 2,
			Name:    "Bar Store",
			Products: []Product{
				{ProductID: 3, Name: "Orange", Price: 1.50},
				{ProductID: 4, Name: "Grapes", Price: 2.00},
			},
		},
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

func updateOrder(order Order) bool {
	for i, o := range orders {
		if o.OrderID == order.OrderID {
			orders[i] = order
			// TODO persist to db
			return true
		} else {
			fmt.Println("Updating order failed: Order not found")
		}
	}
	return false
}

// --- HTTP handlers ------------------------------

func jsonResponse(w http.ResponseWriter, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(data)
}

func handleGetProducts(w http.ResponseWriter, r *http.Request) {
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
	jsonResponse(w, products)
}

func handleAddOrder(w http.ResponseWriter, r *http.Request) {
	var partialOrder PartialOrder
	err := json.NewDecoder(r.Body).Decode(&partialOrder)
	if err != nil {
		http.Error(w, "Invalid order data", http.StatusBadRequest)
		return
	}
	var order Order
	partialOrder.toOrder(&order, len(orders)+1)
	addOrder(order)
	jsonResponse(w, map[string]string{
		"ok": "true",
		"id": strconv.Itoa(order.OrderID),
	})
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
			jsonResponse(w, order)
			return
		}
	}
	http.Error(w, "Order not found", http.StatusNotFound)
}

func main() {
	log.Println("hello")
	http.HandleFunc("/store/products", handleGetProducts)
	http.HandleFunc("/orders/", handleGetOrder)
	http.HandleFunc("/orders/add", handleAddOrder)
	http.ListenAndServe(":8080", nil)
}
