import { Elysia, t } from "elysia"
import { cors }      from "@elysiajs/cors"
import { openapi }   from '@elysiajs/openapi'

import { State } from "./state"
import * as log  from "./log"
import { orderPlugin } from "./routes/order"

const port = process.env.PORT || 3000
const db_path = process.env.DB_PATH || "data.db"

/// Global application state
export const state = new State(db_path)

const app = new Elysia()
  .use(cors())
  .use(openapi({
    documentation: {
      tags: [
        { name: "Order",  description: "Order related endpoints"               },
        { name: "User",   description: "Endpoints that will be used by user"   },
        { name: "Seller", description: "Endpoints that will be used by seller" },
      ]
    },
    path: "/docs",
  }))
  .onError(({ error, set }) => {
    if (error instanceof Error) {
      log.error(error.message)
      set.status = 500
      return { message: `Internal Server Error: ${error.message}` }
    }
  })
  .use(orderPlugin)
  .listen(port)

log.info(`Server running at http://localhost:${port}`)

// Cleanup on exit
process.on("SIGINT", () => {
  log.info("Shutting down server...")
  state.cleanup()
  app.stop().then(() => {
    log.info("Server stopped.")
    process.exit(0)
  })
})

export type App = typeof app
