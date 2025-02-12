import { styled } from "@mui/material";
import { getDensityPadding } from "../table/styles";

export const StyledLogsTable = styled("table", {
  shouldForwardProp: (prop) =>
    prop !== "fontSize" || prop !== "density" || prop !== "highlighted",
})((styledProps) => {
  const theme = styledProps.theme;
  const fontSize = styledProps.fontSize;
  const density = styledProps.density;

  return {
    // TABLE
    fontSize:
      fontSize === "small"
        ? "0.85rem"
        : fontSize === "large"
        ? "1.15rem"
        : "1rem",
    borderCollapse: "collapse",
    borderSpacing: 0,
    border: `1px solid ${theme.palette.divider}`,
    width: "100%",
    "& td": {
      ...getDensityPadding(density, theme),
    },
    "& th": {
      ...getDensityPadding(density, theme),
      verticalAlign: "middle",
      height: "3rem",
    },
    "& tbody tr": {
      verticalAlign: "top",
    },
    "&.highlighted tbody tr.highlighted": {
      fontWeight: "normal",
    },
    "&.highlighted tbody tr:not(.highlighted)": {
      opacity: 0.4,
    },
  };
});

export const StyledLogsTr = styled("tr")((styledProps) => {
  const theme = styledProps.theme;

  return {
    borderBottom: `1px solid ${theme.palette.divider}`,
    verticalAlign: "top",
  };
});
