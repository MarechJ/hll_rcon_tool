import React, { Component } from "react";
import Button from "@material-ui/core/Button";
import Chip from '@material-ui/core/Chip'
import ButtonGroup from "@material-ui/core/ButtonGroup";
import TextField from "@material-ui/core/TextField";
import _ from "lodash";
import Badge from '@material-ui/core/Badge';
import Menu from "@material-ui/core/Menu";
import MenuItem from "@material-ui/core/MenuItem";
import ArrowDropDownIcon from "@material-ui/icons/ArrowDropDown";
import "react-toastify/dist/ReactToastify.css";
import useStyles from "../useStyles";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogTitle from "@material-ui/core/DialogTitle";
import { Map } from 'immutable';
import FlagOutlinedIcon from '@material-ui/icons/FlagOutlined';

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

const DropMenu = ({ startIdx, actions, handleAction }) => {
  return <React.Fragment></React.Fragment>;
};

const PlayerActions = ({ size, handleAction, onFlag, displayCount = 3, disable = false, penaltyCount = Map() }) => {
  const classes = useStyles();
  const [anchorEl, setAnchorEl] = React.useState(null);
  const handleClick = event => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };
  const remap_penalties = {
    "perma_ban": 'PERMABAN',
    'punish': "PUNISH",
    'kick': "KICK",
    "temp_ban": "TEMPBAN"
  }

  const actions = [
    ["punish", "PUNISH"],
    ["kick", "KICK"],
    ["temp_ban", "2H BAN"],
    ["switch_player_now", "SWITCH"],
    ["switch_player_on_death", "SWITCH ON DEATH"],
    ["perma_ban", "PERMA BAN"]
  ];
  const show = Math.min(displayCount, actions.length);

  return (
    <React.Fragment>
      <ButtonGroup size={size} aria-label="small outlined button group">

        {_.range(show).map(idx => (
          <Button disabled={disable && !actions[idx][0].startsWith("switch")} onClick={() => handleAction(actions[idx][0])}>
            <Badge size="small" color="secondary" max={9} badgeContent={penaltyCount.get(remap_penalties[actions[idx][0]], 0)}>{actions[idx][1]}</Badge>
          </Button>
        ))}
        { onFlag ? <Button size="small" onClick={onFlag}><FlagOutlinedIcon fontSize="small" /></Button> : ''}
        {show < actions.length ?
          <Button
            disabled={disable}
            aria-controls="simple-menu"
            aria-haspopup="true"
            onClick={handleClick}
          >
            <ArrowDropDownIcon />
          </Button> : ""}
      </ButtonGroup>
      {show < actions.length ? (
        <Menu
          id="simple-menu"
          anchorEl={anchorEl}
          keepMounted
          open={Boolean(anchorEl)}
          onClose={handleClose}
        >
          {_.range(show, actions.length).map(idx => {
            const count = penaltyCount.get(remap_penalties[actions[idx][0]], 0)
            return <MenuItem
              onClick={() => {
                handleAction(actions[idx][0]);
                handleClose();
              }}
            >
              {actions[idx][1]}{count > 0 ? <Chip size="small" color="secondary" label={count} /> : ''}
            </MenuItem>
          })}
        </Menu>
      ) : (
          ""
        )}
    </React.Fragment>
  );
};

export { ReasonDialog, PlayerActions };
