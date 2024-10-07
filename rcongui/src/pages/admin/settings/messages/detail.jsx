import React, { useEffect, useMemo, useState } from "react";
import Box from "@mui/material/Box";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import {
  Form,
  json,
  Link,
  Outlet,
  useActionData,
  useLoaderData,
  useNavigate,
} from "react-router-dom";
import {
  Avatar,
  Button,
  Divider,
  IconButton,
  InputBase,
  List,
  ListItem,
  ListItemAvatar,
  ListItemButton,
  ListItemText,
  ListSubheader,
  MenuItem,
  Paper,
  Select,
  selectClasses,
  Stack,
  styled,
  TextField,
} from "@mui/material";
import DevicesRoundedIcon from "@mui/icons-material/DevicesRounded";
import AddCircleIcon from "@mui/icons-material/AddCircle";
import { cmd, execute, get, handleHttpError } from "@/utils/fetchUtils";
import { CustomizedDividers, StyledToggleButtonGroup } from "../../views/live";
import SearchIcon from "@mui/icons-material/Search";
import AddIcon from "@mui/icons-material/Add";
import CancelIcon from "@mui/icons-material/Cancel";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import SaveIcon from "@mui/icons-material/Save";
import SaveAsIcon from "@mui/icons-material/SaveAs";
import dayjs from "dayjs";
import debounce from "lodash/debounce";

const MODE = {
  READ: 0,
  EDIT: 1,
  CREATE: 2,
};

const INTENT = {
  CREATE: "create",
  UPDATE: "update",
  DELETE: "delete",
};

const initialState = {
  mode: MODE.READ,
  id: 0,
  title: "",
  content: "",
};

export const loader = async ({ params }) => {
  const { type: category } = params;
  const response = await get(`get_message_templates?category=${category}`);
  handleHttpError(response);
  try {
    const data = await response.json();
    const messages = data.result;
    messages.reverse(); // sort desc by updated_by
    return {
      category,
      messages,
    };
  } catch (error) {
    return {
      category,
      messages: [],
    };
  }
};

export const action = async ({ request }) => {
  const formData = Object.fromEntries(await request.formData());
  const { intent, category, ...message } = formData;

  const title = message.title;
  const content = message.content;
  const id = message.id;

  const hasTitle = !!title?.trim()?.length;
  const hasContent = !!content?.trim()?.length;

  const handleResponse = async (response) => {
    handleHttpError(response);
    if (!response || !response.ok) {
      throw json(
        {
          message: "Something went wrong",
          error: "Form error",
          command: intent,
        },
        { status: 400 }
      );
    }
    const cmdResult = await response.json();
    if (!cmdResult || cmdResult.failed) {
      {
        throw json(
          {
            message: "Action failed",
            error: cmdResult?.error,
            command: cmdResult?.command,
          },
          { status: 400 }
        );
      }
    }
    return { result: cmdResult.result, arguments: cmdResult.arguments };
  };

  let response, data;

  switch (intent) {
    case INTENT.CREATE:
      if (!hasTitle || !hasContent) {
        throw json(
          {
            message: "Missing title or content message attributes.",
            error: "Form error",
            command: intent,
          },
          { status: 400 }
        );
      }
      response = await execute(cmd.ADD_MESSAGE_TEMPLATE, {
        title,
        content,
        category,
      });
      data = await handleResponse(response);
      return json({ intent, message: { ...data.arguments, id: data.result } });

    case INTENT.UPDATE:
      if (!hasTitle || !hasContent || !id) {
        throw json(
          {
            message: "Missing title, content or id message attributes.",
            error: "Form error",
            command: intent,
          },
          { status: 400 }
        );
      }
      response = await execute(cmd.EDIT_MESSAGE_TEMPLATE, {
        id,
        title,
        content,
        category,
      });
      data = await handleResponse(response);
      return json({ intent, message: data.arguments });

    case INTENT.DELETE:
      if (!id) {
        throw json(
          {
            message: "Missing id message attributes.",
            error: "Form error",
            command: intent,
          },
          { status: 400 }
        );
      }
      response = await execute(cmd.DELETE_MESSAGE_TEMPLATE, { id });
      data = await handleResponse(response);
      return json({ intent, message: data.arguments });

    default:
      throw new Error("Invalid intent");
  }
};

const SearchWrapper = styled(Box)({
  display: "flex",
  alignItems: "center",
  justifyContent: "start",
  width: "100%",
});

const StyledTextField = styled(TextField)((theme) => ({
  "& .MuiOutlinedInput-root, & .MuiOutlinedInput-notchedOutline": {
    borderRadius: 0,
  },
}));

