import { useState } from "react";
import { Box, Button, TextField, Tooltip } from "@mui/material";
import HistoryIcon from "@mui/icons-material/History";
import { PopoverMenu } from "@/components/shared/PopoverMenu";

/**
 * @typedef {Object} VisitsSelectionMenuProps
 * @property {(maxVisits: number | null) => void} onVisitsChange
 */

/**
 * Allows selecting players based on their number of visits.
 *
 * @param {VisitsSelectionMenuProps} props
 * @returns {JSX.Element}
 */
export const VisitsSelectionMenu = ({ onVisitsChange }) => {
  const [value, setValue] = useState("");

  const handleChange = (event) => {
    const next = event.target.value;
    setValue(next);

    if (next === "") {
      onVisitsChange?.(null);
      return;
    }

    const numeric = Number(next);
    if (Number.isNaN(numeric) || numeric < 0) {
      return;
    }

    onVisitsChange?.(numeric);
  };

  return (
    <PopoverMenu
      id="visits-picker"
      description="Select all players with this many visits or fewer"
      renderButton={(props) => (
        <Button {...props}>
          <Tooltip title="Select by visits">
            <HistoryIcon />
          </Tooltip>
        </Button>
      )}
    >
      <Box sx={{ p: 2, minWidth: 220 }}>
        <TextField
          label="Max player visits"
          type="number"
          fullWidth
          value={value}
          onChange={handleChange}
          inputProps={{ min: 0 }}
          size="small"
        />
      </Box>
    </PopoverMenu>
  );
};

