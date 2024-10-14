import {
  Form,
  isRouteErrorResponse,
  json,
  Link,
  useActionData,
  useLoaderData,
  useLocation,
  useRevalidator,
  useRouteError,
  useSubmit,
} from "react-router-dom";
import { useEffect, useState } from "react";
import { execute, get, handleHttpError } from "@/utils/fetchUtils";
import Editor from "@monaco-editor/react";
import { Box, Button, Stack, Typography, useTheme } from "@mui/material";
import { a11yDark, a11yLight, CopyBlock } from "react-code-blocks";
import { toast } from "react-toastify";
import { red } from "@mui/material/colors";
import { JsonForms } from "@jsonforms/react";
import {
  materialCells,
  materialRenderers,
} from "@jsonforms/material-renderers";
import { Generate } from "@jsonforms/core";
import ButtonGroup from "@mui/material/ButtonGroup";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import { customRenderers } from "@/pages/admin/settings/[configs]/renderer";

export const loader = async ({ params }) => {
  const { category, type } = params;
  let note, data, details, configTypes, schema;

  // Dynamically load JSON based on route parameters
  try {
    const configMappingModule = await import("../_data/mappings");

    if (!configMappingModule[category]) throw new Error();

    configTypes = configMappingModule[category];

    details = configTypes.find(
      (configType) => type === configType.path.split("/").slice(-1)[0]
    );

    if (!details) throw new Error();
  } catch (error) {
    throw json(
      {
        message: "This config is not known.",
        error: error?.message,
        command: error?.command,
      },
      { status: 404 }
    );
  }

  try {
    note = await import(`../_data/${category}/${type}.js`);
  } catch (error) {
    throw json(
      {
        message: "Unable to locate the documentation file.",
        error: error?.message,
        command: error?.command,
      },
      { status: 404 }
    );
  }

  let response;
  try {
    response = await get(`get_${details.command}`);
  } catch (error) {
    handleHttpError(error);
  }

  data = await response.json();
  if (!data || data.failed)
    throw new Response("Could not load config data", { status: 400 });

  try {
    response = await get(`describe_${details.command}`);
    schema = await response.json();
    if (!schema || schema.failed) throw new Error();
  } catch (error) {
    throw new Response("Could not load schema data", { status: 400 });
  }

  return {
    note: note.default, // .default is needed because dynamic imports return an ES module object
    data: data.result,
    schema: schema.result,
    ...details,
  };
};

export const action = async ({ request }) => {
  let formData = await request.formData();
  let name = formData.get("name");
  let config = formData.get("config");
  let error = null;
  let response;

  if (!(name && config)) return { ok: false, error: "Missing parameters" };

  config = JSON.parse(config);

  try {
    response = await execute(`validate_${name}`, {
      errors_as_json: true,
      ...config,
    });
  } catch (error) {
    handleHttpError(error);
  }

  const data = await response.json();

  if (!data || data.failed) {
    throw json(
      {
        message: "Server failed to validate config data.",
        error: data?.error,
        command: data?.command,
      },
      { status: 400 }
    );
  }

  error = data.error;

  if (error) {
    return { ok: false, error };
  }

  response = await execute(`set_${name}`, config);

  return { ok: true };
};

