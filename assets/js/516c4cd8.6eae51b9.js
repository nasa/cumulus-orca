"use strict";(self.webpackChunkorca_website=self.webpackChunkorca_website||[]).push([[7447],{9117:(e,n,t)=>{t.r(n),t.d(n,{assets:()=>a,contentTitle:()=>s,default:()=>d,frontMatter:()=>i,metadata:()=>r,toc:()=>l});const r=JSON.parse('{"id":"developer/deployment-guide/deployment-s3-bucket","title":"Creating the Archive Bucket","description":"Provides developer with information on archive storage solutions.","source":"@site/docs/developer/deployment-guide/creating-orca-archive-bucket.md","sourceDirName":"developer/deployment-guide","slug":"/developer/deployment-guide/deployment-s3-bucket","permalink":"/cumulus-orca/docs/developer/deployment-guide/deployment-s3-bucket","draft":false,"unlisted":false,"editUrl":"https://github.com/nasa/cumulus-orca/edit/develop/website/docs/developer/deployment-guide/creating-orca-archive-bucket.md","tags":[],"version":"current","frontMatter":{"id":"deployment-s3-bucket","title":"Creating the Archive Bucket","description":"Provides developer with information on archive storage solutions."},"sidebar":"dev_guide","previous":{"title":"Creating a Deployment Environment","permalink":"/cumulus-orca/docs/developer/deployment-guide/deployment-environment"},"next":{"title":"Generating S3 credentials","permalink":"/cumulus-orca/docs/developer/deployment-guide/deployment-s3-credentials"}}');var c=t(4848),o=t(8453);const i={id:"deployment-s3-bucket",title:"Creating the Archive Bucket",description:"Provides developer with information on archive storage solutions."},s=void 0,a={},l=[{value:"Create the ORCA Archive and Report Buckets",id:"create-the-orca-archive-and-report-buckets",level:2},{value:"Provide Cross Account (OU) Access",id:"provide-cross-account-ou-access",level:2},{value:"Via AWS CloudFormation Template",id:"via-aws-cloudformation-template",level:3},{value:"Via Terraform",id:"via-terraform",level:3},{value:"Via AWS GUI",id:"via-aws-gui",level:3},{value:"Archive Bucket:",id:"archive-bucket",level:5},{value:"Reports Bucket:",id:"reports-bucket",level:5},{value:"Bucket policy for load balancer server access logging:",id:"bucket-policy-for-load-balancer-server-access-logging",level:5}];function u(e){const n={a:"a",admonition:"admonition",code:"code",h2:"h2",h3:"h3",h5:"h5",li:"li",ol:"ol",p:"p",pre:"pre",strong:"strong",ul:"ul",...(0,o.R)(),...e.components};return(0,c.jsxs)(c.Fragment,{children:[(0,c.jsxs)(n.p,{children:["ORCA maintains a cloud ready backup of science and ancillary data\nin one of various ",(0,c.jsx)(n.a,{href:"/cumulus-orca/docs/operator/storage-classes",children:"storage classes"}),"\nin ",(0,c.jsx)(n.a,{href:"https://aws.amazon.com/s3/",children:"S3"}),"\nfor the long term. The ORCA archive bucket can live in any NGAP Organizational\nUnit (OU)."]}),"\n",(0,c.jsx)(n.admonition,{title:"Archive Bucket OU Placement",type:"important",children:(0,c.jsxs)(n.p,{children:["Best practice is to place the ORCA archive bucket in your Disaster Recovery OU.\nThis is done to better separate the costs associated with the cloud ready backup\nfrom primary Cumulus holdings and ingest and archive activity. See the\n",(0,c.jsx)(n.a,{href:"/cumulus-orca/docs/about/architecture/architecture-intro",children:"ORCA Architecture Introduction documentation"}),"\nfor more information."]})}),"\n",(0,c.jsx)(n.p,{children:"The sections below go into further detail on creating the ORCA archive bucket."}),"\n",(0,c.jsx)(n.h2,{id:"create-the-orca-archive-and-report-buckets",children:"Create the ORCA Archive and Report Buckets"}),"\n",(0,c.jsxs)(n.p,{children:["Prior to creating the S3 buckets, make sure the deployment environment is created\nper the ",(0,c.jsx)(n.a,{href:"/cumulus-orca/docs/developer/deployment-guide/deployment-environment",children:"Creating the Deployment Environment"}),"\ndocumentation."]}),"\n",(0,c.jsx)(n.p,{children:"To create the ORCA buckets run the AWS CLI command below twice, once for your archive bucket and once for your report bucket.\nReplace the [place holder text] with proper values for your deployment."}),"\n",(0,c.jsx)(n.pre,{children:(0,c.jsx)(n.code,{className:"language-bash",children:'aws s3api create-bucket \\\n    --bucket [orca bucket name] \\\n    --profile [AWS OU profile]  \\\n    --region us-west-2 \\\n    --create-bucket-configuration "LocationConstraint=us-west-2"\n'})}),"\n",(0,c.jsxs)(n.ul,{children:["\n",(0,c.jsxs)(n.li,{children:[(0,c.jsx)(n.strong,{children:"[AWS OU profile]"})," - This is the AWS profile name to use to connect to the proper OU where the bucket will be created."]}),"\n",(0,c.jsxs)(n.li,{children:[(0,c.jsx)(n.strong,{children:"[orca bucket name]"})," - This is the name of your bucket. Example: ",(0,c.jsx)(n.code,{children:"PREFIX-orca-archive"})," and ",(0,c.jsx)(n.code,{children:"PREFIX-orca-reports"}),"\n",(0,c.jsx)(n.admonition,{type:"note",children:(0,c.jsx)(n.p,{children:"Due to limits on report names, the maximum length of a non-report bucket's name is 54 characters."})}),"\n"]}),"\n"]}),"\n",(0,c.jsx)(n.admonition,{type:"note",children:(0,c.jsxs)(n.p,{children:["The ",(0,c.jsx)(n.code,{children:"--region us-west-2"})," and ",(0,c.jsx)(n.code,{children:'--create-bucket-configuration "LocationConstraint=us-west-2"'}),"\nlines are only necessary if you are creating your bucket outside of ",(0,c.jsx)(n.strong,{children:"us-east-1"}),"."]})}),"\n",(0,c.jsxs)(n.p,{children:["For more information on creating an S3 bucket, see the\n",(0,c.jsx)(n.a,{href:"http://docs.aws.amazon.com/AmazonS3/latest/gsg/CreatingABucket.html",children:'AWS "Creating a Bucket" documentation'}),"\nand the ",(0,c.jsx)(n.a,{href:"https://nasa.github.io/cumulus/docs/deployment/create_bucket",children:'Cumulus "Creating an S3 Bucket" documentation'}),"."]}),"\n",(0,c.jsx)(n.h2,{id:"provide-cross-account-ou-access",children:"Provide Cross Account (OU) Access"}),"\n",(0,c.jsx)(n.p,{children:"Per best practice, the ORCA archive bucket will be created in the Disaster\nRecovery OU and the additional ORCA components will be created in the Cumulus OU.\nIn order for the components in the Cumulus OU to interact with the ORCA archive\nbucket in the Cumulus OU, cross account bucket access privileges are needed. This\nsection details the steps needed to request the cross account bucket access."}),"\n",(0,c.jsxs)(n.admonition,{title:"Deploying ORCA with Objects in Different OUs",type:"warning",children:[(0,c.jsx)(n.p,{children:"If you are following best practice and have created your ORCA archive bucket in\nthe Disaster Recovery OU, you must have cross account bucket access permissions\ncreated and enabled before deploying the ORCA code. If you do not, your deployment\nwill return with the following error."}),(0,c.jsx)(n.pre,{children:(0,c.jsx)(n.code,{children:"module.orca.module.orca_lambdas.aws_s3_bucket_notification.copy_lambda_trigger: Creating...\n\nError: Error putting S3 notification configuration: AccessDenied: Access Denied\n\tstatus code: 403, request id: 2E31C2ACD124B50B, host id: 0JrRBUioe/gT......\n"})})]}),"\n",(0,c.jsx)(n.h3,{id:"via-aws-cloudformation-template",children:"Via AWS CloudFormation Template"}),"\n",(0,c.jsxs)(n.p,{children:["The AWS Cloudformation template for creating the ORCA DR buckets can be found ",(0,c.jsx)(n.a,{href:"https://github.com/nasa/cumulus-orca/blob/master/modules/dr_buckets_cloudformation/dr-buckets.yaml",children:"here"}),". Make sure you have AWS CLI installed before deploying this template."]}),"\n",(0,c.jsxs)(n.p,{children:["From your terminal, run the following command by replacing the variables ",(0,c.jsx)(n.code,{children:"<PREFIX>"})," and ",(0,c.jsx)(n.code,{children:"<AWS_ACCOUNT_ID>"})," first:"]}),"\n",(0,c.jsx)(n.pre,{children:(0,c.jsx)(n.code,{children:'aws cloudformation deploy --stack-name <PREFIX>-orca-bucket-stack --template-file dr-buckets.yaml --parameter-overrides "PREFIX"="<PREFIX>" "CumulusAccountID"="<AWS_ACCOUNT_ID>"\n\n'})}),"\n",(0,c.jsx)(n.p,{children:"This will create archive and reports buckets with the necessary bucket policies giving the Cumulus Account permission to write data to the archive bucket."}),"\n",(0,c.jsx)(n.h3,{id:"via-terraform",children:"Via Terraform"}),"\n",(0,c.jsxs)(n.p,{children:["The Terraform template for creating the ORCA DR buckets can be found ",(0,c.jsx)(n.a,{href:"https://github.com/nasa/cumulus-orca/blob/master/modules/dr_buckets/dr_buckets.tf",children:"here"}),". Make sure you have AWS CLI installed and AWS configured to deploy to your DR account."]}),"\n",(0,c.jsxs)(n.p,{children:["From your terminal, first run ",(0,c.jsx)(n.code,{children:"terraform init"})," followed by ",(0,c.jsx)(n.code,{children:"terraform apply"}),". When running the apply, Terraform will ask for the following inputs:"]}),"\n",(0,c.jsxs)(n.ol,{children:["\n",(0,c.jsxs)(n.li,{children:[(0,c.jsx)(n.code,{children:"cumulus_account_id"})," - This is the account ID of the Cumulus AWS account."]}),"\n",(0,c.jsxs)(n.li,{children:[(0,c.jsx)(n.code,{children:"prefix"})," - This is the prefix to use for the bucket names."]}),"\n"]}),"\n",(0,c.jsx)(n.p,{children:"Tags are an optional variable that can be set if you wish to have the DR buckets tagged."}),"\n",(0,c.jsx)(n.p,{children:"Optionally you can provide Terraform the required inputs through the terminal with the following:"}),"\n",(0,c.jsx)(n.pre,{children:(0,c.jsx)(n.code,{children:'terraform apply \\\n-var=cumulus_account_id="<CUMULUS_ACCOUNT_ID>" \\\n-var=prefix="PREFIX"\n'})}),"\n",(0,c.jsx)(n.h3,{id:"via-aws-gui",children:"Via AWS GUI"}),"\n",(0,c.jsx)(n.p,{children:'For each of the buckets listed below\ngo to AWS, open the bucket in question, click "Permissions",\nthen under "Bucket policy" click "Edit".\nThe policy given, once modified, can be pasted into this form.'}),"\n",(0,c.jsx)(n.h5,{id:"archive-bucket",children:"Archive Bucket:"}),"\n",(0,c.jsx)(n.p,{children:"The policy shown below can be used with some minor\nmodifications, which will be detailed below."}),"\n",(0,c.jsx)(n.pre,{children:(0,c.jsx)(n.code,{className:"language-json",children:'{\n   "Version": "2012-10-17",\n   "Statement": [\n      {\n        "Sid": "denyInsecureTransport",\n        "Effect": "Deny",\n        "Principal": "*",\n        "Action": "s3:*",\n        "Resource": [\n          "arn:aws:s3:::PREFIX-orca-archive",\n          "arn:aws:s3:::PREFIX-orca-archive/*"\n        ],\n         "Condition": {\n         "Bool": {\n           "aws:SecureTransport": "false"\n           }\n         }\n      },\n      {\n         "Sid": "Cross Account Access",\n         "Effect": "Allow",\n         "Principal": {\n            "AWS": "arn:aws:iam::012345678912:root"\n         },\n         "Action":[\n            "s3:GetObject",\n            "s3:GetObjectVersion",\n            "s3:RestoreObject",\n            "s3:GetBucketVersioning",\n            "s3:GetBucketNotification",\n            "s3:ListBucket",\n            "s3:PutBucketNotification",\n            "s3:GetInventoryConfiguration",\n            "s3:PutInventoryConfiguration",\n            "s3:ListBucketVersions"\n         ],\n         "Resource": [\n            "arn:aws:s3:::PREFIX-orca-archive",\n            "arn:aws:s3:::PREFIX-orca-archive/*"\n         ]\n      },\n      {\n         "Sid": "Cross Account Write Access",\n         "Effect": "Allow",\n         "Principal": {\n            "AWS": "arn:aws:iam::012345678912:root"\n         },\n         "Action": "s3:PutObject",\n         "Resource": [\n            "arn:aws:s3:::PREFIX-orca-archive/*"\n         ],\n         "Condition": {\n            "StringEquals": {\n               "s3:x-amz-storage-class": [\n                  "GLACIER",\n                  "DEEP_ARCHIVE"\n               ]\n            }\n         }\n      }\n   ]\n}\n'})}),"\n",(0,c.jsx)(n.p,{children:"The Principal value is the AWS root user for your Cumulus application that will\naccess the ORCA archive bucket. The value for this can be retrieved by\nperforming the following."}),"\n",(0,c.jsx)(n.p,{children:"First, change your connection to the Cumulus account/OU rather than the Disaster Recovery account/OU.\nThen, using your AWS CLI client run the following command to get the account number:"}),"\n",(0,c.jsx)(n.pre,{children:(0,c.jsx)(n.code,{className:"language-bash",children:'aws sts get-caller-identity\n\n{\n    "UserId": "ABCWXYZ123...",\n    "Account": "90912...",\n    "Arn": "arn:aws:iam::90912...:user/NGAPShApplicationDeveloper-someone-123"\n}\n'})}),"\n",(0,c.jsxs)(n.p,{children:["Replace the number in ",(0,c.jsx)(n.code,{children:"arn:aws:iam::012345678912:root"})," with the value of your non-DR account number."]}),"\n",(0,c.jsxs)(n.p,{children:["The Resource value is the bucket and bucket paths that the Cumulus application\ncan access. Replace ",(0,c.jsx)(n.code,{children:"PREFIX-orca-archive"})," with the name\nof the Orca archive bucket created in the previous section."]}),"\n",(0,c.jsx)(n.h5,{id:"reports-bucket",children:"Reports Bucket:"}),"\n",(0,c.jsx)(n.p,{children:"The policy shown below can be used with some minor\nmodifications, which will be detailed below."}),"\n",(0,c.jsx)(n.pre,{children:(0,c.jsx)(n.code,{className:"language-json",children:'{\n  "Version": "2012-10-17",\n  "Statement": [\n   {\n     "Sid": "denyInsecureTransport",\n     "Effect": "Deny",\n     "Principal": "*",\n     "Action": "s3:*",\n     "Resource": [\n          "arn:aws:s3:::PREFIX-orca-reports",\n          "arn:aws:s3:::PREFIX-orca-reports/*"\n        ],\n     "Condition": {\n     "Bool": {\n       "aws:SecureTransport": "false"\n        }\n      }\n    },\n    {\n      "Sid": "Cross Account Access",\n      "Effect": "Allow",\n      "Principal": {\n        "AWS": "arn:aws:iam::012345678912:root"\n      },\n      "Action": [\n        "s3:GetObject",\n        "s3:GetBucketNotification",\n        "s3:ListBucket",\n        "s3:PutObject",\n        "s3:PutBucketNotification"\n      ],\n      "Resource": [\n        "arn:aws:s3:::PREFIX-orca-reports",\n        "arn:aws:s3:::PREFIX-orca-reports/*"\n      ]\n    },\n    {\n      "Sid": "Inventory-PREFIX-orca-archive-reports",\n      "Effect": "Allow",\n      "Principal": {\n        "Service": "s3.amazonaws.com"\n      },\n      "Action": "s3:PutObject",\n      "Resource": "arn:aws:s3:::PREFIX-orca-reports/*",\n      "Condition": {\n        "StringEquals": {\n      \t  "aws:SourceAccount": "000000000000"\n        },\n      \t"ArnLike": {\n      \t  "aws:SourceArn": ["arn:aws:s3:::PREFIX-orca-archive"]\n      \t}\n      }\n    }\n  ]\n}\n'})}),"\n",(0,c.jsx)(n.p,{children:"The Principal value is the AWS root user for your Cumulus application that will\naccess the ORCA reports bucket.\nSee the Archive Bucket instructions for assistance getting this value."}),"\n",(0,c.jsxs)(n.p,{children:["Replace the number in ",(0,c.jsx)(n.code,{children:"arn:aws:iam::012345678912:root"})," with the value of your non-DR account number.\nSee the Archive Bucket instructions for assistance getting this value."]}),"\n",(0,c.jsxs)(n.p,{children:["Replace the number ",(0,c.jsx)(n.code,{children:"000000000000"})," with your DR account number."]}),"\n",(0,c.jsxs)(n.p,{children:["The Resource value is the bucket and bucket paths that the Cumulus application\ncan access. Replace ",(0,c.jsx)(n.code,{children:"PREFIX-orca-reports"})," with the name\nof the Orca reports bucket created in the previous section."]}),"\n",(0,c.jsxs)(n.p,{children:["Replace ",(0,c.jsx)(n.code,{children:"PREFIX-orca-archive"})," with the name of your ",(0,c.jsx)(n.a,{href:"#archive-bucket",children:"ORCA archive bucket"}),".\nIf you have multiple ORCA buckets, expand the ",(0,c.jsx)(n.code,{children:"SourceArn"})," array with the following format:"]}),"\n",(0,c.jsx)(n.pre,{children:(0,c.jsx)(n.code,{className:"language-json",children:'"ArnLike": {\n   "aws:SourceArn": ["arn:aws:s3:::BUCKET-NAME", "arn:aws:s3:::BUCKET-NAME"]\n}\n'})}),"\n",(0,c.jsxs)(n.p,{children:["Replace ",(0,c.jsx)(n.code,{children:"PREFIX-orca-archive"})," with the name of your ",(0,c.jsx)(n.a,{href:"#archive-bucket",children:"ORCA archive bucket"}),".\nIf you have multiple ORCA buckets, expand the ",(0,c.jsx)(n.code,{children:"SourceArn"})," array with the following format:"]}),"\n",(0,c.jsx)(n.pre,{children:(0,c.jsx)(n.code,{className:"language-json",children:'"ArnLike": {\n   "aws:SourceArn": ["arn:aws:s3:::BUCKET-NAME", "arn:aws:s3:::BUCKET-NAME"]\n}\n'})}),"\n",(0,c.jsx)(n.h5,{id:"bucket-policy-for-load-balancer-server-access-logging",children:"Bucket policy for load balancer server access logging:"}),"\n",(0,c.jsxs)(n.p,{children:["You must add the following S3 bucket policy to your ",(0,c.jsx)(n.code,{children:"system_bucket"}),", which will likely be named ",(0,c.jsx)(n.code,{children:"<PREFIX>-internal"}),", to give the load balancer access to write logs to the S3 bucket. Otherwise, the deployment will throw an ",(0,c.jsx)(n.code,{children:"Access Denied"})," error. If successful, a test log message will be posted to the bucket under the provided prefix."]}),"\n",(0,c.jsx)(n.pre,{children:(0,c.jsx)(n.code,{className:"language-json",children:'{\n    "Version": "2012-10-17",\n    "Statement": [\n        {\n            "Effect": "Allow",\n            "Principal": {\n                "AWS": "arn:aws:iam::<LOAD_BALANCER_ACCOUNT_ID>:root"\n            },\n            "Action": "s3:PutObject",\n            "Resource": "arn:aws:s3:::<BUCKET_NAME>/<PREFIX>-lb-gql-a-logs/AWSLogs/<AWS_ACCOUNT_ID>/*"\n        }\n    ]\n}\n'})}),"\n",(0,c.jsxs)(n.p,{children:["Replace ",(0,c.jsx)(n.code,{children:"<LOAD_BALANCER_ACCOUNT_ID>"})," with the ID of the AWS account for Elastic Load Balancing for your Region which can be found ",(0,c.jsx)(n.a,{href:"https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/enable-access-logs.html#attach-bucket-policy",children:"here"}),". If you do not know your region name, it can be found ",(0,c.jsx)(n.a,{href:"https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html",children:"here"}),"."]}),"\n",(0,c.jsx)(n.admonition,{type:"note",children:(0,c.jsxs)(n.p,{children:["Note that ",(0,c.jsx)(n.code,{children:"<LOAD_BALANCER_ACCOUNT_ID>"})," is different from your AWS account ID."]})}),"\n",(0,c.jsxs)(n.p,{children:["Replace ",(0,c.jsx)(n.code,{children:"<BUCKET_NAME>"})," with your ",(0,c.jsx)(n.code,{children:"system-bucket"})," name."]}),"\n",(0,c.jsxs)(n.p,{children:["Replace ",(0,c.jsx)(n.code,{children:"<PREFIX>"})," with your prefix."]}),"\n",(0,c.jsxs)(n.p,{children:["Replace ",(0,c.jsx)(n.code,{children:"<AWS_ACCOUNT_ID>"})," with your Cumulus OU account number."]})]})}function d(e={}){const{wrapper:n}={...(0,o.R)(),...e.components};return n?(0,c.jsx)(n,{...e,children:(0,c.jsx)(u,{...e})}):u(e)}},8453:(e,n,t)=>{t.d(n,{R:()=>i,x:()=>s});var r=t(6540);const c={},o=r.createContext(c);function i(e){const n=r.useContext(o);return r.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function s(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(c):e.components||c:i(e.components),r.createElement(o.Provider,{value:n},e.children)}}}]);