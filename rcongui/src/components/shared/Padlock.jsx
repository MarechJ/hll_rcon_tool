import FormControlLabel from "@mui/material/FormControlLabel";
import Switch from "@mui/material/Switch";

export default function Padlock({ handleChange, checked, label, color, name }) {
  return (
    <FormControlLabel
      control={
        <Switch
          checked={checked}
          onChange={(e) => handleChange(e.target.checked)}
          name={name ?? label}
          color={color ? color : "primary"}
        />
      }
      label={label}
    />
  );
}
