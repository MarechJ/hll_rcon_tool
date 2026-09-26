export const byUsage = (percentage, theme) =>
  typeof percentage !== "number"
    ? ""
    : percentage >= 80
    ? theme.palette.error.main
    : percentage >= 67
    ? theme.palette.warning.main
    : "";
