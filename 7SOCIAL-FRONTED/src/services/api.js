// src/services/api.js
import axios from "axios";

export const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "https://yeferson3256457-7social-back.hf.space", // Dirección del backend
});
