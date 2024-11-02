import { useEffect, useMemo, useState } from "react";
import { SearchInput } from "@/components/shared/SearchInput";
import {
  Button,
  ButtonGroup,
  ToggleButtonGroup,
  Tooltip,
} from "@mui/material";
import { Box, Stack } from "@mui/material";
import { PopoverMenu } from "@/components/shared/PopoverMenu";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import GroupIcon from "@mui/icons-material/Groups";
import { CountryFlag } from "@/components/CountryFlag";
import FlagIcon from "@mui/icons-material/Flag";

export const DebouncedSearchInput = ({
  initialValue,
  onChange,
  debounce = 500,
  ...props
}) => {
  const [search, setSearch] = useState(initialValue);

  useEffect(() => {
    setSearch(initialValue);
  }, [initialValue]);

  useEffect(() => {
    const timeout = setTimeout(() => {
      onChange(search);
    }, debounce);

    return () => clearTimeout(timeout);
  }, [search]);

  return (
    <SearchInput
      value={search}
      onChange={(e) => setSearch(e.target.value)}
      {...props}
    />
  );
};

// Add this new component
export const TeamSelectionToolbar = ({ table, teamData }) => {
  const handleTeamSelect = (selectedTeam) => {
    if (!selectedTeam) return;

    table.setRowSelection((prev) => {
      const allRows = table.getRowModel().rows;

      // If any row of this team is already selected, deselect all team members
      const hasSelectedTeamMembers = allRows.some(
        (row) => row.original.team === selectedTeam && prev[row.id]
      );

      return allRows.reduce((acc, row) => {
        acc[row.id] =
          row.original.team === selectedTeam
            ? !hasSelectedTeamMembers
            : prev[row.id];
        return acc;
      }, {});
    });
  };

  const handleUnitSelect = (selectedUnit) => {
    const getIdentifier = (o) => `${o.team}-${o.unit_name}`;
    const squad = teamData[selectedUnit.team].squads[selectedUnit.unit_name];
    if (!squad) return;
    const players = squad.players;
    table.setRowSelection((prev) => {
      const allRows = table.getRowModel().rows;
      const hasSomeNotSelected = players.some(
        (player) => !prev[player.player_id]
      );

      return allRows.reduce((acc, row) => {
        acc[row.original.player_id] =
          getIdentifier(row.original) === getIdentifier(selectedUnit)
            ? hasSomeNotSelected
            : prev[row.original.player_id];
        return acc;
      }, {});
    });
  };

  const handleCountrySelect = (selectedCountry) => {
    const { country } = selectedCountry;
    const allRows = table.getRowModel().rows;
    const countryRows = allRows.filter(
      (row) => row.original.country === country
    );
    table.setRowSelection((prev) => {
      const hasSomeNotSelected = countryRows.some(
        (row) => !prev[row.id]
      );

      return allRows.reduce((acc, row) => {
        acc[row.id] =
          row.original.country === country
            ? hasSomeNotSelected
            : prev[row.id];
        return acc;
      }, {});
    });
  };

  const countryOptions = useMemo(() => {
    const countryCounts = table.getRowModel().rows.reduce((acc, row) => {
      if (row.original.country) {
        acc[row.original.country] = (acc[row.original.country] || 0) + 1;
      }
      return acc;
    }, {});

    delete countryCounts["null"];
    delete countryCounts["private"];
    delete countryCounts["unknown"];

    return Object.keys(countryCounts).map((country) => ({
      country,
      count: countryCounts[country],
    }));
  }, [table.getRowModel().rows]);

  const unitOptions = useMemo(() => {
    const units = [];
    for (const team in teamData) {
      for (const unit_name in teamData[team].squads) {
        const unit = teamData[team].squads[unit_name];
        units.push({
          team,
          unit_name,
          unit: unit_name === "null" ? "Unassigned" : unit_name,
          type: unit.type,
          count: unit.players.length,
          leader:
            unit.players.find((player) =>
              ["officer", "tankcommander", "spotter"].includes(player.role)
            )?.name ?? "",
        });
      }
    }
    units.sort((a, b) =>
      `${a.team}-${a.unit_name}`.localeCompare(`${b.team}-${b.unit_name}`)
    );
    return units;
  }, [teamData]);

  return (
    <Box>
      <Stack direction="row" spacing={1} alignItems="center">
        <ToggleButtonGroup
          exclusive
          onChange={handleTeamSelect}
          size="small"
        ></ToggleButtonGroup>
        <ButtonGroup
          style={{ marginLeft: 0 }}
          sx={{
            "& .MuiButtonGroup-firstButton, .MuiButtonGroup-lastButton": {
              borderRadius: 0,
            },
          }}
          variant="outlined"
          size="small"
        >
          <Tooltip title="Select Axis">
            <Button onClick={() => handleTeamSelect("axis")}>
              <img
                src="/icons/teams/ger.webp"
                width={16}
                height={16}
                style={{ marginRight: 1 }}
              />
            </Button>
          </Tooltip>
          <Tooltip title="Select Allies">
            <Button onClick={() => handleTeamSelect("allies")}>
              <img
                src="/icons/teams/us.webp"
                width={16}
                height={16}
                style={{ marginRight: 1 }}
              />
            </Button>
          </Tooltip>
          <PopoverMenu
            id="unit-picker"
            description="Pick a squad to select all players in it"
            renderButton={(props) => (
              <Button {...props}>
                <Tooltip title="Select by squad">
                  <GroupIcon />
                </Tooltip>
              </Button>
            )}
          >
            <List
              sx={{
                width: "100%",
                bgcolor: "background.paper",
                position: "relative",
                overflowY: "auto",
                overflowX: "hidden",
                maxHeight: 300,
                "& ul": { padding: 0 },
              }}
            >
              {unitOptions.map((option) => (
                <ListItem
                  key={`${option.team}-${option.unit_name}`}
                  dense
                  disableGutters
                  sx={{ "& .MuiButtonBase-root": { opacity: 1 } }}
                >
                  <ListItemButton onClick={() => handleUnitSelect(option)}>
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        overflow: "hidden",
                        px: 0,
                        py: 0.25,
                        gap: 1,
                      }}
                    >
                      <img
                        src={`/icons/teams/${
                          option.team === "axis" ? "ger" : "us"
                        }.webp`}
                        width={16}
                        height={16}
                      />
                      <img
                        src={`/icons/roles/${option.type}.png`}
                        width={16}
                        height={16}
                      />
                      <Box
                        sx={{
                          overflow: "hidden",
                          whiteSpace: "nowrap",
                          textOverflow: "ellipsis",
                        }}
                      >
                        <Box
                          component="span"
                          fontWeight="bold"
                          textTransform="uppercase"
                        >
                          {option.unit} {`(${option.count})`}
                        </Box>
                        <Box component="span">{`${
                          option.leader ? ` - ${option.leader}` : ""
                        }`}</Box>
                      </Box>
                    </Box>
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </PopoverMenu>
          <PopoverMenu
            id="country-picker"
            description="Pick a country to select all players from it"
            renderButton={(props) => (
              <Button {...props}>
                <Tooltip title="Select by country">
                  <FlagIcon />
                </Tooltip>
              </Button>
            )}
          >
            <List
              sx={{
                width: "100%",
                bgcolor: "background.paper",
                position: "relative",
                overflowY: "auto",
                overflowX: "hidden",
                maxHeight: 300,
                "& ul": { padding: 0 },
              }}
            >
              {countryOptions.map((option) => (
                <ListItem
                  key={option.country}
                  dense
                  disableGutters
                  sx={{ "& .MuiButtonBase-root": { opacity: 1 } }}
                >
                  <ListItemButton onClick={() => handleCountrySelect(option)}>
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        overflow: "hidden",
                        px: 0,
                        py: 0.25,
                        gap: 1,
                      }}
                    >
                      <CountryFlag country={option.country} />
                      <Box
                        sx={{
                          overflow: "hidden",
                          whiteSpace: "nowrap",
                          textOverflow: "ellipsis",
                        }}
                      >
                        <Box
                          component="span"
                          fontWeight="bold"
                          textTransform="uppercase"
                        >
                          {option.country} {`(${option.count})`}
                        </Box>
                      </Box>
                    </Box>
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </PopoverMenu>
        </ButtonGroup>
      </Stack>
    </Box>
  );
};
