import { ButtonGroup, Button } from "@material-ui/core";
import React from "react";
import FlagIcon from "@material-ui/icons/Flag";
import Tooltip from "@material-ui/core/Tooltip";
import StarIcon from "@material-ui/icons/Star";
import StarBorder from "@material-ui/icons/StarBorder";
import HowToRegIcon from "@material-ui/icons/HowToReg";
import AccessTimeIcon from "@material-ui/icons/AccessTime";
import BlockIcon from "@material-ui/icons/Block";
import VisibilityIcon from "@material-ui/icons/Visibility";

export const ActionButton = ({
  blacklisted,
  onUnBlacklist,
  onBlacklist,
  onTempBan,
  onUnban,
  onflag,
  isVip,
  onAddVip,
  onDeleteVip,
  isWatched,
  onAddToWatchList,
  onRemoveFromWatchList,
}) => {
  return (
    <ButtonGroup size="small" variant="text">
      <Button>
        {blacklisted ? (
          <Tooltip
            title="Remove the player from the blacklist. This will also remove any bans already applied."
            arrow
          >
            <BlockIcon size="small" color="primary" onClick={onUnBlacklist} />
          </Tooltip>
        ) : (
          <Tooltip
            title="Blacklist the player"
            arrow
          >
            <BlockIcon size="small" onClick={onBlacklist} />
          </Tooltip>
        )}
      </Button>

      <Button>
        <Tooltip
          title="Apply temp ban to player (time will start from now). (applied to all servers)"
          arrow
        >
          <AccessTimeIcon size="small" onClick={onTempBan} />
        </Tooltip>
      </Button>

      <Button>
        <Tooltip title="Remove all bans (temp or perma)" arrow>
          <HowToRegIcon size="small" onClick={onUnban} />
        </Tooltip>
      </Button>

      <Button>
        <Tooltip title="Add a Flag to the player" arrow>
          <FlagIcon size="small" onClick={onflag} />
        </Tooltip>
      </Button>

      <Button>
        {isVip ? (
          <Tooltip title="Remove player from VIPs." arrow>
            <StarBorder color="primary" onClick={onDeleteVip} />
          </Tooltip>
        ) : (
          <Tooltip title="Add player to VIPs." arrow>
            <StarIcon size="small" onClick={onAddVip} />
          </Tooltip>
        )}
      </Button>

      <Button>
        {isWatched ? (
          <Tooltip title="Remove player from the watchlist." arrow>
            <VisibilityIcon
              size="small"
              color="primary"
              onClick={onRemoveFromWatchList}
            />
          </Tooltip>
        ) : (
          <Tooltip
            title="Add player to watchlist. You'll be notified on your configured webhook(s) upon their connections"
            arrow
          >
            <VisibilityIcon size="small" onClick={onAddToWatchList} />
          </Tooltip>
        )}
      </Button>
    </ButtonGroup>
  );
};
