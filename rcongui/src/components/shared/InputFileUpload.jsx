import * as React from 'react';
import { styled } from '@mui/material/styles';
import Button from '@mui/material/Button';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

const VisuallyHiddenInput = styled('input')({
  clip: 'rect(0 0 0 0)',
  clipPath: 'inset(50%)',
  height: 1,
  overflow: 'hidden',
  position: 'absolute',
  bottom: 0,
  left: 0,
  whiteSpace: 'nowrap',
  width: 1,
});

export function InputFileUpload({ text, icon, color, variant, ...props }) {
  return (
    <Button
      component="label"
      role={undefined}
      variant={variant ?? "contained"}
      color={color ?? "primary"}
      tabIndex={-1}
      startIcon={icon ?? <CloudUploadIcon />}
    >
      {text ?? "Upload file"}
      <VisuallyHiddenInput
        type="file"
        {...props}
      />
    </Button>
  );
}
