import { TimePickerButtons } from "@/components/shared/TimePickerButtons";
import { ExpirationField } from "../fields/ExpirationField";
import { ForwardField } from "../fields/ForwardField";
import { Box, Button, Stack, TextField } from "@mui/material";
import dayjs from "dayjs";
import { ControlledTextInput } from "@/components/form/core/ControlledTextInput";

const presetTimes = [
  [2, "hours"],
  [1, "day"],
  [1, "week"],
  [1, "month"],
];

export const AddVipFormFields = ({ control, errors, setValue, getValues }) => {
  return (
    <Stack gap={3}>
      <TextField
        label="Description (Preview)"
        value={
          (getValues()?.prefix ?? "") +
          "<Player>" +
          (getValues()?.suffix ?? "")
        }
        helperText="The VIP will be displayed as <PREFIX><PLAYER_NAME><SUFFIX>"
        fullWidth
        disabled
      />
      <Stack direction={["column", "row"]} gap={1}>
        <ControlledTextInput
          control={control}
          errors={errors}
          // shouldValidate is needed to trigger rerendering
          // so the description field is updated
          onChange={(e) => setValue("prefix", e.target.value, { shouldValidate: true })}
          value={getValues()?.prefix ?? ""}
          name="prefix"
          label="Prefix"
          placeholder="[TAG]"
          helperText="Prefix to be added to the front of the player's name"
          sx={{ flex: 1 }}
        />
        <ControlledTextInput
          control={control}
          errors={errors}
          // shouldValidate is needed to trigger rerendering
          // so the description f is updated
          onChange={(e) => setValue("suffix", e.target.value, { shouldValidate: true })}
          value={getValues()?.suffix ?? ""}
          name="suffix"
          label="Suffix"
          placeholder="[TAG]"
          helperText="Suffix to be added to the end of the player's name"
          sx={{ flex: 1 }}
        />
      </Stack>
      <ExpirationField control={control} errors={errors} />
      <Box>
        <Button
          variant="outlined"
          size="small"
          color="secondary"
          style={{ display: "block", width: "100%", marginBottom: 4 }}
          onClick={() => setValue("expiration", dayjs().add(15, "minutes"))}
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
            setExpirationTimestamp={(value) => {
              setValue("expiration", value, {
                shouldTouch: true,
                shouldValidate: true,
              });
            }}
          />
        ))}
        <Button
          variant="outlined"
          size="small"
          color="secondary"
          style={{ display: "block", width: "100%" }}
          onClick={() =>
            setValue("expiration", dayjs("3000-01-01T00:00:00+00:00"))
          }
        >
          Never expires
        </Button>
      </Box>
      <ForwardField control={control} errors={errors} />
    </Stack>
  );
};
