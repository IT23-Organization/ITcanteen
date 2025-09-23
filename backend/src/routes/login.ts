import { Elysia, t } from "elysia"
import { jwt } from "@elysiajs/jwt"
import { state } from "../main"
import * as log from "../log"

export const loginPlugin = new Elysia()
  .use(jwt({
      name: "jwt",
      secret: "iloveit23",
      exp: "7d"
  }))
  .group("/api/auth", app => app
    .post("/signup", async ({ body }) => {
      const password_hash = await Bun.password.hash(body.password, {
        algorithm: "argon2id",
      })

      const result = state.createUser(body.username, password_hash)
      if (result === true) {
        return { message: "User created successfully" }
      } else {
        return { message: result }
      }
    }, {
      tags: ["Auth"],
      body: t.Object({
        username: t.String(),
        password: t.String(),
      }),
      response: {
        200: t.Object({
          message: t.String(),
        })
      }
    })
    .post("/login", async ({ jwt, body, cookie: { auth } }) => {
      if (await jwt.verify(auth.value)) {
        return { message: "Already logged in" }
      }

      const user = state.cache.sellers.find(u => u.name === body.username)

      if (!user) {
        return { message: "Invalid username or password" }
      }

      const valid = await Bun.password.verify(body.password, user.password)
      .catch((e) => {
        if (e instanceof Error) {
          log.error(`Password verification error for ${body.username}: ${e.message}`)
        }
        return false
      })

      if (valid) {
        const token = await jwt.sign({ user: body.username })

        auth.set({
          value: token,
          httpOnly: true,
          maxAge: 7 * 24 * 60 * 60, // 7 days
          path: "/",
        })

        return { message: "Login successful", token }
      } else {
        return { message: "Invalid username or password" }
      }
    }, {
      tags: ["Auth"],
      body: t.Object({
        username: t.String(),
        password: t.String(),
      }),
      response: {
        200: t.Object({
          message: t.String(),
          token: t.Optional(t.String())
        })
      },
      cookie: t.Cookie({
        auth: t.Optional(t.String()),
      })
    })
  )