const unpackBroadcastMessage = (message) =>
  message.length
    ? message.split("\n").map((line) => {
        const regex = /(\d+)\s+(.*)/;
        const match = line.match(regex);
        if (!match) return { time: "", message: "" };
        const [_, time, content] = match;
        return { time, message: content };
      })
    : [];

const parseBroadcastMessages = (messages) =>
  messages.reduce((acc, msg, index, arr) => {
    let str = acc + `${msg.time} ${msg.message}`;
    str += index !== arr.length - 1 ? "\n" : "";
    return str;
  }, "");

function EditorActions({ editor, actions }) {
  const canBeSaved = editor.title.trim() && editor.content.trim();

  return (
    <Paper
      elevation={0}
      sx={(theme) => ({
        display: "flex",
        flexWrap: "wrap",
        padding: theme.spacing(1),
        borderRadius: 0,
      })}
    >
      <Box sx={{ flexGrow: 1 }} />
      {editor.mode === MODE.READ && editor.id !== 0 && (
        <Button onClick={actions.update} startIcon={<EditIcon />}>
          Edit
        </Button>
      )}
      {editor.mode === MODE.CREATE && (
        <>
          <Button onClick={actions.cancelCreate} startIcon={<CancelIcon />}>
            Cancel
          </Button>
          <Button
            type="submit"
            name="intent"
            value={INTENT.CREATE}
            startIcon={<SaveIcon />}
            disabled={!canBeSaved}
          >
            Save
          </Button>
        </>
      )}
      {editor.mode === MODE.EDIT && (
        <>
          <Button onClick={actions.cancelEdit} startIcon={<CancelIcon />}>
            Cancel
          </Button>
          <Button
            type="submit"
            name="intent"
            value={INTENT.UPDATE}
            startIcon={<SaveIcon />}
            disabled={!canBeSaved}
          >
            Save
          </Button>
          <Button
            type="submit"
            name="intent"
            value={INTENT.CREATE}
            startIcon={<SaveAsIcon />}
            disabled={!canBeSaved}
          >
            Save As New
          </Button>
        </>
      )}
      {editor.mode !== MODE.CREATE && editor.id !== 0 && (
        <>
          <Button
            color="warning"
            type="submit"
            name="intent"
            value={INTENT.DELETE}
            startIcon={<DeleteIcon />}
          >
            Delete
          </Button>
        </>
      )}
      {editor.mode === MODE.READ && (
        <>
          <Button onClick={actions.create} startIcon={<AddIcon />}>
            Create New
          </Button>
        </>
      )}
    </Paper>
  );
}

function BroadcastFields({ editor, onChange }) {
  const rows = unpackBroadcastMessage(editor.content);

  const handleAddRow = () => {
    onChange({
      content: parseBroadcastMessages([...rows, { time: "", message: "" }]),
    });
  };

  const handleDeleteRow = (index) => {
    onChange({
      content: parseBroadcastMessages(
        rows.slice(0, index).concat(rows.slice(index + 1))
      ),
    });
  };

  const handleRowChange = (lineIndex, key) => (event) => {
    onChange({
      content: parseBroadcastMessages(
        rows.map((line, i) =>
          lineIndex === i ? { ...line, [key]: event.target.value } : line
        )
      ),
    });
  };

  return (
    <>
      <textarea
        name="content"
        value={editor.content}
        disabled={editor.mode === MODE.READ}
        required
        readOnly
        hidden
      />
      {rows.map(({ time, message }, index) => (
        <Stack key={"line" + index} direction={"row"}>
          <StyledTextField
            required
            value={time}
            onChange={handleRowChange(index, "time")}
            placeholder="Time"
            sx={{ width: "100px" }}
            slotProps={{
              input: {
                type: "number",
                min: 1,
                max: 999,
              },
            }}
            disabled={editor.mode === MODE.READ}
          />
          <StyledTextField
            required
            fullWidth
            value={message}
            onChange={handleRowChange(index, "message")}
            placeholder="Message"
            disabled={editor.mode === MODE.READ}
          />
          {editor.mode !== MODE.READ && (
            <IconButton color="error" onClick={() => handleDeleteRow(index)}>
              <DeleteIcon />
            </IconButton>
          )}
        </Stack>
      ))}
      {editor.mode !== MODE.READ && (
        <Button onClick={handleAddRow} startIcon={<AddIcon />}>
          Add
        </Button>
      )}
    </>
  );
}

function EditorFields({ editor, category, onChange, onInputChange }) {
  return (
    <>
      <input name="id" value={editor.id} hidden readOnly />
      <input name="category" value={category} hidden readOnly />
      <StyledTextField
        name="title"
        value={editor.title}
        onChange={onInputChange}
        placeholder="Message title"
        fullWidth
        required
        disabled={editor.mode === MODE.READ}
      />
      {category === "broadcast" ? (
        <BroadcastFields editor={editor} onChange={onChange} />
      ) : (
        <StyledTextField
          name="content"
          value={editor.content}
          onChange={onInputChange}
          placeholder="Message content"
          multiline
          minRows={16}
          fullWidth
          required
          disabled={editor.mode === MODE.READ}
        />
      )}
    </>
  );
}

