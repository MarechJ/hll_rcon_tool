import { Box, styled } from "@mui/material";

const StyledBox = styled(Box)(({ theme }) => ({
  position: "sticky",
  top: 64,
  marginLeft: theme.spacing(-2),
  marginRight: theme.spacing(-2),
  zIndex: theme.zIndex.appBar - 1,
  [theme.breakpoints.up("lg")]: {
    top: -1, // ??? There is a 1px gap between the window and the sticky container
    marginLeft: 0,
    marginRight: 0,
  },
}));

export default function StickyContainer({ children, ...props }) {
  return (
    <StyledBox {...props}>
      {children}
    </StyledBox>
  );
}
