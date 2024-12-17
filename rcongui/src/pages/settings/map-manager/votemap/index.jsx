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
  Accordion,
  AccordionSummary,
  AccordionDetails,
  AccordionActions,
  List,
  IconButton,
} from "@mui/material";
import { makeStyles } from "@mui/styles";
import {
  getVotemapConfig,
  getVotemapStatus,
  getVotemapWhitelist,
  resetVotemapState,
  resetVotemapWhitelist,
  setVotemapWhitelist,
  updateVotemapConfig,
} from "@/utils/fetchUtils";
import Padlock from "@/components/shared/Padlock";
import { VoteStatus } from "./vote-status";
import {
  defaultMapOptions,
  messageFieldConfigs,
  padlockConfigs,
  textFieldConfigs,
} from "./configs-data";
import isEqual from "lodash/isEqual";
import isEmpty from "lodash/isEmpty";
import { Alert } from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { MapAutocomplete } from "@/components/MapManager/map-autocomplete";
import { MapListItem } from "@/components/MapManager/map-list-item";
import DeleteIcon from "@mui/icons-material/Delete";
import { useOutletContext } from "react-router-dom";
import { mapIdsToLayers } from "@/utils/lib";
import { toast } from "react-toastify";
import {useEffect, useMemo, useRef, useState} from "react";

const useStyles = makeStyles((theme) => ({
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
}));

const UPDATE_INTERVAL = 15 * 1000;

const VoteMapConfig = () => {
  const { maps } = useOutletContext();
  const [_config, setConfig] = useState({});
  const [configChanges, setConfigChanges] = useState({});
  const [whitelist, setWhitelist] = useState([]);
  const [mapsToAdd, setMapsToAdd] = useState([]);
  const [incomingChanges, setIncomingChanges] = useState(null);
  const [status, setStatus] = useState([]);
  const statusIntervalRef = useRef(null);
  const configIntervalRef = useRef(null);

  const classes = useStyles();

  const config = {
    ..._config,
    ...configChanges,
  };

  const hasChanges = Object.keys(configChanges).length > 0;

  const autocompleteSelection = useMemo(() => {
    if (!maps.length) return [];

    const mapSelection = maps.reduce((acc, map) => {
      acc[map.id] = map;
      return acc;
    }, {});

    whitelist.forEach((map) => {
      if (map.id in mapSelection) {
        delete mapSelection[map.id];
      }
    });

    return Object.values(mapSelection);
  }, [maps, whitelist]);

  const whitelistSorted = useMemo(() => {
    const sorted = [...whitelist];
    sorted.sort((mapA, mapB) => {
      if (mapA.pretty_name < mapB.pretty_name) {
        return -1;
      }
      if (mapA.pretty_name > mapB.pretty_name) {
        return 1;
      }
      return 0;
    });
    return sorted;
  }, [whitelist]);

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
    if (!maps.length) return;
    const whitelistRaw = await getVotemapWhitelist();
    if (whitelistRaw) {
      const mapLayers = [];
      const invalidMapIds = [];
      whitelistRaw.forEach((mapId) => {
        const mapLayer = maps.find((mapLayer) => mapLayer.id === mapId);
        if (mapLayer) {
          mapLayers.push(mapLayer);
        } else {
          invalidMapIds.push(mapId);
        }
      });
      setWhitelist(mapLayers);
      if (invalidMapIds.length) {
        toast.error(
          `Some maps in your whitelist have been deleted or renamed: ${invalidMapIds.join(
            ", "
          )}. Reset the whitelist or changed your auto settings.`
        );
      }
    }
  }

  async function submitWhitelist() {
    const whitelistRaw = whitelist.map((map) => map.id);
    const returnedWhitelist = await setVotemapWhitelist(whitelistRaw);
    if (returnedWhitelist) {
      getWhitelist();
    }
  }

  async function resetWhitelist() {
    const whitelistMapIds = await resetVotemapWhitelist();
    if (whitelistMapIds) {
      setWhitelist(mapIdsToLayers(maps, whitelistMapIds));
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

  useEffect(() => {
    getConfig();
    getStatus();
  }, []);

  useEffect(() => {
    statusIntervalRef.current = setInterval(getStatus, UPDATE_INTERVAL);
    return () => clearInterval(statusIntervalRef.current);
  }, []);

  useEffect(() => {
    configIntervalRef.current = setInterval(async () => {
      const freshConfig = await getVotemapConfig();
      if (!isEqual(_config, freshConfig)) {
        setIncomingChanges(freshConfig);
      }
    }, UPDATE_INTERVAL);
    return () => clearInterval(configIntervalRef.current);
  }, [_config]);

  useEffect(() => {
    if (incomingChanges !== null && isEmpty(configChanges)) {
      acceptIncomingConfigChanges();
    }
  }, [incomingChanges, configChanges]);

  useEffect(() => {
    getWhitelist();
  }, [maps]);

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
              color={hasChanges ? "secondary" : "inherit"}
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
              color={hasChanges ? "secondary" : "inherit"}
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
            aria-controls="panel3a-content"
            id="panel3a-header"
          >
            <Typography className={classes.heading}>
              {"Allowed maps (Whitelist)"}
            </Typography>
          </AccordionSummary>

          <AccordionActions>
            <Button size="small" variant="outlined" onClick={getWhitelist}>
              Refresh
            </Button>
            <Button
              color={"secondary"}
              size="small"
              variant="outlined"
              onClick={resetWhitelist}
            >
              Reset whitelist
            </Button>
            <Button
              color={"secondary"}
              size="small"
              variant="outlined"
              onClick={submitWhitelist}
            >
              Save whitelist
            </Button>
          </AccordionActions>

          <AccordionDetails>
            <Box component={"section"} className={classes.section}>
              <Box style={{ display: "flex", gap: "0.5rem" }}>
                <MapAutocomplete
                  options={autocompleteSelection}
                  style={{ flexGrow: 1 }}
                  onChange={(e, v) => setMapsToAdd(v)}
                  value={mapsToAdd}
                />
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => {
                    setWhitelist(whitelist.concat(mapsToAdd));
                    setMapsToAdd([]);
                  }}
                  style={{ width: 60 }}
                >
                  Add
                </Button>
              </Box>
              <List dense={true}>
                {whitelistSorted.map((thisMapLayer, index) => (
                  <MapListItem
                    key={`${index}#${thisMapLayer.id}`}
                    mapLayer={thisMapLayer}
                    secondaryAction={
                      <IconButton
                        edge="end"
                        aria-label="delete"
                        onClick={() =>
                          setWhitelist((prevWhitelist) =>
                            prevWhitelist.filter(
                              (mapLayer) => mapLayer.id !== thisMapLayer.id
                            )
                          )
                        }
                        size="large"
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
