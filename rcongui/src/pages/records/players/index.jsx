import React from "react";
import {
  addPlayerToWatchList,
  get,
  handle_http_errors,
  postData,
  sendAction,
  showResponse,
} from "../../../utils/fetchUtils";
import { toast } from "react-toastify";
import Pagination from '@mui/material/Pagination';
import {
  Button,
  Chip,
  LinearProgress,
  TextField,
  Typography,
} from "@mui/material";
import Grid from "@mui/material/Unstable_Grid2";
import { ReasonDialog } from "../../../components/PlayerView/playerActions";
import { omitBy } from "lodash/object";
import SearchBar from "../../../components/PlayersHistory/searchBar";
import { fromJS, List, Map } from "immutable";
import FlagIcon from "@mui/icons-material/Flag";
import data from '@emoji-mart/data'
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import { getEmojiFlag } from "../../../utils/emoji";
import PlayerGrid from "../../../components/PlayersHistory/playerGrid";
import { VipExpirationDialog } from "../../../components/VipDialog";
import { vipListFromServer } from "../../../components/VipDialog/vipFromServer";
import { banListFromServer } from "../../../components/PlayersHistory/PlayerTile/PlayerBan";
import BlacklistRecordCreateDialog from "../../../components/Blacklist/BlacklistRecordCreateDialog";
import EmojiPicker from "@emoji-mart/react";

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
      Player ID: {player ? player.get("player_id") : ""}
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
      (<Dialog open={open} aria-labelledby="form-dialog-title">
        <DialogTitle id="form-dialog-title">
          <SummaryRenderer player={open} flag={flag} />
        </DialogTitle>
        <DialogContent>
          <Grid
            container
            alignContent="center"
            alignItems="center"
            justifyContent="center"
            spacing={2}
          >
            <Grid xs={12}>
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
            justifyContent="center"
            spacing={2}
          >
            <Grid xs={12}>
            <EmojiPicker
                style={{ border: '1px solid red' }}
                perLine={8}
                data={data}
                onEmojiSelect={(emoji) => this.setState({ flag: emoji.native })}
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
      </Dialog>)
    );
  }
}

const FlagButton = ({ onflag }) => (
  <Button variant="outlined" onClick={onflag}>
    <FlagIcon />
  </Button>
);

