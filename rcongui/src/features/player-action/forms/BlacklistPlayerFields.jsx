import { TimePickerButtons } from "@/components/shared/TimePickerButtons";
import { ExpirationField } from "../fields/ExpirationField";
import { ReasonField } from "../fields/ReasonField";
import { Alert, Box, Button, Stack } from "@mui/material";
import dayjs from "dayjs";
import { ControlledSelect } from "@/components/form/core/ControlledSelect";
import { useEffect } from "react";

const presetTimes = [
  [2, "hours"],
  [1, "day"],
  [1, "week"],
  [1, "month"],
];

export const BlacklistPlayerFormFields = ({
  control,
  errors,
  setValue,
  getValues,
  contextData,
  setError,
  contextError,
}) => {
  const expiresAt = getValues()?.expires_at;
  
  useEffect(() => {
    if (contextError) {
      setError("blacklist_id", { message: contextError.message });
    }
  }, [contextError]);

  return (
    <Stack gap={3}>
      <ControlledSelect
        control={control}
        errors={errors}
        name={"blacklist_id"}
        label={"Blacklist"}
        required={true}
        defaultValue={contextData?.blacklists?.length ? "0" : ""} // there is always the Default blacklist with id 0
        options={
          contextData?.blacklists?.map((blacklist) => ({
            label: `${blacklist.name} - ${blacklist.sync}`,
            value: String(blacklist.id),
          })) ?? []
        }
      />
      {expiresAt !== null ? (
        <ExpirationField name="expires_at" control={control} errors={errors} />
      ) : (
        <>
          <Alert severity="info">
            Selected players will be blacklisted indefinitely.
          </Alert>
          <input type="hidden" name="expires_at" value={null} />
        </>
      )}
        <Box>
        {presetTimes.map(([amount, unit], index) => (
          <TimePickerButtons
            key={unit + index}
            amount={amount}
            unit={unit}
            expirationTimestamp={getValues()?.expires_at ?? dayjs()}
            setExpirationTimestamp={(value) => {
              // shouldValidate is needed to trigger rerendering
              // so the getValues()?.expires_at is updated
              setValue("expires_at", value, {
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
            setValue("expires_at", null, {
              shouldTouch: true,
              shouldValidate: true,
            })
          }
        >
          Never expires
        </Button>
      </Box>
      <ReasonField control={control} errors={errors} setValue={setValue} />
    </Stack>
  );
};
