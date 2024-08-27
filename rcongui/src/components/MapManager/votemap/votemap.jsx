import {
  Box,
  Button,
  FormControl,
  InputLabel,
  NativeSelect,
  Paper,
  TextField,
  Typography,
  Snackbar,
  makeStyles,
  createStyles,
} from "@material-ui/core";
import React from "react";
import {
  getVotemapConfig,
  getVotemapStatus,
  resetVotemapState,
  updateVotemapConfig,
} from "../../../utils/fetchUtils";
import Padlock from "../../shared/padlock";
import { VoteStatus } from "./vote-status";
import { messageFieldConfigs, padlockConfigs, textFieldConfigs } from "./configs-data";
import { isEmpty, isEqual } from "lodash";
import { Alert } from "@material-ui/lab";

const useStyles = makeStyles((theme) => createStyles({
  spacing: {
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1),
  },
  messages: {
    maxWidth: theme.breakpoints.values.md,
  },
  container: {
    display: "flex",
    flexDirection: "column",
    gap: theme.spacing(2),
  },
  numberFields: { 
    display: "flex",
    flexDirection: "column",
    gap: theme.spacing(1),
    maxWidth: theme.breakpoints.values.sm,
  },
}))

const UPDATE_INTERVAL = 15 * 1000

const VoteMapConfig = () => {
  const [_config, setConfig] = React.useState({});
  const [configChanges, setConfigChanges] = React.useState({})
  const [incomingChanges, setIncomingChanges] = React.useState(null)
  const [status, setStatus] = React.useState([]);
  const statusIntervalRef = React.useRef(null)
  const configIntervalRef = React.useRef(null)

  const classes = useStyles();

  const config = {
    ..._config,
    ...configChanges,
  }

  async function updateConfig() {
    await updateVotemapConfig(config);
    await getConfig();
    setConfigChanges({});
    setIncomingChanges(null);
  }

  async function getConfig() {
    const config = await getVotemapConfig();
    if (config) {
      setConfig(config);
    }
  }

  async function getStatus() {
    const status = await getVotemapStatus()
    if (status) {
      setStatus(status)
    }
  }

  async function resetState() {
    const newStatus = await resetVotemapState();
    if (newStatus) {
      setStatus(newStatus)
    }
  }

  const handleConfigChange = (propName) => (value) => {
    // When Event object is being passed in as a value
    if (typeof value === "object" && "target" in value) {
      value = value.target.value;
    }
    setConfigChanges((prevConfig) => ({
      ...prevConfig,
      [propName]: value,
    }));
  }

  const acceptIncomingConfigChanges = () => {
    setConfig(incomingChanges);
    setConfigChanges({});
    setIncomingChanges(null);
  }

  React.useEffect(() => {
    getConfig();
    getStatus();
  }, [])

  React.useEffect(() => {
    statusIntervalRef.current = setInterval(getStatus, UPDATE_INTERVAL);
    return () => clearInterval(statusIntervalRef.current);
  }, []);

  React.useEffect(() => {
    configIntervalRef.current = setInterval(async () => {
      const freshConfig = await getVotemapConfig();
      if (!isEqual(_config, freshConfig)) {
        setIncomingChanges(freshConfig);
      }
    }, UPDATE_INTERVAL);
    return () => clearInterval(configIntervalRef.current);
  }, [_config]);

  React.useEffect(() => {
    if (incomingChanges !== null && isEmpty(configChanges)) {
      acceptIncomingConfigChanges()
    }
  }, [incomingChanges, configChanges])

  return (
    <>
      <Snackbar open={incomingChanges !== null} anchorOrigin={{ vertical: 'top', horizontal: 'center' }}>
        <Alert severity="warning" action={
          <Button color="inherit" size="small" onClick={acceptIncomingConfigChanges}>
            Accept changes
          </Button>
        }>The config has changed!</Alert>
      </Snackbar>
      <Box className={classes.container}>
        <Box style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <Padlock
            label="Enabled"
            checked={config.enabled ?? false}
            handleChange={handleConfigChange("enabled")}
          />
          <Box style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
            <Button
              size="small" variant="outlined"
              color="secondary"
              onClick={() => {
                if (window.confirm("Are you sure?") === true) {
                  resetState().then(loadData);
                }
              }}
            >
              Reset selection & votes
            </Button>
            <Button size="small" variant="outlined" onClick={updateConfig}>
              Save changes
            </Button>
          </Box>
        </Box>

        <Box component={Paper} >
          <VoteStatus voteStatus={status} />
        </Box>

        <Typography variant="h6">In-Game Texts</Typography>
        <Box className={classes.messages}>
          {messageFieldConfigs.map((configItem) => (
            <TextField
              key={configItem.name}
              className={classes.spacing}
              fullWidth
              variant="filled"
              multiline
              rows={configItem.rows}
              label={configItem.label}
              helperText={configItem.helperText}
              value={config[configItem.name] ?? ""}
              onChange={handleConfigChange(configItem.name)}
            />
          ))}
        </Box>

        <Typography variant="h6">Other settings</Typography>

        <FormControl className={classes.spacing}>
          <InputLabel>Default map method (when no votes)</InputLabel>
          <NativeSelect
            value={config.default_method ?? ""}
            onChange={handleConfigChange("default_method")}
          >
            <option value="least_played_from_suggestions">
              Pick least played map from suggestions
            </option>
            <option value="least_played_from_all_map">
              Pick least played map from all maps
            </option>
            <option value="random_from_suggestions">
              Pick randomly from suggestions
            </option>
            <option value="random_from_all_maps">
              Pick randomly from all maps
            </option>
          </NativeSelect>
        </FormControl>

        {padlockConfigs.map(({ name, label }) => (
          <Padlock
            key={name}
            label={label}
            checked={config[name] ?? false}
            handleChange={handleConfigChange(name)}
          />
        ))}

        <Box className={classes.numberFields}>
          {textFieldConfigs.map((configItem) => (
            <TextField
              key={configItem.name}
              variant="filled"
              fullWidth
              type="number"
              inputProps={configItem.inputProps}
              label={configItem.label}
              helperText={configItem.helperText}
              value={config[configItem.name] ?? false}
              onChange={handleConfigChange(configItem.name)}
            />
          ))}
        </Box>
      </Box>
    </>
  );
};

export default VoteMapConfig;
