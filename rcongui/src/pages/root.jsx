import * as React from "react";
import { styled, ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import Container from "@mui/material/Container";
import themes from "../themes";
import { Outlet } from "react-router-dom";
import { useStorageState } from "../hooks/useStorageState";
import Header from "../components/Header";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const AppWrapper = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  minHeight: "100vh",
}));

const Main = styled("main")(({ theme }) => ({
  backgroundColor:
    theme.palette.mode === "light"
      ? theme.palette.grey[100]
      : theme.palette.grey[900],
  flexGrow: 1,
  display: "flex",
  flexDirection: "column",
  overflowY: "auto",
  overflowX: "clip",
  position: "relative",
}));

export default function Root() {
  const [theme] = useStorageState("crconTheme", "Dark");

  const defaultTheme = themes[theme];

  return (
    <ThemeProvider theme={defaultTheme}>
      <AppWrapper>
        <CssBaseline />
        <Header />
        <Main>
          <Container maxWidth="xl" sx={{ mt: 2, mb: 4, flexGrow: 1 }}>
            <Outlet />
          </Container>
        </Main>
      </AppWrapper>
      <ToastContainer />
    </ThemeProvider>
  );
}
