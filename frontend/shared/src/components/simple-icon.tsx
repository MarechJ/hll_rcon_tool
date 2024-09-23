import React from 'react';
import type { SimpleIcon } from 'simple-icons';

interface IconProps {
  icon: SimpleIcon;
  size?: number;
  color?: string;
}

const SimpleIcon: React.FC<IconProps> = ({ icon, size = 24, color = 'inherit' }) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
      dangerouslySetInnerHTML={{ __html: icon.svg }}
    />
  );
};

export { SimpleIcon };