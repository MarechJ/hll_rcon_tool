import {
  Box,
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Stack,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from "@mui/material";
import TableConfigDrawer from "@/components/table/TableConfigDrawer";
import { Fragment, memo, useEffect, useState } from "react";
import { useLogsTableStore, useLogsSearchStore } from "@/stores/table-config";
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
import TableColumnSelection from "@/components/table/TableColumnSelection";
import { LogTeamSelectionMenu } from "@/components/table/selection/LogTeamSelectionMenu";

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
};

const updateFilterActionSelection = (action) => (prev) => {
  const isToggled = prev.filters.actions.selected.includes(action);
  const actions = isToggled
    ? prev.filters.actions.selected.filter((aAction) => aAction !== action)
    : prev.filters.actions.selected.concat(action);
  return {
    ...prev,
    filters: {
      ...prev.filters,
      actions: {
        ...prev.filters.actions,
        selected: actions,
      },
    },
  };
};

function LogsTable({
  table,
  logsViewData,
  onColumnVisibilityChange,
  isFetching,
  isLoading,
}) {
  const [tableConfigDrawerOpen, setTableConfigDrawerOpen] = useState(false);

  const tableConfig = useLogsTableStore();
  const searchParams = useLogsSearchStore();
  const setParamsFilterEnabled = useLogsSearchStore((state) => state.setEnabled);

  const [playerOptions, setPlayerOptions] = useState({});

  const [selectedTeams, setSelectedTeams] = useState([]);

  const handleFilterChange = (fn) => {
    table.setPageIndex(0);
    fn();
  };

  const handleTableConfigClick = () => {
    // toggle config drawer
    setTableConfigDrawerOpen((prev) => !prev);
  };

  const handleClientActionFilterChange = (actionName) => {
    tableConfig.setConfig(updateFilterActionSelection(actionName));
  };

  const handleClientActionFilterToggle = () => {
    handleFilterChange(() => {
      tableConfig.setConfig((prev) => ({
        ...prev,
        filters: {
          ...prev.filters,
          actions: {
            ...prev.filters.actions,
            enabled: !prev.filters.actions.enabled,
          },
        },
      }));
    });
  };

  const handleClientPlayerFilterChange = (playerName) => {
    handleFilterChange(() => {
      setPlayerOptions((prev) => ({
        ...prev,
        [playerName]: !prev[playerName],
      }));
    });
  };

  const handleQueryActionParamSelect = (action) => {
    handleFilterChange(() => {
      searchParams.setSearchParams(updateActionSelection(action));
    });
  };

  const handleHighlightActionSelect = (action) => {
    tableConfig.setConfig(updateActionSelection(action));
  };

  const handleClientHighlightActionToggle = () => {
    tableConfig.setConfig((prev) => ({
      ...prev,
      highlighted: !prev.highlighted,
    }));
  };

  const handleQueryLimitInputBlur = (event) => {
    const [min, max] = [10, 100_000];
    const inputValue = Number(event.target.value);
    const limit = inputValue < min ? min : inputValue > max ? max : inputValue;
    handleFilterChange(() => {
      searchParams.setSearchParams((prev) => ({
        ...prev,
        limit,
      }));
    });
  };

  const handleQueryInclusiveFilterChange = (e, mode) => {
    if (mode === null) return; // the active value was selected
    console.log(mode);
    handleFilterChange(() => {
      searchParams.setSearchParams((prev) => ({
        ...prev,
        inclusive_filter: mode === "exclusive" ? false : true,
      }));
    });
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
    if (tableConfig.filters.actions.enabled) {
      table
        .getColumn("action")
        ?.setFilterValue(tableConfig.filters.actions.selected);
    } else {
      table.getColumn("action")?.setFilterValue(null);
    }
  }, [
    tableConfig.filters.actions.selected,
    tableConfig.filters.actions.enabled,
  ]);

  useEffect(() => {
    const selectedPlayers = Object.entries(playerOptions)
      .filter(([_, selected]) => selected)
      .map(([name]) => name);
    table.getColumn("player_name_1")?.setFilterValue(selectedPlayers);
    table.getColumn("player_name_2")?.setFilterValue(selectedPlayers);
  }, [playerOptions]);

  const highlightedActionOptions = Object.entries(logActions).reduce(
    (acc, [name]) => {
      acc[name] = tableConfig.actions.includes(name);
      return acc;
    },
    {}
  );

  const filterActionOptions = Object.entries(logActions).reduce(
    (acc, [name]) => {
      acc[name] = tableConfig.filters.actions.selected.includes(name);
      return acc;
    },
    {}
  );

  const searchQueryParamsOptions = Object.entries(logActions).reduce((acc, [name]) => {
    acc[name] = searchParams.actions.includes(name);
    return acc;
  }, {});

  const handleTeamSelect = (team) => {
    handleFilterChange(() => {
      setSelectedTeams((prev) => {
        const isSelected = prev.includes(team);
        if (isSelected) {
          return prev.filter((t) => t !== team);
        }
        return [...prev, team];
      });
    });
  };

  useEffect(() => {
    table.getColumn("team")?.setFilterValue(selectedTeams);
  }, [selectedTeams]);

  return (
    <>
      <TableAddons>
        <LogActionSelectionMenu
          actionOptions={filterActionOptions}
          onActionSelect={handleClientActionFilterChange}
          toggleValue={tableConfig.filters.actions.enabled}
          onToggle={handleClientActionFilterToggle}
        />
        <LogTeamSelectionMenu
          selectedTeams={selectedTeams}
          onTeamSelect={handleTeamSelect}
        />
        <LogPlayerSelectionMenu
          actionOptions={playerOptions}
          onActionSelect={handleClientPlayerFilterChange}
        />
        <LogActionHighlightMenu
          actionOptions={highlightedActionOptions}
          onActionSelect={handleHighlightActionSelect}
          toggleValue={tableConfig.highlighted}
          onToggle={handleClientHighlightActionToggle}
        />
      </TableAddons>
      <Stack direction="column" spacing={0}>
        <TableToolbar>
          <DebouncedSearchInput
            placeholder={"Search logs"}
            onChange={(value) => {
              handleFilterChange(() => {
                table.getColumn("message")?.setFilterValue(value);
              });
            }}
          />
          <Box sx={{ flexGrow: 1 }} />
          <TablePagination table={table} />
          <Divider
            flexItem
            orientation="vertical"
            sx={{ marginLeft: 0, marginRight: 0 }}
          />
          <TableColumnSelection
            table={table}
            onColumnVisibilityChange={onColumnVisibilityChange}
          />
          <IconButton
            size="small"
            aria-label="Table settings"
            aria-description="Configure the table"
            sx={{ p: 0.5, borderRadius: 0 }}
            onClick={handleTableConfigClick}
          >
            <SettingsIcon sx={{ fontSize: "1rem" }} />
          </IconButton>
        </TableToolbar>
        <LiveLogsTable table={table} config={tableConfig} isFetching={isFetching} isLoading={isLoading} />
        <TableToolbar
          sx={{
            borderBottomWidth: "1px",
            borderBottomStyle: "solid",
            borderTop: "none",
          }}
        >
          <TablePagination table={table} />
        </TableToolbar>
      </Stack>
      <TableConfigDrawer
        name={"Logs"}
        open={tableConfigDrawerOpen}
        onClose={(config) => {
          setTableConfigDrawerOpen(false);
          tableConfig.setConfig(config);
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
            value={searchParams.inclusive_filter ? "inclusive" : "exclusive"}
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
            actionOptions={searchQueryParamsOptions}
            selectedActions={searchParams.actions}
            onActionSelect={handleQueryActionParamSelect}
            toggleValue={searchParams.enabled}
            onToggle={setParamsFilterEnabled}
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

export default memo(LogsTable);
