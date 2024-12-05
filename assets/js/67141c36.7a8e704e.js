"use strict";(self.webpackChunkorca_website=self.webpackChunkorca_website||[]).push([[8574],{2282:(e,n,r)=>{r.r(n),r.d(n,{assets:()=>l,contentTitle:()=>s,default:()=>h,frontMatter:()=>i,metadata:()=>c,toc:()=>d});var t=r(4848),o=r(8453),a=r(6025);const i={id:"data-recovery",title:"Data Recovery",description:"Provides documentation for Operators to recover missing data."},s=void 0,c={id:"operator/data-recovery",title:"Data Recovery",description:"Provides documentation for Operators to recover missing data.",source:"@site/docs/operator/data-recovery.md",sourceDirName:"operator",slug:"/operator/data-recovery",permalink:"/cumulus-orca/docs/operator/data-recovery",draft:!1,unlisted:!1,editUrl:"https://github.com/nasa/cumulus-orca/edit/develop/website/docs/operator/data-recovery.md",tags:[],version:"current",frontMatter:{id:"data-recovery",title:"Data Recovery",description:"Provides documentation for Operators to recover missing data."},sidebar:"ops_guide",previous:{title:"Operator Introduction",permalink:"/cumulus-orca/docs/operator/operator-intro"},next:{title:"Re-Ingesting Data to ORCA",permalink:"/cumulus-orca/docs/operator/reingest-to-orca"}},l={},d=[{value:"Recovery via Cumulus Dashboard",id:"recovery-via-cumulus-dashboard",level:2},{value:"Manual recovery via step function workflow",id:"manual-recovery-via-step-function-workflow",level:2},{value:"Recovery workflow input and output examples",id:"recovery-workflow-input-and-output-examples",level:3},{value:"Recovery workflow configurable parameters",id:"recovery-workflow-configurable-parameters",level:3}];function u(e){const n={a:"a",admonition:"admonition",code:"code",h2:"h2",h3:"h3",li:"li",p:"p",pre:"pre",ul:"ul",...(0,o.R)(),...e.components};return(0,t.jsxs)(t.Fragment,{children:[(0,t.jsx)(n.admonition,{type:"important",children:(0,t.jsxs)(n.p,{children:["As of ORCA v8.1 the Cumulus Message Adapter is no longer used. Users will need to deploy the recovery adapter before the recovery can be ran. Reference ",(0,t.jsx)(n.a,{href:"https://nasa.github.io/cumulus-orca/docs/developer/deployment-guide/deployment-with-cumulus#modify-the-recovery-workflow",children:"Deployment with Cumulus"})]})}),"\n",(0,t.jsx)(n.h2,{id:"recovery-via-cumulus-dashboard",children:"Recovery via Cumulus Dashboard"}),"\n",(0,t.jsx)(n.p,{children:"Recovery processes are kicked off manually by an operator through the Cumulus Dashboard.\nThe dashboard calls an API which kicks off a recovery workflow.\nRecovery is an asynchronous operation since data\nrequested from GLACIER can take 4 hours or more to reconstitute,\nand DEEP_ARCHIVE can take 12 hours.\nSince it is asynchronous, the recovery container\nrelies on a database to maintain the status of the request and event\ndriven triggers to restore the data once it has been reconstituted\nfrom archive into an S3 bucket. Currently, data is copied back to the\nCumulus S3 primary data bucket which is the default bucket. The operator\nhas the option to override the default bucket with another restore bucket if desired.\nDetermining the status of the recovery job is done manually by querying the database\ndirectly or by checking the status on the dashboard."}),"\n",(0,t.jsx)(n.p,{children:"A screenshot of the Cumulus dashboard used for recovering granules is shown below."}),"\n",(0,t.jsx)("img",{src:(0,a.Ay)("img/Cumulus-Dashboard-Recovery-Workflow.png"),imageAlt:"Cumulus Dashboard used for recovery",zoomInPic:(0,a.Ay)("img/zoom-in.svg"),zoomOutPic:(0,a.Ay)("img/zoom-out.svg"),resetPic:(0,a.Ay)("img/zoom-pan-reset.svg")}),"\n",(0,t.jsxs)(n.p,{children:["On the dashboard home page, click on ",(0,t.jsx)(n.code,{children:"Granules"})," option and add the granule to recover.\nThen click on the ",(0,t.jsx)(n.code,{children:"Options"})," button and select ",(0,t.jsx)(n.code,{children:"Execute"}),". From the dropdown menu,\nselect ",(0,t.jsx)(n.code,{children:"OrcaRecoveryWorkflow"})," and hit ",(0,t.jsx)(n.code,{children:"Confirm"}),". This will execute the recovery process.\nThere are several configurable parameters that can be set up while running the workflow and are explained in\nthe section ",(0,t.jsx)(n.a,{href:"#recovery-workflow-configurable-parameters",children:"below"}),"."]}),"\n",(0,t.jsx)(n.h2,{id:"manual-recovery-via-step-function-workflow",children:"Manual recovery via step function workflow"}),"\n",(0,t.jsxs)(n.p,{children:["An operator can also run the recovery by running the ",(0,t.jsx)(n.code,{children:"Recovery Workflow"})," in step function."]}),"\n",(0,t.jsx)(n.admonition,{type:"warning",children:(0,t.jsx)(n.p,{children:"The operator should have access to AWS console to manually run the workflow which is not ideal."})}),"\n",(0,t.jsx)(n.h3,{id:"recovery-workflow-input-and-output-examples",children:"Recovery workflow input and output examples"}),"\n",(0,t.jsx)(n.p,{children:"The following is an input event example that an operator might set up while running the recovery workflow."}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-json",children:'{\n  "payload": {\n    "granules": [\n      {\n        "collectionId": "1234",\n        "granuleId": "integrationGranuleId",\n        "version": "integrationGranuleVersion",\n        "files": [\n          {\n            "fileName": "MOD09GQ.A2017025.h21v00.006.2017034065104.hdf",\n            "key": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065104.hdf",\n            "bucket": "test-orca-primary"\n          }\n        ]\n      }\n    ]\n  },\n  "meta": {\n    "buckets": {\n      "protected": {\n        "name": "test-protected",\n        "type": "protected"\n      },\n      "internal": {\n        "name": "test-internal",\n        "type": "internal"\n      },\n      "private": {\n        "name": "test-private",\n        "type": "private"\n      },\n      "public": {\n        "name": "test-public",\n        "type": "public"\n      },\n      "orca_default": {\n        "name": "test-orca-primary",\n        "type": "orca"\n      }\n    },\n    "collection": {\n      "meta": {\n        "orca": {\n          "excludedFileExtensions": [\n            ".xml"\n          ],\n          "defaultBucketOverride": "test-orca-primary",\n          "defaultRecoveryTypeOverride": "Standard"\n        },\n        "s3MultipartChunksizeMb": 200\n      },\n      "files": [\n        {\n          "regex": ".*.tar.gz",\n          "sampleFileName": "blah.tar.gz",\n          "bucket": "public"\n        }\n      ]\n    }\n  },\n  "cumulus_meta": {\n    "system_bucket": "test-internal",\n    "asyncOperationId": "1234"\n  }\n}\n'})}),"\n",(0,t.jsx)(n.p,{children:"The following is the corresponding output that the workflow will return if successful."}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-json",children:'\n{\n  "granules": [\n    {\n      "collectionId": "integrationCollectionId",\n      "granuleId": "integrationGranuleId",\n      "version": "integrationGranuleVersion",\n      "files": [\n        {\n          "fileName": "MOD09GQ.A2017025.h21v00.006.2017034065104.hdf",\n          "key": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065104.hdf",\n          "bucket": "test-orca-primary"\n        }\n      ],\n      "keys": [\n        {\n          "key": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065104.hdf",\n          "destBucket": "test-public"\n        }\n      ],\n      "recoverFiles": [\n        {\n          "success": true,\n          "filename": "MOD09GQ.A2017025.h21v00.006.2017034065104.hdf",\n          "keyPath": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065104.hdf",\n          "restoreDestination": "test-public",\n          "s3MultipartChunksizeMb": 200,\n          "statusId": 1,\n          "requestTime": "2022-11-16T17:29:19.008088+00:00",\n          "lastUpdate": "2022-11-16T17:29:19.008088+00:00",\n          "completionTime": "2022-11-16T17:29:19.008088+00:00"\n        }\n      ]\n    }\n  ],\n  "asyncOperationId": "1234"\n}\n\n'})}),"\n",(0,t.jsx)(n.h3,{id:"recovery-workflow-configurable-parameters",children:"Recovery workflow configurable parameters"}),"\n",(0,t.jsx)(n.p,{children:"The following are the parameters needed for recovery workflow:"}),"\n",(0,t.jsxs)(n.ul,{children:["\n",(0,t.jsxs)(n.li,{children:["\n",(0,t.jsx)(n.p,{children:"buckets- AWS S3 bucket mapping used for Cumulus and ORCA configuration. Contains the following properties:"}),"\n",(0,t.jsxs)(n.ul,{children:["\n",(0,t.jsx)(n.li,{children:"name (Required)- Name of the S3 bucket."}),"\n",(0,t.jsx)(n.li,{children:"type (Optional)- the type of bucket - i.e. internal, public, private, protected."}),"\n"]}),"\n",(0,t.jsx)(n.p,{children:"It can be set up using the following configuration."}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-json",children:'"config": {\n  "buckets.$": "$.meta.buckets"\n}\n'})}),"\n",(0,t.jsx)(n.p,{children:"Example:"}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-json",children:'"buckets": {\n  "protected": {\n    "name": "test-protected",\n    "type": "protected"\n  },\n  "internal": {\n    "name": "test-internal",\n    "type": "internal"\n  },\n  "private": {\n    "name": "test-private",\n    "type": "private"\n  },\n  "public": {\n    "name": "test-public",\n    "type": "public"\n  }\n}\n\n'})}),"\n"]}),"\n",(0,t.jsxs)(n.li,{children:["\n",(0,t.jsx)(n.p,{children:"fileBucketMaps- A list of dictionaries that contains details of the configured storage bucket and file regex. Contains the following properties:"}),"\n",(0,t.jsxs)(n.ul,{children:["\n",(0,t.jsx)(n.li,{children:"regex (Required)- The regex that matches the file extension type."}),"\n",(0,t.jsx)(n.li,{children:"bucket (Required))- The name of the key that points to the correct S3 bucket. Examples include public, private, protected, etc."}),"\n",(0,t.jsx)(n.li,{children:"sampleFileName (Optional)- name of a sample file having extension."}),"\n"]}),"\n",(0,t.jsx)(n.p,{children:"It can be set up using the following configuration."}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-json",children:'"config": {\n  "fileBucketMaps.$": "$.meta.collection.files"\n}\n'})}),"\n",(0,t.jsx)(n.p,{children:"Example:"}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-json",children:'"fileBucketMaps": [\n  {\n    "regex": ".*.h5$",\n    "sampleFileName": "L0A_HR_RAW_product_0010-of-0420.h5",\n    "bucket": "protected"\n  },\n  {\n    "regex": ".*.cmr.xml$",\n    "sampleFileName": "L0A_HR_RAW_product_0010-of-0420.cmr.xml",\n    "bucket": "protected"\n  }\n]\n'})}),"\n"]}),"\n",(0,t.jsxs)(n.li,{children:["\n",(0,t.jsx)(n.p,{children:"excludedFileExtensions (Optional)- A list of file extensions to ignore when copying files.\nIt can be set up using the following configuration."}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-json",children:'"config": {\n  "excludedFileExtensions.$": "$.meta.collection.meta.orca.excludedFileExtensions"\n}\n'})}),"\n",(0,t.jsx)(n.p,{children:"Example:"}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-json",children:'"collection": {\n  "meta": {\n    "orca": {\n      "excludedFileExtensions": [\n        ".xml"\n      ]\n    }\n  }\n}\n'})}),"\n"]}),"\n",(0,t.jsxs)(n.li,{children:["\n",(0,t.jsxs)(n.p,{children:["defaultRecoveryTypeOverride (Optional)- Overrides the ",(0,t.jsx)(n.a,{href:"https://github.com/nasa/cumulus-orca/blob/master/website/docs/developer/deployment-guide/deployment-with-cumulus.md#orca-optional-variables",children:"orca_default_recovery_type"})," via a change in the collections configuration under ",(0,t.jsx)(n.code,{children:"meta"})," tag as shown below."]}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-json",children:'  "config": {\n    "defaultRecoveryTypeOverride": "{$.event.meta.collection.meta.orca.defaultRecoveryTypeOverride}"\n  }\n'})}),"\n",(0,t.jsx)(n.p,{children:"Example:"}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-json",children:'    "collection": {\n        "meta":{\n            "orca": {\n              "defaultRecoveryTypeOverride": "Standard"\n          }\n      }\n    }\n'})}),"\n"]}),"\n",(0,t.jsxs)(n.li,{children:["\n",(0,t.jsxs)(n.p,{children:["defaultBucketOverride (Optional)- Overrides the ",(0,t.jsx)(n.a,{href:"https://github.com/nasa/cumulus-orca/blob/master/website/docs/developer/deployment-guide/deployment-with-cumulus.md#orca-required-variables",children:"orca_default_bucket"})," to copy recovered files to."]}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-json",children:'"config": {\n    "defaultBucketOverride": "{$.meta.collection.meta.orca.defaultBucketOverride}"\n  }\n'})}),"\n",(0,t.jsx)(n.p,{children:"Example:"}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-json",children:'"collection": {\n  "meta": {\n    "orca": {\n      "defaultBucketOverride": "orca-bucket"\n    }\n  }\n}\n'})}),"\n"]}),"\n",(0,t.jsxs)(n.li,{children:["\n",(0,t.jsxs)(n.p,{children:["s3MultipartChunksizeMb (Optional)- Overrides the ",(0,t.jsx)(n.a,{href:"https://github.com/nasa/cumulus-orca/blob/master/website/docs/developer/deployment-guide/deployment-with-cumulus.md#orca-optional-variables",children:"default_multipart_chunksize_mb"})," from TF. Defaults to 250."]}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-json",children:'"config": {\n  "s3MultipartChunksizeMb": "{$.meta.collection.meta.s3MultipartChunksizeMb}"\n}\n'})}),"\n",(0,t.jsx)(n.p,{children:"Example:"}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-json",children:'"collection": {\n  "meta": {\n    "s3MultipartChunksizeMb": 300\n  }\n}\n'})}),"\n"]}),"\n",(0,t.jsxs)(n.li,{children:["\n",(0,t.jsx)(n.p,{children:"asyncOperationId (Optional)- The unique identifier used for tracking requests. If not present, it will be generated."}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-json",children:'"config": {\n  "asyncOperationId": "{$.cumulus_meta.asyncOperationId}"\n}\n'})}),"\n",(0,t.jsx)(n.p,{children:"Example:"}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-json",children:'"cumulus_meta": {\n  "asyncOperationId": "1234"\n}\n'})}),"\n"]}),"\n"]}),"\n",(0,t.jsx)(n.p,{children:"For full definition of the parameters, see the following schema."}),"\n",(0,t.jsxs)(n.ul,{children:["\n",(0,t.jsx)(n.li,{children:(0,t.jsx)(n.a,{href:"https://github.com/nasa/cumulus-orca/blob/master/tasks/request_from_archive/schemas/config.json",children:"request_from_archive schema"})}),"\n",(0,t.jsx)(n.li,{children:(0,t.jsx)(n.a,{href:"https://github.com/nasa/cumulus-orca/blob/master/tasks/extract_filepaths_for_granule/schemas/config.json",children:"extract_filepath_from_granule schema"})}),"\n"]})]})}function h(e={}){const{wrapper:n}={...(0,o.R)(),...e.components};return n?(0,t.jsx)(n,{...e,children:(0,t.jsx)(u,{...e})}):u(e)}},8453:(e,n,r)=>{r.d(n,{R:()=>i,x:()=>s});var t=r(6540);const o={},a=t.createContext(o);function i(e){const n=t.useContext(a);return t.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function s(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(o):e.components||o:i(e.components),t.createElement(a.Provider,{value:n},e.children)}}}]);