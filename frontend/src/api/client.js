import axios from "axios";

// All requests go through the gateway (Spring Cloud Gateway), which routes
// /api/auth/** -> auth-service, /api/resumes/** -> resume-service,
// /api/ai/** -> ai-service. Point this at the gateway in prod; falls back
// to localhost:8080 for local `npm run dev` against docker-compose.
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

const api = axios.create({ baseURL: BASE_URL });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
