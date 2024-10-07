import { ControlledTextInput } from "@/components/form/core/ControlledTextInput";
import { MenuItem, Select } from "@mui/material";
import { useStoredTexts } from "@/hooks/useStoredTexts";
import { useState } from "react";

export const ReasonField = ({ control, errors, setValue, ...props }) => {
  const { value: storedMessages } = useStoredTexts("reason");
  const [selectedMessage, setSelectedMessage] = useState("");
  const error = errors["reason"];
  const hasError = !!error;

  const handleOnSelectChange = (event) => {
    const value = event.target.value ?? "";
    if (value === "") {
      setSelectedMessage(value);
    } else {
      const message = storedMessages[value];
      setSelectedMessage(String(value));
      setValue("reason", message.content, { shouldTouch: true });
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
        {...props}
      />
      <Select
        id="saved-reasons-select"
        value={selectedMessage}
        onChange={handleOnSelectChange}
        inputProps={{ "aria-label": "Saved Reasons" }}
        fullWidth
        displayEmpty
      >
        <MenuItem value="">
          <em>Saved Reasons</em>
        </MenuItem>
        {storedMessages.map((message, i) => {
          return (
            <MenuItem key={message.title + i} value={String(i)}>
              {message.title}
            </MenuItem>
          );
        })}
      </Select>
    </>
  );
};
