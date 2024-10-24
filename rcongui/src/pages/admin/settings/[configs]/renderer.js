import {and, createCombinatorRenderInfos, rankWith, schemaMatches, schemaTypeIs, uiTypeIs} from "@jsonforms/core";
import {JsonFormsDispatch, withJsonFormsAnyOfProps, withJsonFormsControlProps} from "@jsonforms/react";
import React, {useCallback} from "react";
import {Unwrapped} from "@jsonforms/material-renderers";

const {MaterialTextControl} = Unwrapped;

/**
 * A usual MaterialTextControl used in a anyOfNullRenderer to render a text input which value is null when an empty
 * string or undefined is dispatched (instead of the usual undefined value). This ensures that the field is still
 * present in the JSON, and has the value "null" instead of being removed.
 *
 * @param props
 * @returns {Element}
 */
const nullableTextControl = (props) => {
  const nullableChange = useCallback((path, newValue) => {
    if (!newValue) {
      props.handleChange(path, null);
    } else {
      props.handleChange(path, newValue);
    }
  }, [props.handleChange]);

  return <MaterialTextControl {...props} handleChange={nullableChange}/>;
}

const NullableTextControl = withJsonFormsControlProps(nullableTextControl);

/**
 * Custom tester for a nullable text input, for use in anyOfNullRenderer.
 *
 * @type {Tester}
 */
const nullableTextTester = and(uiTypeIs('Control'), schemaTypeIs('string'));

/**
 * Dispatches rendering of a JSON Form element based on the schema type of one of the anyOf elements.
 * Expects a schema with anyOf with exactly two elements, one of them having the type "null", making the other fields
 * value optional.
 *
 * In contrast to the JSON Forms shipped renderer, this renderer will not render a tab layout, but the element that is
 * in the schema, next to the null type element, e.g. a text input.
 *
 * @param schema
 * @param rootSchema
 * @param path
 * @param renderers
 * @param cells
 * @param uischema
 * @param uischemas
 * @returns {Element}
 */
const anyOfNullRenderer = ({
  schema,
  rootSchema,
  path,
  renderers,
  cells,
  uischema,
  uischemas,
}) => {
  const anyOf = 'anyOf';
  const anyOfRenderInfos = createCombinatorRenderInfos(
    schema.anyOf,
    rootSchema,
    anyOf,
    uischema,
    path,
    uischemas
  );
  const anyOfRenderInfo = anyOfRenderInfos.find((e) => e.schema.type !== 'null');

  return <JsonFormsDispatch
    schema={{
      description: schema.description,
      title: schema.title,
      default: null,
      ...anyOfRenderInfo.schema,
    }}
    uischema={anyOfRenderInfo.uischema}
    path={path}
    renderers={[{tester: nullableTextTester, renderer: NullableTextControl}, ...renderers]}
    cells={cells}
  />
}

/**
 * Explicitly tests for an optional field (in pydantic `Any | None` or Optional[Any]) and renders the underlying field.
 */
const isAnyOfNullControl = and(
  uiTypeIs('Control'),
  schemaMatches((schema) => {
      return Object.prototype.hasOwnProperty.call(schema, 'anyOf') &&
        schema.anyOf.some((e) => e.type === 'null') &&
        schema.anyOf.length === 2;
    }
  )
);

const anyOfNullTester = rankWith(
  3,
  isAnyOfNullControl
);

export const customRenderers = [
  {tester: anyOfNullTester, renderer: withJsonFormsAnyOfProps(anyOfNullRenderer)},
]
