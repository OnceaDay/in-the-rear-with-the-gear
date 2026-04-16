import axios from "axios";

const AUTH_BASE_URL = "http://127.0.0.1:8000/api";

export const loginUser = async (credentials) => {
  const response = await axios.post(`${AUTH_BASE_URL}/token/`, credentials);
  return response.data;
};

export const refreshAccessToken = async (refreshToken) => {
  const response = await axios.post(`${AUTH_BASE_URL}/token/refresh/`, {
    refresh: refreshToken,
  });
  return response.data;
};

export const logoutUser = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
};