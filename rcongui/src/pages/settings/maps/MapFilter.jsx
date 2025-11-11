import {
  Stack,
  Checkbox,
  FormControlLabel,
  Typography,
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
  const [selectedModes, setSelectedModes] = useState(["warfare"]);
  const [selectedWeathers, setSelectedWeathers] = useState(["day"]);

  // Compute unique modes and weathers for dropdowns
  const allModes = useMemo(() => {
    return Array.from(
      new Set(maps.map((map) => unifiedGamemodeName(map.game_mode)))
    ).sort();
  }, [maps]);

  const allWeather = useMemo(() => {
    return Array.from(new Set(maps.map((map) => map.environment))).sort();
  }, [maps]);

  // Compute filtered maps based on filter criteria
  const filteredMaps = useMemo(() => {
    return maps.filter((mapLayer) => {
      const matchesSearch = mapLayer.map.pretty_name
        .toLowerCase()
        .includes(searchTerm.toLowerCase());
      const matchesModes =
        !selectedModes.length ||
        selectedModes.includes(unifiedGamemodeName(mapLayer.game_mode));
      const matchesWeather =
        !selectedWeathers.length ||
        selectedWeathers.includes(mapLayer.environment);
      return matchesSearch && matchesModes && matchesWeather;
    });
  }, [maps, searchTerm, selectedModes, selectedWeathers]);

  // Notify parent of filter changes
  useEffect(() => {
    onFilterChange(filteredMaps);
  }, [filteredMaps, onFilterChange]);

  const handleModeChange = (mode) => {
    setSelectedModes((prev) =>
      prev.includes(mode) ? prev.filter((m) => m !== mode) : [...prev, mode]
    );
  };

  const handleWeatherChange = (weather) => {
    setSelectedWeathers((prev) =>
      prev.includes(weather)
        ? prev.filter((w) => w !== weather)
        : [...prev, weather]
    );
  };

  return (
    <Stack
      alignItems={"center"}
      flexWrap={"wrap"}
      gap={1}
      direction={"row"}
      sx={{ 
        py: 1, 
        gap: 1,
        // Card-like styles
        borderRadius: 1,
        boxShadow: 1,
        border: '1px solid',
        borderColor: 'divider',
        p: 2,
        mb: 2
      }}
    >
      <DebouncedSearchInput
        size="small"
        placeholder="Search maps..."
        onChange={setSearchTerm}
      />

      <Stack direction={"column"} sx={{ width: "100%", px: 1 }}>
        <Stack direction={"row"} gap={1} alignItems={"center"}>
          <Typography
            variant="subtitle2"
            fontSize={10}
            sx={{ textTransform: "uppercase", width: 70 }}
          >
            Game Mode
          </Typography>
          <Stack direction={"row"} flexWrap={"wrap"}>
            {allModes.map((mode) => (
              <FormControlLabel
                key={mode}
                control={
                  <Checkbox
                    checked={selectedModes.includes(mode)}
                    onChange={() => handleModeChange(mode)}
                    size="small"
                    sx={{
                      "& .MuiSvgIcon-root": { fontSize: 14 },
                    }}
                  />
                }
                label={unifiedGamemodeName(mode)}
                sx={{ textTransform: "uppercase", '& .MuiFormControlLabel-label': { fontSize: 10 } }}
              />
            ))}
          </Stack>
        </Stack>

        <Stack direction={"row"} gap={1} alignItems={"center"}>
          <Typography
            variant="subtitle2"
            fontSize={10}
            sx={{ textTransform: "uppercase", width: 70 }}
          >
            Weather
          </Typography>
          <Stack direction={"row"} flexWrap={"wrap"}>
            {allWeather.map((weather) => (
              <FormControlLabel
                key={weather}
                control={
                  <Checkbox
                    checked={selectedWeathers.includes(weather)}
                    onChange={() => handleWeatherChange(weather)}
                    size="small"
                    sx={{
                      "& .MuiSvgIcon-root": { fontSize: 14 },
                    }}
                  />
                }
                label={weather}
                sx={{ textTransform: "uppercase", '& .MuiFormControlLabel-label': { fontSize: 10 } }}
              />
            ))}
          </Stack>
        </Stack>
      </Stack>
    </Stack>
  );
};
