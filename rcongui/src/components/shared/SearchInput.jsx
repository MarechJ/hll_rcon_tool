import { InputBase, Box, styled } from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";

const SearchWrapper = styled(Box)({
  display: "flex",
  alignItems: "center",
  justifyContent: "start",
  width: "100%",
});

export function SearchInput({ ...props }) {
  return (
    <SearchWrapper>
      <Box sx={{ p: "10px", display: "grid", alignItems: "center" }}>
        <SearchIcon />
      </Box>
      <InputBase
        sx={{ ml: 1 }}
        placeholder={props.placeholder ?? "Search"}
        inputProps={{
          "aria-label": props.placeholder?.toLowerCase() ?? "search",
        }}
        {...props}
      />
    </SearchWrapper>
  );
}
