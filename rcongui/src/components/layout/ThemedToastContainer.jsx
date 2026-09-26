import { GlobalStyles } from "@mui/material";
import { alpha, useColorScheme } from "@mui/material/styles";
import { ToastContainer } from "react-toastify";

export default function ThemedToastContainer() {
  const { mode } = useColorScheme();

  return (
    <>
      <GlobalStyles
        styles={(theme) => ({
          ".Toastify__toast-container": {
            "--toastify-color-light": theme.palette.background.paper,
            "--toastify-color-dark": theme.palette.background.paper,
            "--toastify-text-color-light": theme.palette.text.primary,
            "--toastify-text-color-dark": theme.palette.text.primary,
            "--toastify-color-info": theme.palette.info.main,
            "--toastify-color-success": theme.palette.success.main,
            "--toastify-color-warning": theme.palette.warning.main,
            "--toastify-color-error": theme.palette.error.main,
            "--toastify-icon-color-info": theme.palette.info.main,
            "--toastify-icon-color-success": theme.palette.success.main,
            "--toastify-icon-color-warning": theme.palette.warning.main,
            "--toastify-icon-color-error": theme.palette.error.main,
          },
          ".Toastify__toast": {
            color: theme.palette.text.primary,
            backgroundColor: theme.palette.background.paper,
            border: `1px solid ${theme.palette.divider}`,
            borderRadius: `${theme.shape.borderRadius}px`,
            boxShadow: theme.shadows[4],
          },
          ".Toastify__toast--info": {
            borderLeft: `5px solid ${theme.palette.info.main}`,
          },
          ".Toastify__toast--success": {
            borderLeft: `5px solid ${theme.palette.success.main}`,
          },
          ".Toastify__toast--warning": {
            borderLeft: `5px solid ${theme.palette.warning.main}`,
          },
          ".Toastify__toast--error": {
            borderLeft: `5px solid ${theme.palette.error.main}`,
          },
          ".Toastify__toast-body": {
            color: "inherit",
            fontFamily: theme.typography.fontFamily,
            lineHeight: theme.typography.body2.lineHeight,
          },
          ".Toastify__close-button": {
            color: theme.palette.text.primary,
            opacity: 0.72,
            borderRadius: `${theme.shape.borderRadius}px`,
            "&:hover": {
              color: theme.palette.text.primary,
              backgroundColor: theme.palette.action.hover,
              opacity: 1,
            },
            "&:focus-visible": {
              outline: `3px solid ${alpha(theme.palette.primary.main, 0.55)}`,
              outlineOffset: 1,
            },
          },
          ".Toastify__progress-bar--info": {
            backgroundColor: theme.palette.info.main,
          },
          ".Toastify__progress-bar--success": {
            backgroundColor: theme.palette.success.main,
          },
          ".Toastify__progress-bar--warning": {
            backgroundColor: theme.palette.warning.main,
          },
          ".Toastify__progress-bar--error": {
            backgroundColor: theme.palette.error.main,
          },
        })}
      />
      <ToastContainer theme={mode === "dark" ? "dark" : "light"} />
    </>
  );
}
