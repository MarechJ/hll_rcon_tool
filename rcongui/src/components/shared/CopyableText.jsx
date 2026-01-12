import { Stack, IconButton, Tooltip } from "@mui/material";
import React, { useState, useEffect } from "react";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import DoneAllIcon from "@mui/icons-material/DoneAll";

export default function CopyableText({
  text,
  label,
  size = "1em",
  position = "end",
  ...props
}) {
  const [isClipboardAvailable, setIsClipboardAvailable] = useState(false);
  const [isCopied, setIsCopied] = useState(false);

  useEffect(() => {
    // Check if the Clipboard API is available
    setIsClipboardAvailable(
      navigator?.clipboard !== undefined &&
        typeof navigator?.clipboard?.writeText === "function"
    );
  }, []);

  useEffect(() => {
    if (isCopied) {
      setTimeout(() => {
        setIsCopied(false);
      }, 2000);
    }
  }, [isCopied]);

  const handleCopy = (e) => {
    e.stopPropagation();
    navigator.clipboard.writeText(text);
    setIsCopied(true);
  };

  const icon = isClipboardAvailable ? (
    <Tooltip title={isCopied ? "Copied!" : "Copy"}>
      <IconButton
        onClick={handleCopy}
        className="copyable-text-icon-button"
        size="small"
        disableRipple
      >
        {isCopied ? (
          <DoneAllIcon sx={{ width: "0.5em", color: "success.main" }} />
        ) : (
          <ContentCopyIcon sx={{ width: "0.5em" }} />
        )}
      </IconButton>
    </Tooltip>
  ) : null;

  return (
    <Stack
      direction="row"
      alignItems="center"
      component={"span"}
      gap={"0.25em"}
      sx={{
        ...props.sx,
        fontSize: size,
        "& .copyable-text-icon-button": {
          width: size,
          height: size,
          color: "text.secondary",
          visibility: "hidden",
        },
        "&:hover .copyable-text-icon-button": {
          visibility: "visible",
        },
      }}
    >
      {position === "start" && icon}
      {label || text}
      {position === "end" && icon}
    </Stack>
  );
}
