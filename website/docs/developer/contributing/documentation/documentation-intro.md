---
id: contrib-documentation-intro
title: Documentation Introduction
desc: Provides basic information on ORCA documentation including layout and key information for contributing to overall documentation.
---

ORCA project documentation is hosted on [NASA's GitHub Pages](https://nasa.github.io/cumulus-orca/).
The project utilizes the open-source static website generator [Docusaurus](https://v2.docusaurus.io/)
to build html files from markdown documentation, add some organization and navigation,
and provide other niceties in the final website (search, easy templating, etc.).

The sections below go into greater detail and provide information on the ORCA
documentation layout and key Docusarus files to manage.


## Docusaurus Documentation Layout

With few exceptions, ORCA's documentation is maintained under the [`website`](https://github.com/nasa/cumulus-orca/tree/master/website)
directory in the [ORCA GitHub repository](https://github.com/nasa/cumulus-orca/).
Under the `website` directory, there are three primary directories which contain
ORCA documentation content. Those directories are `docs`, `static`, and `src`.
The sections below go into detail on the contents of each of those directories
and their layout.


### `docs` Directory

The `website/docs` directory contains a majority of ORCA's documentation in the
form of [Markdown (`.md`)](https://guides.github.com/features/mastering-markdown/)
and [MDX Markdown (`.mdx`)](https://mdxjs.com/). The `docs` directory is split into
five subdirectories as seen below. Each subdirectory corresponds to the major
ORCA documentation sections.

```sh
docs
├── about
├── components
├── cookbook
├── developer
└── operator
```


#### `docs/about`

The `docs/about` subdirectory contains all documentation related to the
[**About ORCA**](https://github.com/nasa/cumulus-orca/docs/about/introduction/orca-intro)
documents and navigation. This directory contains overview
information related to ORCA uses, architectures, policies, and contribution
guidelines. Under the `docs/about` directory information is broken up based on
the sidebar menu layout similar to the layout seen below.

```sh
docs/about
├── architecture
├── introduction
├── team
└── tips
```


#### `docs/components`

The `docs/components` subdirectory contains templates and non-static reusable
markdown and MDX markdown files that are utilized to provide additional
functionality to the documentation like image manipulation and standardized layouts.
More information on these types of files can be found in the
[embed static content documentation](documentation-embed-static.md).


#### `docs/cookbook`

The `docs/cookbook` subdirectory contains all documentation related to the
[**ORCA Cookbooks**](https://github.com/nasa/cumulus-orca/docs/cookbook/cookbook-intro)
documentation and navigation. This directory contains information
related to ORCA cookbooks and real world implementations of the ORCA codebase
in Cumulus. Under the `docs/cookbook` directory, information is broken up based
on the sidebar menu layout.


#### `docs/developer`

The `docs/developer` subdirectory contains all documentation related to the
[**Developer Guide**](https://github.com/nasa/cumulus-orca/docs/developer/developer-intro)
documentation and navigation. This directory contains information related to
integrating ORCA into Cumulus, developing for ORCA, development standards and
procedures, and other developer specific information needed to interact and
contribute to the ORCA product. Under the `docs/developer` directory, information
is broken up based on the sidebar menu layout.


#### `docs/operator`

The `docs/operator` subdirectory contains all documentation related to the
[**Operator Guide**](https://github.com/nasa/cumulus-orca/docs/operator/operator-intro)
documentation and navigation. This directory contains information related to
operating ORCA within Cumulus and includes information on collection configuration,
utilizing the Cumulus Dashboard to perform ORCA tasks, and performing tasks related
to operations and data management staff. Under the `docs/operator` directory,
information is broken up based on the sidebar menu layout.


### `static` Directory

The `website/static` directory contains ORCA's static website content. Currently,
this directory contains images used for diagrams, examples, etc. However, all static
content should be placed in this directory for use by the pages under `website/docs`.


### `src` Directory

The `website/src` directory contains the Docusaurus generated index page splash
screen, and css style sheet files. Generally, files in this directory should only
be updated by the ORCA core team members. The index splash scree is controlled
via the `docusaurus.config.js` and `website/src/pages/index.js` files.


## Key Docusaurus Files

Docusaurus contains two key files that control the layout, configuration, style,
and behaviour of the static site. Information on these files are laid out in the
sections below.


### `sidebar.js`

The `website/sidebar.js` file provides the layout information for the sidebar as
well as navigation to all the various documents. More information on the
`sidebar.js` file can be found in the [Docusaurus documentation](https://v2.docusaurus.io/docs/sidebar#sidebar-object).


### `docusaurus.config.js`

The `website/docusaurus.config.js` file provides configuration, plugin and setting
information to the Docusaurus build. More information on the `docusaurus.config.js`
file can be found in the [Docusaurus documentation](https://v2.docusaurus.io/docs/configuration).


## Other Documentation Locations

Although a bulk of the documentation for ORCA resides in the locations discussed
above, there are additional documentation files to be aware of. The information
below provides location information for the file and updating particulars.

### TODO: Work with AD and determine what we put here
- `README.md`
- `tasks/<taskname>README.md`
- others?

