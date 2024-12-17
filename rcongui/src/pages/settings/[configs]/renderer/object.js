import {InputLabel} from "@mui/material";

const objectRenderer = (props) => {
  const name = props.uischema.scope.replace('#/properties/', '');

  return (
    <>
      <InputLabel>{name}</InputLabel>
      The property <code>{name}</code> is not yet supported in the visual editor. To edit it, please use the code editor.
    </>
  );
}

export const renderer = objectRenderer;
