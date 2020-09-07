import React, { Component } from "react";
import _ from "lodash";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import {
  postData,
  showResponse,
  get,
  handle_http_errors,
} from "../../utils/fetchUtils";
import AutoRefreshBar from "./header";
import TextInputBar from "./textInputBar";
import CompactList from "./playerList";
import Chip from "@material-ui/core/Chip";
import { ReasonDialog } from "./playerActions";
import GroupActions from "./groupActions";
import Unban from "./unban";
import { Map, List, fromJS } from "immutable";
import { FlagDialog } from "../PlayersHistory";
import { getEmojiFlag } from "../../utils/emoji";

function stripDiacritics(string) {
  return typeof string.normalize !== "undefined"
    ? string.normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    : string;
}

const PlayerSummary = ({ player, flag }) => {
  return player ? (
    <React.Fragment>
      <p>
        Add flag: {flag ? getEmojiFlag(flag) : <small>Please choose</small>}
      </p>
      <p>
        To:{" "}
        {player.get("names")
          ? player.get("names", []).map((n) => <Chip label={n.get("name")} />)
          : "No name recorded"}
      </p>
      <p>Steamd id: {player.get("steam_id_64", "")}</p>
    </React.Fragment>
  ) : (
    ""
  );
};

class PlayerView extends Component {
  constructor(props) {
    super();
    this.state = {
      selectedPlayers: new List(),
      bannedPlayers: null,
      players: new List(),
      filteredPlayers: new List(),
      /*filteredPlayerNames: [],
      filteredPlayerSteamIDs: [],
      filteredPlayerProfiles: [], */
      filter: "",
      filterTimeout: null,
      actionMessage: "",
      doConfirm: false,
      alphaSort: false,
      openGroupAction: false,
      openUnban: false,
      flag: false,
    };

    this.onPlayerSelected = this.onPlayerSelected.bind(this);
    this.filterPlayers = this.filterPlayers.bind(this);
    this.filterChange = this.filterChange.bind(this);
    this.loadPlayers = this.loadPlayers.bind(this);
    this.handleAction = this.handleAction.bind(this);
    this.loadBans = this.loadBans.bind(this);
    this.unBan = this.unBan.bind(this);
    this.addFlagToPlayer = this.addFlagToPlayer.bind(this);
    this.deleteFlag = this.deleteFlag.bind(this);
  }

  addFlagToPlayer(playerObj, flag, comment = null) {
    return postData(`${process.env.REACT_APP_API_URL}flag_player`, {
      steam_id_64: playerObj.get("steam_id_64"),
      flag: flag,
      comment: comment,
    })
      .then((response) => showResponse(response, "flag_player", true))
      .then(() => this.setState({ flag: false }))
      .then(this.loadPlayers)
      .catch(handle_http_errors);
  }

  deleteFlag(flag_id) {
    return postData(`${process.env.REACT_APP_API_URL}unflag_player`, {
      flag_id: flag_id,
    })
      .then((response) => showResponse(response, "unflag_player", true))
      .then(this.loadPlayers)
      .catch(handle_http_errors);
  }

  unBan(ban) {
    postData(`${process.env.REACT_APP_API_URL}do_remove_${ban.type}_ban`, {
      ban_log: ban.raw,
    })
      .then((response) =>
        showResponse(response, `Remove ${ban.type} ban for ${ban.name}`, true)
      )
      .then(this.loadBans)
      .catch(handle_http_errors);
  }

  handleAction(actionType, player, message = null) {
    if (message === null) {
      message = this.state.actionMessage;
    }
    if (message === "" && !actionType.startsWith("switch_")) {
      this.setState({ doConfirm: { player: player, actionType: actionType } });
    } else {
      postData(`${process.env.REACT_APP_API_URL}do_${actionType}`, {
        player: player,
        reason: message,
      })
        .then((response) =>
          showResponse(response, `${actionType} ${player}`, true)
        )
        .then(this.loadPlayers)
        .catch(handle_http_errors);
    }
  }

  onPlayerSelected(players) {
    this.setState({ selectedPlayers: players });
  }

  async load(command, callback) {
    return get(command)
      .then((response) => showResponse(response, command))
      .then((data) => callback(data))
      .catch(handle_http_errors);
  }

  loadPlayers() {
    return this.load("get_players", (data) => {
      this.setState(
        { players: data.result === null ? new List() : fromJS(data.result) },
        () => {
          this.filterPlayers();
        }
      );
      return data;
    });
  }

