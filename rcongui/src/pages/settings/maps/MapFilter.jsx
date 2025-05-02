import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
} from "@mui/material";
import { DebouncedSearchInput } from "@/components/shared/DebouncedSearchInput";
import CloseIcon from "@mui/icons-material/Close";
import { useState, useEffect, useMemo } from "react";
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
  const [selectedMode, setSelectedMode] = useState("");
  const [selectedWeather, setSelectedWeather] = useState("");

  const allModes = useMemo(
    () => Array.from(new Set(maps.map((map) => map.game_mode))).sort(),
    [maps]
  );

  const allWeather = useMemo(
    () => Array.from(new Set(maps.map((map) => map.environment))).sort(),
    [maps]
  );

  const clearFilters = () => {
    setSearchTerm("");
    setSelectedMode("");
    setSelectedWeather("");
    onFilterChange(maps);
  };

  useEffect(() => {
    // Filter map variants based on search term and filters
    const filteredMaps = maps.filter((mapLayer) => {
      const matchesSearch = mapLayer.map.pretty_name
        .toLowerCase()
        .includes(searchTerm.toLowerCase());
      const matchesMode = selectedMode
        ? mapLayer.game_mode === selectedMode
        : true;
      const matchesWeather = selectedWeather
        ? mapLayer.environment === selectedWeather
        : true;
      return matchesSearch && matchesMode && matchesWeather;
    });
    onFilterChange(filteredMaps);
  }, [maps, searchTerm, selectedMode, selectedWeather]);

  return (
    <Box>
      <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
        <DebouncedSearchInput
          fullWidth
          size="small"
          placeholder="Search maps..."
          onChange={setSearchTerm}
        />
      </Box>

      <Box sx={{ display: "flex", gap: 1, mb: 2 }}>
        <FormControl size="small" sx={{ minWidth: 180 }}>
          <InputLabel>Game Mode</InputLabel>
          <Select
            value={selectedMode}
            onChange={(e) => setSelectedMode(e.target.value)}
            label="Game Mode"
          >
            <MenuItem value="">All game modes</MenuItem>
            {allModes.map((mode) => (
              <MenuItem key={mode} value={mode}>
                {mode}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 180 }}>
          <InputLabel>Weather</InputLabel>
          <Select
            value={selectedWeather}
            onChange={(e) => setSelectedWeather(e.target.value)}
            label="Weather"
          >
            <MenuItem value="">All weather</MenuItem>
            {allWeather.map((weather) => (
              <MenuItem key={weather} value={weather}>
                {weather}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {(selectedMode || selectedWeather) && (
          <Button
            variant="outlined"
            size="small"
            onClick={clearFilters}
            startIcon={<CloseIcon />}
          >
            Clear Filters
          </Button>
        )}
      </Box>
    </Box>
  );
};
