import { Elysia, t } from "elysia"
import { jwt } from "@elysiajs/jwt"
import { state } from "../main"

export const orderPlugin = new Elysia()
  .use(jwt({
      name: "jwt",
      secret: "iloveit23",
      exp: "7d"
  }))
  .group("/api/order", app => app
    .get("/seller", async ({ query, jwt, cookie: { auth } }) => {
      if (!(await jwt.verify(auth.value))) {
        return {
          success: false,
          message: "Unauthorized"
        }
      }
      return {
        success: true,
        orders: state.getOrdersForSeller(
          query.seller_id,
          query.only_pending || true
        )
      }
    }, {
      tags: ["Orders"],
      detail: {
        description: "Get all orders for a specific seller"
      },
      query: t.Object({
        seller_id: t.Number({
          description: "The seller ID whose orders are to be fetched"
        }),
        only_pending: t.Optional(t.Boolean({
          description: "Whether to fetch only pending orders",
          default: true
        }))
      }),
      response: {
        200: t.Object({
          success: t.Boolean(),
          // TODO: Schema -> Typescript types
          orders: t.Array(t.Any())
        }),
        // Unauthorized
        401: t.Object({
          success: t.Boolean(),
          message: t.String(),
        })
      },
      cookie: t.Cookie({
        auth: t.String(),
      })
    })
    // Update order status (e.g., mark as completed or canceled)
    // to be used by seller
    .post("/seller/update", async ({ body, jwt, cookie: { auth } }) => {
      if (!(await jwt.verify(auth.value))) {
        return {
          success: false,
          message: "Unauthorized"
        }
      }

      // ? Maybe check if the order belongs to the seller?
      const success = state.updateOrder(
        body.order_id,
        body.status,
        body.paid
      )
      return { success }
    }, {
      tags: ["Orders"],
      detail: {
        description: "Update the status of a specific order"
      },
      body: t.Object({
        order_id: t.Number({
          description: "The ID of the order to be updated"
        }),
        status: t.Optional(t.UnionEnum(["pending", "completed", "canceled"])),
        paid:   t.Optional(t.Boolean())
      }),
      response: {
        200: t.Object({
          success: t.Boolean()
        }),
        401: t.Object({
          success: t.Boolean(),
          message: t.String(),
        })
      },
      cookie: t.Cookie({
        auth: t.String(),
      })
    })
    .get("/user", ({ query }) => {
      return {
        success: true,
        orders:  state.getOrdersForUser(query.user)
      }
    }, {
      tags: ["Orders"],
      detail: {
        description: "Get all orders placed by a specific user"
      },
      query: t.Object({
        user: t.String({
          description: "The user ID whose orders are to be fetched"
        })
      }),
      response: t.Object({
        success: t.Boolean(),
        // TODO: Schema -> Typescript types
        orders: t.Array(t.Any())
      })
    })
    .post("/user/place", ({ body }) => {
      const order_id = state.placeOrder({
        seller_id:  body.seller_id,
        product_id: body.product_id,
        user:       body.user,
        quantity:   body.quantity,
        price:      body.price,
        note:       body.note || ""
      })
      return {
        success: true,
        order_id
      }
    }, {
      tags: ["Orders"],
      detail: {
        description: "Place a new order",
      },
      body: t.Object({
        seller_id:  t.Number({
          description: "Reference to the seller from whom the order is placed"
        }),
        product_id: t.Number({
          description: "Reference to the product being ordered"
        }),
        user:       t.String({
          description: "The user ID who placed the order"
        }),
        quantity:   t.Number(),
        price:      t.Number(),
        note:       t.Optional(t.String({
          description: "Optional note from the user about the order"
        }))
      }),
      response: t.Object({
        success: t.Boolean(),
        order_id: t.Optional(t.Number())
      })
    })
)