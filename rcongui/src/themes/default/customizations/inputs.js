import { alpha } from "@mui/material/styles";

const getPaletteColor = (theme, color) => {
  if (!color || color === "default" || color === "inherit") return null;
  return theme.palette[color]?.main ? theme.palette[color] : null;
};

const outlinedColorStyles = (paletteColor) => ({
  color: paletteColor.main,
  borderColor: alpha(paletteColor.main, 0.55),
  backgroundColor: alpha(paletteColor.main, 0.035),
  "&:hover": {
    color: paletteColor.main,
    borderColor: paletteColor.main,
    backgroundColor: alpha(paletteColor.main, 0.11),
  },
  "&:focus-visible": {
    outlineColor: alpha(paletteColor.main, 0.38),
  },
});

/* eslint-disable import/prefer-default-export */
export const inputsCustomizations = ({ brand, gray }) => ({
  MuiButtonBase: {
    defaultProps: { disableTouchRipple: true },
    styleOverrides: {
      root: {
        boxSizing: "border-box",
        transition:
          "background-color 120ms ease, border-color 120ms ease, color 120ms ease, box-shadow 120ms ease",
        "&:focus-visible": {
          outline: `3px solid ${alpha(brand[500], 0.35)}`,
          outlineOffset: 2,
        },
      },
    },
  },
  MuiButton: {
    defaultProps: { disableElevation: true },
    styleOverrides: {
      root: ({ theme }) => ({
        minHeight: 36,
        padding: "6px 14px",
        borderRadius: theme.shape.borderRadius,
        textTransform: "none",
        boxShadow: "none",
        "&:active": { transform: "translateY(1px)" },
        "&.Mui-disabled": { borderColor: alpha(gray[500], 0.18) },
      }),
      sizeSmall: { minHeight: 30, padding: "4px 10px" },
      sizeLarge: { minHeight: 42, padding: "8px 18px" },
      containedPrimary: ({ theme }) => ({
        color: theme.palette.primary.contrastText,
        backgroundColor: theme.palette.primary.main,
        border: `1px solid ${theme.palette.primary.dark}`,
        boxShadow: `inset 0 1px 0 ${alpha(brand[50], 0.22)}`,
        "&:hover": {
          backgroundColor: theme.palette.primary.dark,
          boxShadow: `inset 0 1px 0 ${alpha(brand[50], 0.14)}`,
        },
      }),
      containedSecondary: ({ theme }) => ({
        color: theme.palette.secondary.contrastText,
        backgroundColor: theme.palette.secondary.main,
        border: `1px solid ${theme.palette.secondary.dark}`,
        boxShadow: `inset 0 1px 0 ${alpha(theme.palette.common.white, 0.18)}`,
        "&:hover": { backgroundColor: theme.palette.secondary.dark },
      }),
      outlined: ({ theme, ownerState }) => {
        const paletteColor = getPaletteColor(theme, ownerState.color);
        if (paletteColor) return outlinedColorStyles(paletteColor);

        return {
          color: theme.palette.text.secondary,
          borderColor: theme.palette.divider,
          backgroundColor: alpha(gray[50], 0.48),
          "&:hover": {
            color: theme.palette.text.primary,
            borderColor: gray[500],
            backgroundColor: alpha(gray[200], 0.5),
          },
          ...theme.applyStyles("dark", {
            backgroundColor: alpha(gray[800], 0.72),
            "&:hover": {
              borderColor: gray[400],
              backgroundColor: alpha(gray[700], 0.5),
            },
          }),
        };
      },
      text: ({ theme, ownerState }) => {
        const paletteColor = getPaletteColor(theme, ownerState.color);
        if (paletteColor) {
          return {
            color: paletteColor.main,
            "&:hover": {
              color: paletteColor.main,
              backgroundColor: alpha(paletteColor.main, 0.11),
            },
            "&:focus-visible": {
              outlineColor: alpha(paletteColor.main, 0.38),
            },
          };
        }

        return {
          color: theme.palette.text.secondary,
          "&:hover": {
            color: theme.palette.text.primary,
            backgroundColor: alpha(gray[300], 0.2),
          },
        };
      },
    },
  },
  MuiIconButton: {
    styleOverrides: {
      root: ({ theme, ownerState }) => {
        const paletteColor = getPaletteColor(theme, ownerState.color);
        if (paletteColor) {
          return {
            borderRadius: theme.shape.borderRadius,
            color: paletteColor.main,
            "&:hover": {
              color: paletteColor.main,
              backgroundColor: alpha(paletteColor.main, 0.13),
            },
            "&:focus-visible": {
              outlineColor: alpha(paletteColor.main, 0.38),
            },
          };
        }

        return {
          borderRadius: theme.shape.borderRadius,
          color: theme.palette.text.secondary,
          "&:hover": {
            color: theme.palette.text.primary,
            backgroundColor: alpha(gray[300], 0.2),
          },
        };
      },
    },
  },
  MuiButtonGroup: {
    styleOverrides: {
      root: ({ theme }) => ({
        borderRadius: theme.shape.borderRadius,
        boxShadow: "none",
      }),
      grouped: ({ theme }) => ({
        minWidth: 36,
        borderColor: theme.palette.divider,
      }),
    },
  },
  MuiToggleButtonGroup: {
    styleOverrides: {
      root: ({ theme }) => ({
        gap: 2,
        padding: 2,
        border: `1px solid ${theme.palette.divider}`,
        borderRadius: theme.shape.borderRadius,
        backgroundColor: alpha(gray[200], 0.45),
        ...theme.applyStyles("dark", {
          backgroundColor: alpha(gray[900], 0.6),
        }),
      }),
      grouped: {
        border: 0,
      },
    },
  },
  MuiToggleButton: {
    styleOverrides: {
      root: ({ theme }) => ({
        minHeight: 32,
        padding: "5px 11px",
        color: theme.palette.text.secondary,
        textTransform: "none",
        "&.Mui-selected": {
          color: theme.palette.primary.contrastText,
          backgroundColor: theme.palette.primary.main,
          "&:hover": { backgroundColor: theme.palette.primary.dark },
        },
      }),
    },
  },
  MuiTextField: {
    defaultProps: { size: "small", variant: "outlined" },
  },
  MuiFormControl: {
    defaultProps: { size: "small" },
  },
  MuiInputBase: {
    styleOverrides: {
      root: ({ theme }) => ({ color: theme.palette.text.primary }),
      input: {
        "&::placeholder": { color: gray[500], opacity: 0.82 },
      },
    },
  },
  MuiOutlinedInput: {
    styleOverrides: {
      root: ({ theme }) => ({
        minHeight: 40,
        borderRadius: theme.shape.borderRadius,
        backgroundColor: alpha(gray[50], 0.86),
        "& .MuiOutlinedInput-notchedOutline": {
          borderColor: theme.palette.divider,
          transition: "border-color 120ms ease, border-width 120ms ease",
        },
        "&:hover .MuiOutlinedInput-notchedOutline": {
          borderColor: gray[500],
        },
        "&.Mui-focused": {
          boxShadow: `0 0 0 3px ${alpha(brand[500], 0.2)}`,
        },
        "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
          borderWidth: 1,
          borderColor: brand[600],
        },
        "&.Mui-error": {
          boxShadow: `0 0 0 3px ${alpha(theme.palette.error.main, 0.12)}`,
        },
        "&.Mui-disabled": { backgroundColor: alpha(gray[200], 0.48) },
        "&.Mui-disabled .MuiOutlinedInput-notchedOutline": {
          borderColor: alpha(gray[500], 0.2),
        },
        "&.MuiInputBase-multiline": { padding: "10px 12px" },
        ...theme.applyStyles("dark", {
          backgroundColor: alpha(gray[800], 0.78),
          "&:hover .MuiOutlinedInput-notchedOutline": {
            borderColor: gray[400],
          },
          "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
            borderColor: brand[400],
          },
          "&.Mui-disabled": { backgroundColor: alpha(gray[900], 0.58) },
        }),
      }),
      input: {
        padding: "9px 12px",
        "&.MuiInputBase-inputMultiline": { padding: 0 },
      },
    },
  },
  MuiFilledInput: {
    defaultProps: { disableUnderline: true },
    styleOverrides: {
      root: ({ theme }) => ({
        border: `1px solid ${theme.palette.divider}`,
        borderRadius: theme.shape.borderRadius,
        backgroundColor: alpha(gray[200], 0.52),
        "&:hover": { backgroundColor: alpha(gray[200], 0.72) },
        "&.Mui-focused": {
          borderColor: brand[600],
          backgroundColor: alpha(brand[50], 0.45),
          boxShadow: `0 0 0 3px ${alpha(brand[500], 0.2)}`,
        },
        ...theme.applyStyles("dark", {
          backgroundColor: alpha(gray[800], 0.78),
          "&:hover": { backgroundColor: gray[800] },
          "&.Mui-focused": {
            borderColor: brand[400],
            backgroundColor: alpha(gray[800], 0.9),
          },
        }),
      }),
    },
  },
  MuiInput: {
    styleOverrides: {
      root: ({ theme }) => ({
        "&::before": { borderBottomColor: theme.palette.divider },
        "&:hover:not(.Mui-disabled)::before": { borderBottomColor: gray[500] },
        "&::after": { borderBottomColor: theme.palette.primary.main },
      }),
    },
  },
  MuiInputLabel: {
    styleOverrides: {
      root: ({ theme }) => ({
        color: theme.palette.text.secondary,
        fontWeight: 500,
        "&.Mui-focused": { color: theme.palette.primary.main },
        "&.Mui-error": { color: theme.palette.error.main },
      }),
    },
  },
  MuiFormLabel: {
    styleOverrides: {
      root: ({ theme }) => ({
        color: theme.palette.text.secondary,
        fontSize: theme.typography.body2.fontSize,
        fontWeight: 600,
        "&.Mui-focused": { color: theme.palette.primary.main },
      }),
    },
  },
  MuiFormHelperText: {
    styleOverrides: {
      root: { marginTop: 5, marginLeft: 2, lineHeight: 1.3 },
    },
  },
  MuiInputAdornment: {
    styleOverrides: {
      root: ({ theme }) => ({
        color: theme.palette.text.secondary,
        "& .MuiIconButton-root": { margin: -5 },
      }),
    },
  },
  MuiSelect: {
    defaultProps: {
      MenuProps: { PaperProps: { variant: "outlined" } },
    },
    styleOverrides: {
      select: {
        display: "flex",
        alignItems: "center",
        minHeight: "unset",
      },
      icon: ({ theme }) => ({
        color: theme.palette.text.secondary,
        right: 8,
      }),
    },
  },
  MuiAutocomplete: {
    defaultProps: { size: "small" },
    styleOverrides: {
      root: {
        "& .MuiOutlinedInput-root": { paddingTop: 2, paddingBottom: 2 },
      },
      paper: ({ theme }) => ({
        marginTop: 4,
        border: `1px solid ${theme.palette.divider}`,
        borderRadius: theme.shape.borderRadius,
        backgroundImage: "none",
      }),
      listbox: ({ theme }) => ({
        padding: 4,
        "& .MuiAutocomplete-option": {
          minHeight: 34,
          margin: 2,
          borderRadius: theme.shape.borderRadius,
        },
      }),
      option: ({ theme }) => ({
        "&[aria-selected='true']": {
          backgroundColor: alpha(brand[400], 0.18),
        },
        "&.Mui-focused": { backgroundColor: alpha(brand[300], 0.16) },
        ...theme.applyStyles("dark", {
          "&[aria-selected='true']": {
            backgroundColor: alpha(brand[500], 0.26),
          },
        }),
      }),
      popupIndicator: { border: 0, backgroundColor: "transparent" },
      clearIndicator: { border: 0, backgroundColor: "transparent" },
    },
  },
  MuiCheckbox: {
    defaultProps: { size: "small", disableRipple: true },
    styleOverrides: {
      root: ({ theme }) => ({
        padding: 6,
        color: gray[500],
        borderRadius: theme.shape.borderRadius,
        "&:hover": {
          color: brand[600],
          backgroundColor: alpha(brand[300], 0.16),
        },
        "&.Mui-checked, &.MuiCheckbox-indeterminate": {
          color: theme.palette.primary.main,
        },
      }),
    },
  },
  MuiRadio: {
    defaultProps: { size: "small", disableRipple: true },
    styleOverrides: {
      root: ({ theme }) => ({
        padding: 6,
        color: gray[500],
        "&:hover": {
          color: brand[600],
          backgroundColor: alpha(brand[300], 0.16),
        },
        "&.Mui-checked": { color: theme.palette.primary.main },
      }),
    },
  },
  MuiSwitch: {
    defaultProps: { size: "small", disableRipple: true },
    styleOverrides: {
      root: { width: 38, height: 24, padding: 4 },
      switchBase: ({ theme }) => ({
        padding: 7,
        "&.Mui-checked": {
          transform: "translateX(14px)",
          color: theme.palette.primary.contrastText,
          "+ .MuiSwitch-track": {
            borderColor: theme.palette.primary.dark,
            backgroundColor: theme.palette.primary.main,
            opacity: 1,
          },
        },
      }),
      thumb: { width: 10, height: 10, boxShadow: "none" },
      track: ({ theme }) => ({
        border: `1px solid ${gray[500]}`,
        borderRadius: 8,
        backgroundColor: gray[300],
        opacity: 1,
        ...theme.applyStyles("dark", {
          borderColor: gray[600],
          backgroundColor: gray[700],
        }),
      }),
    },
  },
  MuiFormControlLabel: {
    styleOverrides: {
      root: { gap: 3, marginLeft: -4, marginRight: 12 },
      label: ({ theme }) => ({
        color: theme.palette.text.secondary,
        fontSize: theme.typography.body2.fontSize,
      }),
    },
  },
  MuiSlider: {
    styleOverrides: {
      root: ({ theme }) => ({ color: theme.palette.primary.main, height: 4 }),
      rail: { opacity: 0.28 },
      thumb: ({ theme }) => ({
        width: 14,
        height: 14,
        border: `2px solid ${theme.palette.background.paper}`,
        boxShadow: `0 0 0 1px ${theme.palette.primary.main}`,
        "&:hover, &.Mui-focusVisible": {
          boxShadow: `0 0 0 5px ${alpha(brand[500], 0.2)}`,
        },
      }),
      valueLabel: ({ theme }) => ({
        borderRadius: theme.shape.borderRadius,
        backgroundColor: theme.palette.grey[900],
      }),
    },
  },
});
