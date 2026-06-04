import { useThemedImages } from "@/hooks/useThemedImages";

export const RoleIcon = ({ role, ...props }) => {
  const themedImg = useThemedImages();
  return (
    <img
      src={themedImg.getRoleIconSrc(role)}
      width={16}
      height={16}
      alt={role}
      {...props}
    />
  );
};
