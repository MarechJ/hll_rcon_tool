import React from "react";
import {
  Button,
  Grid,
  IconButton,
  Link,
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
import { toast } from "react-toastify";
import _ from "lodash";
import Padlock from "../../components/SettingsView/padlock";
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

const ManualWatchList = ({ classes }) => {
  const [name, setName] = React.useState("");
  const [steamId64, setSteamId64] = React.useState("");
  const [reason, setReason] = React.useState("");
  const [sharedMessages, setSharedMessages] = React.useState([]);

  React.useEffect(() => {
    getSharedMessages("punitions").then((data) => setSharedMessages(data));
  }, []);
  const textHistory = new TextHistory("watchlist");

  return (
    <ManualPlayerInput
      name={name}
      setName={setName}
      steam_id={steamId64}
      setSteamId={setSteamId64}
      reason={reason}
      setReason={setReason}
      textHistory={textHistory}
      sharedMessages={sharedMessages}
      classes={classes}
      actionName="Watch"
      tooltipText="You will get a notification on you watchlist discord hook when this player enters your server"
      onSubmit={() => addPlayerToWatchList(steamId64, reason, null, name)}
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

class RconSettings extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      broadcastMessages: [],
      standardMessages: [],
      standardMessagesType: "punitions",
      randomized: false,
      enabled: false,
      cameraBroadcast: false,
      cameraWelcome: false,
      autovotekickEnabled: false,
      autovotekickMinIngameMods: 0,
      autovotekickMinOnlineMods: 0,
      autovotekickConditionType: "OR",
    };

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
  }

  async loadCameraConfig() {
    return get(`get_camera_config`)
      .then((res) => showResponse(res, "get_camera_config", false))
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
    return postData(`${process.env.REACT_APP_API_URL}set_camera_config`, data)
      .then((res) => showResponse(res, "set_camera_config", true))
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
            autovotekickEnabled: data.result.is_enabled,
            autovotekickMinIngameMods: data.result.min_ingame_mods,
            autovotekickMinOnlineMods: data.result.min_online_mods,
            autovotekickConditionType: data.result.condition_type,
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
            broadcastMessages: data.result.messages,
            randomized: data.result.randomized,
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
    return get(
      `get_standard_messages?message_type=${this.state.standardMessagesType}`
    )
      .then((res) => showResponse(res, "get_standard_messages", false))
      .then(
        (data) =>
          !data.failed &&
          this.setState({
            standardMessages: data.result,
          })
      )
      .catch(handle_http_errors);
  }

  async saveStandardMessages() {
    return postData(`${process.env.REACT_APP_API_URL}set_standard_messages`, {
      message_type: this.state.standardMessagesType,
      messages: this.state.standardMessages,
    })
      .then((res) => showResponse(res, "set_standard_messages", true))
      .then(this.loadStandardMessages)
      .catch(handle_http_errors);
  }

  async clearCache() {
    return postData(`${process.env.REACT_APP_API_URL}clear_cache`, {})
      .then((res) => showResponse(res, "clear_cache", true))
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
      this.saveBroadcastsSettings({ messages: this.state.broadcastMessages });
    }
  }

  componentDidMount() {
    this.loadBroadcastsSettings();
    this.loadStandardMessages();
    this.loadCameraConfig();
    this.loadAutoVotekickConfig();
  }

  render() {
    const {
      broadcastMessages,
      standardMessages,
      standardMessagesType,
      enabled,
      randomized,
      cameraBroadcast,
      cameraWelcome,
      autovotekickEnabled,
      autovotekickMinIngameMods,
      autovotekickMinOnlineMods,
      autovotekickConditionType,
    } = this.state;
    const { classes, theme, themes, setTheme } = this.props;

    return (
      <Grid container className={classes.paper} spacing={3}>
        <Grid item xs={12}>
          <h2>Advanced RCON settings</h2>
        </Grid>
        <Grid item xs={12} className={classes.padding}>
          <Typography variant="h6">Your RCON color theme</Typography>
        </Grid>
        <Grid item xs={12} className={classes.padding}>
          <FormControl style={{ minWidth: "200px" }}>
            <InputLabel>Pick your theme</InputLabel>
            <Select
              value={theme}
              onChange={(event) => setTheme(event.target.value)}
            >
              {themes.map((t) => (
                <MenuItem key={t} value={t}>
                  {t}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} className={classes.padding}>
          <Typography variant="h6">Automated broadcast cycle</Typography>
        </Grid>
        <Grid item xs={12}>
          <Grid container justify="space-evenly">
            <Grid item>
              <Padlock
                handleChange={(v) =>
                  this.saveBroadcastsSettings({ enabled: v })
                }
                checked={enabled}
                label="Auto broadcast enabled"
              />
            </Grid>
            <Grid item>
              <Padlock
                handleChange={(v) =>
                  this.saveBroadcastsSettings({ randomized: v })
                }
                checked={randomized}
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
            helperText="You can use the following variables in the text using the following syntax: '60 Welcome to {servername}. The next map is {nextmap}.'
              (nextmap, maprotation, servername, vips, randomvip, votenextmap_line, votenextmap_line, votenextmap_noscroll, votenextmap_vertical,
              votenextmap_by_mod_line, votenextmap_by_mod_vertical, votenextmap_by_mod_vertical_all, votenextmap_by_mod_split, total_votes,
              winning_maps_short, winning_maps_all, scrolling_votemap, online_mods, ingame_mods)"
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
        <Grid item xs={12} className={classes.padding}>
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
          className={classes.root}
        >
          <Grid item xs={12} className={`${classes.padding} ${classes.margin}`}>
            <TextHistoryManager classes={classes} />
          </Grid>
        </Grid>
        <Grid item xs={12} className={classes.padding}>
          <Typography variant="h6">Manage shared standard messages</Typography>
        </Grid>
        <Grid item xs={12} className={classes.padding}>
          <SelectNameSpace
            value={standardMessagesType}
            handleChange={(v) =>
              this.setState(
                { standardMessagesType: v },
                this.loadStandardMessages
              )
            }
            values={["punitions", "welcome", "broadcast"]}
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
        <Grid item className={classes.paddingTop} justify="center" xs={12}>
          <Typography variant="h5">Blacklist player by Steam ID</Typography>
        </Grid>
        <Grid item className={classes.paddingTop} justify="center" xs={12}>
          <Blacklist classes={classes} />
        </Grid>
        <Grid item className={classes.paddingTop} justify="center" xs={12}>
          <Typography variant="h5">Add player to watchlist</Typography>
        </Grid>
        <Grid item xs={12}>
          <ManualWatchList classes={classes} />
        </Grid>
        <Grid item className={classes.paddingTop} justify="center" xs={12}>
          <Typography variant="h5">Manage services</Typography>
        </Grid>
        <Grid item className={classes.paddingTop} justify="center" xs={12}>
          <Grid container justify="center">
            <Grid item md={8} xs={12}>
              <ServicesList classes={classes} />
            </Grid>
          </Grid>
        </Grid>
        <Grid item className={classes.paddingTop} justify="center" xs={12}>
          <Typography variant="h5">Discord Webhooks configuration</Typography>
        </Grid>
        <Grid
          item
          xs={12}
          className={`${classes.padding} ${classes.margin} ${classes.root}`}
          alignContent="center"
          justify="center"
          alignItems="center"
        >
          <WebhooksConfig classes={classes} />
        </Grid>
        <Grid item className={classes.paddingTop} justify="center" xs={12}>
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
          className={`${classes.padding} ${classes.margin}`}
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
                this.saveAutoVotekickConfig({ min_ingame_mods: e.target.value })
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
                    condition_type: e.target.value,
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
                this.saveAutoVotekickConfig({ min_online_mods: e.target.value })
              }
              helperText="number of moderator with the rcon openned"
            />
          </Grid>
          <Grid item>
            <Padlock
              label="Auto votekick toggle enabled"
              checked={autovotekickEnabled}
              handleChange={(v) =>
                this.saveAutoVotekickConfig({ is_enabled: v })
              }
            />
          </Grid>
        </Grid>
        <Grid item className={classes.paddingTop} justify="center" xs={12}>
          <Typography variant="h5">Camera notification config</Typography>
        </Grid>
        <Grid
          container
          className={`${classes.padding} ${classes.margin} ${classes.root}`}
          alignContent="center"
          justify="center"
          alignItems="center"
        >
          <Padlock
            label="broadcast"
            checked={cameraBroadcast}
            handleChange={(v) => this.saveCameraConfig({ broadcast: v })}
          />
          <Padlock
            label="set welcome message"
            checked={cameraWelcome}
            handleChange={(v) => this.saveCameraConfig({ welcome: v })}
          />
        </Grid>
        <Grid item className={classes.paddingTop} justify="center" xs={12}>
          <Typography variant="h5">Misc. options</Typography>
        </Grid>
        ]{" "}
        <Grid
          container
          className={`${classes.padding} ${classes.margin} ${classes.root}`}
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
            <RealVip classes={classes} />
          </Grid>
        </Grid>
        <Grid
          container
          className={`${classes.padding} ${classes.margin} ${classes.root}`}
          alignContent="center"
          justify="center"
          alignItems="center"
        >
          <Grid item xs={12}>
            <Typography variant="h5">
              Server Name
              <Tooltip title="Only users with a GTX server can use this, it won't work for others. GTX users must set extra info in config/config.yml for it to work. The name change is only applied after a change of map">
                <HelpIcon fontSize="small" />
              </Tooltip>{" "}
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <ServerName classes={classes} />
          </Grid>
        </Grid>
        <Grid
          item
          xs={12}
          className={`${classes.padding} ${classes.margin} ${classes.root}`}
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
      </Grid>
    );
  }
}

export default RconSettings;
