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
} from "@mui/material";
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
import { Alert } from '@mui/material';
import { styled } from "@mui/material/styles"

const Messages = styled('div')(({ theme }) => ({
  maxWidth: theme.breakpoints.values.md,
}));

const Container = styled('div')(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  gap: theme.spacing(2),
  marginTop: theme.spacing(1),
  marginBottom: theme.spacing(1),
}));

const NumberFields = styled('div')(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  gap: theme.spacing(1),
  maxWidth: theme.breakpoints.values.sm,
  marginTop: theme.spacing(1),
  marginBottom: theme.spacing(1),
}));

const UPDATE_INTERVAL = 15 * 1000;

const VoteMapConfig = ({ maps }) => {
  const [_config, setConfig] = React.useState({});
  const [configChanges, setConfigChanges] = React.useState({});
  const [whitelist, setWhitelist] = React.useState([]);
  const [mapsToAdd, setMapsToAdd] = React.useState([]);
  const [incomingChanges, setIncomingChanges] = React.useState(null);
  const [status, setStatus] = React.useState([]);
  const statusIntervalRef = React.useRef(null);
  const configIntervalRef = React.useRef(null);

  const config = {
    ..._config,
    ...configChanges,
  };

  const hasChanges = Object.keys(configChanges).length > 0;

  const autocompleteSelection = React.useMemo(() => {
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

  const whitelistSorted = React.useMemo(() => {
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
    const whitelistRaw = await resetVotemapWhitelist();
    if (whitelistRaw) {
      setWhitelist(
        whitelistRaw.map((mapId) =>
          maps.find((mapLayer) => mapLayer.id === mapId)
        )
      );
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

  React.useEffect(() => {
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
      <Container>
        <Box style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <Padlock
            label="Enabled"
            checked={config.enabled ?? false}
            handleChange={handleConfigChange("enabled")}
          />
          <Box style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
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

        <Box component={Paper} >
          <VoteStatus voteStatus={status} />
        </Box>

        <Typography variant="h6">In-Game Texts</Typography>
        <Messages>
          {messageFieldConfigs.map((configItem) => (
            <TextField
              key={configItem.name}
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
        </Messages>

        <Typography variant="h6">Other settings</Typography>

        <FormControl>
          <InputLabel>Default map method (when no votes)</InputLabel>
          <NativeSelect
            value={config.default_method ?? ""}
            onChange={handleConfigChange("default_method")}
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

        <NumberFields>
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
        </NumberFields>
      </Container>
    </>
  );
};

export default VoteMapConfig;
