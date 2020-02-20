import React from "react";
import { Grid, TextField, Slider, Typography } from "@material-ui/core";

const NumSlider = ({
  classes,
  text,
  min = 0,
  max,
  value,
  step = 1,
  setValue
}) => (
  <div className={classes.slider}>
    {/*  <TextField
    fullWidth
    type="number"
    label="Autobalance threshold"
    helperText="The maximum difference in number of players between the two teams"
  /> */}
    <Typography id="discrete-slider-always" color="textSecondary" gutterBottom>
      {text}
    </Typography>
    <Slider
      value={value}
      onChange={(e, newVal) => setValue(newVal)}
      aria-labelledby="discrete-slider-always"
      step={step}
      marks
      min={min}
      max={max}
      valueLabelDisplay="auto"
    />
  </div>
);

class HLLSettings extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      autoBalanceThres: 3,
      teamSwitchCooldownMin: 15,
      idleAutokickMin: 5,
      maxPingMs: 500,
      queueLength: 5,
      vipSlots: 2
    };
  }

  render() {
    const {
      autoBalanceThres,
      teamSwitchCooldownMin,
      idleAutokickMin,
      maxPingMs,
      queueLength,
      vipSlots
    } = this.state;
    const { classes } = this.props;

    return (
      <Grid container spacing={3} className={classes.paper}>
        <Grid item className={classes.paper} xs={12}>
          <TextField
            fullWidth
            label="Server name"
            helperText="The server name as displayed in the server browser"
          />
        </Grid>
        <Grid item className={classes.paper} xs={12} md={6} lg={4} xl={3}>
          <NumSlider
            classes={classes}
            text="Teamswitch cooldown (minutes)"
            max={90}
            value={teamSwitchCooldownMin}
            setValue={val => this.setState({ teamSwitchCooldownMin: val })}
          />
        </Grid>
        <Grid item className={classes.paper} xs={12} md={6} lg={4} xl={3}>
          <NumSlider
            classes={classes}
            text="Autobalance threshold"
            max={50}
            value={autoBalanceThres}
            setValue={val => this.setState({ autoBalanceThres: val })}
          />
        </Grid>
        <Grid item className={classes.paper} xs={12} md={6} lg={4} xl={3}>
          <NumSlider
            classes={classes}
            text="Idle autokick (minutes)"
            max={100}
            step={5}
            value={idleAutokickMin}
            setValue={val => this.setState({ idleAutokickMin: val })}
          />
        </Grid>
        <Grid item className={classes.paper} xs={12} md={6} lg={4} xl={3}>
          <NumSlider
            classes={classes}
            text="Maximum ping (ms)"
            max={2000}
            min={10}
            step={10}
            value={maxPingMs}
            setValue={val => this.setState({ maxPingMs: val })}
          />
        </Grid>
        <Grid item className={classes.paper} xs={12} md={6} lg={4} xl={3}>
          <NumSlider
            classes={classes}
            text="Max queue length"
            max={5}
            min={1}
            value={queueLength}
            setValue={val => this.setState({ queueLength: val })}
          />
        </Grid>
        <Grid item className={classes.paper} xs={12} md={6} lg={4} xl={3}>
          <NumSlider
            classes={classes}
            text="Vip slots"
            max={100}
            value={vipSlots}
            setValue={val => this.setState({ vipSlots: val })}
          />
        </Grid>
      </Grid>
    );
  }
}

export default HLLSettings;
