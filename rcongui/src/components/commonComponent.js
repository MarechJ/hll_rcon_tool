import React from 'react'
import {
    FormControlLabel,
    Checkbox,
  } from "@material-ui/core";
import Chip from "@material-ui/core/Chip";
import Autocomplete from "@material-ui/lab/Autocomplete";
import TextField from "@material-ui/core/TextField";

export const ForwardCheckBox = ({ bool, onChange }) => (
    <FormControlLabel
      control={
        <Checkbox
          checked={bool}
          onChange={(e) => {
            onChange(e.target.checked);
          }}
        />
      }
      label="Forward to all servers"
    />
  );

  export const WordList = ({ words, onWordsChange, label, placeholder, helperText }) => {
    return (
      <Autocomplete
        multiple
        freeSolo
        options={[]}
        onChange={(e, val) => onWordsChange(val)}
        value={words}
        renderTags={(value, getTagProps) =>
          value.map((option, index) => (
            <Chip variant="default" label={option} {...getTagProps({ index })} />
          ))
        }
        renderInput={(params) => (
          <TextField
            {...params}
            label={label}
            placeholder={placeholder}
            helperText={helperText}
          />
        )}
      />
    );
  };

