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
import ReportIcon from "@material-ui/icons/Report";


export const ActionButton = ({
  blacklisted,
  onUnBlacklist,
  onBlacklist,
  onTempBan,
  onPermaBan,
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
      {blacklisted ? (
        <Tooltip
          title="Remove the player from the blacklist. This will also remove any bans already applied."
          arrow
        >
          <Button>
            <BlockIcon size="small" color="primary" onClick={onUnBlacklist} />
          </Button>
        </Tooltip>
      ) : (
        <Tooltip
          title="Blacklist the player"
          arrow
        >
          <Button>
            <BlockIcon size="small" onClick={onBlacklist} />
          </Button>
        </Tooltip>
      )}

      <Tooltip
        title="Apply temp ban to player (time will start from now). Applies only to the current server, use the Blacklist feature with an expiration date to apply to all servers"
        arrow
      >
        <Button>
          <AccessTimeIcon size="small" onClick={onTempBan} />
        </Button>
      </Tooltip>
      <Tooltip
        title="Apply perma ban to player. Applies only to the current server, use the Blacklist feature to apply to all servers"
        arrow
      >
        <Button>
          <ReportIcon size="small" onClick={onPermaBan} />
        </Button>
      </Tooltip>

      <Tooltip title="Remove all bans (temp or perma)" arrow>
        <Button>
          <HowToRegIcon size="small" onClick={onUnban} />
        </Button>
      </Tooltip>

      <Tooltip title="Add a Flag to the player" arrow>
        <Button>
          <FlagIcon size="small" onClick={onflag} />
        </Button>
      </Tooltip>

      <Tooltip title="Manage player's VIP" arrow>
        <Button color={isVip && "secondary"}>
          <StarIcon size="small" onClick={onAddVip} />
        </Button>
      </Tooltip>

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
