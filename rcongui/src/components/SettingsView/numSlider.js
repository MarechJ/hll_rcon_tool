import React from "react";
import {
    Slider, Typography
} from "@material-ui/core";


const NumSlider = ({
    classes,
    text,
    min = 0,
    max,
    value,
    marks = true,
    step = 1,
    setValue,
    saveValue,
    helpText,
    disabled
  }) => (
      <div className={classes.slider}>
        <Typography variant="h5" id="discrete-slider-always" gutterBottom>
          {text} 
        </Typography>
        <Typography variant="caption" color="textSecondary">{helpText}</Typography>
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
          valueLabelDisplay="auto"
        />
      </div>
    );

export default NumSlider