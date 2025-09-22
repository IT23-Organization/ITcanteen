import { useEffect, useState } from "react"

const incrementCount = async (by: number) => {
  await fetch("http://localhost:3000/api/count/incr", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ by })
  })
}

function Main() {
  const [count, setCount] = useState(0)
  const [incrementBy, setIncrementBy] = useState(1)

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:3000/count")

    ws.onopen = () => {
      ws.send("get")
    }

    ws.onmessage = (event) => {
      console.log("Message from server:", event.data)
      setCount(Number(event.data))
    }
  }, [])

  return (
    <>
      <div className="h-screen flex flex-col items-center justify-center">
        <input
          type="number"
          value={incrementBy}
          onChange={(e) => setIncrementBy(Number(e.target.value))}
          className="mb-4 px-2 py-1 border border-gray-300 rounded"
        />
        <button
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          onClick={() => incrementCount(incrementBy)}
        >
          Count is {count ?? "Loading..."}
        </button>
      </div>
    </>
  )
}

export default Main
