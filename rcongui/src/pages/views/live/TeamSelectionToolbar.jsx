import { useMemo } from "react";
import { Button, Tooltip } from "@mui/material";
import { CountrySelectionMenu } from "@/components/table/selection/CountrySelectionMenu";
import { UnitSelectionMenu } from "@/components/table/selection/UnitSelectionMenu";
import { RoleSelectionMenu } from "@/components/table/selection/RoleSelectionMenu";
import { RankSelectionMenu } from "@/components/table/selection/RankSelectionMenu";
import { levelToRank } from "@/utils/lib";
import TableAddons from "@/components/table/TableAddons";

export const TeamSelectionToolbar = ({ table, teamData }) => {
  // handleGenericSelect is a generic function that allows for the selection of a row based on a key and value.
  // It is used to select rows based on the team, unit, country, role, and rank.
  const handleGenericSelect = (key, value, rowTransform = (row) => row.original[key]) => {
    const allRows = table.getRowModel().rows;
    const matchingRows = allRows.filter(row => rowTransform(row) === value);
    
    table.setRowSelection((prev) => {
      const hasSomeNotSelected = matchingRows.some(row => !prev[row.id]);
      
      return allRows.reduce((acc, row) => {
        acc[row.id] = rowTransform(row) === value ? hasSomeNotSelected : prev[row.id];
        return acc;
      }, {});
    });
  };

  const handleTeamSelect = (selectedTeam) => {
    if (!selectedTeam) return;
    handleGenericSelect('team', selectedTeam);
  };

  const handleUnitSelect = (selectedUnit) => {
    if (!selectedUnit) return;
    const getIdentifier = (o) => `${o.team}-${o.unit_name}`;
    handleGenericSelect(
      'unit', 
      `${selectedUnit.team}-${selectedUnit.unit_name}`,
      row => getIdentifier(row.original)
    );
  };

  const handleCountrySelect = (selectedCountry) => {
    handleGenericSelect('country', selectedCountry.country);
  };

  const handleRoleSelect = (selectedRole) => {
    handleGenericSelect('role', selectedRole.role);
  };

  const handleRankSelect = (selectedRank) => {
    handleGenericSelect(
      'rank', 
      selectedRank.rank,
      row => levelToRank(row.original.level)
    );
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
    <TableAddons>
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
      <RankSelectionMenu rankOptions={rankOptions} onRankSelect={handleRankSelect} />
    </TableAddons>
  );
};
