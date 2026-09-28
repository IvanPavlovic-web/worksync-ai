import axios from "axios";
import { clearAuth } from "./auth";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api",
  timeout: 15000,
});

api.interceptors.request.use((cfg) => {
  if (typeof window !== "undefined") {
    const t = localStorage.getItem("token");
    if (t) cfg.headers.Authorization = `Bearer ${t}`;
  }
  return cfg;
});
api.interceptors.response.use((response) => response, (error) => {
  if (error?.response?.status === 401 && typeof window !== "undefined") clearAuth();
  return Promise.reject(error);
});

export async function serverFetch<T>(
  path: string,
  revalidate = 3600,
): Promise<T | null> {
  try {
    const url = `${process.env.API_URL}${path}`;
    const r = await fetch(url, { next: { revalidate } });
    if (!r.ok) return null;
    return (await r.json()) as T;
  } catch {
    return null;
  }
}
