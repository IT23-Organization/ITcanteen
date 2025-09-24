"use client";

import React from "react";

export default function Footer() {
  return (
    <footer className="bg-[#2f3337] text-white mt-10">
      <div className="mx-auto max-w-screen-xl px-4 py-6 flex flex-col sm:flex-row justify-between items-center gap-4">
        {/* ซ้าย */}
        <p className="text-sm">&copy; {new Date().getFullYear()} NAME OF SHOP. All rights reserved.</p>

        {/* ขวา */}
        <div className="flex gap-4">
          <a href="#" className="hover:text-gray-300">
            Privacy Policy
          </a>
          <a href="#" className="hover:text-gray-300">
            Terms of Service
          </a>
        </div>
      </div>
    </footer>
  );
}
