# OCP directory

Worksheet components and tables shared by OCP users. OCP lists them in **Insert › Directory**
(Windows) and **⋮ › Directory** (phone), and installs one with a click.

## Sharing yours

In OCP, open **Components** (or **Tables**), pick yours and choose **Publish**. OCP asks you to
sign in to GitHub once (with a code on github.com) and opens a pull request here. When it is
reviewed and merged, everyone sees it in the directory.

What is shared is a worksheet (a component) or data (a table): nothing here runs code.

## How it works

- `components/<id>.ocpc` + `components/<id>.json`, `tables/<Name>.csv` + `tables/<Name>.json`
- `build_index.py` checks contributions (on pull requests) and rebuilds `index.json` (on merge),
  with each file's size and SHA-256, which OCP checks before installing.
