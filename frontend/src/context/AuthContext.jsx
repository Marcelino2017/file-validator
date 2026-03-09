import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { fetchProfile, loginUser } from "../api/authService";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("auth_token"));
  const [user, setUser] = useState(null);
  const [loadingProfile, setLoadingProfile] = useState(false);

  useEffect(() => {
    if (!token) {
      setUser(null);
      return;
    }
    setLoadingProfile(true);
    fetchProfile()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("auth_token");
        setToken(null);
      })
      .finally(() => setLoadingProfile(false));
  }, [token]);

  const signIn = async (credentials) => {
    const response = await loginUser(credentials);
    localStorage.setItem("auth_token", response.access_token);
    setToken(response.access_token);
    return response;
  };

  const signOut = () => {
    localStorage.removeItem("auth_token");
    setToken(null);
    setUser(null);
  };

  const value = useMemo(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(token),
      loadingProfile,
      signIn,
      signOut,
    }),
    [loadingProfile, token, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuthContext debe usarse dentro de AuthProvider");
  }
  return context;
}
