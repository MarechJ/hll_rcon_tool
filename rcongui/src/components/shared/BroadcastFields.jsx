import { parseBroadcastMessages, unpackBroadcastMessage } from "@/utils/lib";
import React from "react";
import {
  Box,
  Button,
  IconButton,
  Stack,
  styled,
  TextField,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";

const StyledTextField = styled(TextField)((theme) => ({
    "& .MuiOutlinedInput-root, & .MuiOutlinedInput-notchedOutline": {
      borderRadius: 0,
    },
  }));

export function BroadcastFields({ message, disabled, onChange, ...props }) {
  const rows = unpackBroadcastMessage(message);

  const handleAddRow = () => {
    onChange(parseBroadcastMessages([...rows, { time: "", message: "" }]));
  };

  const handleDeleteRow = (index) => {
    onChange(
      parseBroadcastMessages(rows.slice(0, index).concat(rows.slice(index + 1)))
    );
  };

  const handleRowChange = (lineIndex, key) => (event) => {
    onChange(
      parseBroadcastMessages(
        rows.map((line, i) =>
          lineIndex === i ? { ...line, [key]: event.target.value } : line
        )
      )
    );
  };

  return (
    <Box {...props}>
      <textarea
        name="content"
        value={message}
        disabled={disabled}
        required
        readOnly
        hidden
      />
      {rows.map(({ time, message }, index) => (
        <Stack key={"line" + index} direction={"row"}>
          <StyledTextField
            required
            value={time}
            onChange={handleRowChange(index, "time")}
            placeholder="Time"
            sx={{ width: "100px" }}
            slotProps={{
              input: {
                type: "number",
                min: 1,
                max: 999,
              },
            }}
            disabled={disabled}
          />
          <StyledTextField
            required
            fullWidth
            value={message}
            onChange={handleRowChange(index, "message")}
            placeholder="Message"
            disabled={disabled}
          />
          {!disabled && (
            <IconButton color="error" onClick={() => handleDeleteRow(index)}>
              <DeleteIcon />
            </IconButton>
          )}
        </Stack>
      ))}
      {!disabled && (
        <Button onClick={handleAddRow} startIcon={<AddIcon />}>
          Add
        </Button>
      )}
    </Box>
  );
}