const MyPagination = ({ pageSize, total, page, setPage }) => (
  <Pagination
    count={Math.ceil(total / pageSize)}
    page={page}
    onChange={(e, val) => setPage(val)}
    showFirstButton
    showLastButton
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
      byPlayerId: "",
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
      blacklists: [],
      blacklistDialogOpen: false,
      blacklistDialogInitialValues: undefined,
    };

    this.getPlayerHistory = this.getPlayerHistory.bind(this);
    this.loadBans = this.loadBans.bind(this);
    this.blacklistPlayer = this.blacklistPlayer.bind(this);
    this.unblacklistPlayer = this.unblacklistPlayer.bind(this);
    this.addFlagToPlayer = this.addFlagToPlayer.bind(this);
    this.deleteFlag = this.deleteFlag.bind(this);
    this.loadVips = this.loadVips.bind(this);
    this.loadBlacklists = this.loadBlacklists.bind(this);
    this.addVip = this.addVip.bind(this);
    this.deleteVip = this.deleteVip.bind(this);
    this.unBanPlayer = this.unBanPlayer.bind(this);
    this.tempBan = this.tempBan.bind(this);
    this.permaBan = this.permaBan.bind(this);
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
    this.onPermaBan = this.onPermaBan.bind(this);
    this.onAddVip = this.onAddVip.bind(this);
    this.onDeleteVip = this.onDeleteVip.bind(this);
    this.onAddToWatchList = this.onAddToWatchList.bind(this);
    this.onRemoveFromWatchList = this.onRemoveFromWatchList.bind(this);
  }

  tempBan(playerId, reason, durationHours, comment) {
    this.postComment(
      playerId,
      comment,
      `Player ID ${playerId} temp banned ${durationHours} for ${reason}`
    );
    postData(`${process.env.REACT_APP_API_URL}temp_ban`, {
      player_id: playerId,
      reason: reason,
      duration_hours: durationHours,
    })
      .then((response) =>
        showResponse(
          response,
          `Player ID ${playerId} temp banned ${durationHours} for ${reason}`,
          true
        )
      )
      .then(this._reloadOnSuccess)
      .catch((error) => toast.error("Unable to connect to API " + error));
  }

  permaBan(playerId, reason, comment) {
    this.postComment(
      playerId,
      comment,
      `Player ID ${playerId} perma banned for ${reason}`
    );
    postData(`${process.env.REACT_APP_API_URL}perma_ban`, {
      player_id: playerId,
      reason: reason,
    })
      .then((response) =>
        showResponse(
          response,
          `Player ID ${playerId} perma banned for ${reason}`,
          true
        )
      )
      .then(this._reloadOnSuccess)
      .catch((error) => toast.error("Unable to connect to API " + error));
  }

  addVip(player, expirationTimestamp, forwardVIP) {
    const player_id = player.get("player_id");
    const name = player.get("names").get(0).get("name");

    return sendAction("add_vip", {
      player_id: player_id,
      description: name,
      expiration: expirationTimestamp,
      forward: forwardVIP,
    }).then(this._reloadOnSuccess);
  }

  deleteVip(playerId, forwardVIP) {
    return sendAction("remove_vip", {
      player_id: playerId,
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

  loadBlacklists() {
    return this._loadToState("get_blacklists", false, (data) =>
      this.setState({
        blacklists: data.result,
      })
    );
  }

  getPlayerHistory() {
    const {
      pageSize,
      page,
      byName,
      byPlayerId: byPlayerId,
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
        player_id: byPlayerId,
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
    return postData(`${process.env.REACT_APP_API_URL}flag_player`, {
      player_id: playerObj.get("player_id"),
      flag: flag,
      comment: comment,
    })
      .then((response) => showResponse(response, "flag_player"))
      .then(this._reloadOnSuccess)
      .catch((error) => toast.error("Unable to connect to API " + error));
  }

  deleteFlag(flag_id) {
    return postData(`${process.env.REACT_APP_API_URL}unflag_player`, {
      flag_id: flag_id,
    })
      .then((response) => showResponse(response, "unflag_player"))
      .then(this._reloadOnSuccess)
      .catch((error) => toast.error("Unable to connect to API " + error));
  }

  postComment(playerId, comment, action) {
    postData(`${process.env.REACT_APP_API_URL}post_player_comment`, {
      player_id: playerId,
      comment: action,
    })
      .then((response) => {
        return showResponse(response, "post_player_comment", false);
      })
      .then(() => {
        if (comment && comment !== "" && comment !== null) {
          postData(`${process.env.REACT_APP_API_URL}post_player_comment`, {
            player_id: playerId,
            comment: comment,
          })
            .then((response) => {
              return showResponse(response, "post_player_comment", false);
            })
            .catch((error) => toast.error("Unable to connect to API " + error));
        }
      })
      .catch((error) => toast.error("Unable to connect to API " + error));
  }

  blacklistPlayer({
    blacklistId,
    playerId,
    expiresAt,
    reason
  }) {
    this.postComment(
      playerId,
      null,
      `Player ID ${playerId} blacklist for ${reason}`
    );
    postData(`${process.env.REACT_APP_API_URL}add_blacklist_record`, {
      blacklist_id: blacklistId,
      player_id: playerId,
      expires_at: expiresAt || null,
      reason
    })
      .then((response) =>
        showResponse(response, `Player ID ${playerId} was blacklisted`, true)
      )
      .then(this._reloadOnSuccess)
      .catch(handle_http_errors);
  }

  unblacklistPlayer(playerId) {
    this.postComment(
      playerId,
      null,
      `Expired all blacklists for player ID ${playerId}`
    );
    postData(`${process.env.REACT_APP_API_URL}unblacklist_player`, {
      player_id: playerId,
    })
      .then((response) =>
        showResponse(
          response,
          `Expired all blacklists for player ID ${playerId}`,
          true
        )
      )
      .then(this._reloadOnSuccess)
      .catch((error) => toast.error("Unable to connect to API " + error));
  }

  unBanPlayer(playerId) {
    this.postComment(playerId, null, `Player ID ${playerId} unbanned`);
    postData(`${process.env.REACT_APP_API_URL}unban`, {
      player_id: playerId,
    })
      .then((response) =>
        showResponse(response, `Player ID ${playerId} unbanned`, true)
      )
      .then(this._reloadOnSuccess)
      .catch((error) => toast.error("Unable to connect to API " + error));
  }

  addToWatchlist(playerId, reason, comment, playerName) {
    this.postComment(playerId, comment, `Player ID ${playerId} watched`);
    return addPlayerToWatchList(playerId, reason, playerName).then(
      this._reloadOnSuccess
    );
  }

  removeFromWatchList(playerId, playerName) {
    postData(`${process.env.REACT_APP_API_URL}unwatch_player`, {
      player_id: playerId,
      player_name: playerName,
    })
      .then((response) =>
        showResponse(response, `Player ID ${playerId} unwatched`, true)
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
    this.setState({
      blacklistDialogOpen: true,
      blacklistDialogInitialValues: {
        playerId: player.get("player_id")
      }
    });
    if (!this.state.blacklists.length) {
      this.loadBlacklists()
    }
  }

  onUnBlacklist(player) {
    return this.unblacklistPlayer(player.get("player_id"));
  }

  onUnban(player) {
    return this.unBanPlayer(player.get("player_id"));
  }

  onTempBan(player) {
    return this.setDoConfirmPlayer({
      player: player.get("player_id"),
      actionType: "temp_ban",
      player_id: player.get("player_id"),
    });
  }

  onPermaBan(player) {
    return this.setDoConfirmPlayer({
      player: player.get("player_id"),
      actionType: "perma_ban",
      player_id: player.get("player_id"),
    });
  }

  onAddVip(player) {
    return this.setDoVIPPlayer({
      player,
    });
  }

  onDeleteVip(player, forwardVIP) {
    return this.deleteVip(player.get("player_id"), forwardVIP);
  }
  onAddToWatchList(player) {
    const playerName = player.get("names")?.get(0)?.get("name");
    return this.setDoConfirmPlayer({
      player: playerName,
      actionType: "watchlist",
      player_id: player.get("player_id"),
    });
  }

  onRemoveFromWatchList(player) {
    const playerName = player.get("names")?.get(0)?.get("name");
    return this.removeFromWatchList(player.get("player_id"), playerName);
  }

  render() {
    const {
      playersHistory,
      pageSize,
      page,
      total,
      byName,
      byPlayerId,
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
      blacklists,
      blacklistDialogOpen,
      blacklistDialogInitialValues,
    } = this.state;

    // Perfomance is crappy. It's less crappy after switcing to immutables but still...
    // It should be refactored so that the search bar does not trigger useless renderings
    return (
      <Grid container spacing={1}>
        <Grid xs={12}>
          <SearchBar
            pageSize={pageSize}
            setPageSize={(v) => this.setState({ pageSize: v })}
            lastSeenFrom={lastSeenFrom}
            setLastSeenFrom={(v) => this.setState({ lastSeenFrom: v })}
            lastSeenUntil={lastSeenUntil}
            setLastSeenUntil={(v) => this.setState({ lastSeenUntil: v })}
            name={byName}
            setName={(v) => this.setState({ byName: v })}
            playerId={byPlayerId}
            setPlayerId={(v) => this.setState({ byPlayerId: v })}
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
        <Grid xs={12}>
          <MyPagination
            pageSize={pageSize}
            page={page}
            setPage={(page) =>
              this.setState({ page: page }, this.getPlayerHistory)
            }
            total={total}
          />
        </Grid>
        <Grid xs={12}>
          {isLoading ? <LinearProgress color="secondary" /> : ""}
          <PlayerGrid
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
            onPermaBan={this.onPermaBan}
            onAddVip={this.setDoVIPPlayer}
            onDeleteVip={this.onDeleteVip}
            onAddToWatchList={this.onAddToWatchList}
          />
        </Grid>
        <Grid xs={12}>
          <MyPagination
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
            playerId
          ) => {
            if (actionType === "blacklist") {
              this.blacklistPlayer(playerId, reason, comment);
            } else if (actionType === "temp_ban") {
              this.tempBan(playerId, reason, durationHours, comment);
            } else if (actionType === "perma_ban") {
              this.permaBan(playerId, reason, comment);
            } else if (actionType === "watchlist") {
              this.addToWatchlist(playerId, reason, comment, player);
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
          player={doVIPPlayer}
          vips={vips}
          onDeleteVip={this.onDeleteVip}
          handleClose={() => this.setDoVIPPlayer(false)}
          handleConfirm={(playerObj, expirationTimestamp, forwardVIP) => {
            this.addVip(playerObj, expirationTimestamp, forwardVIP);
            this.setDoVIPPlayer(false);
          }}
        />
        <BlacklistRecordCreateDialog
          open={blacklistDialogOpen}
          setOpen={(value) => this.setState({ blacklistDialogOpen: value })}
          blacklists={blacklists}
          initialValues={blacklistDialogInitialValues}
          onSubmit={this.blacklistPlayer}
          disablePlayerId
        />
      </Grid>
    );
  }
}

export default PlayersHistory;
export { FlagDialog, FlagButton, PlayersHistory };
