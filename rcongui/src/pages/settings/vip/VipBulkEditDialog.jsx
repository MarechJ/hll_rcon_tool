import { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Tabs,
  Tab,
  Box,
  Typography,
  Stack,
} from "@mui/material";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { DesktopDateTimePicker } from "@mui/x-date-pickers";
import dayjs from "dayjs";
import Padlock from "@/components/shared/Padlock";
import { TimePickerButtons } from "@/components/shared/TimePickerButtons";

const INDEFINITE_EXPIRATION = "3000-01-01T00:00:00+00:00";

const TabPanel = ({ children, value, index, ...other }) => (
  <div role="tabpanel" hidden={value !== index} {...other}>
    {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
  </div>
);

export const VipBulkEditDialog = ({
  open,
  onClose,
  onConfirm,
  selectedCount,
}) => {
  const [tab, setTab] = useState(0);
  const [expiration, setExpiration] = useState(dayjs().add(5, "minutes"));
  const [indefinitely, setIndefinitely] = useState(false);
  const [extensionAmount, setExtensionAmount] = useState(dayjs());

  const extensionDiff = extensionAmount.diff(dayjs());

  const handleTabChange = (_, newValue) => {
    setTab(newValue);
  };

  const handleConfirm = () => {
    onConfirm({
      mode: tab === 0 ? "set" : "extend",
      value: tab === 0 ? (indefinitely ? null : expiration) : extensionAmount,
    });
    handleClose();
  };

  const handleClose = () => {
    setExtensionAmount(dayjs());
    setIndefinitely(false);
    setExpiration(dayjs().add(5, "minutes"));
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Edit VIP Expiration ({selectedCount} selected)</DialogTitle>
      <DialogContent>
        <Tabs value={tab} onChange={handleTabChange}>
          <Tab label="Set Expiration" />
          <Tab label="Extend Time" />
        </Tabs>

        <TabPanel value={tab} index={0}>
          <Stack spacing={2}>
            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <DesktopDateTimePicker
                label="Expiration"
                value={expiration}
                onChange={setExpiration}
                format="LLL"
                maxDateTime={dayjs(INDEFINITE_EXPIRATION)}
                disabled={indefinitely}
                disablePast={true}
              />
            </LocalizationProvider>
            <Stack>
              <TimePickerButtons
                amount={1}
                unit="hour"
                expirationTimestamp={expiration}
                setExpirationTimestamp={setExpiration}
                enablePast={true}
              />
              <TimePickerButtons
                amount={1}
                unit="day"
                expirationTimestamp={expiration}
                setExpirationTimestamp={setExpiration}
                enablePast={true}
              />
              <TimePickerButtons
                amount={1}
                unit="month"
                expirationTimestamp={expiration}
                setExpirationTimestamp={setExpiration}
                enablePast={true}
              />
            </Stack>
            <Padlock
              checked={indefinitely}
              handleChange={setIndefinitely}
              label="Never expires"
            />
          </Stack>
        </TabPanel>

        <TabPanel value={tab} index={1}>
          <Stack spacing={2}>
            <Typography>
              <Box
                component="span"
                fontWeight="bold"
                sx={{
                  color: extensionDiff > 0 ? "success.main" : "warning.main",
                }}
              >
                {extensionDiff > 0 ? "Extend " : "Reduce "}
              </Box>
              {`expiration time for all selected VIPs by: `}
              <Box
                component="span"
                fontWeight="bold"
                sx={{
                  color: extensionDiff > 0 ? "success.main" : "warning.main",
                }}
              >
                {dayjs.duration(extensionDiff).humanize()}
              </Box>
              <Typography variant="caption" color="text.secondary">
                {` (${dayjs
                  .duration(extensionDiff)
                  .asHours()
                  .toFixed(0)} hours)`}
              </Typography>
            </Typography>
            <Stack>
              <TimePickerButtons
                amount={1}
                unit="hour"
                expirationTimestamp={extensionAmount}
                setExpirationTimestamp={setExtensionAmount}
                enablePast={true}
              />
              <TimePickerButtons
                amount={1}
                unit="day"
                expirationTimestamp={extensionAmount}
                setExpirationTimestamp={setExtensionAmount}
                enablePast={true}
              />
              <TimePickerButtons
                amount={1}
                unit="month"
                expirationTimestamp={extensionAmount}
                setExpirationTimestamp={setExtensionAmount}
                enablePast={true}
              />
            </Stack>
          </Stack>
        </TabPanel>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          variant="contained"
          color="primary"
          onClick={() => handleConfirm()}
        >
          Apply
        </Button>
      </DialogActions>
    </Dialog>
  );
};
