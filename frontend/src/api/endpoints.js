import api from "./client";

export const authApi = {
  register: (data) => api.post("/api/auth/register", data),
  login: (data) => api.post("/api/auth/login", data),
  me: () => api.get("/api/auth/me"),
};

export const resumeApi = {
  upload: (data) => api.post("/api/resumes", data),
  list: () => api.get("/api/resumes"),
  get: (id) => api.get(`/api/resumes/${id}`),
  analyze: (id) => api.post(`/api/resumes/${id}/analyze`),
  remove: (id) => api.delete(`/api/resumes/${id}`),
};

export const aiApi = {
  ingestDocument: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/api/ai/documents/ingest", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  queryDocument: (data) => api.post("/api/ai/documents/query", data),
  generateInterviewQuestions: (data) => api.post("/api/ai/interview/questions", data),
  evaluateAnswer: (data) => api.post("/api/ai/interview/evaluate", data),
};
