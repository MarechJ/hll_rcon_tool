export const HIGHLIGHT = {
  danger: "#f44336",
  warning: "#ffc107",
  success: "#76ff03",
};

export const byUsage = (percentage) =>
  typeof percentage !== "number"
    ? ""
    : percentage >= 80
    ? HIGHLIGHT.danger
    : percentage >= 67
    ? HIGHLIGHT.warning
    : "";
