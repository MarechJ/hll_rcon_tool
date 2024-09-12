import { ControlledTextInput } from "@/components/form/core/ControlledTextInput";
import { useStoredTexts } from "@/hooks/useStoredTexts";
import { MenuItem, Select } from "@mui/material";
import { useState } from "react";

export const MessageField = ({ control, errors, setValue, ...props }) => {
  const { value: storedMessages } = useStoredTexts("messages");
  const [selectedMessage, setSelectedMessage] = useState("");
  const error = errors["message"];
  const hasError = !!error;

  const handleOnSelectChange = (event) => {
    const value = event.target.value ?? '';
    if (value === '') {
      setSelectedMessage(value)
    } else {
      const message = storedMessages[value]
      setSelectedMessage(String(value))
      setValue('message', message.content, { shouldTouch: true })
    }
  }

  return (
    <>
      <ControlledTextInput
        error={hasError}
        name={"message"}
        label={"Message"}
        control={control}
        rules={{ required: "Message is required" }}
        helperText={
          hasError ? error.message : "The message displayed to the player."
        }
        multiline
        minRows={5}
        fullWidth
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
