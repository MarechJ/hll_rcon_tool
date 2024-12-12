import TextField from "@mui/material/TextField";
import "react-toastify/dist/ReactToastify.css";
import TextHistory from "../textHistory";
import Autocomplete from '@mui/material/Autocomplete';
import FormControlLabel from "@mui/material/FormControlLabel";
import Checkbox from "@mui/material/Checkbox";

import { getSharedMessages } from "@/utils/fetchUtils";
import {Fragment, useEffect, useState} from "react";

const Reason = ({
  handleMessageChange,
  helperText = "Leave blank if you want a confirmation popup",
  message,
  label = "In Game Message/Punish/Kick/Ban message",
  textHistory,
  saveMessage,
  setSaveMessage,
}) => {
  const autoCompletehistory = textHistory
    ? textHistory.getTexts()
    : new TextHistory("punishments").getTexts();

  const [sharedMessages, setSharedMessages] = useState([]);
  useEffect(() => {
    getSharedMessages("punishments").then((data) => setSharedMessages(data));
  }, []);

  return (
    (<Fragment>
      <Autocomplete
        freeSolo
        fullWidth
        options={sharedMessages.concat(autoCompletehistory)}
        inputValue={message}
        onInputChange={(e, value) => {
          if (e) {
            e.preventDefault();
          }
          handleMessageChange(value);
        }}
        renderInput={(params) => (
          <TextField
            {...params}
            label={label}
            multiline
            minRows={1}
            maxRows={10}
            margin="dense"
            helperText={helperText}
          />
        )}
      />
      {saveMessage !== undefined ? (
        <FormControlLabel
          control={
            <Checkbox
              checked={saveMessage}
              onChange={() => setSaveMessage(!saveMessage)}
              color="primary"
            />
          }
          label="Save message as template"
        />
      ) : (
        ""
      )}
    </Fragment>)
  );
};

export { Reason };
