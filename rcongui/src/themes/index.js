// Easy way to make ugly ass themes:
// https://material.io/resources/color/#!/?view.left=0&view.right=0&primary.color=33691E&secondary.color=3E2723

import _Dark from './dark';
import _Light from './light';
import _GreenYellowLight from './greenYellowDark';
import _GreenYellowDark from './greenYellowDark';
import _PurplePink from './purplePink';
import _Red from './red';
import _YellowGreen from './yellowGreen';
import _HLL from './hll';
import _HLL_No_Background from './hllNoBg';
import _GreyBlueDark from './greyBlueDark';
import _CamoLight from './camoLight';
import _CamoDark from './camoDark';
import { createTheme } from '@mui/material';

const withOtherStyles = (theme) => createTheme(theme, {
  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 900,
      lg: 1200,
      xl: 1920,
    },
  },
  typography: {
    h1: {
      fontSize: "3rem",
      fontWeight: 700,
    },
    h2: {
      fontSize: "2.25rem",
      fontWeight: 600,
    },
    h3: {
      fontSize: "1.75rem",
      fontWeight: 400,
    }
  },
  components: {
    MuiButton: {
      variants:  [
        {
          props: { variant: 'link' },
          style: {
            paddingLeft: theme.spacing(1),
            paddingRight: theme.spacing(1),
          },
        },
        {
          props: { variant: 'link', color: 'primary' },
          style: {
            color: theme.palette.primary.contrastText,
            "&:hover": {
              background: theme.palette.primary.dark,
            }
          }
        }
      ]
    }
  }
})

export default {
  CamoDark: withOtherStyles(_CamoDark),
  CamoLight: withOtherStyles(_CamoLight),
  Dark: withOtherStyles(_Dark),
  GreyBlueDark: withOtherStyles(_GreyBlueDark),
  GreenYellowDark: withOtherStyles(_GreenYellowDark),
  GreenYellowLight: withOtherStyles(_GreenYellowLight),
  HLL: withOtherStyles(_HLL),
  HLL_No_Background: withOtherStyles(_HLL_No_Background),
  Light: withOtherStyles(_Light),
  PurplePink: withOtherStyles(_PurplePink),
  Red: withOtherStyles(_Red),
  YellowGreen: withOtherStyles(_YellowGreen),
};
