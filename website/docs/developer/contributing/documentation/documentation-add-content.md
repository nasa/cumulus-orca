---
id: contrib-documentation-add
title: Adding New Content
desc: Provides instruction on adding a page to ORCA documentaion.
---

## Add a New Documentation Page

Adding a new page should be as simple as writing some documentation in markdown,
placing it under the correct directory in the docs/ folder and adding some
configuration values wrapped by `---` at the top of the file. There are many
files that already have this header which can be used as reference.

```yaml
---
id: doc-unique-id    # unique id for this document. This must be unique accross ALL documentation under docs/
title: Title Of Doc  # Whatever title you feel like adding. This will show up as the index to this page on the sidebar.
hide_title: false
---
```

:::note

To have the new page show up in a sidebar the designated id must be added to a
sidebar in the website/sidebars.json file. Docusaurus has an in depth 
explanation of sidebars here.
:::

### MD or MDX Format

Some stuff here

### Embedding Static Content or Template Information

Some Stuff Here

## Add a New Template Page

Stuff goes here.


## Add a New Image or Diagram

Stuff goes here.
