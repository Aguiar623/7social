// src/services/api.js
import axios from "axios";

export const api = axios.create({
  baseURL: "http://127.0.0.1:8000", // Dirección del backend
});
