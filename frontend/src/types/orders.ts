export type OrderStatus =
  | "CONFIRMED"
  | "WAITING_CONFIRMATION"
  | "DISPATCHED_UBER"
  | "DELIVERED"
  | "CANCELLED";

export interface Order {
  id: number;
  created_at: string;
  customer_name: string;
  customer_phone: string;
  formatted_phone: string;
  product_sku: string;
  quantity: number;
  product_price: number;
  destination_address?: string;
  status: OrderStatus;
  expires_at: string;
}

export interface Product {
  sku: string;
  name: string;
  category: string;
  quality: string;
  cost_price: number;
  price: number;
  stock_quantity: number;
  supplier_name?: string;
  location?: string;
}
