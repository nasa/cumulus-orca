---
id: contrib-documentation-templates
title: Documentation Templates
desc: Provides information on the templates currently offered.
---

ORCA utilizes templates to easily manage documentation objects so that they
have a consistent look and feel for the end user. The sections below detail
the templates currently being maintained. All templates are maintained in the
`website/docs/templates` folder of the ORCA repository.


## `pan-zoom-image.mdx` Template

The `pan-zoom-image.mdx` template provides an author with a template that renders
images on the website that can be panned and zoomed. In addition, the end user is
provided notes and links to display the image in a separate window. An example
of this template in use can be seen on the [ORCA Architecture Introduction page](../../../about/architecture/architecture-intro.mdx).

To use the template create an `.mdx` content file as laid out in [Adding New Content](documentation-add-content.md).
A sample of a content file using the template is provided below.

```mdx
---
id: my-unique-id
title: My Content Page
desc: Provides information on my content.
---

import MyImage from '@site/docs/templates/pan-zoom-image.mdx';¬
import useBaseUrl from '@docusaurus/useBaseUrl';

The grey fox jumped over the red fern chasing the pink pig.

<MyImage¬
    imageSource={useBaseUrl('img/my-image.svg')}¬
    imageAlt="A fox chasing a pig."¬
    zoomInPic={useBaseUrl('img/zoom-in.svg')}¬
    zoomOutPic={useBaseUrl('img/zoom-out.svg')}¬
    resetPic={useBaseUrl('img/zoom-pan-reset.svg')}¬
/>
```

When using the template as seen from the example above, you must import both the
`useBaseUrl` library and the template. More information on the `useBaseUrl`
functionality can be found in the [Docusaurus API documentation](https://v2.docusaurus.io/docs/docusaurus-core#usebaseurl).

```mdx
import MyImage from '@site/docs/templates/pan-zoom-image.mdx';¬
import useBaseUrl from '@docusaurus/useBaseUrl';
```

:::tip `useBaseUrl`

The `useBaseURL` library allows us to reference the `img` path and image
file without having to create a relative location path from the current document.

:::

:::important Image Location and Path

Note that the `img` directory is in `website/static/img` but because of the way
Docusaurus builds, anything within the static directory will be copied to the
root of the build directory for deployment. See information about this in the
[Docusaurus documentation](https://v2.docusaurus.io/docs/deployment/#deploying-to-github-pages).

:::

:::tip Using `@site`

The `MyImage` import provides a name to reference the `pan-zoom-image.mdx` template.
This name can be any alphanumeric value and is often camel cased.

By using `@site/docs/templates/` as the path, the template does not need to be
referenced via relative location. This allows Docusaurus to figure out the template
locations starting at the `website` root directory.

:::

The position of the template content in the document is based on where you place
the tag for `MyImage`. In the example above, the tag was placed at the end of the
document. This means that the content from the template will appear at the end of
the document. In addition, this particular template requires the end user to
populate specific variables.

```mdx
<MyImage¬
    imageSource={useBaseUrl('img/my-image.svg')}¬
    imageAlt="A fox chasing a pig."¬
    zoomInPic={useBaseUrl('img/zoom-in.svg')}¬
    zoomOutPic={useBaseUrl('img/zoom-out.svg')}¬
    resetPic={useBaseUrl('img/zoom-pan-reset.svg')}¬
/>
```

There are five required variables that need to be set for the template.

- **imageSource**: This is the location and name of the image to display.
- **imageAlt**: This is an alternative description of the image.
- **zoomInPic**: Picture for zooming in icon. This value should be the same as the example.
- **zoomOutPic**: Picture for zooming out icon. This value should be the same as the example.
- **resetPic**: Picture for the reset icon. This value should be the same as the example.
