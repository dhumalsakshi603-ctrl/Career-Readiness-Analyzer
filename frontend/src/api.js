import axios from "axios";

const API_BASE =
  import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
});

function getCookie(name) {
  const match = document.cookie.match(
    new RegExp("(^| )" + name + "=([^;]+)")
  );
  return match ? decodeURIComponent(match[2]) : null;
}

api.interceptors.request.use((config) => {
  const method = (config.method || "get").toLowerCase();

  if (["post", "put", "patch", "delete"].includes(method)) {
    const csrfToken = getCookie("csrftoken");

    if (csrfToken) {
      config.headers["X-CSRFToken"] = csrfToken;
    }
  }

  return config;
});

export const fetchCsrfToken = () =>
  api.get("/auth/csrf/");

export const registerUser = (username, email, password) =>
  api.post("/auth/register/", {
    username,
    email,
    password,
  });

export const loginUser = (username, password) =>
  api.post("/auth/login/", {
    username,
    password,
  });

export const logoutUser = () =>
  api.post("/auth/logout/");

export const getCurrentUser = () =>
  api.get("/auth/me/");

export const getProfile = () =>
  api.get("/profile/");

export const updateProfile = (data) =>
  api.put("/profile/", data);

export const uploadResume = (file) => {
  const formData = new FormData();
  formData.append("file", file);

  return api.post("/resume/upload/", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

export const getLatestResume = () =>
  api.get("/resume/latest/");

export const generateQuiz = (topic, difficulty, count) =>
  api.post("/quiz/generate/", {
    topic,
    difficulty,
    count,
  });

export const getQuiz = (quizId) =>
  api.get(`/quiz/${quizId}/`);

export const submitQuiz = (quizId, answers) =>
  api.post(`/quiz/${quizId}/submit/`, {
    answers,
  });

export const calculateReadiness = (attemptId) =>
  api.post(
    "/readiness/calculate/",
    attemptId
      ? { attempt_id: attemptId }
      : {}
  );

export const getReadinessHistory = () =>
  api.get("/readiness/history/");

export const getLatestReadiness = () =>
  api.get("/readiness/latest/");