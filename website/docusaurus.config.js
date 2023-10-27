module.exports = {
  title: 'Operational Recovery Cloud Archive (ORCA)',
  tagline: 'Providing a second line of defense for your Cumulus data.',
  url: 'https://nasa.github.io/',
  baseUrl: '/cumulus-orca/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',
  organizationName: 'nasa', // Usually your GitHub org/user name.
  projectName: 'cumulus-orca', // Usually your repo name.
  trailingSlash: false,
  themeConfig: {
    navbar: {
      title: 'Operational Recovery Cloud Archive (ORCA)',
      logo: {
        alt: 'ORCA site logo',
        src: 'img/cumulus-orca-logo.svg',
      },
      items: [
        {
          to: 'docs/about/introduction/orca-intro',
          activeBasePath: 'docs/about/',
          label: 'About ORCA',
          position: 'right',
        },
        {
          to: 'docs/developer/quickstart/developer-intro',
          activeBasePath: 'docs/developer/',
          label: 'Developer Guide',
          position: 'right',
        },
        {
          to: 'docs/operator/operator-intro',
          activeBasePath: 'docs/operator/',
          label: 'Operator Guide',
          position: 'right',
        },
        {
          href: 'https://github.com/nasa/cumulus-orca',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'About ORCA',
              to: 'docs/about/introduction/orca-intro',
            },
            {
              label: 'ORCA Developer Guide',
              to: 'docs/developer/quickstart/developer-intro',
            },
            {
              label: 'ORCA Operator Guide',
              to: 'docs/operator/operator-intro',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'ORCA Working Group',
              href: 'https://wiki.earthdata.nasa.gov/display/CUMULUS/ORCA+Working+Group',
            },
            {
              label: 'Cumulus Project',
              href: 'https://github.com/nasa/cumulus',
            },
            {
              label: 'Cumulus Integrator Working Group',
              href: 'https://wiki.earthdata.nasa.gov/display/CUMULUS/Cumulus+Integrators+Working+Group',
            },
            {
              label: 'Cumulus Operator Working Group',
              href: 'https://wiki.earthdata.nasa.gov/display/CUMULUS/Cumulus+Operator+Working+Group',
            },
            {
              label: 'Cumulus Documentation',
              href: 'https://nasa.github.io/cumulus/docs/cumulus-docs-readme'
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/nasa/cumulus-orca',
            },
          ],
        },
      ],
    },
  },
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl:
            'https://github.com/nasa/cumulus-orca/edit/develop/website/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
};
