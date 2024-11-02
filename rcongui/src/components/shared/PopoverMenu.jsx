import * as React from "react";
import { useTheme, styled } from "@mui/material/styles";
import Popper from "@mui/material/Popper";
import ClickAwayListener from "@mui/material/ClickAwayListener";
import SettingsIcon from "@mui/icons-material/Settings";
import CloseIcon from "@mui/icons-material/Close";
import DoneIcon from "@mui/icons-material/Done";
import Autocomplete, { autocompleteClasses } from "@mui/material/Autocomplete";
import ButtonBase from "@mui/material/ButtonBase";
import InputBase from "@mui/material/InputBase";
import Box from "@mui/material/Box";
import FlagIcon from "@mui/icons-material/Flag";

function PopperComponent(props) {
  const { disablePortal, anchorEl, open, ...other } = props;
  return <StyledAutocompletePopper {...other} />;
}

const StyledPopper = styled(Popper)(({ theme }) => ({
  border: `1px solid ${"#e1e4e8"}`,
  boxShadow: `0 8px 24px ${"rgba(149, 157, 165, 0.2)"}`,
  backgroundColor: theme.palette.background.paper,
  borderRadius: 0,
  width: 300,
  zIndex: theme.zIndex.modal,
  fontSize: 12,
  ...theme.applyStyles("dark", {
    border: `1px solid ${"#30363d"}`,
    boxShadow: `0 8px 24px ${"rgb(1, 4, 9)"}`,
    color: "#c9d1d9",
  }),
}));

const StyledInput = styled(InputBase)(({ theme }) => ({
  padding: 10,
  width: "100%",
  borderBottom: `1px solid ${theme.palette.divider}`,
  "& input": {
    borderRadius: 4,
    backgroundColor: "#fff",
    border: `1px solid ${theme.palette.divider}`,
    padding: 8,
    transition: theme.transitions.create(["border-color", "box-shadow"]),
    fontSize: 14,
    "&:focus": {
      boxShadow: `0px 0px 0px 3px ${"rgba(3, 102, 214, 0.3)"}`,
      borderColor: "#0366d6",
      ...theme.applyStyles("dark", {
        boxShadow: `0px 0px 0px 3px ${"rgb(12, 45, 107)"}`,
        borderColor: "#388bfd",
      }),
    },
    ...theme.applyStyles("dark", {
      backgroundColor: theme.palette.background.paper,
      border: `1px solid ${theme.palette.divider}`,
    }),
  },
  ...theme.applyStyles("dark", {
    borderBottom: `1px solid ${theme.palette.divider}`,
  }),
}));

const Button = styled(ButtonBase)(({ theme }) => ({
  fontSize: 12,
  width: "100%",
  height: "100%",
  textAlign: "left",
  fontWeight: 600,
  "&:hover,&:focus": {
    ...theme.applyStyles("dark", {}),
  },
  "& span": {
    width: "100%",
  },
  "& svg": {
    width: 16,
    height: 16,
  },
  ...theme.applyStyles("dark", {}),
}));

export const PopoverMenu = ({ id, children, renderButton, description }) => {
  const [anchorEl, setAnchorEl] = React.useState(null);

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
    <React.Fragment>
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
                borderBottom: `1px solid ${"#30363d"}`,
                padding: "8px 10px",
                fontWeight: 600,
                ...t.applyStyles("light", {
                  borderBottom: `1px solid ${"#eaecef"}`,
                }),
              })}
            >
              {description}
            </Box>
            {children}
          </div>
        </ClickAwayListener>
      </StyledPopper>
    </React.Fragment>
  );
};
