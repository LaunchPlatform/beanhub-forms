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

The file name `file` can also be a Jinja2 template. The file name `books/{{ date.year }}.bean` with `2023` the input value in the form will end up as `books/2023.bean`.
This allows you to organize entries by dates or other variables into different files and folders easily.

Read the [documentations here](https://beanhub-forms-docs.beanhub.io).

# Sponsor

<p align="center">
  <a href="https://beanhub.io"><img src="https://github.com/LaunchPlatform/beanhub-forms/raw/master/assets/beanhub.svg?raw=true" alt="BeanHub logo" /></a>
</p>

A modern accounting book service based on the most popular open source version control system [Git](https://git-scm.com/) and text-based double entry accounting book software [Beancount](https://beancount.github.io/docs/index.html).


## Install

This library provides schema definition of the forms and the libraries for generating [WTForms](https://wtforms.readthedocs.io/) plus processing the form data.
For most users, you don't need to install beanhub-forms.
You can install [beanhub-cli](https://github.com/LaunchPlatform/beanhub-cli) instead if you only want to use it.

To install this library, simply run

```bash
pip install beanhub-forms
```

