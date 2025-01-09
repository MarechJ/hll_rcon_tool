import {Fragment, useState} from "react";
import ListItem from "@mui/material/ListItem";
import ListItemSecondaryAction from "@mui/material/ListItemSecondaryAction";
import ListItemText from "@mui/material/ListItemText";
import "react-toastify/dist/ReactToastify.css";
import { PlayerActions } from "./playerActions";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faExclamationCircle,
  faLock,
  faQuestionCircle,
  faStar,
} from "@fortawesome/free-solid-svg-icons";
import { faSteam, faWindows } from "@fortawesome/free-brands-svg-icons";
import Link from "@mui/material/Link";
import Icon from "@mui/material/Icon";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import { getEmoji } from "@/utils/emoji";
import { Map } from "immutable";
import { getName } from "country-list";
import Popover from "@mui/material/Popover";
import Typography from "@mui/material/Typography";
import { Link as RouterLink } from "react-router-dom";
import {
  Avatar,
  Badge,
  Checkbox,
  Chip,
  ListItemAvatar,
} from "@mui/material";
import makePlayerProfileUrl from "../../utils/makePlayerProfileUrl";
import moment from "moment";
import Grid from "@mui/material/Grid2";


const zeroPad = (num, places) => String(num).padStart(places, "0");

function WithPopOver(props) {
  const [anchorEl, setAnchorEl] = useState(null);

  const handlePopoverOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handlePopoverClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);

  return (
    <Fragment>
      <Typography
        style={{ display: "inline" }}
        aria-owns={open ? "mouse-over-popover" : undefined}
        aria-haspopup="true"
        onMouseEnter={handlePopoverOpen}
        onMouseLeave={handlePopoverClose}
      >
        {props.children}
      </Typography>
      <Popover
        id="mouse-over-popover"
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
        <Typography>{props.content}</Typography>
      </Popover>
    </Fragment>
  );
}

function seconds_to_time(seconds) {
  const hours = Math.trunc(seconds / 60 / 60);
  const minutes = Math.trunc(seconds / 60 - hours * 60);

  return `${zeroPad(hours, 2)}:${zeroPad(minutes, 2)}`;
}

const getCountry = (player) => {
  const country = player.get("country");

  if (country === "private") {
    return (
      <WithPopOver content="Account is private">
        <FontAwesomeIcon icon={faLock} />
      </WithPopOver>
    );
  }
  if (country === "" || country === null) {
    return (
      <WithPopOver content="No country specified">
        <FontAwesomeIcon icon={faQuestionCircle} />
      </WithPopOver>
    );
  }
  return (
    <img
      alt={country}
      title={country ? getName(country) : ""}
      style={{ height: "12px" }}
      src={`https://catamphetamine.gitlab.io/country-flag-icons/3x2/${country}.svg`}
    />
  );
};

const getBans = (profile) => {
  return profile.get("steam_bans") &&
    profile.get("steam_bans").get("has_bans") === true ? (
    <WithPopOver
      content={`Players has bans: ${JSON.stringify(profile.get("steam_bans"))}`}
    >
      <FontAwesomeIcon color="red" icon={faExclamationCircle} />
    </WithPopOver>
  ) : (
    ""
  );
};

const Flag = ({ data, onDeleteFlag }) => {
  return (
    <Link
      onClick={() =>
        window.confirm("Delete flag?") ? onDeleteFlag(data.get("id")) : ""
      }
    >
      <WithPopOver content={`Comment: ${data.get("comment")}`}>
        {getEmoji(data.get("flag"), 22)}
      </WithPopOver>
    </Link>
  )
};

const formatPunitions = (profile) => {
  const formatTime = (item) =>
    moment.utc(item.get("time")).local().format("ddd Do MMM HH:mm:ss");
  return profile
    .get("received_actions", [])
    .map((item) => (
      <Typography display="block" variant="caption" key={item}>{`${formatTime(
        item
      )} ${item.get("action_type")} by ${item.get("by")}: ${item.get(
        "reason"
      )}`}</Typography>
    ));
};

const ScoreChips = ({ player }) => {
  return (
    <Fragment>
      <Grid>
        <Chip
          size="small"
          variant="outlined"
          avatar={
            <Avatar
              alt="Combat"
              src="icons/roles/score_combat.png"
            />
          }
          label={player.get("combat", 0)}
        />
      </Grid>
      <Grid>
        <Chip
          size="small"
          variant="outlined"
          avatar={
            <Avatar
              alt="Offensive"
              src="icons/roles/score_offensive.png"
            />
          }
          label={player.get("offense", 0)}
        />
      </Grid>
      <Grid>
        <Chip
          size="small"
          variant="outlined"
          avatar={
            <Avatar
              alt="Defensive"
              src="icons/roles/score_defensive.png"
            />
          }
          label={player.get("defense", 0)}
        />
      </Grid>
      <Grid>
        <Chip
          size="small"
          variant="outlined"
          avatar={
            <Avatar
              alt="Support"
              src="icons/roles/score_support.png"
            />
          }
          label={player.get("support", 0)}
        />
      </Grid>
    </Fragment>
  );
};

