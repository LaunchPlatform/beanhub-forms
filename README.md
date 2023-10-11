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

And then use tools like beanhub-cli command to launch a web app server locally:

```
bh form server
```

Then, the user can use the rendered form to input repeating similar Beancount entries easily.

