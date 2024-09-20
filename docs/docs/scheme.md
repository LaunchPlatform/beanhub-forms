# Scheme definition

### Form Doc
The root object of the form YAML at `.beanhub/forms.yaml` is a Form Doc, and at this moment, it contains only the key `forms` to the list of form definitions.
One Form Doc can have multiple Form Definitions.

### Form Definition

A Form Definition is an object consisting of the following keys:

- `name` is the unique slug (URL-friendly name string) id of this form in the Form Doc (**required**)
- `fields` is the list of Field Definitions (**required**)
- `operations` is the list of Operation Definitions. (**required**)
- `display_name` is the display name of the form. If not provided, the `name` value will be used (**optional**)
- `commit` is the Commit Options object (**optional**)
- `auto_format` is the boolean flag to determine whether to auto-format the Beancount files after the form operations update them. By default, it's true. (**optional**)

### Field Definition

A Form Definition is an object consisting of the following keys:

- `name` is the unique input field variable name to be referenced in the operation template (**required**)
- `type` is the type of the field. It determines which kind of input UI to present in the form. For the available types of fields, please see below. (**required**)
- `display_name` is the display name of the field. If not provided, the `name` value will be used (**optional**)
- `default` is the default value for the field (**optional**)
- `required` is the boolean flag to determine whether this field is required. By default, it's false (**optional**)

At this moment, we provide six field types as listed below:

- `str` simple string field
- `number` number field
- `date` date field
- `file` Beancount file path field
- `currency` currency field
- `account` account field

For the `file`, `currency`, and `account` fields, only the current present values in your Beancount books are for selection in the input UI.
However, we provide extra parameters for these three fields to enable inputting a value that doesn't exist in your Beancount books.
Here are the extra keys for these three fields:

#### File field
- `creatable` is a boolean flag to determine whether is inputting a currently non-existing Beancount file path allowed. By default, it's false (**optional**)

#### Account field
- `creatable` is a boolean flag to determine whether is inputting a currently non-existing account allowed. By default, it's false (**optional**)

#### Currency field
- `creatable` is a boolean flag to determine whether is inputting a currently non-existing currency allowed. By default, it's false (**optional**)
- `multiple` is a boolean flag to determine whether is inputting multiple currency values allowed. By default, it's false (**optional**)

## Operation Definition

An operation of the form is for performing update operations to your Beancount files based on the form input values.
It is an object consisting of the following keys:

- `type` is the type of operation. Currently, only `append` is supported (**required**)
- `file` is the path to the target file for the operation to perform. This parameter will be rendered as a template (**required**)
- `content` is the content of the operation to perform, such as the text to append to the file. This parameter will be rendered as a template (**required**)

## Commit Options
The Commit Options is an object for changing the default Git commit behavior.
It's an object consisting of the following keys:

- `message` is the message of the Git commit to make. This parameter will be rendered as a template (**optional**).

## The template syntax
For more details about the template syntax, please see the [Jinja2 documents](https://jinja.palletsprojects.com/en/3.1.x/).
At this moment, most of the Jinja2 syntax is supported.
When rendering a template parameter, all the available input form fields will be provided as a variable.
Please note that the Python object type of variables is going to be different based on the field's `type` value.
Here is the table of variable types for each field:

| Field Type             | Template variable type |
| ---------------------- | ---------------------- |
| `str`                  | `str`                  |
| `number`               | `decimal.Decimal`      |
| `date`                 | `datetime.date`        |
| `account`              | `str`                  |
| `file`                 | `str`                  |
| `currency` (single)    | `str`                  |
| `currency` (multiple)  | `list[str]`            |
