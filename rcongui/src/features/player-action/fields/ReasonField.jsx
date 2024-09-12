import { ControlledTextInput } from "@/components/form/core/ControlledTextInput";
import { MenuItem, Select } from "@mui/material";
import { useStoredTexts } from "@/hooks/useStoredTexts";
import { useState } from "react";

export const ReasonField = ({ control, errors, setValue, ...props }) => {
  const { value: storedMessages } = useStoredTexts("punishments");
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
        rules={{ required: "Reason is required" }}
        helperText={
          hasError ? error.message : "The message displayed to the player."
        }
        name={"reason"}
        label={"Reason"}
        multiline
        minRows={5}
        fullWidth
        control={control}
        {...props}
      />
      <Select
        id="saved-messages-select"
        value={selectedMessage}
        onChange={handleOnSelectChange}
        inputProps={{ "aria-label": "Saved Messages" }}
        fullWidth
        displayEmpty
      >
        <MenuItem value="">
          <em>Saved Messages</em>
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
