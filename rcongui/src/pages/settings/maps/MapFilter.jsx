import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
  Checkbox,
  ListItemText,
  OutlinedInput,
} from "@mui/material";
import { DebouncedSearchInput } from "@/components/shared/DebouncedSearchInput";
import { useState, useEffect, useMemo } from "react";
import { unifiedGamemodeName } from "./objectives/helpers";

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
      textTransform: "uppercase",
    },
  },
};

/**
 * @typedef {Function} onFilterChange
 * @param {Object[]} maps - The list of maps to filter
 */

/**
 * @typedef {Object} MapFilterProps
 * @property {Object[]} maps - The list of maps to filter
 * @property {Function} onFilterChange - The function that is called when the filter changes
 */

/**
 * A component that renders a filter for the map list
 * It accepts a list of maps and a function that returns a filtered list of maps on filter change
 * @param {MapFilterProps} props - The component props
 * @returns {JSX.Element} The rendered component
 */
export const MapFilter = ({ maps, onFilterChange }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedModes, setSelectedModes] = useState([]);
  const [selectedWeathers, setSelectedWeathers] = useState([]);

  // Compute unique modes and weathers for dropdowns
  const allModes = useMemo(() => {
    return Array.from(new Set(maps.map((map) => unifiedGamemodeName(map.game_mode)))).sort();
  }, [maps]);

  const allWeather = useMemo(() => {
    return Array.from(new Set(maps.map((map) => map.environment))).sort();
  }, [maps]);

  // Compute filtered maps based on filter criteria
  const filteredMaps = useMemo(() => {
    return maps.filter((mapLayer) => {
      const matchesSearch = mapLayer.map.pretty_name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesModes = !selectedModes.length || selectedModes.includes(unifiedGamemodeName(mapLayer.game_mode));
      const matchesWeather = !selectedWeathers.length || selectedWeathers.includes(mapLayer.environment);
      return matchesSearch && matchesModes && matchesWeather;
    });
  }, [maps, searchTerm, selectedModes, selectedWeathers]);

  // Notify parent of filter changes
  useEffect(() => {
    onFilterChange(filteredMaps);
  }, [filteredMaps, onFilterChange]);

  return (
    <Stack
      alignItems={"center"}
      flexWrap={"wrap"}
      gap={1}
      direction={"row"}
      sx={{ py: 1, gap: 1 }}
    >
      <DebouncedSearchInput
        size="small"
        placeholder="Search maps..."
        onChange={setSearchTerm}
      />

      <Stack direction={"row"} sx={{ gap: 1, mb: 2, width: "100%" }}>
        <FormControl size="small" sx={{ width: { xs: "100%", md: "50%" } }}>
          <InputLabel id={"game-mode"}>Game Mode</InputLabel>
          <Select
            labelId={"game-mode"}
            value={selectedModes}
            onChange={(e) => setSelectedModes(e.target.value)}
            multiple
            renderValue={(selected) => selected.join(", ")}
            input={<OutlinedInput label="Game Mode" />}
            MenuProps={MenuProps}
            SelectDisplayProps={{ style: { display: "block", textTransform: "uppercase" } }}
          >
            {allModes.map((mode) => (
              <MenuItem key={mode} value={mode}>
                <Checkbox checked={selectedModes.includes(mode)} />
                <ListItemText primary={unifiedGamemodeName(mode)} />
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ width: { xs: "100%", md: "50%" } }}>
          <InputLabel id={"game-weather"}>Weather</InputLabel>
          <Select
            labelId={"game-weather"}
            value={selectedWeathers}
            onChange={(e) => setSelectedWeathers(e.target.value)}
            multiple
            renderValue={(selected) => selected.join(", ")}
            input={<OutlinedInput label="Weather" />}
            MenuProps={MenuProps}
            SelectDisplayProps={{ style: { display: "block", textTransform: "uppercase" } }}
          >
            {allWeather.map((weather) => (
              <MenuItem key={weather} value={weather}>
                <Checkbox checked={selectedWeathers.includes(weather)} />
                <ListItemText primary={weather} />
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Stack>
    </Stack>
  );
};
