import { createContext, useContext, useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Box, CircularProgress, Typography, Alert, AlertTitle, Button } from "@mui/material";
import SettingsIcon from "@mui/icons-material/Settings";
import BlockIcon from "@mui/icons-material/Block";
import { AuthError, cmd, PermissionError } from "@/utils/fetchUtils";
import { useQuery } from "@tanstack/react-query";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [permissionError, setPermissionError] = useState(null);

  // Step 1: First, fetch the authentication status
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
    error: permissionsErrorObj,
  } = useQuery({
    queryKey: ["user", "permissions"],
    queryFn: cmd.GET_PERMISSIONS,
    enabled: isAuthSuccess && user?.authenticated, // Fetch only if authenticated
    refetchOnWindowFocus: false,
    retry: (failureCount, error) => {
      // Don't retry on 403 errors (permission denied)
      if (error?.status === 403 || error?.name === "PermissionError") {
        return false;
      }
      return failureCount < 1;
    },
  });

  useEffect(() => {
    // Check if it's a permission error (403)
    if (isPermissionsError && permissionsErrorObj) {
      if (permissionsErrorObj.status === 403 || permissionsErrorObj.name === "PermissionError") {
        setPermissionError(permissionsErrorObj);
        return; // Don't redirect to login for permission errors
      }
    }

    // Only redirect to login for authentication errors (401)
    if (isAuthError) {
      const from = encodeURIComponent(location.pathname + location.search);
      navigate(`/login?from=${from}`);
    }
  }, [isAuthError, isPermissionsError, permissionsErrorObj, navigate, location]);

  // Handle loading state
  const isLoading = isAuthLoading || isPermissionsLoading;

  // Show permission error if user is authenticated but doesn't have server access
  if (permissionError) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
          flexDirection: "column",
          padding: 3,
        }}
      >
        <BlockIcon sx={{ fontSize: 80, color: "error.main", mb: 2 }} />
        <Alert severity="error" sx={{ maxWidth: 600, mb: 2 }}>
          <AlertTitle>Access Denied</AlertTitle>
          <Typography variant="body1" gutterBottom>
            {permissionError.text || permissionError.message || "You do not have permission to access this server."}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Please contact your administrator if you believe this is an error.
          </Typography>
        </Alert>
        <Box sx={{ display: "flex", gap: 2, mt: 2 }}>
          <Button
            variant="contained"
            onClick={() => {
              setPermissionError(null);
              window.location.href = "/";
            }}
          >
            Go to Home
          </Button>
          <Button
            variant="outlined"
            onClick={() => {
              setPermissionError(null);
              navigate("/login");
            }}
          >
            Switch Account
          </Button>
        </Box>
      </Box>
    );
  }

  if (isLoading || isAuthError) {
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