const ConfigPage = () => {
  const { note, command, name, data, schema } = useLoaderData();
  const [validationErrors, setValidationErrors] = useState(null);
  const [jsonData, setJsonData] = useState(data);
  const [editorContent, setEditorContent] = useState("");
  const [mode, setMode] = useState("visual");
  const revalidator = useRevalidator();
  const actionData = useActionData();
  const submit = useSubmit();
  const theme = useTheme();

  useEffect(() => {
    setEditorContent(JSON.stringify(data, null, 2));
    setJsonData(data);
  }, [data]);

  useEffect(() => {
    if (actionData && actionData.ok === false) {
      setValidationErrors(actionData.error);
      toast.error(name + " config saving failed!");
    } else if (actionData && actionData.ok) {
      setValidationErrors(null);
      toast.success(name + " config saved!");
    }
  }, [actionData]);

  useEffect(() => {
    setValidationErrors(null);
  }, [command]);

  const handleSubmit = (e) => {
    const formData = new FormData();
    formData.append("config", editorContent);
    formData.append("name", command);
    submit(formData, { method: "post" });
    e.preventDefault();
  };

  const handleRefresh = () => {
    revalidator.revalidate();
    setValidationErrors(null);
  };

  function updateMode(mode) {
    if (mode === "visual") {
      try {
        setJsonData(JSON.parse(editorContent));
      } catch (e) {
        setValidationErrors("Invalid JSON: " + e);
      }
    } else if (jsonData) {
      setEditorContent(JSON.stringify(jsonData, null, 2));
    }
    setMode(mode);
  }

  const visualTheme = createTheme({
    ...theme,
    components: {
      ...theme.components,
      ...{
        MuiFormControl: {
          ...theme.components.MuiFormControl,
          styleOverrides: {
            root: {
              marginTop: "14px",
            },
          },
        },
      },
    },
  });

  return (
    <Stack direction={"column"} spacing={4}>
      <Form method="post" onSubmit={handleSubmit}>
        <Stack direction={"row"} justifyContent={"space-between"}>
          <Typography variant="h3">{name}</Typography>
          <ButtonGroup variant="outlined">
            <Button
              variant={mode === "visual" ? "contained" : "outlined"}
              onClick={() => updateMode("visual")}
            >
              Visual
            </Button>
            <Button
              variant={mode === "code" ? "contained" : "outlined"}
              onClick={() => updateMode("code")}
            >
              Code
            </Button>
          </ButtonGroup>
        </Stack>
        <Stack spacing={2} direction={"column"}>
          {validationErrors && (
            <Box sx={{ mb: 2 }}>
              <CopyBlock
                wrapLongLines
                text={JSON.stringify(validationErrors, null, 2)}
                language="json"
                theme={theme.palette.mode === "dark" ? a11yDark : a11yLight}
                customStyle={{ border: `2px solid ${red["600"]}` }}
              />
            </Box>
          )}
          {mode === "visual" ? (
            <ThemeProvider theme={visualTheme}>
              <JsonForms
                data={jsonData}
                onChange={({ data }) => {
                  setEditorContent(JSON.stringify(data, null, 2));
                  setJsonData(data);
                }}
                schema={schema}
                uischema={Generate.uiSchema(schema)}
                renderers={[...customRenderers, ...materialRenderers]}
                cells={materialCells}
              />
            </ThemeProvider>
          ) : (
            <Editor
              height="70vh"
              defaultLanguage="json"
              value={editorContent}
              defaultValue=""
              theme={theme.palette.mode === "dark" ? "vs-dark" : "vs-light"}
              onChange={(value) => setEditorContent(value)}
            />
          )}
          <Stack direction={"row"} spacing={1}>
            <Button variant={"outlined"} onClick={handleRefresh}>
              Refresh
            </Button>
            <Button variant={"contained"} type="submit">
              Submit
            </Button>
          </Stack>
        </Stack>
      </Form>
      {mode === "code" ? (
        <>
          <Typography variant="h4">Documentation</Typography>
          <CopyBlock
            wrapLongLines
            text={note}
            language="json"
            wrapLines
            theme={theme.palette.mode === "dark" ? a11yDark : a11yLight}
          />
          <Typography variant="h4">Model Schema</Typography>
          <CopyBlock
            wrapLongLines
            text={JSON.stringify(schema, null, 2)}
            language="json"
            wrapLines
            theme={theme.palette.mode === "dark" ? a11yDark : a11yLight}
          />
        </>
      ) : (
        <></>
      )}
    </Stack>
  );
};

export function ErrorElement() {
  const error = useRouteError();
  const location = useLocation();

  if (
    isRouteErrorResponse(error) &&
    error.status >= 400 &&
    error.status < 500
  ) {
    // the response json is automatically parsed to
    // `error.data`, you also have access to the status
    return (
      <Stack spacing={2} alignItems={"center"} justifyContent={"center"}>
        <Typography variant="h3">{error.status}</Typography>
        <Typography variant="h4">{error.data.command}</Typography>
        <Typography>{error.data.message}</Typography>
        <Typography>{error.data.error}</Typography>
        <Button variant="contained" LinkComponent={Link} to={location.pathname}>
          Try again!
        </Button>
      </Stack>
    );
  }

  // rethrow to let the parent error boundary handle it
  // when it's not a special case for this route
  throw error;
}

export default ConfigPage;
