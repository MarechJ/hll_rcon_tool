import { TimePickerButtons } from "@/components/shared/TimePickerButtons";
import { ExpirationField } from "../fields/ExpirationField";
import { ReasonField } from "../fields/ReasonField";
import { Box, Stack } from "@mui/material";
import dayjs from "dayjs";
import { ControlledSelect } from "@/components/form/core/ControlledSelect";

const presetTimes = [
  [2, "hours"],
  [1, "day"],
  [1, "week"],
  [1, "month"],
];

export const BlacklistPlayerFormFields = ({ control, errors, setValue, getValues, contextData }) => {

  return (
    <Stack gap={3}>
      <ControlledSelect
        control={control}
        errors={errors}
        name={"blacklist_id"}
        label={"Blacklist"}
        required={true}
        defaultValue={"0"} // there is always the Default blacklist with id 0
        options={contextData?.get_blacklists?.map(blacklist => ({
            label: `${blacklist.name} - ${blacklist.sync}`,
            value: String(blacklist.id),
        })) ?? []}
      />
      <ExpirationField control={control} errors={errors} />
      <Box>
        {presetTimes.map(([amount, unit], index) => (
          <TimePickerButtons
            key={unit + index}
            amount={amount}
            unit={unit}
            expirationTimestamp={getValues()?.expiration ?? dayjs()}
            setExpirationTimestamp={(value) => {
              setValue("expiration", value, { shouldTouch: true });
            }}
          />
        ))}
      </Box>
      <ReasonField control={control} errors={errors} setValue={setValue} />
    </Stack>
  );
};