  loadBans() {
    return this.load("get_bans", (data) =>
      this.setState({ bannedPlayers: data.result })
    );
  }

  componentDidMount() {
    this.loadPlayers();
  }

  filterChange(filter) {
    clearTimeout(this.state.filterTimeout); // switch to lodash debounce
    this.setState({
      filter: filter,
      filterTimeout: setTimeout(this.filterPlayers, 200),
    });
  }

  filterPlayers() {
    // TODO this is shit. The point was to prevent uncessary refreshes to save perf
    // But we could just switch to immutables for that
    const { filter, players } = this.state;
    /*
    const makeCombinedProfile = players => players.map(p => fromJS({...(p.profile || {}), country: p.country, steam_bans: p.steam_bans}));

    if (!filter) {
      const filteredPlayerNames = players.map(p => p.name);
      const filteredPlayerSteamIDs = players.map(p => p.steam_id_64);
      const filteredPlayerProfiles = makeCombinedProfile(players)
      return this.setState({ filteredPlayerSteamIDs, filteredPlayerNames, filteredPlayerProfiles });
    }
    const filteredPlayers = _.filter(
      players,
      p => stripDiacritics(p.name).toLowerCase().indexOf(filter.toLowerCase()) >= 0
    );

    const filteredPlayerNames = filteredPlayers.map(p => p.name);
    const filteredPlayerSteamIDs = filteredPlayers.map(p => p.steam_id_64);
    const filteredPlayerProfiles =  makeCombinedProfile(filteredPlayers) 
    this.setState({ filteredPlayerNames, filteredPlayerSteamIDs, filteredPlayerProfiles });
    */
    if (filter) {
      const filteredPlayers = players.filter(
        (p) =>
          stripDiacritics(p.get('name')).toLowerCase().indexOf(filter.toLowerCase()) >=
          0
      );
      this.setState({ filteredPlayers: filteredPlayers });
    }

    if (!filter) {
      this.setState({ filteredPlayers: players });
    }
  }

  render() {
    const { classes } = this.props;
    const {
      openGroupAction,
      openUnban,
      players,
      filteredPlayers,
      actionMessage,
      doConfirm,
      alphaSort,
      bannedPlayers,
      flag,
    } = this.state;
    const playersCopy = players;

    return (
      <React.Fragment>
        <AutoRefreshBar
          intervalFunction={this.loadPlayers}
          everyMs={15000}
          refreshIntevalMs={100}
          onGroupActionClick={() => this.setState({ openGroupAction: true })}
          onUnbanClick={() => {
            this.loadBans();
            this.setState({ openUnban: true });
          }}
        />
        <TextInputBar
          classes={classes}
          handleChange={this.filterChange}
          total={players.size}
          showCount={filteredPlayers.size}
          handleMessageChange={(text) => this.setState({ actionMessage: text })}
          actionMessage={actionMessage}
          handleToggleAlphaSort={(bool) => this.setState({ alphaSort: bool })}
        />

        <CompactList
          classes={classes}
          alphaSort={alphaSort}
          players={filteredPlayers}
          /*playerNames={filteredPlayerNames}
          playerSteamIDs={filteredPlayerSteamIDs}
          playerProfiles={filteredPlayerProfiles}*/
          handleAction={(actionType, player) =>
            this.handleAction(actionType, player)
          }
          handleToggle={() => 1}
          onFlag={(player) => this.setState({ flag: player })}
          onDeleteFlag={(flagId) => this.deleteFlag(flagId)}
        />

        <GroupActions
          onClose={() => this.setState({ openGroupAction: false })}
          open={openGroupAction}
          classes={classes}
          players={players} /* Todo handle immuatable */
          handleAction={this.handleAction}
        />
        <Unban
          open={openUnban}
          onReload={this.loadBans}
          handleUnban={this.unBan}
          bannedPlayers={bannedPlayers}
          classes={classes}
          onClose={() => this.setState({ openUnban: false })}
        />
        <ReasonDialog
          open={doConfirm}
          handleClose={() => this.setState({ doConfirm: false })}
          handleConfirm={(action, player, reason) => {
            this.handleAction(action, player, reason);
            this.setState({ doConfirm: false });
          }}
        />
        <FlagDialog
          open={flag}
          handleClose={() => this.setState({ flag: false })}
          handleConfirm={this.addFlagToPlayer}
          SummaryRenderer={PlayerSummary}
        />
      </React.Fragment>
    );
  }
}

export default PlayerView;
