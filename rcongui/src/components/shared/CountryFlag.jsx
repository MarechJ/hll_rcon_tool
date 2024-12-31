import { getName } from "country-list";

export const CountryFlag = ({ country }) => {
  const countryName = getName(country);
  return (
    <img
      src={`https://flagcdn.com/w20/${country.toLowerCase()}.png`}
      width={20}
      height={10}
      aria-label={`Flag of ${countryName}`}
      alt={countryName}
      title={countryName}
    />
  );
};
  