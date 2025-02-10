import { useEffect, useState } from "react";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from "@mui/material";

import { DesktopDateTimePicker } from '@mui/x-date-pickers/DesktopDateTimePicker';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { PlayerVipSummary } from "./PlayerVipSummary";
import { ForwardCheckBox } from "../commonComponent";
import { TimePickerButtons } from "@/components/shared/TimePickerButtons";
import dayjs from "dayjs";

const presetTimes = [
  [2, "hours"],
  [1, "day"],
  [1, "week"],
  [1, "month"]
];

/**
 * 
 * @param open [NEW] boolean - signaling opened/closed dialog window
 * @param open [OLD] boolean | ImmutablePlayer{} - signaling opened/closed dialog window and passing down the player object
 * @param player [NEW] ImmutablePlayer{} - the Player object
 */
export function VipExpirationDialog({ open, vips, onDeleteVip, handleClose, handleConfirm, player }) {
  const [expirationTimestamp, setExpirationTimestamp] = useState("");
  const [isVip, setIsVip] = useState(false);
  const [forward, setForward] = useState(false);

  useEffect(() => {
    // handle old usage
    if (typeof open === "object") {
      setIsVip(!!vips.get(open.get("player_id")));
      if (open.get("expires_at")) {
        setExpirationTimestamp(open.get("expires_at"));
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
        let pExpiration = p?.expires_at
        // A player can have VIP on the server but no corresponding record w/ expiration in CRCON
        setExpirationTimestamp(dayjs(pExpiration ? pExpiration : dayjs()).format("YYYY-MM-DD HH:mm:ssZ"))
        return
      }
      // if player provided from "api/get_players_history" we need to look inside "api/get_vip_ids" and find him there
      if (vips.some((playerVIP) => playerVIP.player_id === player.get("player_id"))) {
        setIsVip(true)
        setExpirationTimestamp(dayjs(player.get("expires_at")).format("YYYY-MM-DD HH:mm:ssZ"));
        return
      }
    }

    setIsVip(false);
  }, [open, vips]);

  if (!open || !player) {
    return null;
  }

  const currentVipExpiration = typeof open === "object" ? open?.get("expires_at")
    : player?.has("expires_at") ? player?.get("expires_at") :
      vips?.find(vipObj => vipObj.player_id === player?.get("player_id"))?.expires_at

  return (
    <Dialog open={open} maxWidth="xs" fullWidth={true} onClose={handleClose} aria-labelledby="form-dialog-title">
      <DialogTitle id="form-dialog-title">
        Manage VIP
      </DialogTitle>
      <DialogContent>
        <Box style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <PlayerVipSummary player={player ?? open} vipExpiration={currentVipExpiration} isVip={isVip} />
          <LocalizationProvider dateAdapter={AdapterDayjs}>
            <DesktopDateTimePicker
              label="New VIP Expiration"
              value={dayjs(expirationTimestamp)}
              onChange={(value) => console.log(value)} // send value to hook form
              format='LLL'
              maxDate={dayjs("3000-01-01T00:00:00+00:00")}
            />
          </LocalizationProvider>
          <Box>
            <Button variant="outlined" size="small" color="secondary" style={{ display: "block", width: "100%", marginBottom: 4 }} onClick={() => setExpirationTimestamp(dayjs().add(15, "minutes"))}>Help to join!</Button>
            {presetTimes.map(([amount, unit], index) => (
              <TimePickerButtons
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
              setExpirationTimestamp(dayjs().format());
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
              dayjs(expirationTimestamp).format("YYYY-MM-DD HH:mm:ssZ"),
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
