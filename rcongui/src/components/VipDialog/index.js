import React, { useEffect, useState } from "react";
import {
  Box,
  Button,
  ButtonGroup,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from "@mui/material";

import { DesktopDateTimePicker } from '@mui/x-date-pickers/DesktopDateTimePicker';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import moment from "moment";
import { PlayerVipSummary } from "./PlayerVipSummary";
import { ForwardCheckBox } from "../commonComponent";

const vipButtons = [
  [2, "hours"],
  [1, "day"],
  [1, "week"],
  [1, "month"]
];

const VipTimeButtons = ({
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

/**
 * 
 * @param open [NEW] boolean - signaling opened/closed dialog window
 * @param open [OLD] boolean | ImmutablePlayer{} - signaling opened/closed dialog window and passing down the player object
 * @param player [NEW] ImmutablePlayer{} - the Player object
 */
export function VipExpirationDialog({ open, vips, onDeleteVip, handleClose, handleConfirm, player }) {
  const [expirationTimestamp, setExpirationTimestamp] = useState();
  const [isVip, setIsVip] = useState(false);
  const [forward, setForward] = useState(false);

  useEffect(() => {
    // handle old usage
    if (typeof open === "object") {
      setIsVip(!!vips.get(open.get("player_id")));
      if (open.get("vip_expiration")) {
        setExpirationTimestamp(open.get("vip_expiration"));
      }
      return
    }

    // handle new usage
    if (open === true && player) {
      // if player provided from "api/get_players" it already includes "is_vip" param
      if (player?.has("is_vip") && player.get("is_vip")) {
        setIsVip(true)
        // but the expiration date needs to be found from "api/get_vip_ids"
        let p = vips.find(vipObj => vipObj.player_id === player.get("player_id"))
        let pExpiration = p?.vip_expiration
        // A player can have VIP on the server but no corresponding record w/ expiration in CRCON
        setExpirationTimestamp(moment.utc(pExpiration ? pExpiration : moment()).format("YYYY-MM-DD HH:mm:ssZ"))
        return
      }
      // if player provided from "api/get_players_history" we need to look inside "api/get_vip_ids" and find him there
      if (vips.some((playerVIP) => playerVIP.player_id === player.get("player_id"))) {
        setIsVip(true)
        setExpirationTimestamp(moment.utc(player.get("vip_expiration")).format("YYYY-MM-DD HH:mm:ssZ"));
        return
      }
    }

    setIsVip(false);
  }, [open, vips]);

  if (!open || !player) {
    return null;
  }

  const currentVipExpiration = typeof open === "object" ? open?.get("vip_expiration")
    : player?.has("vip_expiration") ? player?.get("vip_expiration") :
      vips?.find(vipObj => vipObj.player_id === player?.get("player_id"))?.vip_expiration

  return (
    <Dialog open={open} maxWidth="xs" fullWidth={true} onClose={handleClose} aria-labelledby="form-dialog-title">
      <DialogTitle id="form-dialog-title">
        Manage VIP
      </DialogTitle>
      <DialogContent>
        <Box style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <PlayerVipSummary player={player ?? open} vipExpiration={currentVipExpiration} isVip={isVip} />
          {/* <MuiPickersUtilsProvider utils={MomentUtils}>
            <DateTimePicker
              label="New VIP Expiration"
              value={expirationTimestamp}
              onChange={(value) => {
                setExpirationTimestamp(value.format());
              }}
              format="YYYY/MM/DD HH:mm"
              maxDate={moment("3000-01-01T00:00:00+00:00")}
            />
          </MuiPickersUtilsProvider> */}
          <LocalizationProvider dateAdapter={AdapterDayjs}>
          <DesktopDateTimePicker
            label="New VIP Expiration"
            onChange={(value) => console.log(value)} // send value to hook form
            format='LLL'
          />
        </LocalizationProvider>
          <Box>
            <Button variant="outlined" size="small" color="secondary" style={{ display: "block", width: "100%", marginBottom: 4 }} onClick={() => setExpirationTimestamp(moment().add(15, "minutes"))}>Help to join!</Button>
            {vipButtons.map(([amount, unit], index) => (
              <VipTimeButtons
                key={unit + index}
                amount={amount}
                unit={unit}
                expirationTimestamp={expirationTimestamp}
                setExpirationTimestamp={setExpirationTimestamp}
              />
            ))}
            <Button variant="outlined" size="small" color="secondary" style={{ display: "block", width: "100%" }} onClick={() => setExpirationTimestamp("3000-01-01T00:00:00+00:00")}>Indefinite</Button>
          </Box>
          <ForwardCheckBox
            label={<span>Apply VIP to <strong>ALL</strong> servers?</span>}
            bool={forward}
            onChange={() => setForward(!forward)}
          />
        </Box>
      </DialogContent>
      <DialogActions>
        {isVip && (
          <Button
            color="secondary"
            onClick={() => {
              setExpirationTimestamp(moment().format());
              onDeleteVip(player ?? open, forward);
              handleClose();
            }}
          >
            Remove VIP
          </Button>
        )}
        <Box style={{ flexGrow: 1 }} />
        <Button
          onClick={() => {
            handleClose();
          }}
        >
          Cancel
        </Button>
        <Button
          color="primary"
          onClick={() => {
            handleConfirm(
              player ?? open,
              moment.utc(expirationTimestamp).format("YYYY-MM-DD HH:mm:ssZ"),
              forward
            );
            handleClose();
          }}
        >
          Confirm
        </Button>
      </DialogActions>
    </Dialog>
  );
}