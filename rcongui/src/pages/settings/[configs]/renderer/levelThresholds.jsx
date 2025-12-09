import { withJsonFormsControlProps } from "@jsonforms/react";
import {
  Box,
  Button,
  FormControl,
  FormHelperText,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { rankWith, scopeEndsWith } from "@jsonforms/core";
import DeleteIcon from "@mui/icons-material/Delete";
import AddIcon from "@mui/icons-material/Add";
import { useState } from "react";
import { getAllRoles, getRoleLabel } from "@/constants/roles";

const LevelThresholdsRenderer = (props) => {
  const { data, handleChange, path, label, description, errors } = props;
  const [selectedRole, setSelectedRole] = useState("");

  const thresholds = data || {};
  const configuredRoles = Object.keys(thresholds);
  const allRoles = getAllRoles();
  const availableRolesToAdd = allRoles.filter(
    (role) => !configuredRoles.includes(role.value)
  );

  const handleAddRole = () => {
    if (!selectedRole) return;

    const newThresholds = {
      ...thresholds,
      [selectedRole]: {
        label: getRoleLabel(selectedRole),
        min_players: 0,
        min_level: 0,
      },
    };

    handleChange(path, newThresholds);
    setSelectedRole("");
  };

  const handleRemoveRole = (roleKey) => {
    const newThresholds = { ...thresholds };
    delete newThresholds[roleKey];
    handleChange(path, newThresholds);
  };

  const handleUpdateRole = (roleKey, field, value) => {
    const newThresholds = {
      ...thresholds,
      [roleKey]: {
        ...thresholds[roleKey],
        [field]: field === "label" ? value : parseInt(value, 10) || 0,
      },
    };
    handleChange(path, newThresholds);
  };

  return (
    <FormControl fullWidth margin="normal" error={errors && errors.length > 0}>
      <InputLabel shrink sx={{ position: "relative", transform: "none", mb: 1 }}>
        {label || "level_thresholds"}
      </InputLabel>
      {description && (
        <FormHelperText sx={{ mt: 0, mb: 1 }}>{description}</FormHelperText>
      )}

      <Box sx={{ mt: 1 }}>
        {configuredRoles.map((roleKey, index) => {
          const roleConfig = thresholds[roleKey];
          const roleLabel = getRoleLabel(roleKey);

          return (
            <Box key={roleKey} sx={{ mb: 2 }}>
              <Stack direction="row" spacing={1} alignItems="flex-start" sx={{ mb: 1 }}>
                <Typography variant="body2" sx={{ pt: 1, minWidth: 120 }}>
                  {roleLabel}
                </Typography>
                <Box sx={{ flex: 1 }}>
                  <Stack spacing={1}>
                    <TextField
                      fullWidth
                      label="Label"
                      value={roleConfig.label || ""}
                      onChange={(e) => handleUpdateRole(roleKey, "label", e.target.value)}
                      size="small"
                    />
                    <Stack direction="row" spacing={1}>
                      <TextField
                        label="Min Players"
                        type="number"
                        value={roleConfig.min_players ?? 0}
                        onChange={(e) => handleUpdateRole(roleKey, "min_players", e.target.value)}
                        inputProps={{ min: 0, max: 100 }}
                        size="small"
                        sx={{ flex: 1 }}
                      />
                      <TextField
                        label="Min Level"
                        type="number"
                        value={roleConfig.min_level ?? 0}
                        onChange={(e) => handleUpdateRole(roleKey, "min_level", e.target.value)}
                        inputProps={{ min: 0, max: 500 }}
                        size="small"
                        sx={{ flex: 1 }}
                      />
                    </Stack>
                  </Stack>
                </Box>
                <IconButton
                  size="small"
                  onClick={() => handleRemoveRole(roleKey)}
                  aria-label={`Remove ${roleLabel}`}
                  sx={{ mt: 0.5 }}
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Stack>
            </Box>
          );
        })}

        {availableRolesToAdd.length > 0 && (
          <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 1 }}>
            <Select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
              size="small"
              displayEmpty
              sx={{ minWidth: 200 }}
            >
              <MenuItem value="" disabled>
                Select role...
              </MenuItem>
              {availableRolesToAdd.map((role) => (
                <MenuItem key={role.value} value={role.value}>
                  {role.label}
                </MenuItem>
              ))}
            </Select>
            <Button
              variant="text"
              startIcon={<AddIcon />}
              onClick={handleAddRole}
              disabled={!selectedRole}
              size="small"
            >
              Add
            </Button>
          </Stack>
        )}
      </Box>

      {errors && errors.length > 0 && (
        <FormHelperText error>{errors}</FormHelperText>
      )}
    </FormControl>
  );
};

export const levelThresholdsTester = rankWith(
  10,
  scopeEndsWith("level_thresholds")
);

export const renderer = withJsonFormsControlProps(LevelThresholdsRenderer);

