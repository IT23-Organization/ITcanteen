"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";


type Summary = {
  today: {
    total: number;
    orders: number;
  };
  week: {
    total: number;
    orders: number;
  };
  month: {
    total: number;
    orders: number;
  };
};

export default function TotalPage() {
  // mock data
  const [summary, setSummary] = useState<Summary>({
    today: { total: 2304, orders: 99 },
    week: { total: 15000, orders: 450 },
    month: { total: 60000, orders: 1800 },
  });

  // 👉 api ครับเอยยยยยยยย
  useEffect(() => {
    // fetch("/api/summary")
    //   .then((res) => res.json())
    //   .then((data) => setSummary(data));
  }, []);

  return (
    <div className="mt-6 sm:mt-8 px-4 sm:px-6 md:px-8">
      {/* Tabs */}
      <div className="flex gap-6 sm:gap-12 md:gap-16 font-medium overflow-x-auto pb-2">
        <Link href='/main' className="cursor-pointer text-2xl sm:text-3xl md:text-4xl lg:text-5xl text-[#A3A3A3] shrink-0">
          ORDER
        </Link>
        <Link href='/history' className="cursor-pointer text-2xl sm:text-3xl md:text-4xl lg:text-5xl text-[#A3A3A3] shrink-0">
          HISTORY
        </Link>
        <Link href='/total' className="cursor-pointer text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold shrink-0">
          TOTAL
        </Link>
      </div>

      {/* Summary Cards */}
      <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Today */}
        <div className="bg-[#1BB98D] text-white rounded-2xl shadow-lg p-6 flex flex-col justify-between">
          <h2 className="text-lg font-bold">TODAY TOTAL</h2>
          <p className="text-3xl sm:text-4xl font-extrabold mt-3">
            {summary.today.total.toLocaleString()} ฿
          </p>
          <span className="text-sm mt-2 opacity-80">
            {summary.today.orders} ORDERS
          </span>

        </div>

        {/* Week */}
        <div className="bg-[#D74343] text-white rounded-2xl shadow-lg p-6 flex flex-col justify-between">
          <h2 className="text-lg font-bold">WEEK TOTAL</h2>
          <p className="text-3xl sm:text-4xl font-extrabold mt-3">
            {summary.week.total.toLocaleString()} ฿
          </p>
          <span className="text-sm mt-2 opacity-80">
            {summary.week.orders} ORDERS
          </span>
        </div>

        {/* Month */}
        <div className="bg-[#E9801D] text-white rounded-2xl shadow-lg p-6 flex flex-col justify-between">
          <h2 className="text-lg font-bold">MONTH TOTAL</h2>
          <p className="text-3xl sm:text-4xl font-extrabold mt-3">
            {summary.month.total.toLocaleString()} ฿
          </p>
          <span className="text-sm mt-2 opacity-80">
            {summary.month.orders} ORDERS
          </span>
        </div>
      </div>
    </div>
  );
}
