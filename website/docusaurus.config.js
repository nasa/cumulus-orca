module.exports = {
  title: 'Operational Recovery Cloud Archive (ORCA)',
  tagline: 'Providing a second line of defense for your Cumulus data.',
  url: 'https://nasa.github.io/docs/cumulus-orca',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',
  organizationName: 'nasa', // Usually your GitHub org/user name.
  projectName: 'cumulus-orca', // Usually your repo name.
  themeConfig: {
    navbar: {
      title: 'Operational Recovery Cloud Archive (ORCA)',
      logo: {
        alt: 'ORCA site logo',
        src: 'img/cumulus-orca-logo.svg',
      },
      items: [
        {
          to: 'docs/',
          activeBasePath: 'docs',
          label: 'Versions',
          position: 'left',
          items: [
            {
              to: 'docs/',
              label: 'v1.0',
            },
          ],
        },
        {
          to: 'docs/about/introduction/orca-intro',
          activeBasePath: 'docs/about/',
          label: 'About ORCA',
          position: 'right',
        },
        {
          to: 'docs/developer/developer-intro',
          activeBasePath: 'docs/developer/',
          label: 'Developer Guide',
          position: 'right',
        },
        {
          to: 'docs/cookbook/',
          activeBasePath: 'docs/cookbook/',
          label: 'ORCA Cookbooks',
          position: 'right',
        },
        {
          to: 'docs/operator/',
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
              to: 'docs/about/',
            },
            {
              label: 'Developer Guide',
              to: 'docs/',
            },
            {
              label: 'ORCA Cookbooks',
              to: 'docs/cookbook/',
            },
            {
              label: 'Operator Guide',
              to: 'docs/operator/',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'ORCA Working Group',
              href: 'https://github.com/nasa',
            },
            {
              label: 'Cumulus Project',
              href: 'https://github.com/nasa/cumulus',
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
          // Please change this to your repo.
          editUrl:
            'https://github.com/nasa/cumulus-orca/edit/master/website/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
};
