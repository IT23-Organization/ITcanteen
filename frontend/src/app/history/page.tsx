"use client";

import React, { useState } from "react";
import { FaCheckCircle, FaTimesCircle } from "react-icons/fa";
import Link from "next/link";

import { OrderDisplay } from "../lib/types";

const historyOrders: OrderDisplay[] = [];

const fetchOrders = async () => {
  try {
    const response = await fetch("http://localhost:8080/store/orders?store_id=1");
    const data = await response.json()
        .then((res: any[]) => res.filter((order) => order.paid || order.done));

    // fetch each order's product name
    const ordersDisplay: OrderDisplay[] = [];
    for (const order of data) {
      const productResponse = await fetch(`http://localhost:8080/product?product_id=${order.product_id}`);
      const productData = await productResponse.json();
      ordersDisplay.push({
        order_id: order.order_id,
        student_id: order.student_id,
        product_name: productData.name,
        total_price: order.total_price,
        paid: order.paid,
        done: order.done,
      });
    }

    return ordersDisplay;
  } catch (error) {
    console.error("Error fetching orders:", error);
    return [];
  }
};

export default function HistoryPage() {
  const [page, setPage] = useState(0);
  const ordersPerPage = 4;

  const totalPages = Math.ceil(historyOrders.length / ordersPerPage);
  const startIndex = page * ordersPerPage;
  const [currentOrders, setCurrentOrders] = useState<OrderDisplay[]>([]);

  React.useEffect(() => {
    const loadOrders = async () => {
      const orders = await fetchOrders();
      setCurrentOrders(orders.slice(startIndex, startIndex + ordersPerPage));
    };
    loadOrders();
  }, [page, startIndex]);

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
          {currentOrders.map((order, i) => (
            <div
              key={i}
              className="bg-white w-full rounded-3xl p-4 md:p-5 shadow-xl flex flex-col justify-between"
            >
              <div>
                <h3 className="text-lg font-semibold mb-2">
                  {order.product_name}
                </h3>
                <p className="text-gray-800 mb-1">
                  รหัสนักศึกษา: {order.student_id}
                </p>
                <p className="text-gray-800 mb-1">
                  ราคาทั้งหมด: {order.total_price} บาท
                </p>
              </div>
              <div className="mt-4">
                {order.done ? (
                  <div className="flex items-center text-green-600">
                    <FaCheckCircle className="mr-2" />
                    <span>เสร็จแล้ว</span>
                  </div>
                ) : (
                  <div className="flex items-center text-red-600">
                    <FaTimesCircle className="mr-2" />
                    <span>ยกเลิกออเดอร์</span>
                  </div>
                )}
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
