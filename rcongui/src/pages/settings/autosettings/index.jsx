import Padlock from "@/components/shared/Padlock";
import SplitButton from "@/components/shared/SplitButton";
import {cmd} from "@/utils/fetchUtils";
import {TEMPLATE_CATEGORY} from "@/utils/lib";
import {Alert, Autocomplete, Box, Button, Paper, Skeleton, TextField, useTheme} from "@mui/material";
import {Stack} from "@mui/system";
import {lazy, Suspense, useEffect, useState} from "react";
import {Await, defer, json, useActionData, useLoaderData, useSubmit,} from "react-router-dom";
import {AsyncClientError} from "@/components/shared/AsyncClientError";

const Editor = lazy(() => import("@monaco-editor/react"));

const INTENT = {
  APPLY_SINGLE: "0",
  APPLY_ALL: "1",
  TOGGLE_SERVICE: "2",
};

export const loader = async () => {
  const autosettings = await cmd.GET_AUTOSETTINGS();
  const services = await cmd.GET_SERVICES();
  const templates = cmd.GET_MESSAGE_TEMPLATES({
    params: {category: TEMPLATE_CATEGORY.AUTO_SETTINGS},
  });
  return defer({
    service: services.find((service) => service.name === "auto_settings"),
    autosettings,
    templates,
  });
};

export const action = async ({request}) => {
  const formData = Object.fromEntries(await request.formData());
  const {intent, ...data} = formData;
  let result;

  try {
    switch (intent) {
      case INTENT.APPLY_ALL:
      case INTENT.APPLY_SINGLE:
        result = await cmd.SET_AUTOSETTINGS({payload: data});
        break;
      case INTENT.TOGGLE_SERVICE:
        result = await cmd.TOGGLE_SERVICE({payload: data});
        break;
      default:
        return json(
          {
            error: "InvalidIntent",
          },
          {status: 400}
        );
    }
  } catch (error) {
    return json(
      {
        error: error,
      },
      {status: 400}
    );
  }

  return result;
};

const isRunning = (service) => service.statename === "RUNNING";

const TemplateSkeleton = () => <Skeleton height={80}/>;

const Autosettings = () => {
  const data = useLoaderData();
  const [editorContent, setEditorContent] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const actionData = useActionData();
  const submit = useSubmit();
  const theme = useTheme();

  const handleApplyClick = (intent) => (e) => {
    setSubmitting(true);
    const formData = new FormData();
    formData.append("intent", intent);
    formData.append("forward", intent === INTENT.APPLY_ALL);
    formData.append("settings", editorContent);
    submit(formData, {method: "post"});
  };

  const handleToggleService = (checked) => {
    const formData = new FormData();
    formData.append("intent", INTENT.TOGGLE_SERVICE);
    formData.append("action", checked ? "start" : "stop");
    formData.append("service_name", "auto_settings");
    submit(formData, {method: "post"});
  };

  const handleTemplateChange = (e, message) => {
    setEditorContent(message ? message.content : JSON.stringify(data.autosettings, null, 2));
  };

  useEffect(() => {
    if (!actionData?.error) {
      setEditorContent(JSON.stringify(data.autosettings, null, 2));
    }
  }, [data.autosettings, actionData]);

  useEffect(() => {
    setSubmitting(false);
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
        sx={{p: 1, mb: 1}}
        direction={"row"}
        justifyContent={"space-between"}
        gap={1}
      >
        <Padlock
          label={isRunning(data.service) ? "ON" : "OFF"}
          checked={isRunning(data.service)}
          handleChange={handleToggleService}
        />
        <Stack direction={"row"} gap={1}>
          <Button
            variant="contained"
            color="secondary"
            href="https://github.com/MarechJ/hll_rcon_tool/wiki/User-Guide-%E2%80%90-Main-interface-%E2%80%90-Settings-%E2%80%90-Autosettings"
            component={"a"}
          >
            Read docs
          </Button>
          <SplitButton
            disabled={submitting}
            options={[
              {
                name: submitting ? "Submitting..." : "Apply",
                buttonProps: {
                  onClick: handleApplyClick(INTENT.APPLY_SINGLE),
                  disabled: submitting,
                },
              },
              {
                name: submitting ? "Submitting..." : "Apply all servers",
                buttonProps: {
                  onClick: handleApplyClick(INTENT.APPLY_ALL),
                  disabled: submitting,
                },
              },
            ]}
          />
        </Stack>
      </Stack>
      {error && <Alert severity="error">{error}</Alert>}
      <Suspense>
        <Editor
          height="70vh"
          defaultLanguage="json"
          value={editorContent}
          defaultValue=""
          theme={theme.palette.mode === "dark" ? "vs-dark" : "vs-light"}
          onChange={(value) => setEditorContent(value)}
        />
      </Suspense>
      <Suspense fallback={<TemplateSkeleton/>}>
        <Await
          resolve={data.templates}
          errorElement={<AsyncClientError title={"Autosettings Templates"}/>}
        >
          {(templates) => {
            return (
              <Autocomplete
                id="template-select"
                fullWidth
                options={templates}
                onChange={handleTemplateChange}
                autoHighlight
                getOptionLabel={(option) => option.title}
                renderOption={(props, option) => {
                  const {key, ...optionProps} = props;
                  return (
                    <Box key={key} component="li" {...optionProps}>
                      #{option.id} {option.title}
                    </Box>
                  );
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Choose a template"
                    slotProps={{
                      htmlInput: {
                        ...params.inputProps,
                      },
                    }}
                  />
                )}
              />
            );
          }}
        </Await>
      </Suspense>
    </Stack>
  );
};

export default Autosettings;
