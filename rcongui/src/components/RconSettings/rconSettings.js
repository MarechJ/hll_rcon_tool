import React from "react";
import {
  Button,
  Grid,
  IconButton,
  TextField,
  Typography,
  Tooltip,
} from "@material-ui/core";
import {
  addPlayerToWatchList,
  get,
  getSharedMessages,
  handle_http_errors,
  postData,
  showResponse,
} from "../../utils/fetchUtils";
import Blacklist from "./blacklist";
import _ from "lodash";
import Padlock from "../shared/padlock";
import TextHistoryManager, { SelectNameSpace } from "./textHistoryManager";
import TextHistory from "../textHistory";
import ServicesList from "../Services";
import InputLabel from "@material-ui/core/InputLabel";
import MenuItem from "@material-ui/core/MenuItem";
import FormHelperText from "@material-ui/core/FormHelperText";
import FormControl from "@material-ui/core/FormControl";
import Select from "@material-ui/core/Select";
import { ManualPlayerInput, WordList } from "../commonComponent";
import DeleteIcon from "@material-ui/icons/Delete";
import AddIcon from "@material-ui/icons/Add";
import SaveIcon from "@material-ui/icons/Save";
import RealVip from "./realVip";
import HelpIcon from "@material-ui/icons/Help";
import ServerName from "./serverName";
import AutoSettings from "./autoSettings";

const ManualWatchList = () => {
  const [name, setName] = React.useState("");
  const [playerId, setPlayerId] = React.useState("");
  const [reason, setReason] = React.useState("");
  const [sharedMessages, setSharedMessages] = React.useState([]);

  React.useEffect(() => {
    getSharedMessages("punishments").then((data) => setSharedMessages(data));
  }, []);
  const textHistory = new TextHistory("watchlist");

  return (
    <ManualPlayerInput
      name={name}
      setName={setName}
      playerId={playerId}
      setPlayerId={setPlayerId}
      reason={reason}
      setReason={setReason}
      textHistory={textHistory}
      sharedMessages={sharedMessages}
      actionName="Watch"
      tooltipText="You will get a notification on you watchlist discord hook when this player enters your server"
      onSubmit={() => addPlayerToWatchList(playerId, reason, null, name)}
    />
  );
};

const Hook = ({
  hook = "",
  roles = [],
  onAddHook,
  onDeleteHook,
  onUpdateHook,
  actionType,
}) => {
  const [myHook, setMyHook] = React.useState(hook);
  const [myRoles, setMyRoles] = React.useState(roles);

  return (
    <Grid container spacing={1}>
      <Grid item xs={4}>
        <TextField
          label="webhook url"
          fullWidth
          value={myHook}
          onChange={(e) => setMyHook(e.target.value)}
          helperText="Discord hook url"
        />
      </Grid>
      <Grid item xs={6}>
        <WordList
          label="Roles"
          helperText="Add roles to be pinged, hit enter to validate"
          placeholder="<@&111117777888889999>"
          words={myRoles}
          onWordsChange={setMyRoles}
        />
      </Grid>
      <Grid item xs={2}>
        {actionType === "delete" ? (
          <React.Fragment>
            <IconButton
              edge="start"
              onClick={() => onDeleteHook(myHook, myRoles)}
            >
              <DeleteIcon />
            </IconButton>
            <IconButton
              edge="start"
              onClick={() => onUpdateHook(myHook, myRoles)}
            >
              <SaveIcon />
            </IconButton>
          </React.Fragment>
        ) : (
          <IconButton
            edge="start"
            onClick={() => {
              onAddHook(myHook, myRoles);
              setMyRoles("");
              setMyHook("");
            }}
          >
            <AddIcon />
          </IconButton>
        )}
      </Grid>
    </Grid>
  );
};

