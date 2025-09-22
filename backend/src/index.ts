import { Elysia, t } from "elysia"
import { cors } from "@elysiajs/cors"

const state = {
  count: 0
}

const app = new Elysia()
  .use(cors())
  .ws("/count", {
    open(ws) {
      ws.subscribe("count")
    },
    message(ws, msg) {
      if (typeof msg === "string" && msg === "get") {
        ws.publish("count", state.count)
      }
    }
  })
  .post("/api/count/incr", ({ body }) => {
    state.count += body.by
    app.server?.publish("count", `${state.count}`)
    return state.count
  }, {
    body: t.Object({
      by: t.Number()
    })
  })
  .listen(3000)

console.log("Server running at http://localhost:3000")
export type App = typeof app
