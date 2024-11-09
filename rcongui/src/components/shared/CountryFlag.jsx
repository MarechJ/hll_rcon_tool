export const CountryFlag = ({ country }) => (
    <img
      src={`https://flagcdn.com/w20/${country.toLowerCase()}.png`}
      width={20}
      height={10}
      alt={country}
    />
  );
  