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

export function VipExpirationDialog(props) {
  const {
    open,
    vips,
    onDeleteVip,
    handleClose,
    handleConfirm,
    SummaryRenderer,
  } = props;
  const [expirationTimestamp, setExpirationTimestamp] = useState();
  const [isVip, setIsVip] = useState();

  /* open is either a boolean or the passed in player Map */
  useEffect(() => {
    if (!(typeof open === "boolean")) {
      if (open && open.get("vip_expiration")) {
        setExpirationTimestamp(open.get("vip_expiration"));
        setIsVip(vips.get(open.get("steam_id_64")) ? true : false);
      }
    }
  }, [open]);

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
            <SummaryRenderer player={open} isVip={isVip} />
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
            handleConfirm(open, moment().add(200, "years").format());
          }}
          color="primary"
        >
          Indefinite VIP
        </Button>
        <Button
          color="secondary"
          onClick={() => {
            setExpirationTimestamp(moment().format());
            onDeleteVip(open);
            handleClose();
          }}
        >
          Remove VIP
        </Button>
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
              moment.utc(expirationTimestamp).format("YYYY-MM-DD HH:MM:SSZ")
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
