"use client";

import { useState } from "react";
import { GiHamburgerMenu } from "react-icons/gi";
import { MdLogout } from "react-icons/md";

export default function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <nav className="bg-[#12314D] relative ">
      {/*จัด nav bar*/}
      <div className="mx-auto max-w-screen-xl h-16 flex items-center justify-start px-5 ">
        {/*ปุ่มแฮมเบออออออเกออออ*/}
        <button
          type="button"
          aria-label="Toggle menu"
          aria-expanded={open}
          aria-controls="extra-menu"
          onClick={() => setOpen(!open)}
          className="flex items-center justify-center"
        >
          <GiHamburgerMenu className="text-white w-8 h-8 sm:w-10 sm:h-10 md:w-12 md:h-14 ml-1" />
        </button>


        <h1 className="text-white font-bold text-xl sm:text-2xl md:text-3xl text-center flex-1">
          NAME OF SHOP
        </h1>


        <div className="w-8 sm:w-10 md:w-12" />
      </div>

      {/*ไว้เพิ่มเมนูตรงปุ่ม hamburgererererer*/}
      {open && (
        <div
          id="extra-menu"
          className="bg-[#0F2740] border-t border-white/10 px-4 py-3"
        >
          <ul className="flex flex-col gap-3 pl-5">
            <li>
              <button className="flex items-center gap-2 text-white/90 text-2xl">
                <MdLogout className="w-6 h-6" />
                Log Out
              </button>
            </li>
          </ul>
        </div>
      )}
    </nav>
  );
}
