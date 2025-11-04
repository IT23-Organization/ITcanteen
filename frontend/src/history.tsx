import React from "react"
import { useSelector } from "react-redux"
import type { OrderDisplay } from "@/lib/types"
import { api } from "@/lib/api"

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "./components/ui/button";
import { toast } from "sonner";

const fetchOrders = async (store_id: number): Promise<OrderDisplay[]> => {
  try {
    const res = await api(`/store/orders?store_id=${store_id}`, {
      method: "GET",
    });

    const data = await res.json()
        .then((res: any[]) => res.filter((order) => order.done))

    // fetch each order's product name
    const ordersDisplay: OrderDisplay[] = [];
    for (const order of data) {
      const productResponse = await api(`/product?product_id=${order.product_id}`, {
        method: "GET",
      });
      const productData = await productResponse.json();
      ordersDisplay.push({
        order_id: order.order_id,
        student_id: order.student_id,
        product_name: productData.name,
        total_price: order.total_price,
        note: order.note,
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

const sendUpdateOrderRequest = async (orderId: number, paid: boolean, done: boolean) => {
  try {
    const response = await api("/orders/update", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        order_id: orderId,
        paid: paid,
        done: done,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error updating order:", error);
    return null;
  }
};

export default function app() {
  const user = useSelector((state: any) => state.user);
  const [ordersState, setOrdersState] = React.useState<OrderDisplay[]>([]);

  const fetchData = async () => {
    const orders = await fetchOrders(user.store_id);
    setOrdersState(orders);
  };

  React.useEffect(() => {
    fetchData();
  }, []);

  return (
    <>
      <h1 className="text-xl mt-8 mb-8">History</h1>
      <div className="mb-4">
        <h2 className="text-lg font-bold mb-2">Statistics</h2>
        <p className="text-lg">
          ออเดอร์ทั้งหมดที่เสร็จสมบูรณ์: {ordersState.length}
        </p>
        <p className="text-lg">
          รายได้ทั้งหมด: $
          {ordersState
            .reduce((total, order) => total + order.total_price, 0)
            .toFixed(2)}
        </p>
      </div>

      <div>
        <h2 className="text-lg font-bold mb-2">Past orders</h2>
        <div className="flex flex-row gap-4">
          {ordersState.map((order) => (
            <Card key={order.order_id} className="mb-4 flex flex-col">
              <CardHeader>
                <CardTitle>Order ID: {order.order_id}</CardTitle>
                <CardDescription>Student ID: {order.student_id}</CardDescription>
              </CardHeader>
              <CardContent className="grow">
                <p>รายการ: {order.product_name}</p>
                <p>ราคาทั้งหมด: ฿{order.total_price.toFixed(2)}</p>
                {order.note && <p>หมายเหตุ: {order.note}</p>}
              </CardContent>
              <CardFooter className="flex justify-end space-x-2">
                <Button
                  onClick={async () => {
                    const updatedOrder = await sendUpdateOrderRequest(order.order_id, order.paid, false);
                    toast.info("ออเดอร์ถูกเปลี่ยนเป็นยังไม่เสร็จ");
                    if (updatedOrder) {
                      fetchData();
                    }
                  }}
                >
                  เปลี่ยนเป็นยังไม่เสร็จ
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      </div>
    </>
  )
}