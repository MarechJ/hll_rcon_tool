import { useClipboard } from "@/hooks/useClipboard";
import { Paper, Typography, IconButton } from "@mui/material";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import DoneAllIcon from "@mui/icons-material/DoneAll";

const formatJSONOrString = (value) => {
  try {
    return JSON.stringify(JSON.parse(value), null, 2);
  } catch (error) {
    return value;
  }
};

/**
 * @typedef {Object} CodeBlockProps
 * @property {string} text
 * @property {Object} [props]
 */

/**
 * @param {CodeBlockProps} props
 * @returns {JSX.Element}
 */
export const CodeBlock = ({ text, ...props }) => {
  const { isClipboardAvailable, isCopied, copyToClipboard } = useClipboard();
  return (
    <Paper
      sx={{
        position: "relative",
        p: 2,
        backgroundColor: (theme) =>
          theme.palette.mode === "dark" ? "grey.900" : "grey.100",
        color: (theme) =>
          theme.palette.mode === "dark" ? "grey.100" : "grey.900",
        fontFamily: 'Consolas, Monaco, "Courier New", monospace',
        fontSize: "0.875rem",
        overflow: "auto",
        maxWidth: "100%",
        ...props.sx,
      }}
    >
      {isClipboardAvailable && (
        <IconButton
          size="small"
          onClick={() => copyToClipboard(text)}
          sx={{ position: "absolute", top: 5, right: 5 }}
        >
          {isCopied ? (
            <DoneAllIcon color="success" sx={{ fontSize: "1rem" }} />
          ) : (
            <ContentCopyIcon sx={{ fontSize: "1rem" }} />
          )}
        </IconButton>
      )}
      <Typography
        component="pre"
        sx={{
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
          m: 0,
        }}
      >
        {formatJSONOrString(text)}
      </Typography>
    </Paper>
  );
};
