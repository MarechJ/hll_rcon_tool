import React from "react";
import {
  Button,
  ButtonGroup,
} from "@material-ui/core";
import moment from "moment";

export const TimePickerButtons = ({
  amount,
  unit,
  expirationTimestamp,
  setExpirationTimestamp,
}) => {

  const adjustTimestamp = (amount, unit) => {
    const after = moment(expirationTimestamp).add(amount, unit);
    const now = moment();

    if (after.isBefore(now)) {
      setExpirationTimestamp(now.format())
      return;
    }

    setExpirationTimestamp(after.format());
  };

  const setTimestamp = (amount, unit) => {
    setExpirationTimestamp(moment().add(amount, unit).format());
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