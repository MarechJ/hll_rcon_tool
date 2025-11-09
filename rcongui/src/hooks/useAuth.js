import { createContext, useContext, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Box, CircularProgress, Typography } from "@mui/material";
import SettingsIcon from "@mui/icons-material/Settings";
import { AuthError, cmd, PermissionError } from "@/utils/fetchUtils";
import { useQuery } from "@tanstack/react-query";
import ServerAccessDenied from "@/components/shared/ServerAccessDenied";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const {
    data: user,
    isLoading: isAuthLoading,
    isError: isAuthError,
    isSuccess: isAuthSuccess,
    error: authError,
  } = useQuery({
    queryKey: ["user", "auth"],
    queryFn: async () => {
      const aUser = await cmd.IS_AUTHENTICATED();
      if (!aUser.authenticated) {
        throw new AuthError();
      }
      return aUser;
    },
    refetchOnWindowFocus: false, // Disable refetching on window focus
    retry: 1,
  });

  const {
    data: permissions,
    isLoading: isPermissionsLoading,
    isError: isPermissionsError,
    error: permissionsErrorObj,
  } = useQuery({
    queryKey: ["user", "permissions"],
    queryFn: cmd.GET_PERMISSIONS,
    enabled: isAuthSuccess && user?.authenticated,
    refetchOnWindowFocus: false,
    retry: 1,
  });

  useEffect(() => {
    if (isAuthError && authError?.name === "AuthError") {
      const from = encodeURIComponent(location.pathname + location.search);
      navigate(`/login?from=${from}`);
    }
  }, [isAuthError, authError, navigate, location]);

  const isLoading = isAuthLoading || isPermissionsLoading;

  if (isPermissionsError && permissionsErrorObj?.name === "PermissionError") {
    return <ServerAccessDenied errorMessage={permissionsErrorObj?.message} />;
  }

  if (isLoading || (isAuthError && authError?.name === "AuthError")) {
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
