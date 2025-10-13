import { Box } from "@mui/material";
import { getName } from "country-list";

export const CountryFlag = ({ country, ...props }) => {
  const countryName = getName(country);
  return (
    <Box
      component={"img"}
      src={`https://flagcdn.com/w20/${country.toLowerCase()}.png`}
      width={20}
      height={10}
      aria-label={`Flag of ${countryName}`}
      alt={countryName}
      title={countryName}
      {...props}
    />
  );
};
  