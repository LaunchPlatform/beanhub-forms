# beanhub-forms [![CircleCI](https://dl.circleci.com/status-badge/img/gh/LaunchPlatform/beanhub-forms/tree/master.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/LaunchPlatform/beanhub-forms/tree/master)

BeanHub Forms was originally developed by [BeanHub](https://beanhub.io) as a [product feature](https://beanhub.io/blog/2023/07/31/automating-beancount-data-input-with-beanhub-custom-forms/) for users to easily define their custom forms and templates for generating Beancount entries.
The BeanHub Forms feature was later extracted as a standalone library beanhub-forms and open-sourced under an MIT license.
With beanhub-forms, one can define a custom form like this in YAML file format:

```yaml
forms:
- name: add-xyz-hours
  display_name: "Hours spent on XYZ contracting project"
  fields:
  - name: date
    type: date
    display_name: "Date"
    required: true
  - name: hours
    type: number
    display_name: "Hours"
    required: true
  - name: rate
    type: number
    display_name: "Rate (USD)"
    default: "300"
    required: true
  - name: narration
    type: str
    default: "Hours spent on the software development project for client XYZ"
    display_name: "Narration"
  operations:
  - type: append
    file: "books/{{ date.year }}.bean"
    content: |
      {{ date }} * {{ narration | tojson }}
        Assets:AccountsReceivable:Contracting:XYZ      {{  hours }} XYZ.HOUR @ {{ rate }} USD
        Income:Contracting:XYZ
```

And then use tools like [beanhub-cli](https://github.com/LaunchPlatform/beanhub-cli) command to launch a web app server locally:

```bash
bh form server
```

Then, the user can use the rendered form to input repeating similar Beancount entries easily.

<p align="center">
  <a href="https://beanhub.io"><img src="https://github.com/LaunchPlatform/beanhub-forms/raw/master/assets/forms-screenshot.png?raw=true" alt="BeanHub Forms screenshot" /></a>
</p>

As you can see, the append operation with [Jinja2](https://jinja.palletsprojects.com/) template as the content is defined in the form doc schema:

```yaml
- type: append
  file: "books/{{ date.year }}.bean"
  content: |
    {{ date }} * {{ narration | tojson }}
      Assets:AccountsReceivable:Contracting:XYZ      {{  hours }} XYZ.HOUR @ {{ rate }} USD
      Income:Contracting:XYZ
```

When you submit the form, the form input data will be used for rendering the template and appending the result to the target file.

```beancount
2023-10-11 * "Hours spent on the software development project for client XYZ"
  Assets:AccountsReceivable:Contracting:XYZ      12 XYZ.HOUR @ 300 USD
  Income:Contracting:XYZ
```

The file name `file` can also be a Jinja2 template. The file name "books/{{ date.year }}.bean" with `2023` the input value in the form will end up as `books/2023.bean`.
This allows you to organize entries by dates or other variables into different files and folders easily.

# Sponsor

<p align="center">
  <a href="https://beanhub.io"><img src="https://github.com/LaunchPlatform/beanhub-forms/raw/master/assets/beanhub.svg?raw=true" alt="BeanHub logo" /></a>
</p>

A modern accounting book service based on the most popular open source version control system [Git](https://git-scm.com/) and text-based double entry accounting book software [Beancount](https://beancount.github.io/docs/index.html).


## Install

This library provides schema definition of the forms and the libraries for generating WTForms plus processing the form data.
For most users, you don't need to install beanhub-forms.
You can install [beanhub-cli](https://github.com/LaunchPlatform/beanhub-cli) instead if you only want to use it.

To install this library, simply run

```bash
pip install beanhub-forms
```

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
