import React, { useEffect, useState } from "react";
import {
  Button,
  ButtonGroup,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
} from "@material-ui/core";

import { DateTimePicker, MuiPickersUtilsProvider } from "@material-ui/pickers";
import MomentUtils from "@date-io/moment";
import moment from "moment";
import { PlayerVipSummary } from "./PlayerVipSummary";
import { ForwardCheckBox } from "../commonComponent";

export function VipExpirationDialog(props) {
  const { open, vips, onDeleteVip, handleClose, handleConfirm } = props;
  const [expirationTimestamp, setExpirationTimestamp] = useState();
  const [isVip, setIsVip] = useState(false);
  const [forward, setForward] = useState(false);

  /* open is either a boolean or the passed in player Map */
  useEffect(() => {
    if (!(typeof open === "boolean") && open) {
      setIsVip(!!vips.get(open.get("steam_id_64")));
      if (open.get("vip_expiration")) {
        setExpirationTimestamp(open.get("vip_expiration"));
      }
    }
  }, [open, vips]);

  const adjustTimestamp = (amount, unit) =>
    setExpirationTimestamp(
      moment(expirationTimestamp).add(amount, unit).format()
    );

  return (
    <Dialog open={open} aria-labelledby="form-dialog-title">
      <DialogTitle id="form-dialog-title">
        Add / Remove / Update VIP Expiration Date
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={2}>
          <Grid item>
            <ForwardCheckBox
              bool={forward}
              onChange={() => setForward(!forward)}
            />
          </Grid>
          <Grid item>
            <PlayerVipSummary player={open} isVip={isVip} />
          </Grid>
          <Grid item container spacing={2}>
            <Grid item xs={12}>
              <ButtonGroup variant="contained">
                <Button
                  type="primary"
                  onClick={() => adjustTimestamp(7, "days")}
                >
                  + 7 Days
                </Button>
                <Button
                  type="primary"
                  onClick={() => adjustTimestamp(-7, "days")}
                >
                  - 7 Days
                </Button>
              </ButtonGroup>
            </Grid>
            <Grid item xs={12}>
              <ButtonGroup variant="contained">
                <Button
                  type="primary"
                  onClick={() => adjustTimestamp(30, "days")}
                >
                  + 30 Days
                </Button>
                <Button
                  type="primary"
                  onClick={() => adjustTimestamp(-30, "days")}
                >
                  - 30 Days
                </Button>
              </ButtonGroup>
            </Grid>
            <Grid item xs={12}>
              <ButtonGroup variant="contained">
                <Button
                  type="primary"
                  onClick={() => adjustTimestamp(60, "days")}
                >
                  + 60 Days
                </Button>
                <Button
                  type="primary"
                  onClick={() => adjustTimestamp(-60, "days")}
                >
                  - 60 Days
                </Button>
              </ButtonGroup>
            </Grid>
            <Grid item xs={12}>
              <ButtonGroup variant="contained">
                <Button
                  type="primary"
                  onClick={() => adjustTimestamp(90, "days")}
                >
                  + 90 Days
                </Button>
                <Button
                  type="primary"
                  onClick={() => adjustTimestamp(-90, "days")}
                >
                  - 90 Days
                </Button>
              </ButtonGroup>
            </Grid>
          </Grid>
          <Grid item>
            <MuiPickersUtilsProvider utils={MomentUtils}>
              <DateTimePicker
                label="New VIP Expiration"
                value={expirationTimestamp}
                onChange={(value) => {
                  setExpirationTimestamp(value.format());
                }}
                format="YYYY/MM/DD HH:mm"
                maxDate={moment("2300-01-01")}
              />
            </MuiPickersUtilsProvider>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button
          onClick={() => {
            handleConfirm(open, moment().add(200, "years").format(), forward);
          }}
          color="primary"
        >
          Indefinite VIP
        </Button>
        {isVip && (
          <Button
            color="secondary"
            onClick={() => {
              setExpirationTimestamp(moment().format());
              onDeleteVip(open, forward);
              handleClose();
            }}
          >
            Remove VIP
          </Button>
        )}
        <Button
          color="primary"
          onClick={() => {
            handleClose();
          }}
        >
          Cancel
        </Button>
        <Button
          onClick={() => {
            handleConfirm(
              open,
              moment.utc(expirationTimestamp).format("YYYY-MM-DD HH:mm:ssZ"),
              forward
            );
          }}
          color="primary"
        >
          Confirm
        </Button>
      </DialogActions>
    </Dialog>
  );
}
