import { styled } from "@mui/material/styles";
import Popper from "@mui/material/Popper";
import ClickAwayListener from "@mui/material/ClickAwayListener";
import Box from "@mui/material/Box";
import {Fragment, useState} from "react";

const StyledPopper = styled(Popper)(({ theme }) => ({
  border: `1px solid #e1e4e8`,
  boxShadow: `0 8px 24px rgba(149, 157, 165, 0.2)`,
  backgroundColor: theme.palette.background.paper,
  borderRadius: 0,
  width: 300,
  zIndex: theme.zIndex.modal,
  fontSize: 12,
  ...theme.applyStyles("dark", {
    border: `1px solid #30363d`,
    boxShadow: `0 8px 24px rgb(1, 4, 9)`,
    color: "#c9d1d9",
  }),
}));

export const PopoverMenu = ({ id, children, renderButton, description }) => {
  const [anchorEl, setAnchorEl] = useState(null);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    if (anchorEl) {
      anchorEl.focus();
    }
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);
  id = open ? id : undefined;

  return (
    <Fragment>
      <Box sx={{ fontSize: 12 }}>{renderButton({ onClick: handleClick })}</Box>
      <StyledPopper
        id={id}
        open={open}
        anchorEl={anchorEl}
        placement="bottom-start"
        popperOptions={{
          modifiers: [
            {
              name: "flip",
              enabled: true,
              options: { fallbackPlacements: ["top", "bottom"] },
            },
          ],
        }}
      >
        <ClickAwayListener onClickAway={handleClose}>
        <div>
            <Box
              sx={(t) => ({
                borderBottom: `1px solid #30363d`,
                padding: "8px 10px",
                fontWeight: 600,
                ...t.applyStyles("light", {
                  borderBottom: `1px solid #eaecef`,
                }),
              })}
            >
              {description}
            </Box>
            {children}
          </div>
        </ClickAwayListener>
      </StyledPopper>
    </Fragment>
  );
};
