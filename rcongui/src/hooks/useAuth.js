import { cmd } from '@/utils/fetchUtils';
import { Box, CircularProgress, Typography } from '@mui/material';
import React, { createContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Settings as SettingsIcon } from '@mui/icons-material';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const auth = await cmd.IS_AUTHENTICATED();
        if (auth.authenticated) {
          const userDetails = await cmd.GET_PERMISSIONS();
          setUser(userDetails);
        } else {
          navigate("/login"); // Redirect if not authenticated
        }
      } catch (error) {
        console.error("Authentication error", error);
        navigate("/login");
      } finally {
        setTimeout(() => {setLoading(false)}, 1250)
      }
    };

    checkAuth();
  }, [navigate]);

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          flexDirection: 'column'
        }}
      >
        <SettingsIcon sx={{ fontSize: 50 }} />
        <Typography variant="h5" gutterBottom>
          Setting up your CRCON app
        </Typography>
        <CircularProgress sx={{ mt: 2 }} />
      </Box>
    )
  }

  return (
    <AuthContext.Provider value={{ user }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => React.useContext(AuthContext);
