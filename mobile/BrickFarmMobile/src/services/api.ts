// src/services/api.ts
import axios from "axios";
import { getToken } from "../services/auth"; // implement simple token retrieval from secure store

const API_BASE = "https://farm.brickservers.ng/api/v1"; // update per env

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000
});

api.interceptors.request.use(async (cfg) => {
  const token = await getToken();
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

export default api;
