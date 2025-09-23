import { Database } from "bun:sqlite"
import { Seller, Product, Order } from "./types"
import * as log from "./log"

export class State {
    db: Database
    /// In-memory cache of orders for reads
    cache: {
        sellers:  Seller[],
        products: Product[],
        orders:   Order[],
    }
    // How many writes until we replicate the in-memory cache to the database
    #writeAmountInterval = 5
    #writeCount = 0

    constructor(db_path: string) {
        this.db = new Database(db_path)

        this.db.run(`
            CREATE TABLE IF NOT EXISTS sellers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name     TEXT
                password TEXT
                products TEXT
            )`)

        this.db.run(`
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_id   INTEGER,
                name        TEXT,
                description TEXT,
                price       REAL,
                available   INTEGER
            )`)

        this.db.run(`
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_id  INTEGER,
                product_id INTEGER,
                user       TEXT,
                quantity   INTEGER,
                price      REAL,
                status     TEXT,
                paid       INTEGER,
                created_at TEXT,
                updated_at TEXT,
                note       TEXT
            )`)

        this.cache = {
            sellers: this.db
                .query("SELECT * FROM sellers")
                .all() as Seller[],
            products: this.db
                .query("SELECT * FROM products")
                .all() as Product[],
            orders: this.db
                .query("SELECT * FROM orders")
                .all() as Order[],
        }
    }

    cleanup() {
        this.replicateCacheToDB()
        this.db.close()
    }

    // ------------------------------------------------------------
    // Order related methods
    // ------------------------------------------------------------

    didWrite() {
        this.#writeCount += 1
        if (this.#writeCount >= this.#writeAmountInterval) {
            this.replicateCacheToDB()
        }
    }

    placeOrder(order: Omit<Order, "id" | "created_at" | "updated_at" | "status" | "paid">): number {
        const new_order: Order = {
            ...order,
            id: this.cache.orders.length + 1,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            status: "pending",
            paid: false,
        }
        this.cache.orders.push(new_order)
        log.info(`New order placed from user ${new_order.user} for product ${new_order.product_id} (order id: ${new_order.id})`)
        this.didWrite()
        return new_order.id
    }

    getOrdersForUser(user: string): Order[] {
        return this.cache.orders.filter(o => o.user === user)
    }

    getOrdersForSeller(seller_id: number, only_pending: boolean): Order[] {
        return this.cache.orders
            .filter(o => o.seller_id === seller_id
                && (!only_pending || o.status === "pending"))
    }

    updateOrder(order_id: number, status?: "pending" | "completed" | "canceled", paid?: boolean): boolean {
        const order = this.cache.orders.find(o => o.id === order_id)
        if (!order) {
            return false
        }
        if (status) {
            order.status = status
        }
        if (paid !== undefined) {
            order.paid = paid
        }
        order.updated_at = new Date().toISOString()
        this.didWrite()
        return true
    }

    replicateCacheToDB() {
        log.info("Replicating in-memory cache to database...")
        const tx = this.db.transaction(() => {
            this.db.run("DELETE FROM sellers")
            this.db.run("DELETE FROM products")
            this.db.run("DELETE FROM orders")
            for (const seller of this.cache.sellers) {
                this.db.run(`
                    INSERT INTO sellers (id, name)
                    VALUES (?, ?)
                `, [seller.id, seller.name])
            }
            for (const product of this.cache.products) {
                this.db.run(`
                    INSERT INTO products (id, seller_id, name, description, price, available)
                    VALUES (?, ?, ?, ?, ?, ?)
                `, [
                    product.id,
                    product.seller_id,
                    product.name,
                    product.description,
                    product.price,
                    product.available ? 1 : 0
                ])
            }
            for (const order of this.cache.orders) {
                this.db.run(`
                    INSERT INTO orders (id, seller_id, product_id, user, quantity, price, status, paid, created_at, updated_at, note)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                `, [
                    order.id,
                    order.seller_id,
                    order.product_id,
                    order.user,
                    order.quantity,
                    order.price,
                    order.status,
                    order.paid ? 1 : 0,
                    order.created_at,
                    order.updated_at,
                    order.note
                ])
            }
        })
        tx()
        log.info("Replication complete.")
    }

    // ------------------------------------------------------------
    // User(Seller) related methods
    // ------------------------------------------------------------

    createUser(username: string, password_hash: string): string | true {
        if (this.cache.sellers.find(u => u.name === username)) {
            return "User already exists"
        }

        const new_user: Seller = {
            id: this.cache.sellers.length + 1,
            name: username,
            password: password_hash,
            products: [],
        }
        this.cache.sellers.push(new_user)
        // Immediate replication for user creation
        this.replicateCacheToDB()
        return true
    }
}