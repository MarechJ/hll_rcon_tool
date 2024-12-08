import * as React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Slider from '@mui/material/Slider';
import MuiInput from '@mui/material/Input';
import { styled } from '@mui/styles';
import Grid from "@mui/material/Grid2"

const Input = styled(MuiInput)(() => ({
    width: '58px'
}))

export default function SliderWithInputField({
  label,
  value: aValue,
  icon,
  name,
  min,
  max,
  step,
  disabled,
  onChange: handleChange,
}) {
  const [value, setValue] = React.useState(aValue ?? 0);

  const handleSliderChange = (event, newValue) => {
    setValue(newValue);
  };

  const handleInputChange = (event) => {
    setValue(event.target.value === '' ? 0 : Number(event.target.value));
    handleChange(event);
  };

  const handleBlur = () => {
    if (value < min) {
      setValue(min);
    } else if (value > max) {
      setValue(max);
    }
  };

  return (
    <Box>
      <Typography id={`input-slider-${name}`} gutterBottom>
        {label}
      </Typography>
      <Grid container spacing={4} alignItems="center">
        <Grid>{icon}</Grid>
        <Grid xs>
          <Slider
            value={typeof value === 'number' ? value : 0}
            onChange={handleSliderChange}
            aria-labelledby="input-slider"
            step={step}
            min={min}
            max={max}
            disabled={disabled}
            marks={[
              {
                value: min,
                label: min,
              },
              {
                value: Math.floor(max / 2),
                label: Math.floor(max / 2),
              },
              {
                value: max,
                label: max,
              },
            ]}
          />
        </Grid>
        <Grid>
          <Input
            value={value}
            disabled={disabled}
            name={name}
            size="small"
            onChange={handleInputChange}
            onBlur={handleBlur}
            inputProps={{
              step: step,
              min: min,
              max: max,
              type: 'number',
              'aria-labelledby': 'input-slider',
            }}
          />
        </Grid>
      </Grid>
    </Box>
  );
}
