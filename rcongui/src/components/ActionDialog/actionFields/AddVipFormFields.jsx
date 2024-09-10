import { TimePickerButtons } from "@/components/shared/TimePickerButtons";
import { ExpirationField } from "../../form/custom/ExpirationField";
import { ForwardField } from "../../form/custom/ForwardField";
import { Box, Button, Stack } from "@mui/material";

const presetTimes = [
  [2, "hours"],
  [1, "day"],
  [1, "week"],
  [1, "month"],
];

export const AddVipFormFields = ({ control, errors }) => {
  return (
    <Stack gap={3}>
      <ForwardField control={control} errors={errors} />
      <ExpirationField control={control} errors={errors} />
      <Box>
        <Button
          variant="outlined"
          size="small"
          color="secondary"
          style={{ display: "block", width: "100%", marginBottom: 4 }}
          onClick={() => setExpirationTimestamp(dayjs().add(15, "minutes"))}
        >
          Help to join!
        </Button>
        {presetTimes.map(([amount, unit], index) => (
          <TimePickerButtons
            key={unit + index}
            amount={amount}
            unit={unit}
            expirationTimestamp={() => {}}
            setExpirationTimestamp={() => {}}
          />
        ))}
        <Button
          variant="outlined"
          size="small"
          color="secondary"
          style={{ display: "block", width: "100%" }}
          onClick={() => setExpirationTimestamp("3000-01-01T00:00:00+00:00")}
        >
          Indefinite
        </Button>
      </Box>
    </Stack>
  );
};
