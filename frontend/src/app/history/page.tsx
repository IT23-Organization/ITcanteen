"use client";

import React, { useState } from "react";
import { FaCheckCircle, FaTimesCircle } from "react-icons/fa";
import Link from "next/link";
type HistoryOrder = {
  id: string;
  img: string;
  menu: string;
  user: string;
  time: string;
  note: string;
  price: string;
  status: "accepted" | "declined";
  finishedAt: string; // เวลาเสร็จสิ้น
};

const historyOrders: HistoryOrder[] = [
  {
    id: "#A001",
    img: "./assets/Mama_instant_noodle_block.jpg",
    menu: "NOOOOODEL",
    user: "68070070",
    time: "10:00 PM",
    note: "lorem20 kfknsnkgns",
    price: "50฿",
    status: "accepted",
    finishedAt: "10:26 PM",
  },
  {
    id: "#A002",
    img: "./assets/ChatGPT Image 13 ส.ค. 2568 21_21_57.png",
    menu: "NOOOOOODEL",
    user: "68070071",
    time: "10:00 PM",
    note: "lorem20 kfknsnkgns",
    price: "50฿",
    status: "declined",
    finishedAt: "10:30 PM",
  },
  // เพิ่มออเดอร์ได้เรื่อย ๆ
];

export default function HistoryPage() {
  const [page, setPage] = useState(0);
  const ordersPerPage = 4;

  const totalPages = Math.ceil(historyOrders.length / ordersPerPage);
  const startIndex = page * ordersPerPage;
  const currentOrders = historyOrders.slice(startIndex, startIndex + ordersPerPage);

  return (
    <div className="mt-6 sm:mt-8">
      {/* Tabs */}
      <div className="flex gap-6 sm:gap-12 md:gap-16 pl-4 sm:pl-6 md:pl-8 font-medium overflow-x-auto pb-2">
        <Link href='/' className="cursor-pointer text-2xl sm:text-3xl md:text-4xl lg:text-5xl text-[#A3A3A3] shrink-0">
          ORDER
        </Link>
        <Link href='/history' className="cursor-pointer text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold shrink-0">
          HISTORY
        </Link>
        <Link href='/total' className="cursor-pointer text-2xl sm:text-3xl md:text-4xl lg:text-5xl text-[#A3A3A3] shrink-0">
          TOTAL
        </Link>
      </div>

      {/* ถ้าไม่มีประวัติ */}
      {currentOrders.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20">
          <img
            src="/assets/empty-box.png"
            alt="No history"
            className="w-40 h-40 opacity-70 mb-6"
          />
          <h2 className="text-2xl font-bold text-[#12314D]">ยังไม่มีประวัติ</h2>
          <p className="text-gray-500 mt-2">ยังไม่เคยมีการรับ/ยกเลิกออเดอร์</p>
        </div>
      ) : (
        <div className="mt-6 sm:mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 sm:gap-8 px-4 sm:px-6 md:px-8">
          {currentOrders.map((order) => (
            <div
              key={order.id}
              className="bg-white w-full rounded-3xl p-4 md:p-5 shadow-xl flex flex-col justify-between"
            >
              <h1 className="text-2xl sm:text-3xl font-extrabold text-center mb-3 text-[#12314D] leading-tight">
                {order.id}
              </h1>

              {/* รูป + overlay + status icon */}
              <div className="relative">
                <img
                  src={order.img}
                  className="rounded-2xl w-full aspect-square object-cover brightness-20"
                  alt={order.menu}
                />
                {order.status === "accepted" ? (
                  <FaCheckCircle className="absolute inset-0 m-auto text-green-500 w-16 h-16 drop-shadow-lg" />
                ) : (
                  <FaTimesCircle className="absolute inset-0 m-auto text-red-500 w-16 h-16 drop-shadow-lg" />
                )}
              </div>

              {/* รายละเอียด */}
              <div className="mt-4 font-bold text-base sm:text-lg leading-relaxed">
                MENU : {order.menu} <br />
                USER : {order.user} <br />
                TIME : {order.time} <br />
                NOTE : {order.note} <br />
                PRICE : {order.price}
              </div>

              {/* เวลา finish/cancel */}
              <div className="mt-4 text-right text-sm text-gray-500 font-semibold">
                {order.status === "accepted"
                  ? `FINISHED ${order.finishedAt}`
                  : `CANCELLED ${order.finishedAt}`}
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
