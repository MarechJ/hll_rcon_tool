import {
  Box,
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemText,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from "@mui/material";
import storageKeys from "@/config/storageKeys";
import TableConfigDrawer from "@/components/table/TableConfigDrawer";
import {Fragment, useEffect, useState} from "react";
import { useStorageState } from "@/hooks/useStorageState";
import { DebouncedSearchInput } from "@/components/shared/DebouncedSearchInput";
import SettingsIcon from "@mui/icons-material/Settings";
import { logActions as _logActions } from "@/utils/lib";
import { LogActionSelectionMenu } from "@/components/table/selection/LogActionSelectionMenu";
import { LogPlayerSelectionMenu } from "@/components/table/selection/LogPlayerSelectionMenu";
import { LogActionQuerySelectionMenu } from "@/components/table/selection/LogActionQuerySelectionMenu";
import DeleteIcon from "@mui/icons-material/Delete";
import { TablePagination } from "@/components/table/TablePagination";
import { TableToolbar } from "@/components/table/TableToolbar";
import TableAddons from "@/components/table/TableAddons";
import { LogActionHighlightMenu } from "@/components/table/selection/LogActionHighlightMenu";
import LiveLogsTable from "@/components/live-logs/LiveLogsTable";

const logActions = Object.entries(_logActions).reduce((acc, [name]) => {
  acc[name] = false;
  return acc;
}, {});

const updateActionSelection = (action) => (prev) => {
  const isToggled = prev.actions.includes(action);
  const actions = isToggled
    ? prev.actions.filter((aAction) => aAction !== action)
    : prev.actions.concat(action);
  return {
    ...prev,
    actions,
  };
}

export default function LogsTable({
  table,
  logsViewData,
  searchParams,
  setSearchParams,
}) {
  const [tableConfigDrawerOpen, setTableConfigDrawerOpen] = useState(false);

  const [tableConfig, setTableConfig] = useStorageState(
    storageKeys.LIVE_LOGS_TABLE_CONFIG,
    {
      density: "normal",
      fontSize: "normal",
      rowsPerPage: "100",
      highlighted: false,
      actions: [],
    }
  );

  const [logActionOptions, setLogActionOptions] = useState(logActions);
  const [playerOptions, setPlayerOptions] = useState({});

  const handleTableConfigClick = () => {
    // toggle config drawer
    setTableConfigDrawerOpen((prev) => !prev);
  };

  const handleClientActionFilterChange = (actionName) => {
    setLogActionOptions((prev) => ({
      ...prev,
      [actionName]: !prev[actionName],
    }));
  };

  const handleClientPlayerFilterChange = (playerName) => {
    setPlayerOptions((prev) => ({
      ...prev,
      [playerName]: !prev[playerName],
    }));
  };

  const handleQueryActionParamSelect = (action) => {
    setSearchParams(updateActionSelection(action));
  };

  const handleHighlightActionSelect = (action) => {
    setTableConfig(updateActionSelection(action));
  };

  const handleQueryLimitInputBlur = (event) => {
    const [min, max] = [10, 100_000];
    const inputValue = Number(event.target.value);
    const limit = inputValue < min ? min : inputValue > max ? max : inputValue;
    setSearchParams((prev) => ({
      ...prev,
      limit,
    }));
  };

  const handleQueryInclusiveFilterChange = (e, mode) => {
    setSearchParams((prev) => ({
      ...prev,
      inclusive_filter: mode === "inclusive",
    }));
  };

  useEffect(() => {
    const incomingPlayers =
      logsViewData?.players?.reduce((acc, player) => {
        acc[player] = false;
        return acc;
      }, {}) ?? {};
    setPlayerOptions((prev) => {
      for (const [name, selected] of Object.entries(prev)) {
        if (name in incomingPlayers) {
          incomingPlayers[name] = selected;
        }
      }
      return incomingPlayers;
    });
  }, [logsViewData.players]);

  useEffect(() => {
    const selectedActions = Object.entries(logActionOptions)
      .filter(([_, selected]) => selected)
      .map(([name]) => name);
    table.getColumn("action")?.setFilterValue(selectedActions);
  }, [logActionOptions]);

  useEffect(() => {
    const selectedPlayers = Object.entries(playerOptions)
      .filter(([_, selected]) => selected)
      .map(([name]) => name);
    table.getColumn("player_name_1")?.setFilterValue(selectedPlayers);
    table.getColumn("player_name_2")?.setFilterValue(selectedPlayers);
  }, [playerOptions]);

  const highlightedActionOptions = Object.entries(logActions).reduce((acc, [name]) => {
    acc[name] = tableConfig.actions.includes(name);
    return acc;
  }, {})

  return (
    <>
      <TableAddons>
        <LogActionSelectionMenu
          actionOptions={logActionOptions}
          onActionSelect={handleClientActionFilterChange}
        />
        <LogPlayerSelectionMenu
          actionOptions={playerOptions}
          onActionSelect={handleClientPlayerFilterChange}
        />
        <LogActionHighlightMenu
          actionOptions={highlightedActionOptions}
          onActionSelect={handleHighlightActionSelect}
          toggleValue={tableConfig.highlighted}
          onToggle={(value) => {
            setTableConfig(prev => ({
              ...prev,
              highlighted: value === "on",
            }))
          }}
        />
      </TableAddons>
      <TableToolbar>
        <DebouncedSearchInput
          placeholder={"Search logs"}
          onChange={(value) => {
            table.getColumn("message")?.setFilterValue(value);
          }}
          sx={{ maxWidth: 230 }}
        />
        <Box sx={{ flexGrow: 1 }} />
        <TablePagination table={table} />
        <Divider flexItem orientation="vertical" />
        <IconButton
          size="small"
          sx={{ width: 20, height: 20, borderRadius: 0, p: 2 }}
          onClick={handleTableConfigClick}
        >
          <SettingsIcon sx={{ fontSize: 16 }} />
        </IconButton>
      </TableToolbar>
      <LiveLogsTable table={table} config={tableConfig} />
      <TableToolbar sx={{ borderBottomWidth: "1px", borderBottomStyle: "solid", borderTop: "none" }}>
        <TablePagination table={table} />
      </TableToolbar>
      <TableConfigDrawer
        table={table}
        name={"Logs"}
        open={tableConfigDrawerOpen}
        onClose={(config) => {
          setTableConfigDrawerOpen(false);
          setTableConfig(config);
        }}
        config={tableConfig}
      >
        <Typography sx={{ fontWeight: 500 }}>
          {"Persistent Logs Query Params"}
        </Typography>
        <Divider flexItem />
        <div>
          <Typography
            sx={{
              mb: 1,
              fontSize: "0.85rem",
              textTransform: "uppercase",
              letterSpacing: 1.5,
            }}
          >
            Filter Mode
          </Typography>
          <ToggleButtonGroup
            value={searchParams.inclusive ? "inclusive" : "exclusive"}
            exclusive
            onChange={handleQueryInclusiveFilterChange}
            aria-label="filter mode change"
            fullWidth
          >
            <ToggleButton value="inclusive" aria-label="inclusive filters">
              Inclusive
            </ToggleButton>
            <ToggleButton value="exclusive" aria-label="exclusives filters">
              Exclusive
            </ToggleButton>
          </ToggleButtonGroup>
        </div>
        <div>
          <Typography
            sx={{
              mb: 1,
              fontSize: "0.85rem",
              textTransform: "uppercase",
              letterSpacing: 1.5,
            }}
          >
            Filter Actions
          </Typography>
          <LogActionQuerySelectionMenu
            selectedActions={searchParams.actions}
            onActionSelect={handleQueryActionParamSelect}
          />
          <List dense={true} disablePadding={true}>
            {searchParams.actions.map((action, i) => (
              <Fragment key={action}>
                {i !== 0 && <Divider component="li" />}
                <ListItem
                  disableGutters={true}
                  secondaryAction={
                    <IconButton
                      edge="end"
                      aria-label="delete"
                      onClick={() => handleQueryActionParamSelect(action)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  }
                >
                  <ListItemText
                    primary={`${_logActions[action]} - ${action}`}
                  />
                </ListItem>
              </Fragment>
            ))}
            {searchParams.actions.length === 0 && (
              <ListItem disableGutters={true}>
                <ListItemText primary={"No Action Filters Selected"} />
              </ListItem>
            )}
          </List>
        </div>
        <div>
          <Typography
            sx={{
              mb: 1,
              fontSize: "0.85rem",
              textTransform: "uppercase",
              letterSpacing: 1.5,
            }}
          >
            Logs Fetch Query Limit
          </Typography>
          <TextField
            fullWidth
            defaultValue={searchParams.limit}
            onBlur={handleQueryLimitInputBlur}
            placeholder="Query limit"
            type="number"
            size="small"
          />
        </div>
      </TableConfigDrawer>
    </>
  );
}
