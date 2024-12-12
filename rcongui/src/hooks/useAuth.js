import { createContext, useContext, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Box, CircularProgress, Typography } from "@mui/material";
import SettingsIcon from "@mui/icons-material/Settings";
import { AuthError, cmd } from "@/utils/fetchUtils";
import { useQuery } from "@tanstack/react-query";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  // Step 1: First, fetch the authentication status
  const {
    data: user,
    isLoading: isAuthLoading,
    isError: isAuthError,
    isSuccess: isAuthSuccess,
  } = useQuery({
    queryKey: ["user", "auth"],
    queryFn: async () => {
      const aUser = await cmd.IS_AUTHENTICATED();
      if (!aUser.authenticated) {
        throw new AuthError(); // Custom error for failed auth
      }
      return aUser;
    },
    refetchOnWindowFocus: false, // Disable refetching on window focus
    retry: 1,
  });

  // Step 2: Fetch permissions, only if authentication is successful
  const {
    data: permissions,
    isLoading: isPermissionsLoading,
    isError: isPermissionsError,
  } = useQuery({
    queryKey: ["user", "permissions"],
    queryFn: cmd.GET_PERMISSIONS,
    enabled: isAuthSuccess && user?.authenticated, // Fetch only if authenticated
    refetchOnWindowFocus: false,
  });

  useEffect(() => {
    if (isAuthError || isPermissionsError) {
      const from = encodeURIComponent(location.pathname + location.search);
      navigate(`/login?from=${from}`);
    }
  }, [isAuthError, isPermissionsError, navigate, location]);

  // Handle loading state
  const isLoading = isAuthLoading || isPermissionsLoading;

  if (isLoading || isAuthError || isPermissionsError) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
          flexDirection: "column",
        }}
      >
        <SettingsIcon sx={{ fontSize: 50 }} />
        <Typography variant="h5" gutterBottom>
          Setting up your CRCON app
        </Typography>
        <CircularProgress sx={{ mt: 2 }} />
      </Box>
    );
  }

  return (
    <AuthContext.Provider value={{ user, permissions }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the AuthContext
export const useAuth = () => useContext(AuthContext);
