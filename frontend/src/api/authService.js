import axiosClient from "./axiosClient";

export async function registerUser(payload) {
  const { data } = await axiosClient.post("/auth/register", payload);
  return data;
}

export async function loginUser(payload) {
  const { data } = await axiosClient.post("/auth/login", payload);
  return data;
}

export async function fetchProfile() {
  const { data } = await axiosClient.get("/auth/me");
  return data;
}
