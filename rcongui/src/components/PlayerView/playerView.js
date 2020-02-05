import React, { Component } from "react";
import Grid from "@material-ui/core/Grid";
import _ from "lodash";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { postData } from "../../utils/fetchUtils";
import AutoRefreshBar from "./header";
import TextInputBar from "./textInputBar";
import CompactList from "./playerList";
import { ReasonDialog } from "./playerActions";
import GroupActions from "./groupActions";

class PlayerView extends Component {
  constructor(props) {
    super();
    this.state = {
      selectedPlayers: [],
      players: [],
      filteredPlayerNames: [],
      filterPlayerSteamIDs: [],
      filter: "",
      filterTimeout: null,
      actionMessage: "",
      doConfirm: false,
      alphaSort: false,
      openGroupAction: false
    };

    this.onPlayerSelected = this.onPlayerSelected.bind(this);
    this.filterPlayers = this.filterPlayers.bind(this);
    this.filterChange = this.filterChange.bind(this);
    this.loadPlayers = this.loadPlayers.bind(this);
  }

  handleAction(actionType, player, message = null) {
    console.log(actionType, player, message);
    if (message === null) {
      message = this.state.actionMessage;
    }
    if (message === "" && !actionType.startsWith("switch_")) {
      this.setState({ doConfirm: { player: player, actionType: actionType } });
    } else {
      postData(`${process.env.REACT_APP_API_URL}do_${actionType}`, {
        player: player,
        reason: message
      })
        .then(response =>
          this.showResponse(response, `${actionType} ${player}`, true)
        )
        .then(this.loadPlayers);
    }
  }

  onPlayerSelected(players) {
    this.setState({ selectedPlayers: players });
  }

  async showResponse(response, command, showSuccess) {
    if (!response.ok) {
      toast.error(`Game server failed to return for ${command}`);
    } else {
      const res = await response.json();
      if (res.failed === true) {
        toast.warning(`Last command failed: ${command}`);
      } else if (showSuccess === true) {
        toast.success(`Done: ${command}`);
      }
      return res;
    }
    return response.json();
  }

  loadPlayers() {
    console.log("Loading players");
    fetch(`${process.env.REACT_APP_API_URL}get_players`)
      .then(response => this.showResponse(response, "get_players"))
      .then(data =>
        this.setState(
          { players: data.result === null ? [] : data.result },
          this.filterPlayers
        )
      )
      .catch(() => toast.error("Unable to connect to API"));
  }

  componentDidMount() {
    this.loadPlayers();
  }

  filterChange(filter) {
    clearTimeout(this.state.filterTimeout); // switch to lodash debounce
    this.setState({
      filter: filter,
      filterTimeout: setTimeout(this.filterPlayers, 200)
    });
  }

  filterPlayers() {
    const { filter, players } = this.state;
    if (!filter) {
      const filteredPlayerNames = players.map(p => p.name);
      const filterPlayerSteamIDs = players.map(p => p.steam_id_64);
      return this.setState({ filterPlayerSteamIDs, filteredPlayerNames });
    }
    const filteredPlayers = _.filter(
      players,
      p => p.name.toLowerCase().indexOf(filter.toLowerCase()) >= 0
    );

    const filteredPlayerNames = filteredPlayers.map(p => p.name);
    const filterPlayerSteamIDs = filteredPlayers.map(p => p.steam_id_64);
    this.setState({ filteredPlayerNames, filterPlayerSteamIDs });
  }

  render() {
    const { classes } = this.props;
    const {
      openGroupAction,
      players,
      filteredPlayerNames,
      filterPlayerSteamIDs,
      actionMessage,
      doConfirm,
      alphaSort
    } = this.state;

    return (
      <Grid container spacing={0}>
        <Grid item sm={12} md={6}>
          <AutoRefreshBar
            intervalFunction={this.loadPlayers}
            everyMs={15000}
            refreshIntevalMs={100}
            onGroupActionClick={() => this.setState({ openGroupAction: true })}
          />
          <TextInputBar
            classes={classes}
            handleChange={this.filterChange}
            total={players.length}
            showCount={filteredPlayerNames.length}
            handleMessageChange={text => this.setState({ actionMessage: text })}
            actionMessage={actionMessage}
            handleToggleAlphaSort={bool => this.setState({ alphaSort: bool })}
          />

          {players ? (
            <CompactList
              classes={classes}
              alphaSort={alphaSort}
              playerNames={filteredPlayerNames}
              playerSteamIDs={filterPlayerSteamIDs}
              handleAction={(actionType, player) =>
                this.handleAction(actionType, player)
              }
              handleToggle={() => 1}
            />
          ) : (
            <p>"No players to show"</p>
          )}
        </Grid>
        <Grid item xs={12} md={6}>
          <GroupActions
            onClose={() => this.setState({ openGroupAction: false })}
            open={openGroupAction}
            classes={classes}
            players={players}
            handleAction={this.handleAction}
          />
        </Grid>
        <ReasonDialog
          open={doConfirm}
          handleClose={() => this.setState({ doConfirm: false })}
          handleConfirm={(action, player, reason) => {
            this.handleAction(action, player, reason);
            this.setState({ doConfirm: false });
          }}
        />
      </Grid>
    );
  }
}

export default PlayerView;
