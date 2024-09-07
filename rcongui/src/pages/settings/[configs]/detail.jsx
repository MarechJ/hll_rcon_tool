import {
  Form,
  isRouteErrorResponse,
  useActionData,
  useLoaderData,
  useRevalidator,
  useRouteError,
  useSubmit,
  json,
  Link,
} from "react-router-dom";
import { useEffect, useState } from "react";
import { get } from "@/utils/fetchUtils";
import Editor from "@monaco-editor/react";
import { Box, Button, Stack, Typography, useTheme } from "@mui/material";
import { CopyBlock, a11yDark, a11yLight } from "react-code-blocks";
import { toast } from "react-toastify";
import { execute } from "../../../utils/fetchUtils";
import { red } from "@mui/material/colors";

export const loader = async ({ params }) => {
  console.log("LOADER RUNNING");
  const { category, type } = params;
  let note, data, details, configTypes, schema;

  // Dynamically load JSON based on route parameters
  try {
    const configMappingModule = await import("../_data/mappings");

    if (!configMappingModule[category]) throw new Error();

    configTypes = configMappingModule[category];

    note = await import(`../_data/${category}/${type}.js`);

    details = configTypes.find(
      (configType) => type === configType.path.split("/").slice(-1)[0]
    );

    if (!details) throw new Error();
  } catch (error) {
    throw new Response("Webhook not found", { status: 404 });
  }

  try {
    const response = await get(`get_${details.command}`);
    data = await response.json();
    if (!data || data.failed) throw new Error();
  } catch (error) {
    throw new Response("Could not load config data", { status: 400 });
  }

  try {
    const response = await get(`describe_${details.command}`);
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
  console.log("ACTION RUNNING");
  let formData = await request.formData();
  let name = formData.get("name");
  let config = formData.get("config");
  let error = null;
  let response;

  if (!(name && config)) return { ok: false, error: "Missing parameters" };

  config = JSON.parse(config);

  response = await execute(`validate_${name}`, {
    errors_as_json: true,
    ...config,
  });

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
  const [editorContent, setEditorContent] = useState(JSON.stringify(data, null, 2));
  const revalidator = useRevalidator();
  const actionData = useActionData();
  const submit = useSubmit();
  const theme = useTheme();

  useEffect(() => {
      setEditorContent(JSON.stringify(data, null, 2));
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
    setValidationErrors(null)
  }, [command])

  const handleSubmit = (e) => {
    const formData = new FormData();
    formData.append("config", editorContent);
    formData.append("name", command);
    submit(formData, { method: "post" });
    e.preventDefault();
  };

  const handleRefresh = () => {
    revalidator.revalidate()
    setValidationErrors(null)
  };

  return (
    <Stack direction={"column"}>
      <Typography variant="h3">{name}</Typography>
      <Form method="post" onSubmit={handleSubmit}>
        <Stack direction={"row"}>
          <Button onClick={handleRefresh}>Refresh</Button>
          <Button type="submit">Submit</Button>
        </Stack>
        {validationErrors && (
          <Box sx={{ mb: 2 }}>
            <CopyBlock
              wrapLongLines
              text={JSON.stringify(JSON.parse(validationErrors), null, 2)}
              language="json"
              theme={theme.palette.mode === "dark" ? a11yDark : a11yLight}
              customStyle={{ border: `2px solid ${red["600"]}` }}
            />
          </Box>
        )}
        <Editor
          height="70vh"
          defaultLanguage="json"
          value={editorContent}
          defaultValue=""
          theme={theme.palette.mode === "dark" ? "vs-dark" : "vs-light"}
          onChange={(value) => setEditorContent(value)}
        />
      </Form>
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
    </Stack>
  );
};

export function ErrorBoundary() {
  const error = useRouteError();

  if (isRouteErrorResponse(error) && error.status === 400) {
    // the response json is automatically parsed to
    // `error.data`, you also have access to the status
    return (
      <Stack spacing={2} alignItems={"center"} justifyContent={"center"}>
        <Typography variant="h3">{error.status}</Typography>
        <Typography variant="h4">{error.data.command}</Typography>
        <Typography>{error.data.message}</Typography>
        <Typography>{error.data.error}</Typography>
        <Button variant="contained" LinkComponent={Link} to={"."}>
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
