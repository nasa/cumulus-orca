module.exports = {
  about_orca: {
    "Introduction": [
        'about/introduction/orca-intro',
        'about/introduction/intro-navigating',
        'about/introduction/intro-contributing',
        'about/introduction/intro-glossary',
    ],
    "Architecture": [
        'about/architecture/architecture-intro',
        'about/architecture/architecture-software-system',
        'about/architecture/architecture-archive-container',
        'about/architecture/architecture-recover-container',
        'about/architecture/architecture-api-container',
        'about/architecture/architecture-database-container',
    ],
    "Helpful Tips": [
        'about/tips',
    ],
    "ORCA Team": [
        'about/team',
    ],
  },
  dev_guide: {
    "Getting Started": [
        'developer/quickstart/developer-intro',
    ],

    "Development Guide": [
        {
            "Developing Code": [
                'developer/development-guide/code/contrib-code-intro',
                'developer/development-guide/code/setup-dev-env',
                'developer/development-guide/code/best-practices',
                'developer/development-guide/code/versioning-releases',
                'developer/development-guide/code/linting',
                'developer/development-guide/code/unit-tests',
                'developer/development-guide/code/postgres-tests',
                'developer/development-guide/code/orca-logging',
            ],
            "Developing Documentation": [
                'developer/development-guide/documentation/contrib-documentation-intro',
                'developer/development-guide/documentation/contrib-documentation-env',
                'developer/development-guide/documentation/contrib-documentation-add',
                'developer/development-guide/documentation/contrib-documentation-templates',
                'developer/development-guide/documentation/contrib-documentation-tasks',
                'developer/development-guide/documentation/documentation-style-guide',
                'developer/development-guide/documentation/contrib-documentation-deploy',
            ],
        },
    ],
    "Deployment Guide": [
        'developer/deployment-guide/deployment',
        'developer/deployment-guide/deployment-environment',
        'developer/deployment-guide/deployment-s3-bucket',
        'developer/deployment-guide/deployment-with-cumulus',
        'developer/deployment-guide/deployment-upgrading-orca',
        'developer/deployment-guide/recovery-workflow',
        'developer/deployment-guide/testing_deployment',
        'developer/deployment-guide/deploying-from-windows',
    ],
    "API Reference": [
      'developer/api/orca-api'
    ],
    "Research": [
      'developer/research/research-intro',
      'developer/research/research-localstack',
      'developer/research/research-APIGateway',
      'developer/research/research-reconciliation',
      'developer/research/research-AuroraServerless',
      'developer/research/research-graphql',
      'developer/research/research-multipart-chunksize',
      'developer/research/research-bamboo',
      'developer/research/research-lambda-container'
    ],
  },
  cookbook: {
    "Getting Started": [
        'cookbook/cookbook-intro',
    ],
  },
  ops_guide: {
    "Getting Started": [
      'operator/operator-intro',
    ],
    "Operations": [
      'operator/data-recovery',
      'operator/restore-to-orca',
    ],
    "Configuration": [
      'operator/collection-configuration',
    ],
  },
};
