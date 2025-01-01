import { alpha } from '@mui/material/styles';
import { outlinedInputClasses } from '@mui/material/OutlinedInput';
import { svgIconClasses } from '@mui/material/SvgIcon';
import { toggleButtonGroupClasses } from '@mui/material/ToggleButtonGroup';
import { toggleButtonClasses } from '@mui/material/ToggleButton';
import CheckBoxOutlineBlankRoundedIcon from '@mui/icons-material/CheckBoxOutlineBlankRounded';
import CheckRoundedIcon from '@mui/icons-material/CheckRounded';
import RemoveRoundedIcon from '@mui/icons-material/RemoveRounded';
import { gray, brand } from '../themePrimitives';

/* eslint-disable import/prefer-default-export */
export const inputsCustomizations = {
  MuiButtonBase: {
    defaultProps: {
      disableTouchRipple: true,
      disableRipple: true,
    },
    styleOverrides: {
      root: ({ theme }) => ({
        boxSizing: 'border-box',
        transition: 'all 100ms ease-in',
        '&:focus-visible': {
          outline: `3px solid ${alpha(theme.palette.primary.main, 0.5)}`,
          outlineOffset: '2px',
        },
      }),
    },
  },
  MuiButton: {
    styleOverrides: {
      root: ({ theme }) => ({
        boxShadow: 'none',
        borderRadius: theme.shape.borderRadius,
        textTransform: 'none',
        variants: [
          {
            props: {
              color: 'secondary',
              variant: 'contained',
            },
            style: {
              color: 'white',
              backgroundColor: brand[300],
              backgroundImage: `linear-gradient(to bottom, ${alpha(brand[400], 0.8)}, ${brand[500]})`,
              boxShadow: `inset 0 2px 0 ${alpha(brand[200], 0.2)}, inset 0 -2px 0 ${alpha(brand[700], 0.4)}`,
              border: `1px solid ${brand[500]}`,
              '&:hover': {
                backgroundColor: brand[700],
                boxShadow: 'none',
              },
              '&:active': {
                backgroundColor: brand[700],
                backgroundImage: 'none',
              },
            },
          },
          {
            props: {
              variant: 'outlined',
            },
            style: {
              color: theme.palette.text.primary,
              border: '1px solid',
              borderColor: gray[200],
              backgroundColor: alpha(gray[50], 0.3),
              '&:hover': {
                backgroundColor: gray[100],
                borderColor: gray[300],
              },
              '&:active': {
                backgroundColor: gray[200],
              },
              ...theme.applyStyles('dark', {
                backgroundColor: gray[800],
                borderColor: gray[700],
                '&:hover': {
                  backgroundColor: gray[900],
                  borderColor: gray[600],
                },
                '&:active': {
                  backgroundColor: gray[900],
                },
              }),
            },
          },
          {
            props: {
              color: 'secondary',
              variant: 'outlined',
            },
            style: {
              color: brand[700],
              border: '1px solid',
              borderColor: brand[200],
              backgroundColor: brand[50],
              '&:hover': {
                backgroundColor: brand[100],
                borderColor: brand[400],
              },
              '&:active': {
                backgroundColor: alpha(brand[200], 0.7),
              },
              ...theme.applyStyles('dark', {
                color: brand[50],
                border: '1px solid',
                borderColor: brand[900],
                backgroundColor: alpha(brand[900], 0.3),
                '&:hover': {
                  borderColor: brand[700],
                  backgroundColor: alpha(brand[900], 0.6),
                },
                '&:active': {
                  backgroundColor: alpha(brand[900], 0.5),
                },
              }),
            },
          },
          {
            props: {
              variant: 'text',
            },
            style: {
              color: gray[600],
              padding: 0,
              margin: 0,
              minWidth: 'auto',
              fontWeight: theme.typography.fontWeightRegular,
              backgroundColor: 'transparent',
              '&:hover': {
                backgroundColor: 'transparent',
                textDecoration: 'underline',
              },
              '&:active': {
                backgroundColor: 'transparent',
              },
              ...theme.applyStyles('dark', {
                color: gray[50],
                '&:hover': {
                  backgroundColor: 'transparent',
                  textDecoration: 'underline',
                },
                '&:active': {
                  backgroundColor: 'transparent',
                },
              }),
            },
          },
          {
            props: {
              color: 'secondary',
              variant: 'text',
            },
            style: {
              color: brand[700],
              padding: 0,
              margin: 0,
              minWidth: 'auto',
              fontWeight: 400,
              backgroundColor: 'transparent',
              '&:hover': {
                backgroundColor: 'transparent',
                textDecoration: 'underline',
              },
              '&:active': {
                backgroundColor: 'transparent',
              },
              ...theme.applyStyles('dark', {
                color: brand[100],
                '&:hover': {
                  backgroundColor: 'transparent',
                  textDecoration: 'underline',
                },
                '&:active': {
                  backgroundColor: 'transparent',
                },
              }),
            },
          },
        ],
      }),
    },
  },
};
