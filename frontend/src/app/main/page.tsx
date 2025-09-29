"use client";

import React, { useState } from "react";
import Link from "next/link";

type Order = {
  id: string;
  img: string;
  menu: string;
  user: string;
  time: string;
  note: string;
  price: number;
};

const orders: Order[] = [
  {
    id: "#A001",
    img: "./assets/Mama_instant_noodle_block.jpg",
    menu: "NOODLE",
    user: "68070070",
    time: "10:00 PM",
    note: "PI SED SAI JAI",
    price: 50,
  },
  {
    id: "#A002",
    img: "./assets/ChatGPT Image 13 ส.ค. 2568 21_21_57.png",
    menu: "NOODLE",
    user: "68070071",
    time: "10:10 PM",
    note: "EXTRA SPICY",
    price: 50,
  },
  {
    id: "#A003",
    img: "./assets/Mama_instant_noodle_block.jpg",
    menu: "NOODLE",
    user: "68070072",
    time: "10:20 PM",
    note: "NO VEGETABLE",
    price: 50,
  },
  {
    id: "#A004",
    img: "./assets/Mama_instant_noodle_block.jpg",
    menu: "NOODLE",
    user: "68070073",
    time: "10:30 PM",
    note: "ADD EGG",
    price: 50,
  },
  {
    id: "#A005",
    img: "./assets/Mama_instant_noodle_block.jpg",
    menu: "NOODLE",
    user: "68070074",
    time: "10:40 PM",
    note: "NO SOUP",
    price: 50,
  },
  // เพิ่ม orders ได้อีก
];

export default function Main() {
  const [page, setPage] = useState(0);
  const ordersPerPage = 4;

  const totalPages = Math.ceil(orders.length / ordersPerPage);
  const startIndex = page * ordersPerPage;
  const currentOrders = orders.slice(startIndex, startIndex + ordersPerPage);

  return (
    <div className="mt-6 sm:mt-8">
      {/* Tabs ORDER / HISTORY / TOTAL */}
      <div className="flex gap-6 sm:gap-12 md:gap-16 pl-4 sm:pl-6 md:pl-8 font-medium overflow-x-auto pb-2">
        <Link href='/'className="cursor-pointer text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold shrink-0">
          ORDER
        </Link>
        <Link href='/history' className="cursor-pointer text-2xl sm:text-3xl md:text-4xl lg:text-5xl text-[#A3A3A3] shrink-0">
          HISTORY
        </Link>
        <Link href='/total' className="cursor-pointer text-2xl sm:text-3xl md:text-4xl lg:text-5xl text-[#A3A3A3] shrink-0">
          TOTAL
        </Link>
      </div>

      {/* แสดง Orders ของหน้านี้ ถ้าไม่มีรายการสั่งเข้ามาจะเป็นหน้าเปล่านะ*/}
      {currentOrders.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20">
          <img
            src="/assets/empty-box.png"
            alt="No orders"
            className="w-40 h-40 opacity-70 mb-6"
          />
          <h2 className="text-2xl font-bold text-[#12314D]">
            ยังไม่มีรายการสั่งซื้อ
          </h2>
          <p className="text-gray-500 mt-2">รอออเดอร์ใหม่จากลูกค้า...</p>
        </div>
      ) : (
        <div className="mt-6 sm:mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 sm:gap-8 px-4 sm:px-6 md:px-8">
          {currentOrders.map((order) => (
            <div
              key={order.id}
              className="bg-white w-full rounded-3xl p-4 md:p-5 shadow-xl"
            >
              <h1 className="text-2xl sm:text-3xl font-extrabold text-center mb-3 text-[#12314D] leading-tight">
                {order.id}
              </h1>
              <img
                src={order.img}
                className="rounded-2xl w-full aspect-square object-cover"
                alt={order.menu}
              />
              <div className="mt-4 font-bold text-base sm:text-lg leading-relaxed">
                MENU : {order.menu} <br />
                USER : {order.user} <br />
                TIME : {order.time} <br />
                NOTE : {order.note} <br />
                PRICE : {order.price}฿
              </div>
              <div className="mt-5 flex flex-col sm:flex-row gap-3 sm:justify-between">
                <button className="bg-[#E3E3E3] px-4 py-3 rounded-xl font-bold shadow-2xl cursor-pointer">
                  DECLINE
                </button>
                <button className="bg-[#ED9133] px-4 py-3 rounded-xl font-bold shadow-2xl cursor-pointer text-white">
                  ACCEPT
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ปุ่มเปลี่ยนหน้า */}
      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-4 mt-6">
          <button
            disabled={page === 0}
            onClick={() => setPage((p) => p - 1)}
            className="px-4 py-2 bg-gray-500 rounded disabled:opacity-50 text-white"
          >
            Prev
          </button>
          <span className="text-black">
            Page {page + 1} of {totalPages}
          </span>
          <button
            disabled={page === totalPages - 1}
            onClick={() => setPage((p) => p + 1)}
            className="px-4 py-2 bg-blue-900 rounded disabled:opacity-50 text-white"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
