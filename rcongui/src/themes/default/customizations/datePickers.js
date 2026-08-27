import { alpha } from "@mui/material/styles";

import {
  pickersYearClasses,
  pickersMonthClasses,
  pickersDayClasses,
} from "@mui/x-date-pickers";
import { menuItemClasses } from "@mui/material/MenuItem";

/* eslint-disable import/prefer-default-export */
export const datePickersCustomizations = ({ brand, gray }) => ({
  MuiPickersPopper: {
    styleOverrides: {
      paper: ({ theme }) => ({
        marginTop: 4,
        borderRadius: theme.shape.borderRadius,
        border: `1px solid ${theme.palette.divider}`,
        backgroundImage: "none",
        background: theme.palette.background.paper,
        boxShadow: theme.shadows[4],
        [`& .${menuItemClasses.root}`]: {
          borderRadius: theme.shape.borderRadius,
          margin: "0 6px",
        },
        ...theme.applyStyles("dark", {
          background: theme.palette.background.paper,
          boxShadow: theme.shadows[4],
        }),
      }),
    },
  },
  MuiPickersArrowSwitcher: {
    styleOverrides: {
      spacer: { width: 16 },
      button: ({ theme }) => ({
        backgroundColor: "transparent",
        color: theme.palette.grey[500],
        ...theme.applyStyles("dark", {
          color: theme.palette.grey[400],
        }),
      }),
    },
  },
  MuiPickersCalendarHeader: {
    styleOverrides: {
      switchViewButton: {
        padding: 0,
        border: "none",
      },
    },
  },
  MuiPickersMonth: {
    styleOverrides: {
      monthButton: ({ theme }) => ({
        fontSize: theme.typography.body1.fontSize,
        color: theme.palette.grey[600],
        padding: theme.spacing(0.5),
        borderRadius: theme.shape.borderRadius,
        "&:hover": {
          backgroundColor: theme.palette.action.hover,
        },
        [`&.${pickersMonthClasses.selected}`]: {
          color: theme.palette.primary.contrastText,
          backgroundColor: theme.palette.primary.main,
          fontWeight: theme.typography.fontWeightMedium,
        },
        "&:focus": {
          outline: `3px solid ${alpha(brand[500], 0.5)}`,
          outlineOffset: "2px",
          backgroundColor: "transparent",
          [`&.${pickersMonthClasses.selected}`]: {
            backgroundColor: theme.palette.primary.main,
          },
        },
        ...theme.applyStyles("dark", {
          color: theme.palette.grey[300],
          "&:hover": {
            backgroundColor: theme.palette.action.hover,
          },
          [`&.${pickersMonthClasses.selected}`]: {
            color: theme.palette.primary.contrastText,
            fontWeight: theme.typography.fontWeightMedium,
            backgroundColor: theme.palette.primary.main,
          },
          "&:focus": {
            outline: `3px solid ${alpha(brand[500], 0.5)}`,
            outlineOffset: "2px",
            backgroundColor: "transparent",
            [`&.${pickersMonthClasses.selected}`]: {
              backgroundColor: theme.palette.primary.main,
            },
          },
        }),
      }),
    },
  },
  MuiPickersYear: {
    styleOverrides: {
      yearButton: ({ theme }) => ({
        fontSize: theme.typography.body1.fontSize,
        color: theme.palette.grey[600],
        padding: theme.spacing(0.5),
        borderRadius: theme.shape.borderRadius,
        height: "fit-content",
        "&:hover": {
          backgroundColor: theme.palette.action.hover,
        },
        [`&.${pickersYearClasses.selected}`]: {
          color: theme.palette.primary.contrastText,
          backgroundColor: theme.palette.primary.main,
          fontWeight: theme.typography.fontWeightMedium,
        },
        "&:focus": {
          outline: `3px solid ${alpha(brand[500], 0.5)}`,
          outlineOffset: "2px",
          backgroundColor: "transparent",
          [`&.${pickersYearClasses.selected}`]: {
            backgroundColor: theme.palette.primary.main,
          },
        },
        ...theme.applyStyles("dark", {
          color: theme.palette.grey[300],
          "&:hover": {
            backgroundColor: theme.palette.action.hover,
          },
          [`&.${pickersYearClasses.selected}`]: {
            color: theme.palette.primary.contrastText,
            fontWeight: theme.typography.fontWeightMedium,
            backgroundColor: theme.palette.primary.main,
          },
          "&:focus": {
            outline: `3px solid ${alpha(brand[500], 0.5)}`,
            outlineOffset: "2px",
            backgroundColor: "transparent",
            [`&.${pickersYearClasses.selected}`]: {
              backgroundColor: theme.palette.primary.main,
            },
          },
        }),
      }),
    },
  },
  MuiPickersDay: {
    styleOverrides: {
      root: ({ theme }) => ({
        fontSize: theme.typography.body1.fontSize,
        color: theme.palette.grey[600],
        padding: theme.spacing(0.5),
        borderRadius: theme.shape.borderRadius,
        "&:hover": {
          backgroundColor: theme.palette.action.hover,
        },
        [`&.${pickersDayClasses.selected}`]: {
          color: theme.palette.primary.contrastText,
          backgroundColor: theme.palette.primary.main,
          fontWeight: theme.typography.fontWeightMedium,
        },
        "&:focus": {
          outline: `3px solid ${alpha(brand[500], 0.5)}`,
          outlineOffset: "2px",
          backgroundColor: "transparent",
          [`&.${pickersDayClasses.selected}`]: {
            backgroundColor: theme.palette.primary.main,
          },
        },
        ...theme.applyStyles("dark", {
          color: theme.palette.grey[300],
          "&:hover": {
            backgroundColor: theme.palette.action.hover,
          },
          [`&.${pickersDayClasses.selected}`]: {
            color: theme.palette.primary.contrastText,
            fontWeight: theme.typography.fontWeightMedium,
            backgroundColor: theme.palette.primary.main,
          },
          "&:focus": {
            outline: `3px solid ${alpha(brand[500], 0.5)}`,
            outlineOffset: "2px",
            backgroundColor: "transparent",
            [`&.${pickersDayClasses.selected}`]: {
              backgroundColor: theme.palette.primary.main,
            },
          },
        }),
      }),
    },
  },
});
