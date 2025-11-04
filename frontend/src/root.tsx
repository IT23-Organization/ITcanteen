import React from "react";
import { useSelector } from "react-redux"
import { useNavigate } from "react-router"
import type { OrderDisplay } from "@/lib/types"
import { api } from "@/lib/api"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { toast } from "sonner"

const fetchOrders = async (store_id: number): Promise<OrderDisplay[]> => {
  try {
    const res = await api(`/store/orders?store_id=${store_id}`, {
      method: "GET",
    });

    const data = await res.json()
        .then((res: any[]) => res.filter((order) => !order.done))

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
  const navigate = useNavigate();

  const [ordersState, setOrdersState] = React.useState<OrderDisplay[]>([]);

  const fetchData = async () => {
    const orders = await fetchOrders(user.store_id);
    setOrdersState(orders);
  };

  React.useEffect(() => {
    // if (!user || !user.username) {
    //   navigate('/login');
    // }
    console.log("User state in history.tsx:", user);

    fetchData();
  }, [user, navigate]);

  return (
    <>
      <h1 className="text-xl mt-8 mb-8">Orders</h1>
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
                  const updatedOrder = await sendUpdateOrderRequest(order.order_id, order.paid, true);
                  toast.success("ออเดอร์เสร็จสิ้นแล้ว");
                  if (updatedOrder) {
                    fetchData();
                  }
                }}
              >
                เสร็จสิ้น
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </>
  );
}