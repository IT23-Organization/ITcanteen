/// A shop/seller providing products
export type Seller = {
    id:       number
    name:     string
    /// List of product IDs provided by this seller
    products: number[]
}

/// A product available for order for each seller
export type Product = {
    id:          number
    /// Reference to the seller ID providing this product
    seller_id:   number
    name:        string
    description: string
    price:       number
    available:   boolean
}

/// The order placed by a user
export type Order = {
    id:         number
    /// Reference to the seller from whom the order is placed
    seller_id:  number
    /// Reference to the product being ordered
    product_id: number
    /// The user ID who placed the order
    user:       string
    quantity:   number
    price:      number

    status:     "pending" | "completed" | "canceled"
    paid:       boolean
    created_at: string
    updated_at: string

    /// Optional note from the user about the order
    note:       string
}