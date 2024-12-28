import { TimePickerButtons } from "@/components/shared/TimePickerButtons";
import { ExpirationField } from "../fields/ExpirationField";
import { ForwardField } from "../fields/ForwardField";
import { Box, Button, Stack } from "@mui/material";
import dayjs from "dayjs";

const presetTimes = [
  [2, "hours"],
  [1, "day"],
  [1, "week"],
  [1, "month"],
];

export const AddVipFormFields = ({ control, errors, setValue, getValues }) => {

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
          onClick={() => setValue('expiration', dayjs().add(15, "minutes"))}
        >
          Help to skip the queue!
        </Button>
        {presetTimes.map(([amount, unit], index) => (
          <TimePickerButtons
            key={unit + index}
            amount={amount}
            unit={unit}
            expirationTimestamp={getValues()?.expiration ?? dayjs()}
            // shouldValidate is needed to trigger rerendering
            // so the getValues()?.expiration is updated
            setExpirationTimestamp={(value) => { setValue('expiration', value, { shouldTouch: true, shouldValidate: true }) }}
          />
        ))}
        <Button
          variant="outlined"
          size="small"
          color="secondary"
          style={{ display: "block", width: "100%" }}
          onClick={() => setValue('expiration', dayjs("3000-01-01T00:00:00+00:00"))}
        >
          Never expires
        </Button>
      </Box>
    </Stack>
  );
};
