import React from "react";
import {
  addPlayerToWatchList,
  get,
  handle_http_errors,
  postData,
  sendAction,
  showResponse,
} from "../../utils/fetchUtils";
import { toast } from "react-toastify";
import { reduce } from "lodash";
import Pagination from "@material-ui/lab/Pagination";
import {
  Button,
  Chip,
  Grid,
  LinearProgress,
  TextField,
  Typography,
} from "@material-ui/core";
import { ReasonDialog } from "../PlayerView/playerActions";
import { omitBy } from "lodash/object";
import SearchBar from "./searchBar";
import { fromJS, List, Map } from "immutable";
import FlagIcon from "@material-ui/icons/Flag";
import "emoji-mart/css/emoji-mart.css";
import { Picker } from "emoji-mart";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogTitle from "@material-ui/core/DialogTitle";
import { getEmojiFlag } from "../../utils/emoji";
import PlayerGrid from "./playerGrid";
import { VipExpirationDialog } from "../VipDialog";
import { vipListFromServer } from "../VipDialog/vipFromServer";
import { banListFromServer } from "../PlayersHistory/PlayerTile/PlayerBan";

const PlayerSummary = ({ player, flag }) => (
  <React.Fragment>
    <Typography variant="body2">
      Add flag: {flag ? getEmojiFlag(flag) : <small>Please choose</small>}
    </Typography>
    <Typography variant="body2">
      To:{" "}
      {player && player.get("names")
        ? player.get("names").map((n) => <Chip label={n.get("name")} />)
        : "No name recorded"}
    </Typography>
    <Typography variant="body2">
      Steamd id: {player ? player.get("steam_id_64") : ""}
    </Typography>
  </React.Fragment>
);

