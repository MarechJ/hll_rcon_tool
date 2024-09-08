import React from "react";
import { Slider, Typography } from "@mui/material";

const NumSlider = ({
  text,
  min = 0,
  max,
  value,
  marks = true,
  step = 1,
  setValue,
  saveValue,
  helpText,
  disabled,
  showValue,
}) => (
  <div >
    <Typography variant="h5" id="discrete-slider-always" gutterBottom>
      {text}
    </Typography>
    <Typography variant="caption">
      {helpText}
    </Typography>
    <Slider
      value={value}
      onChange={(e, newVal) => setValue(newVal)}
      onChangeCommitted={(e, newVal) => saveValue(newVal)}
      aria-labelledby="discrete-slider-always"
      step={step}
      marks={marks}
      min={min}
      max={max}
      disabled={disabled}
      valueLabelDisplay={showValue ? "on" : "auto"}
    />
  </div>
);

export default NumSlider;
