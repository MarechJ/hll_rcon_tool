import React, { Component } from "react";
import Button from "@material-ui/core/Button";
import ButtonGroup from "@material-ui/core/ButtonGroup";
import TextField from "@material-ui/core/TextField";
import _ from "lodash";
import Menu from "@material-ui/core/Menu";
import MenuItem from "@material-ui/core/MenuItem";
import ArrowDropDownIcon from "@material-ui/icons/ArrowDropDown";
import "react-toastify/dist/ReactToastify.css";
import useStyles from "../useStyles";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogTitle from "@material-ui/core/DialogTitle";

class ReasonDialog extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      reason: ""
    };

    this.onChange = this.onChange.bind(this);
  }

  onChange(e) {
    e.preventDefault();
    this.setState({ reason: e.target.value });
  }

  render() {
    const { open, handleClose, handleConfirm } = this.props;
    const { reason } = this.state;

    return (
      <Dialog open={open} aria-labelledby="form-dialog-title">
        <DialogTitle id="form-dialog-title">
          Execute {open.actionType} on {open.player}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="name"
            label="Reason"
            value={reason}
            onChange={this.onChange}
            fullWidth
          />
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              this.setState({ reason: "" }, handleClose);
            }}
            color="primary"
          >
            Cancel
          </Button>
          <Button
            onClick={() => {
              handleConfirm(open.actionType, open.player, reason);
              this.setState({ reason: "" });
            }}
            color="primary"
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    );
  }
}

const PlayerActions = ({ size, handleAction }) => {
  const classes = useStyles();
  const [anchorEl, setAnchorEl] = React.useState(null);
  const handleClick = event => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <React.Fragment>
      <ButtonGroup size={size} aria-label="small outlined button group">
        <Button onClick={() => handleAction("punish")}>PUNISH</Button>
        <Button onClick={() => handleAction("kick")}>KICK</Button>
        <Button onClick={() => handleAction("temp_ban")}>2H BAN</Button>
        <Button
          aria-controls="simple-menu"
          aria-haspopup="true"
          onClick={handleClick}
        >
          <ArrowDropDownIcon />
        </Button>
        <Menu
          id="simple-menu"
          anchorEl={anchorEl}
          keepMounted
          open={Boolean(anchorEl)}
          onClose={handleClose}
        >
          <MenuItem
            onClick={() => {
              handleAction("switch_player_now");
              handleClose();
            }}
          >
            Switch team now
          </MenuItem>
          <MenuItem
            onClick={() => {
              handleAction("switch_player_on_death");
              handleClose();
            }}
          >
            Switch team on death
          </MenuItem>
          <MenuItem
            onClick={() => {
              handleAction("perma_ban");
              handleClose();
            }}
          >
            Perma Ban
          </MenuItem>
        </Menu>
      </ButtonGroup>
    </React.Fragment>
  );
};

export { ReasonDialog, PlayerActions };
