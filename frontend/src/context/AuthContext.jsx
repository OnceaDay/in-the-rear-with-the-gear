import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { loginUser, logoutUser } from "../services/authService";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(localStorage.getItem("access_token"));
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem("refresh_token"));
  const [isAuthenticated, setIsAuthenticated] = useState(Boolean(localStorage.getItem("access_token")));
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setIsAuthenticated(Boolean(accessToken));
  }, [accessToken]);

  const login = async (username, password) => {
    setLoading(true);
    try {
      const data = await loginUser({ username, password });

      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);

      setAccessToken(data.access);
      setRefreshToken(data.refresh);
      setIsAuthenticated(true);

      return { success: true };
    } catch (error) {
      const message =
        error?.response?.data?.detail || "Login failed. Check your credentials.";
      return { success: false, message };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    logoutUser();
    setAccessToken(null);
    setRefreshToken(null);
    setIsAuthenticated(false);
  };

  const value = useMemo(
    () => ({
      accessToken,
      refreshToken,
      isAuthenticated,
      loading,
      login,
      logout,
    }),
    [accessToken, refreshToken, isAuthenticated, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
}