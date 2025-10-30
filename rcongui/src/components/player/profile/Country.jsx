import { Avatar, Chip } from "@mui/material";
import PublicIcon from "@mui/icons-material/Public";
import React from "react";
import { useEditAccountModal } from "@/hooks/useEditAccountModal";

function CountryChip({ country, playerId, currentAccountData }) {
  const { modal, openModal } = useEditAccountModal(
    playerId,
    currentAccountData
  );

  return (
    <>
      {country && country !== "private" ? (
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
          onClick={openModal}
        />
      ) : (
        <Chip
          icon={<PublicIcon />}
          label="unset"
          variant="outlined"
          size="small"
          onClick={openModal}
        />
      )}
      {modal}
    </>
  );
}

export default CountryChip;
