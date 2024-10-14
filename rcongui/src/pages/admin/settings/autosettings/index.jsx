import Padlock from "@/components/shared/Padlock";
import SplitButton from "@/components/shared/SplitButton";
import { UnderConstruction } from "@/components/UnderConstruction";
import { cmd } from "@/utils/fetchUtils";
import { Editor } from "@monaco-editor/react";
import { Box, Button, useTheme } from "@mui/material";
import { Stack } from "@mui/system";
import { useEffect, useState } from "react";
import {
  Form,
  json,
  useActionData,
  useLoaderData,
  useRevalidator,
  useSubmit,
} from "react-router-dom";

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

  switch (intent) {
    case "set_autosettings":
    case "set_autosettings_forward":
      result = await cmd.SET_AUTOSETTINGS({ payload: data });
      break;
    case "toggle_service":
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

  return result;
};

const isRunning = (service) => service.statename === "RUNNING";

const Autosettings = () => {
  const { service, autosettings } = useLoaderData();
  const [editorContent, setEditorContent] = useState("");
  const [validationErrors, setValidationErrors] = useState(null);
  const actionData = useActionData();
  const submit = useSubmit();
  const theme = useTheme();

  const handleApplyClick = (intent) => (e) => {
    const formData = new FormData();
    if (intent === "set_autosettings_forward") {
      formData.append("forward", true);
    }
    formData.append("settings", editorContent);
    console.log(Object.fromEntries(formData));
    submit(formData, { method: "post" });
  };

  const handleToggleService = (checked) => {
    const formData = new FormData();
    formData.append("intent", "toggle_service");
    formData.append("action", checked ? "start" : "stop");
    formData.append("service_name", "auto_settings");
    submit(formData, { method: "post" });
  };

  useEffect(() => {
    setEditorContent(JSON.stringify(autosettings, null, 2));
  }, [autosettings]);

  useEffect(() => {
    if (actionData && actionData.ok === false) {
      setValidationErrors(actionData.error);
      toast.error("Auto-settings saving failed!");
    } else if (actionData && actionData.ok) {
      setValidationErrors(null);
      toast.success("Auto-settings config saved!");
    }
  }, [actionData]);

  return (
    <Stack gap={2}>
      <Stack direction={"row"} justifyContent={"space-between"} gap={1}>
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
                  onClick: handleApplyClick("set_autosettings"),
                },
              },
              {
                name: "Apply all servers",
                buttonProps: {
                  onClick: handleApplyClick("set_autosettings_forward"),
                },
              },
            ]}
          />
        </Stack>
      </Stack>
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
