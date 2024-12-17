import { Button, IconButton, Input, Stack, styled } from "@mui/material";
import { useState } from "react";
import { Link } from "react-router-dom";
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
  <IconButton size="small" component={Link} {...props}>
    <MoreHorizIcon />
  </IconButton>
))({
  width: 20,
  height: 20,
  borderRadius: 0,
  p: 2,
});

export default function NavPagination({ page, maxPages, ...props }) {
  const [insertCustom, setInsertCustom] = useState(false);
  const [customPageValue, setCustomPageValue] = useState(page);

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

  return (
    <Stack
      direction={"row"}
      justifyContent={"end"}
      alignItems={"center"}
      gap={0.5}
      flexGrow={1}
      sx={{ px: 2 }}
      {...props}
    >
      {page > 1 && <PaginationPrevious to={`?page=${page - 1}`} />}
      <PaginationItem
        variant={page === 1 ? "contained" : "outlined"}
        to={`?page=${1}`}
      >
        1
      </PaginationItem>
      {page === 1 && 2 < maxPages && (
        <PaginationItem
          variant={page === 2 ? "contained" : "outlined"}
          to={`?page=${2}`}
        >
          2
        </PaginationItem>
      )}
      {page > 1 && page < maxPages && (
        <PaginationItem
          variant={page === page ? "contained" : "outlined"}
          to={`?page=${page}`}
        >
          {page}
        </PaginationItem>
      )}
      {page !== maxPages - 1 && page !== maxPages && (
        <div>
          {!insertCustom ? (
            <Button size={"small"} onClick={() => setInsertCustom(true)}>
              <PaginationEllipsis />
            </Button>
          ) : (
            <Stack direction={"row"} gap={0.5} alignItems={"center"}>
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
                sx={{ color: green[800], "&:hover": { color: green[600] } }}
              >
                <Link
                  to={`?page=${customPageValue}`}
                  onClick={handleConfirmCustomClick}
                >
                  <CheckIcon size={16} />
                </Link>
              </Button>
            </Stack>
          )}
        </div>
      )}
      <PaginationItem
        variant={page === maxPages ? "contained" : "outlined"}
        to={`?page=${maxPages}`}
      >
        {maxPages}
      </PaginationItem>
      {page < maxPages && <PaginationNext to={`?page=${page + 1}`} />}
    </Stack>
  );
}
