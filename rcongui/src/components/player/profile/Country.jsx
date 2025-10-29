import { Avatar, Chip } from "@mui/material";
import PublicIcon from "@mui/icons-material/Public";
import React from "react";

function CountryChip({ country }) {
  if (!country || country === "private") {
    return (
      <Chip
        icon={<PublicIcon />}
        label={"unset"}
        variant="outlined"
        size="small"
      />
    );
  }

  return (
    <Chip
      avatar={
        <Avatar
          alt={country}
          src={`https://flagcdn.com/w20/${country.toLowerCase()}.png`}
          slotProps={{
            img: {
              sx: { width: 14, height: 14, borderRadius: 50 },
            },
          }}
        />
      }
      label={country}
      variant="outlined"
      size="small"
    />
  );
}

export default CountryChip;