const WebhooksConfig = () => {
  const [hooks, setHooks] = React.useState([]);
  React.useEffect(() => {
    get("get_hooks")
      .then((res) => showResponse(res, "get_hooks", false))
      .then((res) => setHooks(res.result))
      .catch(handle_http_errors);
  }, []);

  const setHookConfig = (hookConfig) =>
    postData(`${process.env.REACT_APP_API_URL}set_hooks`, {
      name: hookConfig.name,
      hooks: hookConfig.hooks,
    })
      .then((res) => showResponse(res, `set_hooks ${hookConfig.name}`, true))
      .then((res) => {
        console.log(res);
        setHooks(res.result);
      });

  if (hooks === null) {
    return (
      <React.Fragment>
        <p>no hooks found</p>
      </React.Fragment>
    );
  }
  return (
    <React.Fragment>
      {hooks.map((hookConfig) => (
        <Grid container>
          <Grid item xs={12}>
            <Typography variant="h6" style={{ "text-transform": "capitalize" }}>
              For: {hookConfig.name}
            </Typography>
            <Grid container>
              {hookConfig.hooks.length ? (
                hookConfig.hooks.map((o, idx) => (
                  <Hook
                    hook={o.hook}
                    roles={o.roles}
                    actionType="delete"
                    onDeleteHook={() => {
                      hookConfig.hooks.splice(idx, 1);
                      setHookConfig(hookConfig);
                    }}
                    onUpdateHook={(hook, roles) => {
                      hookConfig.hooks[idx] = { hook: hook, roles: roles };
                      setHookConfig(hookConfig);
                    }}
                  />
                ))
              ) : (
                <Typography>{`No hooks defined for: ${hookConfig.name}`}</Typography>
              )}
            </Grid>
          </Grid>
          <Grid item xs={12}>
            <Hook
              actionType="add"
              onAddHook={(hook, roles) => {
                hookConfig.hooks.push({ hook: hook, roles: roles });
                setHookConfig(hookConfig);
              }}
            />
          </Grid>
        </Grid>
      ))}
    </React.Fragment>
  );
};

function makeBool(text) {
  if (text === null) {
    return false;
  }
  return text === "true";
}

