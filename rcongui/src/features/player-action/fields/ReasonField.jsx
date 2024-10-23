import { ControlledTextInput } from "@/components/form/core/ControlledTextInput";
import { MenuItem, Select } from "@mui/material";
import { useTemplates } from "@/hooks/useTemplates";
import { useState } from "react";

export const ReasonField = ({ control, errors, setValue, ...props }) => {
  const templates = useTemplates("reason");
  const [selectedTemplate, setSelectedTemplate] = useState("");
  const error = errors["reason"];
  const hasError = !!error;

  const handleOnSelectChange = (event) => {
    const value = event.target.value ?? "";
    if (value === "") {
      setSelectedTemplate(value);
    } else {
      const template = templates[value];
      setSelectedTemplate(String(value));
      setValue("reason", template.content, { shouldTouch: true });
    }
  };

  return (
    <>
      <ControlledTextInput
        error={hasError}
        name={"reason"}
        label={"Reason"}
        control={control}
        rules={{ required: "Reason is required" }}
        helperText={
          hasError ? error.message : "The message displayed to the player."
        }
        multiline
        minRows={5}
        fullWidth
      />
      <Select
        id="saved-reasons-select"
        value={selectedTemplate}
        onChange={handleOnSelectChange}
        inputProps={{ "aria-label": "Saved Reasons" }}
        fullWidth
        displayEmpty
      >
        <MenuItem value="">
          <em>Saved Reasons</em>
        </MenuItem>
        {templates.map((template, i) => {
          return (
            <MenuItem key={template.id} value={String(i)}>
              {template.title}
            </MenuItem>
          );
        })}
      </Select>
    </>
  );
};
