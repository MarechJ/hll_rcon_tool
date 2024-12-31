import { Button, IconButton, Input, Stack, styled } from "@mui/material";
import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import KeyboardArrowRightIcon from "@mui/icons-material/KeyboardArrowRight";
import KeyboardArrowLeftIcon from "@mui/icons-material/KeyboardArrowLeft";
import MoreHorizIcon from "@mui/icons-material/MoreHoriz";
import CheckIcon from "@mui/icons-material/Check";
import { green } from "@mui/material/colors";

const PaginationItem = styled((props) => (
  <Button size="small" component={Link} {...props} />
))({
  width: 20,
  height: 20,
  borderRadius: 0,
});

const PaginationPrevious = styled((props) => (
  <IconButton size="small" component={Link} {...props}>
    <KeyboardArrowLeftIcon />
  </IconButton>
))({
  width: 20,
  height: 20,
  borderRadius: 0,
  p: 2,
});

const PaginationNext = styled((props) => (
  <IconButton size="small" component={Link} {...props}>
    <KeyboardArrowRightIcon />
  </IconButton>
))({
  width: 20,
  height: 20,
  borderRadius: 0,
  p: 2,
});

const PaginationEllipsis = styled((props) => (
  <IconButton {...props}>
    <MoreHorizIcon />
  </IconButton>
))({
  width: 40,
  height: 20,
  borderRadius: 0,
});

export default function NavPagination({ page, maxPages, disabled, ...props }) {
  const [insertCustom, setInsertCustom] = useState(false);
  const [customPageValue, setCustomPageValue] = useState(page);
  const search = useLocation().search;

  const goToPage = (page) => {
    const params = new URLSearchParams(search);
    params.set("page", page);
    return `?${params.toString()}`;
  };

  const handleConfirmCustomClick = () => {
    setInsertCustom(false);
  };

  const handleCustomValueChange = (e) => {
    let pageValue = Number(e.currentTarget.value);

    if (Number.isNaN(pageValue)) {
      pageValue = page;
    }

    setCustomPageValue(
      pageValue < 1 ? 1 : pageValue > maxPages ? maxPages : pageValue
    );
  };

  if (maxPages === 0) return null;

  return (
    <Stack
      direction={"row"}
      alignItems={"center"}
      gap={0.5}      
      {...props}
    >
      {page > 1 && <PaginationPrevious to={goToPage(page - 1)} />}
      <PaginationItem
        variant={page === 1 ? "contained" : "outlined"}
        to={goToPage(1)}
        disabled={disabled}
      >
        1
      </PaginationItem>
      {page === 1 && 2 < maxPages && (
        <PaginationItem
          variant={page === 2 ? "contained" : "outlined"}
          to={goToPage(2)}
          disabled={disabled}
        >
          2
        </PaginationItem>
      )}
      {page > 1 && page < maxPages && (
        <PaginationItem
          variant={page === page ? "contained" : "outlined"}
          to={goToPage(page)}
          disabled={disabled}
        >
          {page}
        </PaginationItem>
      )}
      {page !== maxPages - 1 && page !== maxPages && (
        <div>
          {!insertCustom ? (
              <PaginationEllipsis onClick={() => setInsertCustom(true)} />
          ) : (
            <Stack direction={"row"} gap={0.5} alignItems={"center"} sx={{ px: 2 }}>
              <Input
                placeholder={"..."}
                value={customPageValue}
                onChange={handleCustomValueChange}
                type="number"
                min={1}
                max={maxPages}
                sx={{ width: 50 }}
              />
              <Button
                variant={"outlined"}
                size={"small"}
                sx={{
                  color: green[800],
                  "&:hover": { color: green[600] },
                  width: 20,
                  height: 20,
                  borderRadius: 0,
                }}
                LinkComponent={Link}
                to={goToPage(customPageValue)}
                onClick={handleConfirmCustomClick}
                disabled={disabled}
              >
                <CheckIcon size={16} />
              </Button>
            </Stack>
          )}
        </div>
      )}
      {maxPages > 1 && (
        <PaginationItem
          variant={page === maxPages ? "contained" : "outlined"}
          to={goToPage(maxPages)}
          disabled={disabled}
        >
          {maxPages}
        </PaginationItem>
      )}
      {page < maxPages && (
        <PaginationNext to={goToPage(page + 1)} disabled={disabled} />
      )}
    </Stack>
  );
}
