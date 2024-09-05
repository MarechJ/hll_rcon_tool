import React from "react";
import {
  Button,
  ButtonGroup,
} from "@mui/material";
import dayjs from "dayjs";

export const TimePickerButtons = ({
  amount,
  unit,
  expirationTimestamp,
  setExpirationTimestamp,
}) => {

  const adjustTimestamp = (amount, unit) => {
    const after = dayjs(expirationTimestamp).add(amount, unit);
    const now = dayjs();
    console.log({expirationTimestamp, after, now})

    if (after.isBefore(now)) {
      setExpirationTimestamp(now.format())
      return;
    }

    setExpirationTimestamp(after.format());
  };

  const setTimestamp = (amount, unit) => {
    setExpirationTimestamp(dayjs().add(amount, unit).format());
  };

  return (
    <ButtonGroup variant="outlined" size="small" style={{ display: "flex", marginBottom: 4 }}>
      <Button style={{ display: "block", width: "100%", maxWidth: "2rem" }} onClick={() => adjustTimestamp(-amount, unit)}>
        -
      </Button>
      <Button style={{ display: "block", width: "100%" }} onClick={() => setTimestamp(amount, unit)}>
        {amount} {unit}
      </Button>
      <Button style={{ display: "block", width: "100%", maxWidth: "2rem" }} onClick={() => adjustTimestamp(amount, unit)}>
        +
      </Button>
    </ButtonGroup>
  );
};