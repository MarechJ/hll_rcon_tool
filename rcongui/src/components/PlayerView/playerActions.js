import React, { Component } from "react";
import Button from "@material-ui/core/Button";
import Chip from "@material-ui/core/Chip";
import ButtonGroup from "@material-ui/core/ButtonGroup";
import TextField from "@material-ui/core/TextField";
import _ from "lodash";
import Badge from "@material-ui/core/Badge";
import Menu from "@material-ui/core/Menu";
import MenuItem from "@material-ui/core/MenuItem";
import ArrowDropDownIcon from "@material-ui/icons/ArrowDropDown";
import "react-toastify/dist/ReactToastify.css";
import useStyles from "../useStyles";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogTitle from "@material-ui/core/DialogTitle";
import { Map } from "immutable";
import FlagOutlinedIcon from "@material-ui/icons/FlagOutlined";
import TextHistory from "../textHistory";
import Autocomplete from "@material-ui/lab/Autocomplete";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import Checkbox from "@material-ui/core/Checkbox";
import { getSharedMessages } from "../../utils/fetchUtils";

class ReasonDialog extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      reason: "",
      saveMessage: true,
      sharedMessages: [],
    };

    this.onChange = this.onChange.bind(this);
  }

  componentDidMount() {
    getSharedMessages("punitions").then((data) =>
      this.setState({ sharedMessages: data })
    );
  }

  onChange(e, value) {
    e.preventDefault();
    this.setState({ reason: value });
  }

  render() {
    const { open, handleClose, handleConfirm } = this.props;
    const { reason, saveMessage, sharedMessages } = this.state;
    const textHistory = new TextHistory("punitions");

    return (
      <Dialog open={open} aria-labelledby="form-dialog-title">
        <DialogTitle id="form-dialog-title">
          Execute {open.actionType} on {open.player}
        </DialogTitle>
        <DialogContent>
          <Autocomplete
            freeSolo
            fullWidth
            options={sharedMessages.concat(textHistory.getTexts())}
            inputValue={reason}
            onInputChange={(e, value) => this.onChange(e, value)}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Reason"
                margin="dense"
                helperText="A message is mandatory"
              />
            )}
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={saveMessage}
                onChange={() => this.setState({ saveMessage: !saveMessage })}
                color="primary"
              />
            }
            label="Save message as template"
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
              if (saveMessage) {
                textHistory.saveText(reason, sharedMessages);
              }
              handleConfirm(open.actionType, open.player, reason);
              this.setState({ reason: "" });
            }}
            color="primary"
            disabled={!reason}
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

const PlayerActions = ({
  size,
  handleAction,
  onFlag,
  displayCount = 3,
  disable = false,
  penaltyCount = Map(),
}) => {
  const classes = useStyles();
  const [anchorEl, setAnchorEl] = React.useState(null);
  const [isOpen, setOpen] = React.useState(false);
  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
    setOpen(true);
  };
  const handleClose = () => {
    setOpen(false);
  };
  const remap_penalties = {
    perma_ban: "PERMABAN",
    punish: "PUNISH",
    kick: "KICK",
    temp_ban: "TEMPBAN",
  };

  const actions = [
    ["punish", "PUNISH"],
    ["kick", "KICK"],
    ["temp_ban", "2H BAN"],
    ["switch_player_now", "SWITCH"],
    ["switch_player_on_death", "SWITCH ON DEATH"],
    ["perma_ban", "PERMA BAN"],
  ];
  const show = Math.min(displayCount, actions.length);

  return (
    <React.Fragment>
      <ButtonGroup size={size} aria-label="small outlined button group">
        {_.range(show).map((idx) => (
          <Button
            key={actions[idx][0]}
            disabled={disable && !actions[idx][0].startsWith("switch")}
            onClick={() => handleAction(actions[idx][0])}
          >
            <Badge
              size="small"
              color="primary"
              max={9}
              badgeContent={penaltyCount.get(
                remap_penalties[actions[idx][0]],
                0
              )}
            >
              {actions[idx][1]}
            </Badge>
          </Button>
        ))}
        {onFlag ? (
          <Button size="small" onClick={onFlag}>
            <FlagOutlinedIcon fontSize="small" />
          </Button>
        ) : (
          ""
        )}
        {show < actions.length ? (
          <Button
            disabled={disable}
            aria-controls="simple-menu"
            aria-haspopup="true"
            onClick={handleClick}
          >
            <ArrowDropDownIcon />
          </Button>
        ) : (
          ""
        )}
      </ButtonGroup>
      {show < actions.length ? (
        <Menu
          id="simple-menu"
          anchorEl={anchorEl}
          keepMounted
          open={isOpen}
          onClose={handleClose}
        >
          {_.range(show, actions.length).map((idx) => {
            const count = penaltyCount.get(remap_penalties[actions[idx][0]], 0);
            return (
              <MenuItem
                key={actions[idx][0]}
                onClick={() => {
                  handleAction(actions[idx][0]);
                  handleClose();
                }}
              >
                {actions[idx][1]}
                {count > 0 ? (
                  <Chip size="small" color="primary" label={count} />
                ) : (
                  ""
                )}
              </MenuItem>
            );
          })}
        </Menu>
      ) : (
        ""
      )}
    </React.Fragment>
  );
};

export { ReasonDialog, PlayerActions };