class FlagDialog extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      flag: null,
      comment: "",
    };
  }

  render() {
    const { open, handleClose, handleConfirm, SummaryRenderer } = this.props;
    const { flag, comment } = this.state;

    return (
      <Dialog open={open} aria-labelledby="form-dialog-title">
        <DialogTitle id="form-dialog-title">
          <SummaryRenderer player={open} flag={flag} />
        </DialogTitle>
        <DialogContent>
          <Grid
            container
            alignContent="center"
            alignItems="center"
            justify="center"
            spacing={2}
          >
            <Grid item xs={12}>
              <TextField
                label="Comment"
                value={comment}
                onChange={(e) => this.setState({ comment: e.target.value })}
              />
            </Grid>
          </Grid>
          <Grid
            container
            alignContent="center"
            alignItems="center"
            justify="center"
            spacing={2}
          >
            <Grid item xs={12}>
              <Picker
                onSelect={(emoji) => this.setState({ flag: emoji.native })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              this.setState({ flag: "" });
              handleClose();
            }}
            color="primary"
          >
            Cancel
          </Button>
          <Button
            onClick={() => {
              handleConfirm(open, flag, comment);
              this.setState({ flag: "", comment: "" });
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

const FlagButton = ({ classes, onflag }) => (
  <Button variant="outlined" onClick={onflag}>
    <FlagIcon />
  </Button>
);

const MyPagination = ({ classes, pageSize, total, page, setPage }) => (
  <Pagination
    count={Math.ceil(total / pageSize)}
    page={page}
    onChange={(e, val) => setPage(val)}
    variant="outlined"
    color="default"
    showFirstButton
    showLastButton
    className={classes.pagination}
  />
);

class PlayersHistory extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      playersHistory: List(),
      total: 0,
      pageSize: 50,
      page: 1,
      byName: "",
      bySteamId: "",
      blacklistedOnly: false,
      lastSeenFrom: null,
      lastSeenUntil: null,
      isLoading: false,
      isWatchedOnly: false,
      vips: new Map(),
      doFlag: false,
      doConfirmPlayer: false,
      doVIPPlayer: false,
      ignoreAccent: true,
      exactMatch: false,
      flags: "",
      country: "",
      bans: new Map(),
    };

    this.getPlayerHistory = this.getPlayerHistory.bind(this);
    this.loadBans = this.loadBans.bind(this);
    this.blacklistPlayer = this.blacklistPlayer.bind(this);
    this.unblacklistPlayer = this.unblacklistPlayer.bind(this);
    this.addFlagToPlayer = this.addFlagToPlayer.bind(this);
    this.deleteFlag = this.deleteFlag.bind(this);
    this.loadVips = this.loadVips.bind(this);
    this.addVip = this.addVip.bind(this);
    this.deleteVip = this.deleteVip.bind(this);
    this.unBanPlayer = this.unBanPlayer.bind(this);
    this.tempBan = this.tempBan.bind(this);
    this.addToWatchlist = this.addToWatchlist.bind(this);
    this.removeFromWatchList = this.removeFromWatchList.bind(this);
    this.setDoFlag = this.setDoFlag.bind(this);
    this.setDoConfirmPlayer = this.setDoConfirmPlayer.bind(this);
    this.setDoVIPPlayer = this.setDoVIPPlayer.bind(this);
    this.setIgnoreAccent = this.setIgnoreAccent.bind(this);
    this.setExactMatch = this.setExactMatch.bind(this);
    this.setFlags = this.setFlags.bind(this);
    this.setCountry = this.setCountry.bind(this);

    this.onBlacklist = this.onBlacklist.bind(this);
    this.onUnBlacklist = this.onUnBlacklist.bind(this);
    this.deleteFlag = this.deleteFlag.bind(this);
    this.removeFromWatchList = this.removeFromWatchList.bind(this);
    this.onUnban = this.onUnban.bind(this);
    this.onTempBan = this.onTempBan.bind(this);
    this.onAddVip = this.onAddVip.bind(this);
    this.onDeleteVip = this.onDeleteVip.bind(this);
    this.onAddToWatchList = this.onAddToWatchList.bind(this);
    this.onRemoveFromWatchList = this.onRemoveFromWatchList.bind(this);
  }

  tempBan(steamId64, reason, durationHours, comment) {
    this.postComment(
      steamId64,
      comment,
      `PlayerID ${steamId64} temp banned ${durationHours} for ${reason}`
    );
    postData(`${process.env.REACT_APP_API_URL}do_temp_ban`, {
      steam_id_64: steamId64,
      reason: reason,
      duration_hours: durationHours,
      forward: true,
    })
      .then((response) =>
        showResponse(
          response,
          `PlayerID ${steamId64} temp banned ${durationHours} for ${reason}`,
          true
        )
      )
      .then(this._reloadOnSuccess)
      .catch((error) => toast.error("Unable to connect to API " + error));
  }

  addVip(player, expirationTimestamp, forwardVIP) {
    const steamID64 = player.get("steam_id_64");
    const name = player.get("names").get(0).get("name");

    return sendAction("do_add_vip", {
      player_id: steamID64,
      description: name,
      expiration: expirationTimestamp,
      forward: forwardVIP,
    }).then(this._reloadOnSuccess);
  }

  deleteVip(steamID64, forwardVIP) {
    return sendAction("do_remove_vip", {
      steam_id_64: steamID64,
      forward: forwardVIP,
    }).then(this._reloadOnSuccess);
  }

  _loadToState(command, showSuccess, stateSetter) {
    return get(command)
      .then((res) => showResponse(res, command, showSuccess))
      .then(stateSetter)
      .catch(handle_http_errors);
  }

  loadVips() {
    return this._loadToState("get_vip_ids", false, (data) =>
      this.setState({
        vips: vipListFromServer(data.result),
      })
    );
  }

  getPlayerHistory() {
    const {
      pageSize,
      page,
      byName,
      bySteamId,
      blacklistedOnly,
      lastSeenFrom,
      lastSeenUntil,
      isWatchedOnly,
      exactMatch,
      ignoreAccent,
      flags,
      country,
    } = this.state;
    const params = omitBy(
      {
        page_size: pageSize,
        page: page,
        player_name: byName,
        player_id: bySteamId,
        blacklisted: blacklistedOnly,
        last_seen_from: lastSeenFrom,
        last_seen_until: lastSeenUntil,
        is_watched: isWatchedOnly,
        exact_name_match: exactMatch,
        ignore_accent: ignoreAccent,
        flags: flags,
        country: country,
      },
      (v) => v === null || v === "" || v === undefined
    );

    this.setState({ isLoading: true });
    return postData(
      `${process.env.REACT_APP_API_URL}get_players_history`,
      params
    )
      .then((response) => showResponse(response, "get_players_history"))
      .then((data) => {
        this.setState({ isLoading: false });
        if (data.failed) {
          return;
        }
        this.setState({
          playersHistory: fromJS(data.result.players),
          total: data.result.total,
          pageSize: data.result.page_size,
          page: data.result.page,
        });
      })
      .then(this.loadVips)
      .then(this.loadBans)
      .catch(handle_http_errors);
  }

  loadBans() {
    return this._loadToState("get_bans", false, (data) =>
      this.setState({
        bans: banListFromServer(data.result),
      })
    );
  }

  _reloadOnSuccess = (data) => {
    if (data.failed) {
      return;
    }
    this.getPlayerHistory().then(this.loadVips).then(this.loadBans);
  };

  addFlagToPlayer(playerObj, flag, comment = null) {
    return postData(`${process.env.REACT_APP_API_URL}do_flag_player`, {
      player_id: playerObj.get("steam_id_64"),
      flag: flag,
      comment: comment,
    })
      .then((response) => showResponse(response, "do_flag_player"))
      .then(this._reloadOnSuccess)
      .catch((error) => toast.error("Unable to connect to API " + error));
  }

  deleteFlag(flag_id) {
    return postData(`${process.env.REACT_APP_API_URL}do_unflag_player`, {
      flag_id: flag_id,
    })
      .then((response) => showResponse(response, "do_unflag_player"))
      .then(this._reloadOnSuccess)
      .catch((error) => toast.error("Unable to connect to API " + error));
  }

  postComment(steamId64, comment, action) {
    postData(`${process.env.REACT_APP_API_URL}post_player_comment`, {
      steam_id_64: steamId64,
      comment: action,
    })
      .then((response) => {
        return showResponse(response, "post_player_comments", false);
      })
      .then(() => {
        if (comment && comment !== "" && comment !== null) {
          postData(`${process.env.REACT_APP_API_URL}post_player_comment`, {
            steam_id_64: steamId64,
            comment: comment,
          })
            .then((response) => {
              return showResponse(response, "post_player_comments", false);
            })
            .catch((error) => toast.error("Unable to connect to API " + error));
        }
      })
      .catch((error) => toast.error("Unable to connect to API " + error));
  }

  blacklistPlayer(steamId64, reason, comment) {
    this.postComment(
      steamId64,
      comment,
      `PlayerID ${steamId64} blacklist for ${reason}`
    );
    postData(`${process.env.REACT_APP_API_URL}do_blacklist_player`, {
      steam_id_64: steamId64,
      reason: reason,
    })
      .then((response) =>
        showResponse(
          response,
          `PlayerID ${steamId64} blacklist for ${reason}`,
          true
        )
      )
      .then(this._reloadOnSuccess)
      .catch((error) => toast.error("Unable to connect to API " + error));
  }

  unblacklistPlayer(steamId64) {
    this.postComment(
      steamId64,
      null,
      `PlayerID ${steamId64} removed from blacklist`
    );
    postData(`${process.env.REACT_APP_API_URL}do_unblacklist_player`, {
      player_id: steamId64,
    })
      .then((response) =>
        showResponse(
          response,
          `PlayerID ${steamId64} removed from blacklist`,
          true
        )
      )
      .then(this._reloadOnSuccess)
      .catch((error) => toast.error("Unable to connect to API " + error));
  }

  unBanPlayer(steamId64) {
    this.postComment(steamId64, null, `PlayerID ${steamId64} unbanned`);
    postData(`${process.env.REACT_APP_API_URL}do_unban`, {
      steam_id_64: steamId64,
    })
      .then((response) =>
        showResponse(response, `PlayerID ${steamId64} unbanned`, true)
      )
      .then(this._reloadOnSuccess)
      .catch((error) => toast.error("Unable to connect to API " + error));
  }

  addToWatchlist(steamId64, reason, comment, playerName) {
    this.postComment(steamId64, comment, `PlayerID ${steamId64} watched`);
    return addPlayerToWatchList(steamId64, reason, playerName).then(
      this._reloadOnSuccess
    );
  }

  removeFromWatchList(steamId64, playerName) {
    postData(`${process.env.REACT_APP_API_URL}do_unwatch_player`, {
      player_id: steamId64,
      player_name: playerName,
    })
      .then((response) =>
        showResponse(response, `PlayerID ${steamId64} unwatched`, true)
      )
      .then(this._reloadOnSuccess)
      .catch(handle_http_errors);
  }

  setDoFlag(playerToFlag) {
    return this.setState({ doFlag: playerToFlag });
  }

  setDoConfirmPlayer(confirmPlayer) {
    return this.setState({ doConfirmPlayer: confirmPlayer });
  }

  setDoVIPPlayer(doVIPPlayer) {
    return this.setState({
      doVIPPlayer,
    });
  }

  setIgnoreAccent(ignoreAccent) {
    return this.setState({ ignoreAccent });
  }

  setExactMatch(exactMatch) {
    return this.setState({ exactMatch });
  }

  setFlags(flags) {
    return this.setState({ flags });
  }

  setCountry(country) {
    return this.setState({ country });
  }

  /* Shortcut function for the grid list */
  onBlacklist(player) {
    return this.setDoConfirmPlayer({
      player: player.get("steam_id_64"),
      actionType: "blacklist",
      steam_id_64: player.get("steam_id_64"),
    });
  }

  onUnBlacklist(player) {
    return this.unblacklistPlayer(player.get("steam_id_64"));
  }

  onUnban(player) {
    return this.unBanPlayer(player.get("steam_id_64"));
  }

  onTempBan(player) {
    return this.setDoConfirmPlayer({
      player: player.get("steam_id_64"),
      actionType: "temp_ban",
      steam_id_64: player.get("steam_id_64"),
    });
  }

  onAddVip(player) {
    return this.setDoVIPPlayer({
      player,
    });
  }

  onDeleteVip(player, forwardVIP) {
    return this.deleteVip(player.get("steam_id_64"), forwardVIP);
  }
  onAddToWatchList(player) {
    const playerName = player.get("names")?.get(0)?.get("name");
    return this.setDoConfirmPlayer({
      player: playerName,
      actionType: "watchlist",
      steam_id_64: player.get("steam_id_64"),
    });
  }

  onRemoveFromWatchList(player) {
    const playerName = player.get("names")?.get(0)?.get("name");
    return this.removeFromWatchList(player.get("steam_id_64"), playerName);
  }

  render() {
    const { classes } = this.props;
    const {
      playersHistory,
      pageSize,
      page,
      total,
      byName,
      bySteamId,
      blacklistedOnly,
      lastSeenFrom,
      lastSeenUntil,
      isLoading,
      isWatchedOnly,
      doFlag,
      doConfirmPlayer,
      doVIPPlayer,
      vips,
      bans,
      ignoreAccent,
      exactMatch,
      flags,
      country,
    } = this.state;

    // Perfomance is crappy. It's less crappy after switcing to immutables but still...
    // It should be refactored so that the search bar does not trigger useless renderings
    return (
      <Grid container spacing={1}>
        <Grid item xs={12}>
          <SearchBar
            classes={classes}
            pageSize={pageSize}
            setPageSize={(v) => this.setState({ pageSize: v })}
            lastSeenFrom={lastSeenFrom}
            setLastSeenFrom={(v) => this.setState({ lastSeenFrom: v })}
            lastSeenUntil={lastSeenUntil}
            setLastSeenUntil={(v) => this.setState({ lastSeenUntil: v })}
            name={byName}
            setName={(v) => this.setState({ byName: v })}
            steamId={bySteamId}
            setSteamId={(v) => this.setState({ bySteamId: v })}
            blacklistedOnly={blacklistedOnly}
            setBlacklistedOnly={(v) => this.setState({ blacklistedOnly: v })}
            isWatchedOnly={isWatchedOnly}
            setIsWatchedOnly={(v) => this.setState({ isWatchedOnly: v })}
            onSearch={this.getPlayerHistory}
            exactMatch={exactMatch}
            setExactMatch={this.setExactMatch}
            ignoreAccent={ignoreAccent}
            setIgnoreAccent={this.setIgnoreAccent}
            country={country}
            setCountry={this.setCountry}
            flags={flags}
            setFlags={this.setFlags}
          />
        </Grid>
        <Grid item xs={12}>
          <MyPagination
            classes={classes}
            pageSize={pageSize}
            page={page}
            setPage={(page) =>
              this.setState({ page: page }, this.getPlayerHistory)
            }
            total={total}
          />
        </Grid>
        <Grid item xs={12}>
          {isLoading ? <LinearProgress color="secondary" /> : ""}
          <PlayerGrid
            classes={classes}
            players={playersHistory}
            onBlacklist={this.onBlacklist}
            onUnBlacklist={this.onUnBlacklist}
            onDeleteFlag={this.deleteFlag}
            onRemoveFromWatchList={this.onRemoveFromWatchList}
            vips={vips}
            bans={bans}
            onflag={this.setDoFlag}
            onUnban={this.onUnban}
            onTempBan={this.onTempBan}
            onAddVip={this.setDoVIPPlayer}
            onDeleteVip={this.onDeleteVip}
            onAddToWatchList={this.onAddToWatchList}
          />
        </Grid>
        <Grid item xs={12} className={classes.padding}>
          <MyPagination
            classes={classes}
            pageSize={pageSize}
            page={page}
            setPage={(page) =>
              this.setState({ page: page }, this.getPlayerHistory)
            }
            total={total}
          />
        </Grid>
        <ReasonDialog
          open={doConfirmPlayer}
          handleClose={() => this.setDoConfirmPlayer(false)}
          handleConfirm={(
            actionType,
            player,
            reason,
            comment,
            durationHours,
            steamId64
          ) => {
            if (actionType === "blacklist") {
              this.blacklistPlayer(steamId64, reason, comment);
            } else if (actionType === "temp_ban") {
              this.tempBan(steamId64, reason, durationHours, comment);
            } else if (actionType === "watchlist") {
              this.addToWatchlist(steamId64, reason, comment, player);
            }
            this.setDoConfirmPlayer(false);
          }}
        />
        <FlagDialog
          open={doFlag}
          handleClose={() => this.setDoFlag(false)}
          handleConfirm={(playerObj, theFlag, theComment) => {
            this.addFlagToPlayer(playerObj, theFlag, theComment);
            this.setDoFlag(false);
          }}
          SummaryRenderer={PlayerSummary}
        />
        <VipExpirationDialog
          open={doVIPPlayer}
          vips={vips}
          onDeleteVip={this.onDeleteVip}
          handleClose={() => this.setDoVIPPlayer(false)}
          handleConfirm={(playerObj, expirationTimestamp, forwardVIP) => {
            this.addVip(playerObj, expirationTimestamp, forwardVIP);
            this.setDoVIPPlayer(false);
          }}
        />
      </Grid>
    );
  }
}

export default PlayersHistory;
export { FlagDialog, FlagButton, PlayersHistory };