function MessageList({ messages, onMessageClick, selected }) {
  return (
    <Paper
      sx={{
        borderRadius: 0,
        minHeight: "300px",
        maxHeight: "calc(100vh - 256px)",
        overflowY: "auto",
        scrollbarWidth: "thin",
        scrollbarGutter: "auto",
      }}
    >
      <List>
        {messages.length ? (
          messages.map((message, index) => (
            <ListItem key={message.id} disablePadding>
              <ListItemButton
                onClick={() => onMessageClick(index)}
                selected={selected !== undefined && message.id === selected}
              >
                <ListItemText
                  sx={{
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                  primary={`#${message.id} - ${message.title}`}
                  secondary={`Last update ${dayjs(message.updated_at).format(
                    "LL"
                  )} by ${message.updated_by}`}
                />
              </ListItemButton>
            </ListItem>
          ))
        ) : (
          <ListItem>
            <ListItemText
              sx={{
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
              primary={"No messages"}
            />
          </ListItem>
        )}
      </List>
    </Paper>
  );
}

const MessagesDetailPage = () => {
  const { category, messages } = useLoaderData();
  const action = useActionData();
  const [editor, setEditor] = useState(initialState);
  const [searchValue, setSearchValue] = useState("");

  useEffect(() => {
    if (!action) return;
    switch (action.intent) {
      case INTENT.DELETE:
        setEditor(initialState);
        break;
      case INTENT.CREATE:
      case INTENT.UPDATE:
        let msg = messages.find((msg) => Number(msg.id) === Number(action.message.id));
        if (msg) {
          setEditor({
            mode: MODE.READ,
            ...msg,
          });
        } else {
          setEditor(initialState);
        }
        break;

      default:
        break;
    }
  }, [action, messages]);

  useEffect(() => {
    setEditor(initialState);
  }, [category]);

  const handleOnInputChange = (event) => {
    const key = event.target.name;
    setEditor((prev) => ({
      ...prev,
      [key]: event.target.value,
    }));
  };

  const handleOnChange = (obj) => {
    setEditor((prev) => ({
      ...prev,
      ...obj,
    }));
  };

  const handleMessageClick = (index) => {
    const message = messages[index];
    if (!message) return;
    setEditor({
      mode: MODE.READ,
      id: message.id,
      title: message.title,
      content: message.content,
    });
  };

  const handleCreate = () => {
    setEditor({ mode: MODE.CREATE, id: 0, title: "", content: "" });
  };

  const handleCancelCreate = () => {
    setEditor(initialState);
  };

  const handleCancelUpdate = () => {
    setEditor((prev) => {
      return {
        ...(messages.find((msg) => Number(msg.id) === Number(prev.id)) ?? initialState),
        mode: MODE.READ,
      };
    });
  };

  const handleUpdate = () => {
    setEditor((prev) => ({ ...prev, mode: MODE.EDIT }));
  };

  const handleSearchChange = debounce((event) => {
    setSearchValue(event.target.value);
  }, 500);

  const filteredMessages = messages.filter(({ title, id, updated_by }) => {
    return `${id} ${title} ${updated_by}`
      .toLowerCase()
      .includes(searchValue.toLocaleLowerCase());
  });

  return (
    <Stack direction={["column", "row"]}>
      <Stack direction={"column"} sx={{ minWidth: 300, width: 300 }}>
        <Paper
          sx={(theme) => ({
            padding: theme.spacing(0.5),
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            borderRadius: 0,
          })}
        >
          <SearchWrapper>
            <Box sx={{ p: "10px", display: "grid", alignItems: "center" }}>
              <SearchIcon />
            </Box>
            <InputBase
              sx={{ ml: 1 }}
              placeholder="Search message"
              inputProps={{ "aria-label": "search message" }}
              onChange={handleSearchChange}
            />
          </SearchWrapper>
        </Paper>
        <MessageList
          selected={editor.id}
          messages={filteredMessages}
          onMessageClick={handleMessageClick}
        />
      </Stack>
      <Box component={Form} method="POST" sx={{ flexGrow: 1, width: "100%" }}>
        <EditorActions
          editor={editor}
          actions={{
            create: handleCreate,
            update: handleUpdate,
            cancelCreate: handleCancelCreate,
            cancelEdit: handleCancelUpdate,
          }}
        />
        <EditorFields
          editor={editor}
          category={category}
          onInputChange={handleOnInputChange}
          onChange={handleOnChange}
        />
      </Box>
    </Stack>
  );
};

export default MessagesDetailPage;
