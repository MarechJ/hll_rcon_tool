import Padlock from "@/components/shared/Padlock";
import SplitButton from "@/components/shared/SplitButton";
import { cmd } from "@/utils/fetchUtils";
import { Editor } from "@monaco-editor/react";
import { Alert, Button, Paper, useTheme } from "@mui/material";
import { Stack } from "@mui/system";
import { useEffect, useState } from "react";
import {
  json,
  useActionData,
  useLoaderData,
  useSubmit,
} from "react-router-dom";

const INTENT = {
  APPLY_SINGLE: "0",
  APPLY_ALL: "1",
  TOGGLE_SERVICE: "2",
};

export const loader = async () => {
  const autosettings = await cmd.GET_AUTOSETTINGS();
  const services = await cmd.GET_SERVICES();
  return {
    service: services.find((service) => service.name === "auto_settings"),
    autosettings,
  };
};

export const action = async ({ request }) => {
  const formData = Object.fromEntries(await request.formData());
  const { intent, ...data } = formData;
  let result;

  try {
    switch (intent) {
      case INTENT.APPLY_ALL:
      case INTENT.APPLY_SINGLE:
        result = await cmd.SET_AUTOSETTINGS({ payload: data });
        break;
      case INTENT.TOGGLE_SERVICE:
        result = await cmd.TOGGLE_SERVICE({ payload: data });
        break;
      default:
        return json(
          {
            error: "InvalidIntent",
          },
          { status: 400 }
        );
    }
  } catch (error) {
    return json(
      {
        error: error,
      },
      { status: 400 }
    );
  }

  return result;
};

const isRunning = (service) => service.statename === "RUNNING";

const Autosettings = () => {
  const { service, autosettings } = useLoaderData();
  const [editorContent, setEditorContent] = useState("");
  const [error, setError] = useState(null);
  const actionData = useActionData();
  const submit = useSubmit();
  const theme = useTheme();

  const handleApplyClick = (intent) => (e) => {
    const formData = new FormData();
    formData.append("intent", intent);
    formData.append("forward", intent === INTENT.APPLY_ALL);
    formData.append("settings", editorContent);
    submit(formData, { method: "post" });
  };

  const handleToggleService = (checked) => {
    const formData = new FormData();
    formData.append("intent", INTENT.TOGGLE_SERVICE);
    formData.append("action", checked ? "start" : "stop");
    formData.append("service_name", "auto_settings");
    submit(formData, { method: "post" });
  };

  useEffect(() => {
    if (!actionData?.error) {
      setEditorContent(JSON.stringify(autosettings, null, 2));
    }
  }, [autosettings, actionData]);

  useEffect(() => {
    if (actionData) {
      if (actionData.error) {
        setError(actionData.error.text);
      } else {
        setError(null);
      }
    }
  }, [actionData]);

  return (
    <Stack gap={2}>
      <Stack
        component={Paper}
        sx={{ p: 1, mb: 1 }}
        direction={"row"}
        justifyContent={"space-between"}
        gap={1}
      >
        <Padlock
          label={isRunning(service) ? "ON" : "OFF"}
          checked={isRunning(service)}
          handleChange={handleToggleService}
        />
        <Stack direction={"row"} gap={1}>
          <Button
            variant="contained"
            color="secondary"
            href="https://github.com/MarechJ/hll_rcon_tool/wiki/User-Guide-:-Autosettings"
            component={"a"}
          >
            Read docs
          </Button>
          <SplitButton
            options={[
              {
                name: "Apply",
                buttonProps: {
                  onClick: handleApplyClick(INTENT.APPLY_SINGLE),
                },
              },
              {
                name: "Apply all servers",
                buttonProps: {
                  onClick: handleApplyClick(INTENT.APPLY_ALL),
                },
              },
            ]}
          />
        </Stack>
      </Stack>
      {error && <Alert severity="error">{error}</Alert>}
      <Editor
        height="70vh"
        defaultLanguage="json"
        value={editorContent}
        defaultValue=""
        theme={theme.palette.mode === "dark" ? "vs-dark" : "vs-light"}
        onChange={(value) => setEditorContent(value)}
      />
    </Stack>
  );
};

export default Autosettings;
