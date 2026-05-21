import axios from "axios";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1",
  withCredentials: true,
});

export type ApiError = {
  message: string;
};

export async function getJson<T>(path: string) {
  const { data } = await api.get<T>(path);
  return data;
}

export async function postJson<T>(path: string, body?: unknown) {
  const { data } = await api.post<T>(path, body);
  return data;
}

export async function putJson<T>(path: string, body?: unknown) {
  const { data } = await api.put<T>(path, body);
  return data;
}
