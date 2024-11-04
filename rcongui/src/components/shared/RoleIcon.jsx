export const RoleIcon = ({ role, ...props }) => (
    <img
      src={`/icons/roles/${role.toLowerCase()}.png`}
      width={16}
      height={16}
      alt={role}
      {...props}
    />
  );
  