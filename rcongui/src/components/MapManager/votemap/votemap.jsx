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
  Accordion,
  AccordionSummary,
  AccordionDetails,
  AccordionActions,
  List,
  IconButton,
} from "@material-ui/core";
import React from "react";
import {
  getVotemapConfig,
  getVotemapStatus,
  getVotemapWhitelist,
  resetVotemapState,
  resetVotemapWhitelist,
  setVotemapWhitelist,
  updateVotemapConfig,
} from "../../../utils/fetchUtils";
import Padlock from "../../shared/padlock";
import { VoteStatus } from "./vote-status";
import {
  defaultMapOptions,
  messageFieldConfigs,
  padlockConfigs,
  textFieldConfigs,
} from "./configs-data";
import { isEmpty, isEqual } from "lodash";
import { Alert } from "@material-ui/lab";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import { MapAutocomplete } from "../map-autocomplete";
import { MapListItem } from "../map-list-item";
import DeleteIcon from "@material-ui/icons/Delete";


const useStyles = makeStyles((theme) =>
  createStyles({
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
    sticky: {
      position: "sticky",
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      padding: theme.spacing(1),
      background: theme.palette.background.default,
      zIndex: theme.zIndex.appBar,
      top: 0,
    },
    section: {
      position: "relative",
      width: "100%",
    },
  })
);

const UPDATE_INTERVAL = 15 * 1000;

const VoteMapConfig = ({ maps }) => {
  const [_config, setConfig] = React.useState({});
  const [configChanges, setConfigChanges] = React.useState({});
  const [whitelistState, setWhitelistState] = React.useState([]);
  const [incomingChanges, setIncomingChanges] = React.useState(null);
  const [status, setStatus] = React.useState([]);
  const statusIntervalRef = React.useRef(null);
  const configIntervalRef = React.useRef(null);

  const classes = useStyles();

  const config = {
    ..._config,
    ...configChanges,
  };

  const hasChanges = Object.keys(configChanges).length > 0;
  const whitelist = React.useMemo(() => {
    if (!maps.length || !whitelistState.length) {
      return [];
    }
    return whitelistState.map((mapId) =>
      maps.find((mapLayer) => mapLayer.id === mapId)
    );
  }, [maps, whitelistState]);

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
    const status = await getVotemapStatus();
    if (status) {
      setStatus(status);
    }
  }

  async function resetState() {
    const newStatus = await resetVotemapState();
    if (newStatus) {
      setStatus(newStatus);
    }
  }

  async function getWhitelist() {
    const whitelist = await getVotemapWhitelist();
    if (whitelist) {
      setWhitelistState(whitelist);
    }
  }

  async function setWhitelist(whitelist) {
    const result = await setVotemapWhitelist(whitelist);
    if (result) {
      await getWhitelist();
    }
  }

  async function resetWhitelist() {
    const newWhitelist = await resetVotemapWhitelist();
    if (newWhitelist) {
      setWhitelistState(newWhitelist);
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
  };

  const handleEnableToggle = async () => {
    await updateVotemapConfig({
      ..._config,
      enabled: !_config.enabled,
    });
    await getConfig();
  };

  const acceptIncomingConfigChanges = () => {
    setConfig(incomingChanges);
    setConfigChanges({});
    setIncomingChanges(null);
  };

  React.useEffect(() => {
    getConfig();
    getStatus();
    getWhitelist();
  }, []);

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
      acceptIncomingConfigChanges();
    }
  }, [incomingChanges, configChanges]);

  return (
    <>
      <Snackbar
        open={incomingChanges !== null}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Alert
          severity="warning"
          action={
            <Button
              color="inherit"
              size="small"
              onClick={acceptIncomingConfigChanges}
            >
              Accept changes
            </Button>
          }
        >
          The config has changed!
        </Alert>
      </Snackbar>
      <Box className={classes.container}>
        <Box component={"section"} className={classes.section}>
          <Box
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              paddingBottom: 4,
            }}
          >
            <Padlock
              label="Enabled"
              checked={config.enabled ?? false}
              handleChange={handleEnableToggle}
            />

            <Button
              size="small"
              variant="outlined"
              color="secondary"
              onClick={() => {
                if (window.confirm("Are you sure?") === true) {
                  resetState();
                }
              }}
            >
              Reset selection & votes
            </Button>
          </Box>

          <Box component={Paper}>
            <VoteStatus voteStatus={status} />
          </Box>
        </Box>

        <Accordion>
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls="panel1a-content"
            id="panel1a-header"
          >
            <Typography className={classes.heading}>In-Game Texts</Typography>
          </AccordionSummary>

          <AccordionDetails>
            <Box component={"section"} className={classes.section}>
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
            </Box>
          </AccordionDetails>

          <AccordionActions>
            <Button
              color={hasChanges ? "secondary" : "default"}
              size="small"
              variant="outlined"
              onClick={updateConfig}
            >
              Save changes
            </Button>
          </AccordionActions>
        </Accordion>
        <Accordion>
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls="panel2a-content"
            id="panel2a-header"
          >
            <Typography className={classes.heading}>Other settings</Typography>
          </AccordionSummary>

          <AccordionDetails>
            <Box component={"section"} className={classes.section}>
              <FormControl className={classes.spacing}>
                <InputLabel>Default map method (when no votes)</InputLabel>
                <NativeSelect
                  value={config.default_method ?? ""}
                  onChange={handleConfigChange("default_method")}
                >
                  {defaultMapOptions.map((option) => (
                    <option key={option.name} value={option.name}>
                      {option.label}
                    </option>
                  ))}
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
          </AccordionDetails>

          <AccordionActions>
            <Button
              color={hasChanges ? "secondary" : "default"}
              size="small"
              variant="outlined"
              onClick={updateConfig}
            >
              Save changes
            </Button>
          </AccordionActions>
        </Accordion>

        <Accordion>
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls="panel2a-content"
            id="panel2a-header"
          >
            <Typography className={classes.heading}>
              {"Allowed maps (Whitelist)"}
            </Typography>
          </AccordionSummary>

          <AccordionActions>
            <Button
              color={"secondary"}
              size="small"
              variant="outlined"
              onClick={() => {
                console.log("TODO");
              }}
            >
              Save whitelist
            </Button>
          </AccordionActions>

          <AccordionDetails>
            <Box component={"section"} className={classes.section}>
              {/* TODO: Provide only those that are not in the list */}
              <MapAutocomplete options={maps} />
              <List dense={true}>
                {whitelist.map((mapLayer, index) => (
                  <MapListItem
                    button
                    onClick={() => {
                      console.log("TODO");
                      // setSelected(mapLayer.id);
                    }}
                    key={`${index}#${mapLayer.id}`}
                    mapLayer={mapLayer}
                    renderAction={(mapLayer) =>
                        <IconButton
                        edge="end"
                        aria-label="delete"
                        onClick={() => setWhitelistState(prevWhitelist => prevWhitelist.filter((mapId => mapId !== mapLayer.id)))}
                      >
                        <DeleteIcon />
                      </IconButton>
                    }
                  />
                ))}
              </List>
            </Box>
          </AccordionDetails>
        </Accordion>
      </Box>
    </>
  );
};

export default VoteMapConfig;
