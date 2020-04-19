import React from 'react';
import FormGroup from '@material-ui/core/FormGroup';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Switch from '@material-ui/core/Switch';

export default function Padlock({handleChange, checked, label}) {

  return (
    <FormGroup row>
      <FormControlLabel
        control={
          <Switch
            checked={checked}
            onChange={e => handleChange(e.target.checked)}
            name={label}
            color="primary"
          />
        }
        label={label}
      />
    </FormGroup>
  );
}