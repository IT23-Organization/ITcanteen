import { Elysia } from "elysia"

const app = new Elysia()
  .get("/", () => "Hello Elysia")
  .listen(3000)

console.log("Server running at http://localhost:3000")
