// Not 1:1 representation of response from /*orders API
export type OrderDisplay = {
  order_id: number;
  student_id: number;
  product_name: string;
  total_price: number;
  note: string;
  paid: boolean;
  done: boolean;
}