import {
  Alert,
  FormControl,
  FormHelperText,
  InputLabel,
  MenuItem,
  Select,
  Stack,
} from "@mui/material";
import {
  and,
  rankWith,
  scopeEndsWith,
  uiTypeIs,
} from "@jsonforms/core";
import { withJsonFormsControlProps } from "@jsonforms/react";
import { useQuery } from "@tanstack/react-query";

import { vipListQueryOptions } from "@/queries/vip-list-query";

const DEFAULT_VALUE = "";

const SeedVipListRenderer = ({
  data,
  handleChange,
  path,
  label,
  description,
  errors,
  enabled,
}) => {
  const {
    data: vipLists = [],
    isLoading: listsLoading,
    isError: listsFailed,
  } = useQuery(vipListQueryOptions.applicableLists());

  const {
    data: defaultList,
    isLoading: defaultLoading,
    isError: defaultFailed,
  } = useQuery(vipListQueryOptions.defaultList());

  const selectedId = data == null ? null : Number(data);
  const selectedList =
    selectedId === null
      ? null
      : vipLists.find((vipList) => Number(vipList.id) === selectedId);
  const invalidSelection = selectedId !== null && !selectedList;
  const loading = listsLoading || defaultLoading;
  const failed = listsFailed || defaultFailed;
  const fieldLabel = label || "Seed VIP reward list";

  return (
    <Stack spacing={1.25} sx={{ mt: 1 }}>
      <FormControl
        fullWidth
        error={Boolean(errors) || invalidSelection || failed}
        disabled={!enabled || loading}
      >
        <InputLabel id="seed-vip-list-label">{fieldLabel}</InputLabel>
        <Select
          labelId="seed-vip-list-label"
          label={fieldLabel}
          value={selectedId ?? DEFAULT_VALUE}
          onChange={(event) =>
            handleChange(
              path,
              event.target.value === DEFAULT_VALUE
                ? null
                : Number(event.target.value)
            )
          }
        >
          <MenuItem value={DEFAULT_VALUE}>
            Use server default VIP list
            {defaultList?.name ? ` (${defaultList.name})` : ""}
          </MenuItem>

          {invalidSelection && (
            <MenuItem value={selectedId}>
              Invalid list ID {selectedId} — default fallback will be used
            </MenuItem>
          )}

          {vipLists.map((vipList) => (
            <MenuItem key={vipList.id} value={Number(vipList.id)}>
              {vipList.name}
              {Number(defaultList?.id) === Number(vipList.id)
                ? " — server default"
                : ""}
            </MenuItem>
          ))}
        </Select>

        {description && <FormHelperText>{description}</FormHelperText>}
        {errors && <FormHelperText error>{errors}</FormHelperText>}
      </FormControl>

      {invalidSelection && (
        <Alert severity="warning">
          VIP list ID {selectedId} no longer exists or does not apply to this
          server. Seed rewards will fall back to the server default list.
        </Alert>
      )}

      {failed && (
        <Alert severity="error">
          The available VIP lists could not be loaded. The stored value has not
          been changed.
        </Alert>
      )}

      {!loading && !failed && vipLists.length === 0 && (
        <Alert severity="warning">
          No VIP list applies to this server. Seed VIP rewards cannot be
          granted until a default VIP list is configured.
        </Alert>
      )}
    </Stack>
  );
};

export const seedVipListTester = rankWith(
  20,
  and(
    uiTypeIs("Control"),
    scopeEndsWith("reward/properties/vip_list_id")
  )
);

export const renderer = withJsonFormsControlProps(SeedVipListRenderer);
