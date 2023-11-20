import React from "react";
import {
  Button,
  Grid,
  IconButton,
  Link,
  TextField,
  Typography,
  Switch,
  Tooltip,
  FormControlLabel,
} from "@material-ui/core";
import {
  get,
  handle_http_errors,
  postData,
  showResponse,
} from "../../utils/fetchUtils";

const RealVip = ({ classes }) => {
  const [enabled, setEnabled] = React.useState(null);
  const [maxVipSlot, setMaxVipSlot] = React.useState(-1);
  const [minVipSlot, setMinVipSlot] = React.useState(-1);
  const isFirstRender = React.useRef(true);

  React.useEffect(() => {
    get("get_real_vip_config")
      .then((res) => showResponse(res, "get_real_vip_config", false))
      .then((res) => {
        if (!res.failed && res.result) {
          setEnabled(res.result.enabled);
          setMaxVipSlot(res.result.desired_total_number_vips);
          setMinVipSlot(res.result.minimum_number_vip_slots);
        }
      });
  }, []);

  React.useEffect(() => {
    if (!isFirstRender.current) {
      postData(`${process.env.REACT_APP_API_URL}set_real_vip_config`, {
        enabled: enabled,
        desired_total_number_vips: maxVipSlot,
        minimum_number_vip_slot: minVipSlot,
      })
        .then((res) => showResponse(res, "set_real_vip_config", true))
        .catch(handle_http_errors);
    } else if (enabled !== null && maxVipSlot !== -1 && minVipSlot !== -1) {
      isFirstRender.current = false;
    }
  }, [enabled, maxVipSlot, minVipSlot]);

  return (
    <Grid container>
      <Grid item xs={12}>
        <FormControlLabel
          control={
            <Switch
              checked={enabled}
              onChange={(e) => setEnabled(e.target.checked)}
            />
          }
          label="Real VIP enabled"
        />
      </Grid>
      <Grid item xs={6}>
        <TextField
          type="number"
          InputProps={{ inputProps: { min: 0, max: 100 } }}
          label="Max num of VIP slot"
          value={maxVipSlot}
          onChange={(e) => setMaxVipSlot(e.target.value)}
        />
      </Grid>
      <Grid item xs={6}>
        <TextField
          type="number"
          InputProps={{ inputProps: { min: 0, max: 100 } }}
          label="Min num of VIP slot"
          value={minVipSlot}
          onChange={(e) => setMinVipSlot(e.target.value)}
        />
      </Grid>
    </Grid>
  );
};

export default RealVip;
