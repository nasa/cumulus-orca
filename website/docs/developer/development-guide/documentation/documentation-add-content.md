---
id: contrib-documentation-add
title: Adding New Content
desc: Provides instruction on adding a page to ORCA documentation.
---

## Add a New Documentation Page

Creating a new page should be as simple as writing some documentation in markdown,
placing it under the correct directory in the docs/ folder and adding some
configuration values wrapped by `---` at the top of the file. There are many
files that already have this header which can be used as reference. For information
on specific values allowed in the header section, see the [Docusaurus documentation](https://v2.docusaurus.io/docs/markdown-features#markdown-headers).

Generally, most markdown files for ORCA use the following items in the header
section.

```yaml
---
id: doc-unique-id    # Unique id for this document.
title: Title Of Doc  # This shows up as the title and sidebar reference.
desc: Breif description of the document
---
```

Once the markdown configuration file is created, the `website/sidebars.json`
file should be updated in order to be able to navigate to the new page. Information
on the `sidebar.json` file can be found in the [Docusaurus documentation](https://v2.docusaurus.io/docs/sidebar#sidebar-object).

When writing markdown for this project, please reference the
[documentation style guide](./documentation-style-guide.md)


### MD or MDX Format

Generally, all documentation should be written in Markdown however, when adding
templates, images, or dynamic content a MDX format should be used. More information
on MDX content can be found in the [Docusaurus documentation](https://v2.docusaurus.io/docs/markdown-features/#embedding-react-components-with-mdx)
and the [MDX website](https://mdxjs.com/).


### Embedding Static Content or Template Information

To embed static content like images or a template into your MDX documentation,
refer to the [Docusaurus documentation](https://v2.docusaurus.io/docs/static-assets/)
and the [documentation template guide](documentaion-templates.md).


## Add a New Template Page

To create a template page, follow the same standards a creating an MDX or
Markdown documentation page. All templates should reside in the `website/docs/templates`
folder. Once the template is created and tested, update the [template guide](documentaion-templates.md)
located in `website/docs/developer/contribute/documentation/documentaion-templates.md`
with the pertinent information.

:::danger

Do not include the standard Docusaurus header in a template. This will cause
builds to break badly.

```yaml
---
id: doc-unique-id    # Unique id for this document.
title: Title Of Doc  # This shows up as the title and sidbar refrence.
desc: Breif description of the document
---
```

:::


## Add a New Image or Diagram

All images should be properly named and saved to the `website/static/img` directory.
Ideally images should be in an SVG or PNG format. Diagrams are created and
maintained in [Lucidchart](https://www.lucidchart.com/) by the ORCA core team.
To access the diagrams for an update, please speak to a ORCA core team member.
