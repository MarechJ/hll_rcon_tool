import useTheme from "@mui/material/styles/useTheme";

export const RoleIcon = ({ role, ...props }) => {
  const theme = useTheme();
  const mode = theme?.palette?.mode || "light";
  const src =
    mode === "light"
      ? `/icons/roles/${role.toLowerCase()}_black.png`
      : `/icons/roles/${role.toLowerCase()}.png`;
  return (
    <img
      src={src}
      width={16}
      height={16}
      alt={role}
      {...props}
    />
  );
};
