import { useMemo } from "react";
import { Button, ButtonGroup, ToggleButtonGroup, Tooltip } from "@mui/material";
import { Box, Stack } from "@mui/material";
import { CountrySelectionMenu } from "@/components/table/selection/CountrySelectionMenu";
import { UnitSelectionMenu } from "@/components/table/selection/UnitSelectionMenu";
import { RoleSelectionMenu } from "@/components/table/selection/RoleSelectionMenu";
import { RankSelectionMenu } from "@/components/table/selection/RankSelectionMenu";
import { levelToRank } from "@/utils/lib";
import TableToolbar from "@/components/table/TableToolbar";

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
      const hasSomeNotSelected = countryRows.some((row) => !prev[row.id]);

      return allRows.reduce((acc, row) => {
        acc[row.id] =
          row.original.country === country ? hasSomeNotSelected : prev[row.id];
        return acc;
      }, {});
    });
  };

  const handleRoleSelect = (selectedRole) => {
    const { role } = selectedRole;
    const allRows = table.getRowModel().rows;
    const roleRows = allRows.filter((row) => row.original.role === role);
    table.setRowSelection((prev) => {
      const hasSomeNotSelected = roleRows.some((row) => !prev[row.id]);
      return allRows.reduce((acc, row) => {
        acc[row.id] =
          row.original.role === role ? hasSomeNotSelected : prev[row.id];
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

  const roleOptions = useMemo(() => {
    const roleCounts = table.getRowModel().rows.reduce((acc, row) => {
      if (row.original.role) {
        acc[row.original.role] = (acc[row.original.role] || 0) + 1;
      }
      return acc;
    }, {});

    return Object.keys(roleCounts).map((role) => ({
      role,
      count: roleCounts[role],
    }));
  }, [table.getRowModel().rows]);

  const rankOptions = useMemo(() => {
    const ranksCounts = table.getRowModel().rows.reduce((acc, row) => {
      if (row.original.level) {
        const rank = levelToRank(row.original.level);
        acc[rank] = (acc[rank] || 0) + 1;
      }
      return acc;
    }, {});
    return Object.keys(ranksCounts).map((rank) => ({
      rank,
      count: ranksCounts[rank],
    }));
  }, [table.getRowModel().rows]);

  return (
    <TableToolbar>
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
      <UnitSelectionMenu
        unitOptions={unitOptions}
        onUnitSelect={handleUnitSelect}
      />
      <CountrySelectionMenu
        countryOptions={countryOptions}
        onCountrySelect={handleCountrySelect}
      />
      <RoleSelectionMenu
        roleOptions={roleOptions}
        onRoleSelect={handleRoleSelect}
      />
      <RankSelectionMenu rankOptions={rankOptions} onRankSelect={() => {}} />
    </TableToolbar>
  );
};
