import { styled } from "@mui/material/styles";
import Popper from "@mui/material/Popper";
import ClickAwayListener from "@mui/material/ClickAwayListener";
import Autocomplete, { autocompleteClasses } from "@mui/material/Autocomplete";
import InputBase from "@mui/material/InputBase";
import Box from "@mui/material/Box";
import { Fragment, useState } from "react";

const StyledAutocompletePopper = styled("div")(({ theme }) => ({
  [`& .${autocompleteClasses.paper}`]: {
    boxShadow: "none",
    margin: 0,
    color: "inherit",
    fontSize: 12,
  },
  [`& .${autocompleteClasses.listbox}`]: {
    backgroundColor: theme.palette.background.paper,
    padding: 0,
    [`& .${autocompleteClasses.option}`]: {
      minHeight: "auto",
      alignItems: "center",
      gap: 4,
      textOverflow: "ellipsis",
      whiteSpace: "nowrap",
      padding: 8,
      borderBottom: `1px solid ${theme.palette.divider}`,
      '&[aria-selected="true"]': {
        backgroundColor: "transparent",
      },
      [`&.${autocompleteClasses.focused}, &.${autocompleteClasses.focused}[aria-selected="true"]`]:
        {
          backgroundColor: theme.palette.action.hover,
        },
    },
  },
  [`&.${autocompleteClasses.popperDisablePortal}`]: {
    position: "relative",
  },
}));

function PopperComponent(props) {
  const { disablePortal, anchorEl, open, ...other } = props;
  return <StyledAutocompletePopper {...other} />;
}

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

const StyledInput = styled(InputBase)(({ theme }) => ({
  padding: 10,
  width: "100%",
  borderBottom: `1px solid ${theme.palette.divider}`,
  "& input": {
    borderRadius: theme.shape.borderRadius,
    color: theme.palette.text.primary,
    backgroundColor: theme.palette.background.default,
    border: `1px solid ${theme.palette.divider}`,
    padding: 8,
    transition: theme.transitions.create(["border-color", "box-shadow"]),
    fontSize: 14,
    "&:focus": {
      boxShadow: `0 0 0 3px ${theme.palette.action.selected}`,
      borderColor: theme.palette.primary.main,
    },
  },
}));

export function Picker({
  options,
  renderButton,
  id,
  description,
  onClose,
  ...props
}) {
  const [anchorEl, setAnchorEl] = useState(null);
  const [value, setValue] = useState([]);
  const [pendingValue, setPendingValue] = useState([]);

  const handleClick = (event) => {
    setPendingValue(value);
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setValue(pendingValue);
    onClose(pendingValue);
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
            <Autocomplete
              open
              multiple
              onClose={(event, reason) => {
                if (reason === "escape") {
                  handleClose();
                }
              }}
              value={pendingValue}
              onChange={(event, newValue, reason) => {
                if (
                  event.type === "keydown" &&
                  (event.key === "Backspace" || event.key === "Delete") &&
                  reason === "removeOption"
                ) {
                  return;
                }
                setPendingValue(newValue);
              }}
              disableCloseOnSelect
              renderTags={() => null}
              noOptionsText="No options"
              options={options}
              groupBy={(option) => option.team}
              renderInput={(params) => (
                <StyledInput
                  ref={params.InputProps.ref}
                  inputProps={params.inputProps}
                  autoFocus
                  placeholder="Filter options"
                />
              )}
              slots={{
                popper: PopperComponent,
              }}
              {...props}
            />
          </div>
        </ClickAwayListener>
      </StyledPopper>
    </Fragment>
  );
}
