import { TimePickerButtons } from "@/components/shared/TimePickerButtons";
import { ExpirationField } from "../fields/ExpirationField";
import { Alert, Box, Button, Stack, Typography } from "@mui/material";
import dayjs from "dayjs";
import { ControlledTextInput } from "@/components/form/core/ControlledTextInput";
import { ControlledSelect } from "@/components/form/core/ControlledSelect";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useMemo } from "react";
import { useWatch } from "react-hook-form";
import { vipListQueryOptions } from "@/queries/vip-list-query";
import { useGlobalStore } from "@/stores/global-state";

const presetTimes = [
  [2, "hours"],
  [1, "day"],
  [1, "week"],
  [1, "month"],
];

export const AddVipFormFields = ({ control, errors, setValue, getValues }) => {
  const expiration = getValues()?.expiration;
  const selectedListId = useWatch({ control, name: "vip_list_id" });
  const serverNumber = useGlobalStore((state) => state.status?.server_number);
  const { data: allLists = [], isLoading, error: listsError } = useQuery(
    vipListQueryOptions.lists()
  );
  const lists = useMemo(() => allLists.filter((list) => !list.is_imported), [allLists]);
  const { data: defaultList, isLoading: defaultLoading, error: defaultError } = useQuery(
    vipListQueryOptions.defaultList(serverNumber)
  );
  const selectedDuration = lists.find((item) => item.id === Number(selectedListId))?.default_expiration_seconds;

  useEffect(() => {
    if (defaultLoading || lists.length === 0 || getValues("vip_list_id")) return;
    const preferred = lists.find((list) => list.id === defaultList?.id) ?? lists[0];
    setValue("vip_list_id", String(preferred.id), { shouldValidate: true });
  }, [lists, defaultList?.id, defaultLoading, getValues, setValue]);

  useEffect(() => {
    if (!selectedListId) return;
    setValue(
      "expiration",
      selectedDuration
        ? dayjs().add(selectedDuration, "seconds")
        : null,
      { shouldValidate: true }
    );
  }, [selectedListId, selectedDuration, setValue]);

  return (
    <Stack gap={3}>
      {(listsError || defaultError) && (
        <Alert severity="error">VIP lists could not be loaded.</Alert>
      )}
      {!isLoading && lists.length === 0 && !listsError && (
        <Alert severity="warning">Create a VIP list before adding records.</Alert>
      )}
      <ControlledSelect
        control={control}
        name="vip_list_id"
        label="Destination VIP list"
        rules={{ required: "Select a VIP list." }}
        disabled={isLoading || defaultLoading || Boolean(listsError) || lists.length === 0}
        options={lists.map((list) => ({
          label: `${list.name} (ID ${list.id}) · ${
            list.servers === null
              ? "All servers"
              : list.servers?.length
              ? list.servers.map((server) => `#${server}`).join(", ")
              : "No servers"
          }`,
          value: String(list.id),
        }))}
      />
      <Typography variant="body2" color="text.secondary">
        Player names come from the player database. Use notes for internal context.
      </Typography>
      <ControlledTextInput
        control={control}
        name="notes"
        label="Notes"
        defaultValue=""
        fullWidth
        multiline
        minRows={2}
      />
      {expiration !== null ? (
        <ExpirationField name="expiration" control={control} errors={errors} />
      ) : (
        <>
          <Alert severity="info">
            Selected players will be VIP indefinitely.
          </Alert>
          <input type="hidden" name="expiration" value={null} />
        </>
      )}
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
            setValue("expiration", null, {
              shouldTouch: true,
              shouldValidate: true,
            })
          }
        >
          Never expires
        </Button>
      </Box>
    </Stack>
  );
};