class RconSettings extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      rawBroadcastMessages: [],
      broadcastMessages: [],
      standardMessages: [],
      standardMessagesType: "punishments",
      randomize: false,
      enabled: false,
      cameraBroadcast: false,
      cameraWelcome: false,
      autovotekickEnabled: false,
      autovotekickMinIngameMods: 0,
      autovotekickMinOnlineMods: 0,
      autovotekickConditionType: "OR",
      autosettings: "{}",
      forwardAutoSettings: makeBool(
        window.localStorage.getItem("forwardAutoSettings")
      ),
    };
    this.editorRef = React.createRef();
    this.handleEditorDidMount = this.handleEditorDidMount.bind(this);

    this.loadBroadcastsSettings = this.loadBroadcastsSettings.bind(this);
    this.validate_messages = this.validate_messages.bind(this);
    this.saveBroadCastMessages = this.saveBroadCastMessages.bind(this);
    this.loadStandardMessages = this.loadStandardMessages.bind(this);
    this.saveStandardMessages = this.saveStandardMessages.bind(this);
    this.clearCache = this.clearCache.bind(this);
    this.loadCameraConfig = this.loadCameraConfig.bind(this);
    this.saveCameraConfig = this.saveCameraConfig.bind(this);
    this.saveAutoVotekickConfig = this.saveAutoVotekickConfig.bind(this);
    this.loadAutoVotekickConfig = this.loadAutoVotekickConfig.bind(this);
    this.saveAutoSettings = this.saveAutoSettings.bind(this);
    this.loadAutoSettings = this.loadAutoSettings.bind(this);
  }

  async loadCameraConfig() {
    return get(`get_camera_notification_config`)
      .then((res) => showResponse(res, "get_camera_notification_config", false))
      .then(
        (data) =>
          !data.failed &&
          this.setState({
            cameraBroadcast: data.result.broadcast,
            cameraWelcome: data.result.welcome,
          })
      )
      .catch(handle_http_errors);
  }

  async saveCameraConfig(data) {
    return postData(
      `${process.env.REACT_APP_API_URL}set_camera_notification_config`,
      data
    )
      .then((res) => showResponse(res, "set_camera_notification_config", true))
      .then(this.loadCameraConfig)
      .catch(handle_http_errors);
  }

  async loadAutoVotekickConfig() {
    return get(`get_votekick_autotoggle_config`)
      .then((res) => showResponse(res, "get_votekick_autotoggle_config", false))
      .then(
        (data) =>
          !data.failed &&
          this.setState({
            autovotekickEnabled: data.result.enabled,
            autovotekickMinIngameMods: data.result.minimum_ingame_mods,
            autovotekickMinOnlineMods: data.result.minimum_online_mods,
            autovotekickConditionType: data.result.condition,
          })
      )
      .catch(handle_http_errors);
  }

  async saveAutoVotekickConfig(data) {
    return postData(
      `${process.env.REACT_APP_API_URL}set_votekick_autotoggle_config`,
      data
    )
      .then((res) => showResponse(res, "set_votekick_autotoggle_config", true))
      .then(this.loadAutoVotekickConfig)
      .catch(handle_http_errors);
  }

  async loadBroadcastsSettings() {
    return get(`get_auto_broadcasts_config`)
      .then((res) => showResponse(res, "get_auto_broadcasts_config", false))
      .then(
        (data) =>
          !data.failed &&
          this.setState({
            broadcastMessages: data.result.messages.map(
              (m) => m.time_sec + " " + m.message
            ),
            randomize: data.result.randomize,
            enabled: data.result.enabled,
          })
      )
      .catch(handle_http_errors);
  }

  async saveBroadcastsSettings(data) {
    return postData(
      `${process.env.REACT_APP_API_URL}set_auto_broadcasts_config`,
      data
    )
      .then((res) => showResponse(res, "set_auto_broadcasts_config", true))
      .then((res) => !res.failed && this.setState(data))
      .catch(handle_http_errors);
  }

  async loadStandardMessages() {
    return get(`get_standard_${this.state.standardMessagesType}_messages`)
      .then((res) =>
        showResponse(
          res,
          `get_standard_${this.state.standardMessagesType}_messages`,
          false
        )
      )
      .then((data) => {
        // This is janky, but convert saved broadcasts from an object to a string
        let formattedMessages = new Array();
        if (this.state.standardMessagesType == "broadcast") {
          data.result.messages.forEach((m) =>
            formattedMessages.push(`${m.time_sec} ${m.message}`)
          );
          data.result.messages = formattedMessages;
        }
        return data;
      })
      .then((data) => {
        return (
          !data.failed &&
          this.setState({
            standardMessages: data.result.messages,
          })
        );
      })
      .catch(handle_http_errors);
  }

  async saveStandardMessages() {
    return postData(
      `${process.env.REACT_APP_API_URL}set_standard_${this.state.standardMessagesType}_messages`,
      {
        messages: this.state.standardMessages,
      }
    )
      .then((res) =>
        showResponse(
          res,
          `set_standard_${this.state.standardMessagesType}_messages`,
          true
        )
      )
      .then(this.loadStandardMessages)
      .catch(handle_http_errors);
  }

  async loadAutoSettings() {
    return get(`get_auto_settings`)
      .then((res) => showResponse(res, "get_auto_settings", false))
      .then(
        (data) =>
          !data.failed &&
          this.setState(
            {
              autosettings: JSON.stringify(data.result, null, 2),
            },
            () =>
              this.editorRef.current &&
              this.editorRef.current.setValue(this.state.autosettings)
          )
      )
      .catch(handle_http_errors);
  }

  async saveAutoSettings() {
    return postData(`${process.env.REACT_APP_API_URL}set_auto_settings`, {
      forward: this.state.forwardAutoSettings,
      settings: this.state.autosettings,
    })
      .then((res) => showResponse(res, `set_auto_settings`, true))
      .catch(handle_http_errors);
  }

  async clearCache() {
    return postData(`${process.env.REACT_APP_API_URL}clear_cache`, {})
      .then((res) => showResponse(res, "clear_cache", true))
      .catch(handle_http_errors);
  }

  async reconnectToGameServer() {
    return postData(`${process.env.REACT_APP_API_URL}reconnect_gameserver`, {})
      .then((res) => showResponse(res, "reconnect_gameserver", true))
      .catch(handle_http_errors);
  }

  validate_messages() {
    let hasErrors = false;
    _.forEach(this.state.broadcastMessages, (m) => {
      const split = _.split(m, " ");

      if (_.isNaN(_.toNumber(split[0]))) {
        toast.error(`Invalid line, must start with number of seconds: ${m}`);
        hasErrors = true;
      }
    });
    return !hasErrors;
  }

  saveBroadCastMessages() {
    if (this.validate_messages()) {
      this.saveBroadcastsSettings({
        enabled: this.state.enabled,
        randomize: this.state.randomize,
        messages: this.state.broadcastMessages,
      });
    }
  }

  handleEditorDidMount(editor, monaco) {
    this.editorRef.current = editor;
  }

  componentDidMount() {
    this.loadBroadcastsSettings();
    this.loadStandardMessages();
    this.loadCameraConfig();
    this.loadAutoVotekickConfig();
    this.loadAutoSettings();
  }

  toggle(name) {
    const bool = !this.state[name];
    window.localStorage.setItem(name, bool);
    this.setState({ [name]: bool });
  }

  render() {
    const {
      broadcastMessages,
      standardMessages,
      standardMessagesType,
      enabled,
      randomize,
      cameraBroadcast,
      cameraWelcome,
      autovotekickEnabled,
      autovotekickMinIngameMods,
      autovotekickMinOnlineMods,
      autovotekickConditionType,
      autosettings,
      forwardAutoSettings,
    } = this.state;

    return (
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <h2>Advanced RCON settings</h2>
        </Grid>
        <Grid item xs={12} >
          <Typography variant="h6">Automated broadcast cycle</Typography>
        </Grid>
        <Grid item xs={12}>
          <Grid container justify="space-evenly">
            <Grid item>
              <Padlock
                handleChange={(v) =>
                  this.saveBroadcastsSettings({
                    enabled: v,
                    randomize: randomize,
                    messages: broadcastMessages,
                  })
                }
                checked={enabled}
                label="Auto broadcast enabled"
              />
            </Grid>
            <Grid item>
              <Padlock
                handleChange={(v) =>
                  this.saveBroadcastsSettings({
                    enabled: enabled,
                    randomize: v,
                    messages: broadcastMessages,
                  })
                }
                checked={randomize}
                label="Randomized messages"
              />
            </Grid>
          </Grid>
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Auto broadcast messages"
            multiline
            rows={4}
            rowsMax={30}
            value={_.join(
              broadcastMessages.map((m) => m.replace(/\n/g, "\\n")),
              "\n"
            )}
            onChange={(e) =>
              this.setState({
                broadcastMessages: _.split(e.target.value, "\n"),
              })
            }
            placeholder="Insert your messages here, one per line, with format: <number of seconds to display> <a message (write: \n if you want a line return)>"
            variant="outlined"
            helperText="You can use the following variables in the text using the following syntax: '60 Welcome to {server_name}. The next map is {next_map}.'
            (admin_names, ingame_mods, junior_names, map_rotation, next_map, online_mods, owner_names, random_vip_name, scrolling_votemap, senior_names, 
            server_name, vip_names, votenextmap_by_mod_line, votenextmap_by_mod_split, votenextmap_by_mod_vertical, votenextmap_by_mod_vertical_all, 
            votenextmap_line, votenextmap_line, votenextmap_noscroll, votenextmap_vertical, winning_maps_all, winning_maps_short)"
          />
        </Grid>
        <Grid item xs={12}>
          <Button
            fullWidth
            onClick={this.saveBroadCastMessages}
            variant="outlined"
          >
            Save auto broadcast messages
          </Button>
        </Grid>
        <Grid item xs={12} >
          <Typography variant="h6">
            Manage your personal text history
          </Typography>
        </Grid>
        <Grid
          container
          spacing={1}
          alignContent="center"
          justify="center"
          alignItems="center"
          
        >
          <Grid item xs={12}>
            <TextHistoryManager  />
          </Grid>
        </Grid>
        <Grid item xs={12} >
          <Typography variant="h6">Manage shared standard messages</Typography>
        </Grid>
        <Grid item xs={12} >
          <SelectNameSpace
            value={standardMessagesType}
            handleChange={(v) =>
              this.setState(
                { standardMessagesType: v },
                this.loadStandardMessages
              )
            }
            values={["punishments", "welcome", "broadcast"]}
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Shared standard messages"
            multiline
            rowsMax={30}
            rows={4}
            value={_.join(
              standardMessages.map((m) => m.replace(/\n/g, "\\n")),
              "\n"
            )}
            onChange={(e) =>
              this.setState({ standardMessages: _.split(e.target.value, "\n") })
            }
            placeholder="Set one message per line. If you want a line return in one of the message write: \n"
            variant="outlined"
            helperText="Set one message per line. If you want a line return in one of the message write: \n"
          />
        </Grid>
        <Grid item xs={12}>
          <Button
            fullWidth
            onClick={this.saveStandardMessages}
            variant="outlined"
          >
            Save shared messages
          </Button>
        </Grid>
        <Grid item  justify="center" xs={12}>
          <Typography variant="h5">Add player to watchlist</Typography>
        </Grid>
        <Grid item xs={12}>
          <ManualWatchList  />
        </Grid>
        <Grid item  justify="center" xs={12}>
          <Typography variant="h5">Manage services</Typography>
        </Grid>
        <Grid item  justify="center" xs={12}>
          <Grid container justify="center">
            <Grid item md={8} xs={12}>
              <ServicesList  />
            </Grid>
          </Grid>
        </Grid>
        {/* <Grid item  justify="center" xs={12}>
          <Typography variant="h5">Discord Webhooks configuration</Typography>
        </Grid>
        <Grid
          item
          xs={12}
          alignContent="center"
          justify="center"
          alignItems="center"
        >
          <WebhooksConfig type="watchlist" />
        </Grid>
        <Grid
          item
          xs={12}
          alignContent="center"
          justify="center"
          alignItems="center"
        >
          <WebhooksConfig type="camera" />
        </Grid> */}
        <Grid item  justify="center" xs={12}>
          <Typography variant="h5">
            Auto votekick toggle{" "}
            <Tooltip title="When enabled this feature manages the votekicks ingame by turning it off if the conditions you set below are met, and turning it back on if they are NOT met">
              <HelpIcon fontSize="small" />
            </Tooltip>
          </Typography>
          <Typography variant="body1">Turn off votekick if</Typography>
        </Grid>
        <Grid
          container
          alignContent="center"
          justify="center"
          alignItems="center"
          spacing={1}
        >
          <Grid item xs={12}>
            <TextField
              type="number"
              label="# ingame moderator"
              value={autovotekickMinIngameMods}
              onChange={(e) =>
                this.saveAutoVotekickConfig({
                  enabled: autovotekickEnabled,
                  minimum_ingame_mods: e.target.value,
                  minimum_online_mods: autovotekickMinOnlineMods,
                  condition: autovotekickConditionType,
                })
              }
              helperText="Number of moderator in game is greater or equal"
            />
            <FormControl>
              <InputLabel>Condition</InputLabel>
              <Select
                native
                value={autovotekickConditionType}
                onChange={(e) =>
                  this.saveAutoVotekickConfig({
                    enabled: autovotekickEnabled,
                    minimum_ingame_mods: autovotekickMinIngameMods,
                    minimum_online_mods: autovotekickMinOnlineMods,
                    condition: e.target.value,
                  })
                }
              >
                <option value="OR">OR</option>
                <option value="AND">AND</option>
              </Select>
              <FormHelperText>and / or</FormHelperText>
            </FormControl>
            <TextField
              type="number"
              label="# online moderator"
              value={autovotekickMinOnlineMods}
              onChange={(e) =>
                this.saveAutoVotekickConfig({
                  enabled: autovotekickEnabled,
                  minimum_ingame_mods: autovotekickMinIngameMods,
                  minimum_online_mods: e.target.value,
                  condition: autovotekickConditionType,
                })
              }
              helperText="number of moderator with the rcon openned"
            />
          </Grid>
          <Grid item>
            <Padlock
              label="Auto votekick toggle enabled"
              checked={autovotekickEnabled}
              handleChange={(v) =>
                this.saveAutoVotekickConfig({
                  enabled: v,
                  minimum_ingame_mods: autovotekickMinIngameMods,
                  minimum_online_mods: autovotekickMinOnlineMods,
                  condition: autovotekickConditionType,
                })
              }
            />
          </Grid>
        </Grid>
        <Grid item  justify="center" xs={12}>
          <Typography variant="h5">Camera notification config</Typography>
        </Grid>
        <Grid
          container
          alignContent="center"
          justify="center"
          alignItems="center"
        >
          <Padlock
            label="broadcast"
            checked={cameraBroadcast}
            handleChange={(v) =>
              this.saveCameraConfig({ welcome: cameraWelcome, broadcast: v })
            }
          />
          <Padlock
            label="set welcome message"
            checked={cameraWelcome}
            handleChange={(v) =>
              this.saveCameraConfig({ welcome: v, broadcast: cameraBroadcast })
            }
          />
        </Grid>
        <Grid
          container
          alignContent="center"
          justify="center"
          alignItems="center"
        >
          <Grid item xs={12}>
            <Typography variant="h5">
              Real VIP slots{" "}
              <Tooltip
                title=" When enabled each VIP that enters the servers takes 1 VIP slot that is
            not release until a VIP leaves. This is done by dynaically settings
            the number of VIP slots based on (Max num of VIP slots - current
            number of vips in game). The number of VIP slots will never fall below
            'Min num of VIP slot', you can set that to 0 to have a hard cap.
            If you use the autoSettings don't forget not set the VIPs in there or it will override the realVip system"
              >
                <HelpIcon fontSize="small" />
              </Tooltip>{" "}
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <RealVip  />
          </Grid>
        </Grid>
        <Grid
          container
          alignContent="center"
          justify="center"
          alignItems="center"
        >
          <Grid item xs={12}>
            <Typography variant="h5">
              Server Name{" "}
              <Tooltip title="Only users with a GTX server can use this, it won't work for others. GTX users must set extra info in config/config.yml for it to work. The name change is only applied after a change of map">
                <HelpIcon fontSize="small" />
              </Tooltip>{" "}
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <ServerName  />
          </Grid>
        </Grid>

        <Grid
          container
          alignContent="center"
          justify="center"
          alignItems="center"
        >
          <Grid item xs={12}>
            <Typography variant="h5" gutterBottom>
              Auto settings
            </Typography>
            <Typography variant="body1">
              Can be turned On and Off under "Manage services"
            </Typography>
          </Grid>
        </Grid>
        <Grid item xs={12}>
          <AutoSettings
            words={autosettings}
            onWordsChange={(words, event) =>
              this.setState({ autosettings: words })
            }
            onSave={() => this.saveAutoSettings(autosettings)}
            forward={forwardAutoSettings}
            onFowardChange={() => this.toggle("forwardAutoSettings")}
            onEditorMount={this.handleEditorDidMount}
          />
        </Grid>

        <Grid
          item
          xs={12}
          alignContent="center"
          justify="center"
          alignItems="center"
        >
          <Button
            color="secondary"
            variant="outlined"
            onClick={this.clearCache}
          >
            Clear application cache
          </Button>
        </Grid>
        <Grid
          item
          xs={12}
          alignContent="center"
          justify="center"
          alignItems="center"
        >
          <Button
            color="secondary"
            variant="outlined"
            onClick={this.reconnectToGameServer}
          >
            Reconnect To Gameserver
          </Button>
        </Grid>
      </Grid>
    );
  }
}

export default RconSettings;
