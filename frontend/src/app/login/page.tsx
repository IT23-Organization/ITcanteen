"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const VALID_USER = "admin";
  const VALID_PASS = "123456";

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (username === VALID_USER && password === VALID_PASS) {
      router.push("/main");
    } else {
      setError("❌ Username หรือ Password ไม่ถูกต้อง");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F7F6F6]">
      <form
        onSubmit={handleLogin}
        className="bg-white shadow-xl rounded-xl p-8 w-full max-w-sm"
      >
        <h1 className="text-2xl font-bold text-center text-[#12314D] mb-6">
          Login
        </h1>

        <div className="mb-4">
          <label className="block mb-1 font-semibold text-gray-700">
            Username
          </label>
          <input
            type="text"
            className="w-full border rounded px-3 py-2"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="ใส่ Username"
            required
          />
        </div>

        <div className="mb-4">
          <label className="block mb-1 font-semibold text-gray-700">
            Password
          </label>
          <input
            type="password"
            className="w-full border rounded px-3 py-2"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="ใส่ Password"
            required
          />
        </div>

        {error && <p className="text-red-600 text-sm mb-3">{error}</p>}

        <button
          type="submit"
          className="w-full bg-[#12314D] text-white py-2 rounded-lg font-bold hover:bg-[#0f253a] transition"
        >
          เข้าสู่ระบบ
        </button>
      </form>
    </div>
  );
}
