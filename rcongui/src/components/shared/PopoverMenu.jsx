import { styled } from "@mui/material/styles";
import Popper from "@mui/material/Popper";
import ClickAwayListener from "@mui/material/ClickAwayListener";
import Box from "@mui/material/Box";
import { Fragment, useState } from "react";

const StyledPopper = styled(Popper)(({ theme }) => ({
  overflow: "hidden",
  border: `1px solid ${theme.palette.divider}`,
  boxShadow: theme.shadows[4],
  backgroundColor: theme.palette.background.paper,
  borderRadius: 0,
  width: 300,
  zIndex: theme.zIndex.modal,
  fontSize: 12,
}));

export const PopoverMenu = ({
  id,
  children,
  renderButton,
  description,
  onOpen,
  onClose,
  sx,
}) => {
  const [anchorEl, setAnchorEl] = useState(null);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
    onOpen?.();
  };

  const handleClose = () => {
    if (anchorEl) {
      anchorEl.focus();
    }
    setAnchorEl(null);
    onClose?.();
  };

  const open = Boolean(anchorEl);
  id = open ? id : undefined;

  return (
    <Fragment>
      {renderButton({ onClick: handleClick })}
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
        sx={sx}
      >
        <ClickAwayListener onClickAway={handleClose}>
          <div>
            <Box
              sx={(t) => ({
                borderBottom: `1px solid ${t.palette.divider}`,
                padding: "8px 10px",
                fontWeight: 600,
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
