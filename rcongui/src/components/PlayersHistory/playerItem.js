/* eslint-disable no-use-before-define */
import React from "react";
import {
  Paper,
  IconButton,
  Typography,
  Grid,
  Link,
  Popover,
} from "@material-ui/core";
import moment from "moment";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import FlagIcon from "@material-ui/icons/Flag";
import "emoji-mart/css/emoji-mart.css";
import Tooltip from "@material-ui/core/Tooltip";
import { getEmojiFlag } from "../../utils/emoji";
import PersonAddDisabledIcon from "@material-ui/icons/PersonAddDisabled";
import PersonAddIcon from "@material-ui/icons/PersonAdd";
import { faSteam } from "@fortawesome/free-brands-svg-icons";
import StarIcon from "@material-ui/icons/Star";
import StarBorder from "@material-ui/icons/StarBorder";
import HowToRegIcon from "@material-ui/icons/HowToReg";
import AccessTimeIcon from "@material-ui/icons/AccessTime";
import BlockIcon from "@material-ui/icons/Block";
import VisibilityIcon from "@material-ui/icons/Visibility";

const WithPopver = ({ classes, popoverContent, children }) => {
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handlePopoverOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handlePopoverClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);

  return (
    <React.Fragment>
      <div onMouseEnter={handlePopoverOpen} onMouseLeave={handlePopoverClose}>
        {children}
      </div>
      <Popover
        id="mouse-over-popover"
        className={classes.popover}
        classes={{
          paper: classes.paper,
        }}
        open={open}
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "left",
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "left",
        }}
        onClose={handlePopoverClose}
        disableRestoreFocus
      >
        {popoverContent}
      </Popover>
    </React.Fragment>
  );
};

const PlayerItem = ({
  classes,
  names,
  steamId64,
  firstSeen,
  lastSeen,
  blacklisted,
  punish,
  kick,
  tempban,
  permaban,
  onBlacklist,
  onUnBlacklist,
  onUnban,
  flags,
  onflag,
  onDeleteFlag,
  onAddVip,
  onDeleteVip,
  onTempBan,
  isVip,
  isWatched,
  onAddToWatchList,
  onRemoveFromWatchList,
  compact = true,
}) => {
  const now = moment();
  const last_seen = moment(lastSeen);
  const first_seen = moment(firstSeen);
  const extraneous = compact ? { display: "none" } : {};
  const penalites = [
    ["Punish", punish, ""],
    ["Kick", kick, classes.low],
    ["2H Ban", tempban, classes.mid],
    ["Perma Ban", permaban, classes.high],
  ];
  const isClean = !punish && !kick && !tempban && !permaban;

  return (
    <Grid container>
      <Grid item xs={12}>
        <Paper className={classes.padding}>
          <Grid
            container
            spacing={0}
            justify="flex-start"
            alignItems="flex-start"
          >
            <Grid item xs={12} sm={12}>
              <Grid container alignContent="flex-start" spacing={0}>
                <Grid item xs={12}>
                  <Typography variant="subtitle1" className={classes.ellipsis}>
                    {names}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <small style={{ display: "flex" }}>
                    <Link
                      target="_blank"
                      color="inherit"
                      href={`${process.env.REACT_APP_API_URL}player?steam_id_64=${steamId64}`}
                    >
                      {steamId64}
                    </Link>
                    <Link
                      className={classes.marginLeft}
                      target="_blank"
                      color="inherit"
                      href={`https://steamcommunity.com/profiles/${steamId64}`}
                    >
                      <FontAwesomeIcon icon={faSteam} />
                    </Link>
                  </small>
                </Grid>

                <Grid
                  container
                  justify="flex-start"
                  alignContent="center"
                  alignItems="center"
                  spacing={0}
                  className={classes.paddingTop}
                >
                  <Grid item>
                    <IconButton size="small">
                      {blacklisted ? (
                        <Tooltip
                          title="Remove the player from the blacklist"
                          arrow
                        >
                          <BlockIcon color="primary" onClick={onUnBlacklist} />
                        </Tooltip>
                      ) : (
                        <Tooltip title="Add the player to the blacklist" arrow>
                          <BlockIcon onClick={onBlacklist} />
                        </Tooltip>
                      )}
                    </IconButton>
                  </Grid>
                  <Grid item>
                    <IconButton size="small">
                      <Tooltip
                        title="Apply temp ban to player (time will start now)"
                        arrow
                      >
                        <AccessTimeIcon onClick={onTempBan} />
                      </Tooltip>
                    </IconButton>
                  </Grid>
                  <Grid item>
                    <IconButton size="small">
                      <Tooltip title="Remove all bans (temp or perma)" arrow>
                        <HowToRegIcon onClick={onUnban} />
                      </Tooltip>
                    </IconButton>
                  </Grid>
                  <Grid item>
                    <IconButton size="small">
                      <Tooltip title="Add Flag to player" arrow>
                        <FlagIcon onClick={onflag} />
                      </Tooltip>
                    </IconButton>
                  </Grid>
                  <Grid item>
                    <IconButton size="small">
                      {isVip ? (
                        <Tooltip title="Remove player from VIPs." arrow>
                          <StarBorder color="primary" onClick={onDeleteVip} />
                        </Tooltip>
                      ) : (
                        <Tooltip title="Add player to VIPs." arrow>
                          <StarIcon onClick={onAddVip} />
                        </Tooltip>
                      )}
                    </IconButton>
                  </Grid>
                  <Grid item>
                    <IconButton size="small">
                      {isWatched ? (
                        <Tooltip title="Remove player from watchlist" arrow>
                          <VisibilityIcon
                            color="primary"
                            onClick={onRemoveFromWatchList}
                          />
                        </Tooltip>
                      ) : (
                        <Tooltip title="Add player to watchlist" arrow>
                          <VisibilityIcon onClick={onAddToWatchList} />
                        </Tooltip>
                      )}
                    </IconButton>
                  </Grid>
                  {flags.map((d) => (
                    <Grid item className={classes.noPaddingMargin}>
                      <Link
                        onClick={() =>
                          window.confirm("Delete flag?")
                            ? onDeleteFlag(d.get("id"))
                            : ""
                        }
                      >
                        {getEmojiFlag(d.get("flag"))}
                      </Link>
                    </Grid>
                  ))}
                </Grid>
              </Grid>
            </Grid>
          </Grid>
          <Grid
            container
            justify="space-between"
            spacing={0}
            style={extraneous}
            className={classes.padding}
          >
            <Grid item xs={6}>
              <WithPopver
                classes={classes}
                popoverContent={<p>{first_seen.format("LLLL")}</p>}
              >
                <small>
                  First seen {moment.duration(now.diff(first_seen)).humanize()}{" "}
                  ago
                </small>
              </WithPopver>
            </Grid>
            <Grid item xs={6}>
              <WithPopver
                classes={classes}
                popoverContent={<p>{last_seen.format("LLLL")}</p>}
              >
                <small>
                  Last seen {moment.duration(now.diff(last_seen)).humanize()}{" "}
                  ago
                </small>
              </WithPopver>
            </Grid>
            <Grid item xs={12}>
              <small>
                {isClean ? "Immaculate record" : ""}
                {penalites.map((e) => {
                  if (e[1] > 0) {
                    return (
                      <span className={classes.marginRight}>
                        {e[0]}: <strong className={e[2]}>{e[1]}</strong>
                      </span>
                    );
                  }
                })}
              </small>
            </Grid>
          </Grid>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default PlayerItem;
