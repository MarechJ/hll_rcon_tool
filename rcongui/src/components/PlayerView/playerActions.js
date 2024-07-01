import React from "react";
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
import { Grid } from "@material-ui/core";
import Tooltip from "@material-ui/core/Tooltip";
import MessageIcon from "@material-ui/icons/Message";
import VisibilityIcon from "@material-ui/icons/Visibility";

const Duration = ({
  durationNumber,
  onNumberChange,
  durationMultiplier,
  onMultiplierChange,
}) => (
  <Grid container spacing={1}>
    <Grid item>
      <TextField
        style={{ minWidth: "200px" }}
        label="TempBan Duration number"
        type="number"
        shrink
        margin="dense"
        value={durationNumber}
        onChange={(event) => onNumberChange(event.target.value)}
      />
    </Grid>
    <Grid item>
      <TextField
        style={{ minWidth: "200px" }}
        select
        value={durationMultiplier}
        onChange={(event) => onMultiplierChange(event.target.value)}
        margin="dense"
        label="TempBan Duration unit"
      >
        <MenuItem key="hours" value={1}>
          hours
        </MenuItem>
        <MenuItem key="days" value={24}>
          days
        </MenuItem>
        <MenuItem key="weeks" value={24 * 7}>
          weeks
        </MenuItem>
        <MenuItem key="months" value={24 * 7 * 4}>
          months
        </MenuItem>
      </TextField>
    </Grid>
  </Grid>
);

class ReasonDialog extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      reason: "",
      comment: "",
      saveMessage: true,
      durationNumber: 2,
      durationMultiplier: 1,
      sharedMessages: [],
    };

    this.onChange = this.onChange.bind(this);
  }

  componentDidMount() {
    getSharedMessages("punishments").then((data) =>
      this.setState({ sharedMessages: data })
    );
  }

  onChange(e, value) {
    if (e) {
      e.preventDefault();
    }

    this.setState({ reason: value });
  }

  mapActionToText(actionType, playerName) {
    switch (actionType) {
      case "watch_player":
        return `Add a watch to ${playerName}`;
      case "punish":
        return `Punish (kill in game) ${playerName}`;
      case "kick":
        return `Kick ${playerName} from the game`;
      case "temp_ban":
        return `Temporary Ban ${playerName}`;
      case "perma_ban":
        return `Permanently Ban ${playerName}`;
      case "message_player":
        return `Message ${playerName}`;
      default:
        return "";
    }
  }

  render() {
    const { open, handleClose, handleConfirm } = this.props;
    const {
      reason,
      comment,
      saveMessage,
      sharedMessages,
      durationNumber,
      durationMultiplier,
    } = this.state;
    const textHistory = new TextHistory("punishments");
    const actionType = open.actionType;
    const playerName = open.player;
    return (
      <Dialog open={open} aria-labelledby="form-dialog-title">
        <DialogTitle id="form-dialog-title">
          {this.mapActionToText(actionType, playerName)}
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
                multiline
                rows={4}
                rowsMax={10}
                label={actionType === "message_player" ? "Message" : "Reason"}
                variant="outlined"
                margin="dense"
                helperText="The message that will be displayed to the player. A message is mandatory"
              />
            )}
          />

          {open.actionType !== "message_player" ? (
            <TextField
              multiline
              rows={4}
              rowsMax={10}
              fullWidth
              value={comment}
              onChange={(e) => this.setState({ comment: e.target.value })}
              label="Comment"
              variant="outlined"
              margin="dense"
              helperText="A comment that will NOT be displayed to the player"
            />
          ) : (
            ""
          )}
          {open.actionType === "temp_ban" ? (
            <Duration
              durationNumber={durationNumber}
              onNumberChange={(number) =>
                this.setState({ durationNumber: number })
              }
              durationMultiplier={durationMultiplier}
              onMultiplierChange={(multiplier) =>
                this.setState({ durationMultiplier: multiplier })
              }
            />
          ) : (
            ""
          )}
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
              handleConfirm(
                open.actionType,
                open.player,
                reason,
                comment,
                durationMultiplier * durationNumber,
                open.player_id
              );
              this.setState({ reason: "", comment: "" });
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

const PlayerActions = ({
  size,
  handleAction,
  onFlag,
  isWatched,
  displayCount = 3,
  disable = false,
  penaltyCount = Map(),
  disableAll = false,
}) => {
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
    ["temp_ban", "TEMP BAN"],
    ["switch_player_now", "SWITCH"],
    ["switch_player_on_death", "SWITCH ON DEATH"],
    ["perma_ban", "PERMA BAN"],
  ];
  const show = Math.min(displayCount, actions.length);

  return (
    <React.Fragment>
      <ButtonGroup
        size={size}
        disabled={disableAll}
        aria-label="small outlined button group"
      >
        <Tooltip title="Message Player">
          <Button onClick={() => handleAction("message_player")}>
            <MessageIcon />
          </Button>
        </Tooltip>
        {show > 1 ? (
          <Tooltip title="Watch Player">
            <Button
              color={isWatched ? "primary" : "default"}
              variant={isWatched ? "contained" : "outlined"}
              size="small"
              onClick={() =>
                handleAction(isWatched ? "unwatch_player" : "watch_player")
              }
            >
              <VisibilityIcon fontSize="small" />
            </Button>
          </Tooltip>
        ) : (
          ""
        )}
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
          <Tooltip title="Flag Player">
            <Button size="small" onClick={onFlag}>
              <FlagOutlinedIcon fontSize="small" />
            </Button>
          </Tooltip>
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
          {show <= 1 ? (
            <MenuItem
              size="small"
              onClick={() =>
                handleAction(isWatched ? "unwatch_player" : "watch_player")
              }
            >
              <VisibilityIcon
                color={isWatched ? "primary" : "default"}
                fontSize="small"
              />
            </MenuItem>
          ) : (
            ""
          )}
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

export { ReasonDialog, PlayerActions, Duration };
