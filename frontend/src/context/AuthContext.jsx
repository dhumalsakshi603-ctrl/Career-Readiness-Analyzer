import { createContext, useContext, useEffect, useState } from "react";
import { fetchCsrfToken, getCurrentUser, loginUser, logoutUser, registerUser } from "../api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function init() {
      try {
        await fetchCsrfToken();
        const res = await getCurrentUser();
        setUser(res.data.id ? res.data : null);
      } catch {
        setUser(null);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  const login = async (username, password) => {
    const res = await loginUser(username, password);
    setUser(res.data);
    return res.data;
  };

  const register = async (username, email, password) => {
    const res = await registerUser(username, email, password);
    setUser(res.data);
    return res.data;
  };

  const logout = async () => {
    await logoutUser();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
