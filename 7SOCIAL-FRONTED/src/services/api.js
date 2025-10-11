// src/services/api.js
import axios from "axios";

export const api = axios.create({
  baseURL: "https://yeferson3256457-7social-back.hf.space", // Dirección del backend
});
