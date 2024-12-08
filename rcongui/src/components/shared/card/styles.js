import { styled } from "@mui/material/styles";
import { Card, CardContent } from "@mui/material";

export const BaseCard = styled(Card)({
  margin: "0 auto",
  width: "100%",
});

export const ScrollableContent = styled(CardContent)({
  overflow: "auto",
  padding: 0,
  "&:last-child": {
    paddingBottom: 0,
  },
  // Hide scrollbar for Chrome, Safari and Opera
  "&::-webkit-scrollbar": {
    display: "none",
  },
  // Hide scrollbar for IE, Edge and Firefox
  "msOverflowStyle": "none",
  scrollbarWidth: "none",
}); 