const KDChips = ({ player }) => {

  return (
    <Fragment>
      <Grid>
        <Chip
          size="small"
          variant="outlined"
          label={`K: ${player.get("kills")}`}
        />
      </Grid>
      <Grid>
        <Chip
          size="small"
          variant="outlined"
          label={`D: ${player.get("deaths")}`}
        />
      </Grid>
      <Grid>
        <Chip
          size="small"
          variant="outlined"
          label={`KD: ${(
            player.get("kills", 0) / Math.max(player.get("deaths", 1), 1)
          ).toFixed(2)}`}
        />
      </Grid>
      {player.get("loadout") ? (
        <Grid>
          <Chip size="small" label={player.get("loadout", "")} />
        </Grid>
      ) : (
        ""
      )}
    </Fragment>
  );
};

const ScoreListText = ({ player }) => {

  return (
    <ListItemText
      primary={
        <Grid container spacing={1}>
          <ScoreChips
            player={player}
          />
        </Grid>
      }
      secondary={
        <Grid container spacing={1}>
          <KDChips player={player} />
        </Grid>
      }
    />
  );
};

const PlayerItem = ({
  player,
  handleAction,
  nbButtons,
  onFlag,
  onDeleteFlag,
  playerHasExtraInfo,
  onSelect,
  isSelected,
  onBlacklist,
  onVipDialogOpen,
}) => {
  const profile = player.get("profile") ? player.get("profile") : new Map();
  const name = player.get("name");
  const player_id = player.get("player_id");

  return (
    <ListItem key={name} dense selected={isSelected}>
      {playerHasExtraInfo ? (
        <ListItemAvatar>
          <Badge
            badgeContent={player.get("level", 0)}
            max={999}
            anchorOrigin={{
              vertical: "bottom",
              horizontal: "right",
            }}
          >
            <Avatar
              variant="square"
              src={`icons/roles/${player.get("role", "rifleman")}.png`}
            ></Avatar>
          </Badge>
        </ListItemAvatar>
      ) : (
        ""
      )}

      <ListItemText
        id={`checkbox-list-label-${player_id}`}
        primary={
          <Fragment>
            <WithPopOver content={formatPunitions(profile)}>{name}</WithPopOver>
            {" - "}
            {getCountry(player)}
            {" - "}
            {player.get("is_vip") ? (
              <Fragment>
                <FontAwesomeIcon icon={faStar} />
                {" - "}
              </Fragment>
            ) : (
              ""
            )}
            <Link
              target="_blank"
              color="inherit"
              href={makePlayerProfileUrl(player_id, name)}
            >
              <FontAwesomeIcon
                icon={player_id.length === 17 ? faSteam : faWindows}
              />
            </Link>
          </Fragment>
        }
        secondary={
          <Fragment>
            <span>
              {seconds_to_time(profile.get("current_playtime_seconds"))} - #
              {profile.get("sessions_count")} - {getBans(player)}
            </span>{" "}
            <Link
              color="inherit"
              component={RouterLink}
              to={`/records/players/${player.get("player_id")}`}
            >
              {player_id} <Icon component={OpenInNewIcon} fontSize="inherit" />
            </Link>
            <div>
              {profile.get("flags", []).map((d) => (
                <Flag key={d} data={d} onDeleteFlag={onDeleteFlag} />
              ))}
            </div>
          </Fragment>
        }
      />
      {playerHasExtraInfo ? (
        <ScoreListText player={player} />
      ) : (
        ""
      )}

      {handleAction ? (
        <ListItemSecondaryAction>
          <PlayerActions
            size="small"
            handleAction={handleAction}
            onFlag={onFlag}
            onBlacklist={onBlacklist}
            onVipDialogOpen={onVipDialogOpen}
            displayCount={nbButtons}
            isWatched={
              profile.get("watchlist")
                ? profile.get("watchlist").get("is_watched", false)
                : false
            }
            penaltyCount={profile.get("penalty_count", Map())}
          />
        </ListItemSecondaryAction>
      ) : (
        ""
      )}

      {onSelect ? (
        <ListItemSecondaryAction>
          <Checkbox checked={isSelected} onChange={onSelect} />
        </ListItemSecondaryAction>
      ) : (
        ""
      )}
    </ListItem>
  );
};

const weightedPenalities = (penaltiesMap) => {
  const weights = {
    PUNISH: 1,
    KICK: 4,
    TEMPBAN: 10,
    PERMABAN: 100,
  };
  const res = penaltiesMap.reduce(
    (sum, value, key) => sum + weights[key] * value,
    0
  );
  console.log("Weighted penalites", res);
  return res;
};

const getSortedPlayers = (players, sortType) => {
  let myPlayers = players;
  const [direction, type] = sortType.split("_");

  if (!sortType || sortType === "") {
    return myPlayers;
  }

  const sortFuncs = {
    alpha: (p) => p.get("name").toLowerCase(),
    time: (p) =>
      !p.get("profile") ? 0 : p.get("profile").get("current_playtime_seconds"),
    country: (p) => {
      const country = p.get("country");
      if (!country) {
        return "zzy";
      }
      if (country === "private") return "zzz";
      return country;
    },
    sessions: (p) =>
      !p.get("profile") ? 0 : p.get("profile").get("sessions_count"),
    penalties: (p) =>
      !p.get("profile")
        ? 0
        : weightedPenalities(p.get("profile").get("penalty_count")),
    vips: (p) => p.get("is_vip"),
  };

  myPlayers = myPlayers.sortBy(sortFuncs[type]);

  if (direction === "desc") {
    myPlayers = myPlayers.reverse();
  }

  return myPlayers;
};

export { PlayerItem, ScoreListText, ScoreChips, KDChips };
