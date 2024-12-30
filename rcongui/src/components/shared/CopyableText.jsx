import { Stack, IconButton, Tooltip } from "@mui/material";
import React, { useState, useEffect } from "react";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import DoneAllIcon from '@mui/icons-material/DoneAll';

export default function CopyableText({ text }) {
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

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setIsCopied(true);
  };

  return (
    <Stack direction="row" alignItems="center" gap={1}>
      {text}
      {isClipboardAvailable && (
        <Tooltip title={isCopied ? "Copied!" : "Copy"}>
          <IconButton
            onClick={handleCopy}
            sx={{
              width: "1rem",
              height: "1rem",
              color: "text.secondary",
              "&:hover": {
                color: "text.primary",
              },
            }}
            size="small"
            disableRipple
          >
            {isCopied ? (
              <DoneAllIcon sx={{ width: "1rem", height: "1rem", color: "success.main" }} />
            ) : (
              <ContentCopyIcon sx={{ width: "1rem", height: "1rem" }} />
            )}
          </IconButton>
        </Tooltip>
      )}
    </Stack>
  );
}
