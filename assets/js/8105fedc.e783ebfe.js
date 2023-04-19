"use strict";(self.webpackChunkorca_website=self.webpackChunkorca_website||[]).push([[7544],{3905:(e,t,a)=>{a.d(t,{Zo:()=>m,kt:()=>k});var n=a(7294);function r(e,t,a){return t in e?Object.defineProperty(e,t,{value:a,enumerable:!0,configurable:!0,writable:!0}):e[t]=a,e}function i(e,t){var a=Object.keys(e);if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(e);t&&(n=n.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),a.push.apply(a,n)}return a}function o(e){for(var t=1;t<arguments.length;t++){var a=null!=arguments[t]?arguments[t]:{};t%2?i(Object(a),!0).forEach((function(t){r(e,t,a[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(a)):i(Object(a)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(a,t))}))}return e}function l(e,t){if(null==e)return{};var a,n,r=function(e,t){if(null==e)return{};var a,n,r={},i=Object.keys(e);for(n=0;n<i.length;n++)a=i[n],t.indexOf(a)>=0||(r[a]=e[a]);return r}(e,t);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);for(n=0;n<i.length;n++)a=i[n],t.indexOf(a)>=0||Object.prototype.propertyIsEnumerable.call(e,a)&&(r[a]=e[a])}return r}var p=n.createContext({}),s=function(e){var t=n.useContext(p),a=t;return e&&(a="function"==typeof e?e(t):o(o({},t),e)),a},m=function(e){var t=s(e.components);return n.createElement(p.Provider,{value:t},e.children)},u="mdxType",d={inlineCode:"code",wrapper:function(e){var t=e.children;return n.createElement(n.Fragment,{},t)}},c=n.forwardRef((function(e,t){var a=e.components,r=e.mdxType,i=e.originalType,p=e.parentName,m=l(e,["components","mdxType","originalType","parentName"]),u=s(a),c=r,k=u["".concat(p,".").concat(c)]||u[c]||d[c]||i;return a?n.createElement(k,o(o({ref:t},m),{},{components:a})):n.createElement(k,o({ref:t},m))}));function k(e,t){var a=arguments,r=t&&t.mdxType;if("string"==typeof e||r){var i=a.length,o=new Array(i);o[0]=c;var l={};for(var p in t)hasOwnProperty.call(t,p)&&(l[p]=t[p]);l.originalType=e,l[u]="string"==typeof e?e:r,o[1]=l;for(var s=2;s<i;s++)o[s]=a[s];return n.createElement.apply(null,o)}return n.createElement.apply(null,a)}c.displayName="MDXCreateElement"},9376:(e,t,a)=>{a.r(t),a.d(t,{assets:()=>s,contentTitle:()=>l,default:()=>d,frontMatter:()=>o,metadata:()=>p,toc:()=>m});var n=a(7462),r=(a(7294),a(3905)),i=a(4996);const o={id:"deploying-from-windows",title:"Deploy from Windows",description:"A concrete set of instructions on deploying from Windows to create a test environment."},l=void 0,p={unversionedId:"developer/deployment-guide/deploying-from-windows",id:"developer/deployment-guide/deploying-from-windows",title:"Deploy from Windows",description:"A concrete set of instructions on deploying from Windows to create a test environment.",source:"@site/docs/developer/deployment-guide/deploying-from-windows.mdx",sourceDirName:"developer/deployment-guide",slug:"/developer/deployment-guide/deploying-from-windows",permalink:"/cumulus-orca/docs/developer/deployment-guide/deploying-from-windows",draft:!1,editUrl:"https://github.com/nasa/cumulus-orca/edit/develop/website/docs/developer/deployment-guide/deploying-from-windows.mdx",tags:[],version:"current",frontMatter:{id:"deploying-from-windows",title:"Deploy from Windows",description:"A concrete set of instructions on deploying from Windows to create a test environment."},sidebar:"dev_guide",previous:{title:"Testing Deployment",permalink:"/cumulus-orca/docs/developer/deployment-guide/testing_deployment"},next:{title:"ORCA API Reference",permalink:"/cumulus-orca/docs/developer/api/orca-api"}},s={},m=[{value:"Notes",id:"notes",level:3},{value:"Application",id:"application",level:2},{value:"Initial Setup",id:"initial-setup",level:2},{value:"Cumulus",id:"cumulus",level:2}],u={toc:m};function d(e){let{components:t,...a}=e;return(0,r.kt)("wrapper",(0,n.Z)({},u,a,{components:t,mdxType:"MDXLayout"}),(0,r.kt)("p",null,"Deploying Cumulus, CumulusDashboard, and ORCA from Windows brings some additional challenges.\nThe goal of this page is to provide a set of modified instructions to get around common errors."),(0,r.kt)("h3",{id:"notes"},"Notes"),(0,r.kt)("ul",null,(0,r.kt)("li",{parentName:"ul"},"Choose a PREFIX that will identify your installation when in AWS. This string will be used throughout deployment."),(0,r.kt)("li",{parentName:"ul"},"Connect to the NASA VPN to be able to connect to AWS.",(0,r.kt)("admonition",{parentName:"li",type:"warning"},(0,r.kt)("p",{parentName:"admonition"},"The VPN drastically slows down Terraform operations, and limits what documentation can be viewed. Switch off when applicable."))),(0,r.kt)("li",{parentName:"ul"},"Commands here will use ",(0,r.kt)("inlineCode",{parentName:"li"},"us-west-2")," for region because of the current state of our sandbox and ESDIS recommendations. Replace consistently as needed.",(0,r.kt)("ul",{parentName:"li"},(0,r.kt)("li",{parentName:"ul"},"Make sure any operations in AWS are done under the correct region.")))),(0,r.kt)("h2",{id:"application"},"Application"),(0,r.kt)("p",null,"This application will be used in future steps to authenticate users."),(0,r.kt)("ul",null,(0,r.kt)("li",{parentName:"ul"},"Go to ",(0,r.kt)("a",{parentName:"li",href:"https://uat.urs.earthdata.nasa.gov/profile"},"https://uat.urs.earthdata.nasa.gov/profile")),(0,r.kt)("li",{parentName:"ul"},"Applications -> My Applications",(0,r.kt)("admonition",{parentName:"li",type:"tip"},(0,r.kt)("p",{parentName:"admonition"},"If this option is not present, then ",(0,r.kt)("a",{parentName:"p",href:"https://wiki.earthdata.nasa.gov/display/EL/How+To+Register+An+Application"},'you must get the "Application Developer" permission.')))),(0,r.kt)("li",{parentName:"ul"},"Create a new Application. Remember to update with your own prefix.",(0,r.kt)("ul",{parentName:"li"},(0,r.kt)("li",{parentName:"ul"},"Application ID: ",(0,r.kt)("inlineCode",{parentName:"li"},"PREFIX_cumulus")),(0,r.kt)("li",{parentName:"ul"},"Application Name ",(0,r.kt)("inlineCode",{parentName:"li"},"PREFIX Cumulus")),(0,r.kt)("li",{parentName:"ul"},"Application Type: ",(0,r.kt)("inlineCode",{parentName:"li"},"OAuth 2")),(0,r.kt)("li",{parentName:"ul"},"Redirect URL: For now, ",(0,r.kt)("inlineCode",{parentName:"li"},"http://localhost:3000/"),". Proper URLs will be defined in the ",(0,r.kt)("a",{parentName:"li",href:"#redirect-definition"},"ORCA deployment"),".")))),(0,r.kt)("h2",{id:"initial-setup"},"Initial Setup"),(0,r.kt)("ul",null,(0,r.kt)("li",{parentName:"ul"},"Follow the ",(0,r.kt)("a",{parentName:"li",href:"/cumulus-orca/docs/developer/deployment-guide/deployment-environment"},"deployment environment setup instructions"),".",(0,r.kt)("ul",{parentName:"li"},(0,r.kt)("li",{parentName:"ul"},"You may need to install Terraform manually."),(0,r.kt)("li",{parentName:"ul"},"Only configure the default profile."),(0,r.kt)("li",{parentName:"ul"},"Keep the access keys in plain-text. You will need to run ",(0,r.kt)("inlineCode",{parentName:"li"},"aws configure")," in multiple environments."))),(0,r.kt)("li",{parentName:"ul"},"Create an AWS Key Value Pair by following  ",(0,r.kt)("a",{parentName:"li",href:"https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#having-ec2-create-your-key-pair"},"the AWS instructions"),".",(0,r.kt)("ul",{parentName:"li"},(0,r.kt)("li",{parentName:"ul"},"Choose the '.pem' format."),(0,r.kt)("li",{parentName:"ul"},"Naming convention is PREFIX-key-pair.pem"))),(0,r.kt)("li",{parentName:"ul"},"Create buckets.",(0,r.kt)("ul",{parentName:"li"},(0,r.kt)("li",{parentName:"ul"},"Same OU and region would not be ideal for a real backup system, and is therefore not sufficient for testing."),(0,r.kt)("li",{parentName:"ul"},"Required buckets are PREFIX-tf-state, PREFIX-orca-primary, PREFIX-internal, PREFIX-private, PREFIX-protected, PREFIX-public, and PREFIX-orca-reports",(0,r.kt)("ul",{parentName:"li"},(0,r.kt)("li",{parentName:"ul"},"PREFIX-orca-* buckets go in a separate DR account. Other buckets simulate Cumulus-managed buckets, and should be placed in the base account.",(0,r.kt)("admonition",{parentName:"li",type:"tip"},(0,r.kt)("p",{parentName:"admonition"},"An example command for creating a bucket in us-west-2. Remember to run ",(0,r.kt)("inlineCode",{parentName:"p"},"aws configure")," for the proper account first.")))),(0,r.kt)("pre",{parentName:"li"},(0,r.kt)("code",{parentName:"pre",className:"language-commandline"},'aws s3api create-bucket --bucket PREFIX-tf-state --profile default --region us-west-2 --create-bucket-configuration "LocationConstraint=us-west-2"\n')))))),(0,r.kt)("h2",{id:"cumulus"},(0,r.kt)("a",{parentName:"h2",href:"https://nasa.github.io/cumulus/docs/deployment/deployment-readme"},"Cumulus")),(0,r.kt)("ul",null,(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"If creating a realistic setup with multiple OUs, apply ",(0,r.kt)("a",{parentName:"p",href:"/cumulus-orca/docs/developer/deployment-guide/deployment-s3-bucket"},"Create the ORCA Archive Bucket")," to your PREFIX-orca-primary and PREFIX-orca-reports.")),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"Run"),(0,r.kt)("pre",{parentName:"li"},(0,r.kt)("code",{parentName:"pre",className:"language-commandline"},"aws dynamodb create-table --table-name PREFIX-tf-locks --attribute-definitions AttributeName=LockID,AttributeType=S --key-schema AttributeName=LockID,KeyType=HASH --billing-mode PAY_PER_REQUEST --region us-west-2\n"))),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"Run"),(0,r.kt)("pre",{parentName:"li"},(0,r.kt)("code",{parentName:"pre",className:"language-commandline"},"aws s3api put-bucket-versioning --bucket PREFIX-tf-state --versioning-configuration Status=Enabled\n")),(0,r.kt)("admonition",{parentName:"li",type:"tip"},(0,r.kt)("p",{parentName:"admonition"},"VPC and Subnets are created by ",(0,r.kt)("a",{parentName:"p",href:"https://wiki.earthdata.nasa.gov/display/ESKB/AWS+Services+Approval+Status+Page#AWSServicesApprovalStatusPage-VPC"},"NGAP"),".\nIt is recommended you copy values from an existing deployment setup."))),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"Go to ",(0,r.kt)("a",{parentName:"p",href:"https://git.earthdata.nasa.gov/projects/ORCA/repos/cumulus-orca-deploy-template/browse"},"this repo")," and clone it to your machine."),(0,r.kt)("admonition",{parentName:"li",type:"warning"},(0,r.kt)("p",{parentName:"admonition"},"It is strongly recommended to use a tested release branch rather than master. These instructions have been tested with ",(0,r.kt)("inlineCode",{parentName:"p"},"release/v9.4.0-v3.0.1")))),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"Unzip.")),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"Remove the '.example' on terraform.tf and terraform.tfvars files in data-persistence-tf, cumulus-tf, and rds-cluster-tf.")),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"Globally find and replace ",(0,r.kt)("inlineCode",{parentName:"p"},"postgres_user_pw")," to ",(0,r.kt)("inlineCode",{parentName:"p"},"db_admin_password")," and ",(0,r.kt)("inlineCode",{parentName:"p"},"database_app_user_pw")," to ",(0,r.kt)("inlineCode",{parentName:"p"},"db_user_password"),".")),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"In each terraform.tf and terraform.tfvars, use your own prefix, region, vpc id, and subnet ids."),(0,r.kt)("admonition",{parentName:"li",type:"warning"},(0,r.kt)("p",{parentName:"admonition"},"The region and prefix are not always in simple variables. Do a global search for 'PREFIX' and 'us-east-1'.")),(0,r.kt)("admonition",{parentName:"li",type:"warning"},(0,r.kt)("p",{parentName:"admonition"},"Only use the non-lambda subnet id in the data-persistence-tf/terraform.tfvars. In cumulus-tf use both.")),(0,r.kt)("admonition",{parentName:"li",type:"warning"},(0,r.kt)("p",{parentName:"admonition"},"Overwrite the ",(0,r.kt)("inlineCode",{parentName:"p"},"orca-sandbox")," in ",(0,r.kt)("inlineCode",{parentName:"p"},"orca-sandbox-tf-locks")," with your prefix as well."))),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"In rds-cluster-tf/terraform.tfvars"),(0,r.kt)("ul",{parentName:"li"},(0,r.kt)("li",{parentName:"ul"},"Use values of your choice for ",(0,r.kt)("inlineCode",{parentName:"li"},"db_admin_username")," and ",(0,r.kt)("inlineCode",{parentName:"li"},"db_admin_password")),(0,r.kt)("li",{parentName:"ul"},"Set ",(0,r.kt)("inlineCode",{parentName:"li"},"tags")," to ",(0,r.kt)("inlineCode",{parentName:"li"},'{ "Deployment" = "PREFIX" }')),(0,r.kt)("li",{parentName:"ul"},"Set ",(0,r.kt)("inlineCode",{parentName:"li"},"permissions_boundary_arn")," to ",(0,r.kt)("inlineCode",{parentName:"li"},"arn:aws:iam::YOUR ACCOUNT ID:policy/NGAPShRoleBoundary")),(0,r.kt)("li",{parentName:"ul"},"Add ",(0,r.kt)("inlineCode",{parentName:"li"},'rds_user_password = "CumulusD3faultPassw0rd"')," and change as desired."),(0,r.kt)("li",{parentName:"ul"},"Set ",(0,r.kt)("inlineCode",{parentName:"li"},"provision_user_database")," to ",(0,r.kt)("inlineCode",{parentName:"li"},"true")),(0,r.kt)("li",{parentName:"ul"},"Set ",(0,r.kt)("inlineCode",{parentName:"li"},"cluster_identifier")," to ",(0,r.kt)("inlineCode",{parentName:"li"},'"PREFIX-cumulus-db"')))),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"In rds-cluster-tf/terraform.tf"),(0,r.kt)("ul",{parentName:"li"},(0,r.kt)("li",{parentName:"ul"},"Set ",(0,r.kt)("inlineCode",{parentName:"li"},"bucket")," to ",(0,r.kt)("inlineCode",{parentName:"li"},'"PREFIX-tf-state"')),(0,r.kt)("li",{parentName:"ul"},"Set ",(0,r.kt)("inlineCode",{parentName:"li"},"key")," to ",(0,r.kt)("inlineCode",{parentName:"li"},'"PREFIX/cumulus/terraform.tfstate"')),(0,r.kt)("li",{parentName:"ul"},"Set ",(0,r.kt)("inlineCode",{parentName:"li"},"dynamodb_table")," to ",(0,r.kt)("inlineCode",{parentName:"li"},'"PREFIX-tf-locks"')))),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"Go to ",(0,r.kt)("a",{parentName:"p",href:"https://github.com/asfadmin/CIRRUS-core/blob/master/Dockerfile"},"https://github.com/asfadmin/CIRRUS-core/blob/master/Dockerfile")," and download the file to the same folder as your downloaded repo and orca folder."),(0,r.kt)("admonition",{parentName:"li",type:"tip"},(0,r.kt)("p",{parentName:"admonition"},"Make sure that no extension is added."))),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"Open a commandline in the same folder."),(0,r.kt)("ul",{parentName:"li"},(0,r.kt)("li",{parentName:"ul"},"Run ",(0,r.kt)("inlineCode",{parentName:"li"},"docker build -t orca .")," and ",(0,r.kt)("inlineCode",{parentName:"li"},"docker run -it --rm -v pathToYourFolder:/CIRRUS-core orca /bin/bash")),(0,r.kt)("li",{parentName:"ul"},"The commandline should now be inside a docker container.",(0,r.kt)("pre",{parentName:"li"},(0,r.kt)("code",{parentName:"pre",className:"language-bash"},"cd cumulus-orca-template-deploy/rds-cluster-tf/\naws configure\nterraform init\nterraform plan\nterraform apply\n"))))),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"In data-persistence-tf/terraform.tfvars"),(0,r.kt)("ul",{parentName:"li"},(0,r.kt)("li",{parentName:"ul"},"Set ",(0,r.kt)("inlineCode",{parentName:"li"},"permissions_boundary_arn")," to ",(0,r.kt)("inlineCode",{parentName:"li"},"arn:aws:iam::12345:policy/NGAPShRoleBoundary")," replacing the ",(0,r.kt)("inlineCode",{parentName:"li"},"12345")," with your Account Id.",(0,r.kt)("img",{alt:"Location of Account Id",src:(0,i.Z)("img/aws-account-id.PNG")})),(0,r.kt)("li",{parentName:"ul"},"Set ",(0,r.kt)("inlineCode",{parentName:"li"},"rds_user_access_secret_arn")," to the ",(0,r.kt)("inlineCode",{parentName:"li"},"user_credentials_secret_urn")," output from ",(0,r.kt)("inlineCode",{parentName:"li"},"terraform apply"),"."),(0,r.kt)("li",{parentName:"ul"},"Set ",(0,r.kt)("inlineCode",{parentName:"li"},"rds_security_group")," to the ",(0,r.kt)("inlineCode",{parentName:"li"},"security_group_id")," output from ",(0,r.kt)("inlineCode",{parentName:"li"},"terraform apply"),"."),(0,r.kt)("li",{parentName:"ul"},"Set ",(0,r.kt)("inlineCode",{parentName:"li"},"vpc_id")," to your borrowed VPC.")))),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-bash"},"cd ../data-persistence-tf/\naws configure\nterraform init\nterraform plan\nterraform apply\n")),(0,r.kt)("ul",null,(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"In cumulus-tf/terraform.tfvars"),(0,r.kt)("ul",{parentName:"li"},(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"Replace 12345 in permissions_boundary_arn with the Account Id.")),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"Add to the buckets:"),(0,r.kt)("pre",{parentName:"li"},(0,r.kt)("code",{parentName:"pre"},'orca_default = {\n  name = "PREFIX-orca-primary"\n  type = "orca"\n},\nprovider = {\n  name = "orca-sandbox-s3-provider"\n  type = "provider"\n}\n')),(0,r.kt)("admonition",{parentName:"li",type:"tip"},(0,r.kt)("p",{parentName:"admonition"},'The "orca-sandbox-s3-provider" bucket contains test data.\nIf creating a separate environment, you can create your own bucket.\nIt is recommended that all buckets include the same test data.'))),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"If the CMA is not deployed, follow ",(0,r.kt)("a",{parentName:"p",href:"https://nasa.github.io/cumulus/docs/deployment/deployment-readme#deploy-the-cumulus-message-adapter-layer"},"the deployment instructions")," and note the version used. Must match ",(0,r.kt)("inlineCode",{parentName:"p"},"cumulus_message_adapter_version"),".\nIf you have already deployed your own CMA layer, it can be found using"),(0,r.kt)("pre",{parentName:"li"},(0,r.kt)("code",{parentName:"pre"},"aws lambda --profile default list-layers --query \"Layers[?LayerName=='PREFIX-CMA-layer'].[LayerName, LayerArn, LatestMatchingVersion.LayerVersionArn]\"\n")),(0,r.kt)("p",{parentName:"li"},":::")),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"Comment out the ",(0,r.kt)("inlineCode",{parentName:"p"},"ecs_cluster_instance_image_id"),". This will use the latest NGAP ECS image.")),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},(0,r.kt)("inlineCode",{parentName:"p"},"ecs_cluster_instance_subnet_ids")," and ",(0,r.kt)("inlineCode",{parentName:"p"},"lambda_subnet_ids")," should have the same two values.")),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"Set ",(0,r.kt)("inlineCode",{parentName:"p"},"urs_client_id")," and ",(0,r.kt)("inlineCode",{parentName:"p"},"urs_client_password")," to the values from your created application.")),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"Add an extra property ",(0,r.kt)("inlineCode",{parentName:"p"},'urs_url = "https://uat.urs.earthdata.nasa.gov"'))),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"Add your username to the ",(0,r.kt)("inlineCode",{parentName:"p"},"api_users")),(0,r.kt)("ul",{parentName:"li"},(0,r.kt)("li",{parentName:"ul"},"If you want all Orca developers to have access, set to",(0,r.kt)("pre",{parentName:"li"},(0,r.kt)("code",{parentName:"pre"},'api_users = [\n  "bhazuka",\n  "andrew.dorn",\n  "rizbi.hassan",\n  "scott.saxon",\n]\n'))))),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"Comment out the ",(0,r.kt)("inlineCode",{parentName:"p"},"archive_api_port")," property and value.")),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"Uncomment the ",(0,r.kt)("inlineCode",{parentName:"p"},"key_name property")," and set the value to ",(0,r.kt)("inlineCode",{parentName:"p"},'"PREFIX-key-pair"'))),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"Add this section to the bottom of the file and edit as desired:"),(0,r.kt)("pre",{parentName:"li"},(0,r.kt)("code",{parentName:"pre"},'## =============================================================================\n## ORCA Variables\n## =============================================================================\n\n## REQUIRED TO BE SET\n## -----------------------------------------------------------------------------\n\n## ORCA application database user password.\ndb_user_password = "This1sAS3cr3t"\n\n## Default archive bucket to use\norca_default_bucket = PREFIX-orca-primary"\n\n## PostgreSQL database (root) user password\ndb_admin_password = "An0th3rS3cr3t"\n')),(0,r.kt)("admonition",{parentName:"li",type:"warning"},(0,r.kt)("p",{parentName:"admonition"},"The instructions in the tfvars file suggest swapping '12345' with your account ID. This may not work, depending on how your dependencies were set up."))))),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("p",{parentName:"li"},"In cumulus-tf/orca.tf:"),(0,r.kt)("ul",{parentName:"li"},(0,r.kt)("li",{parentName:"ul"},"Remove the ",(0,r.kt)("inlineCode",{parentName:"li"},"aws_profile")," and ",(0,r.kt)("inlineCode",{parentName:"li"},"region")," variables."),(0,r.kt)("li",{parentName:"ul"},"Replace the ",(0,r.kt)("inlineCode",{parentName:"li"},"ORCA Variables")," section with the following:",(0,r.kt)("pre",{parentName:"li"},(0,r.kt)("code",{parentName:"pre"},'## --------------------------\n## ORCA Variables\n## --------------------------\n## REQUIRED\norca_default_bucket   = var.orca_default_bucket\ndb_admin_password     = var.db_admin_password\ndb_user_password      = var.db_user_password\ndb_host_endpoint      = var.db_host_endpoint\nrds_security_group_id = var.rds_security_group_id\n## OPTIONAL\ndb_admin_username                                    = "postgres"\norca_delete_old_reconcile_jobs_frequency_cron        = "cron(0 0 ? * SUN *)"\norca_ingest_lambda_memory_size                       = 2240\norca_ingest_lambda_timeout                           = 600\norca_internal_reconciliation_expiration_days         = 30\norca_recovery_buckets                                = []\norca_recovery_complete_filter_prefix                 = ""\norca_recovery_expiration_days                        = 5\norca_recovery_lambda_memory_size                     = 128\norca_recovery_lambda_timeout                         = 300\norca_recovery_retry_limit                            = 3\norca_recovery_retry_interval                         = 1\norca_recovery_retry_backoff                          = 2\ns3_inventory_queue_message_retention_time_seconds    = 432000\ns3_report_frequency                                  = "Daily"\nsqs_delay_time_seconds                               = 0\nsqs_maximum_message_size                             = 262144\nstaged_recovery_queue_message_retention_time_seconds = 432000\nstatus_update_queue_message_retention_time_seconds   = 777600\n'))),(0,r.kt)("li",{parentName:"ul"},"Set the value of ",(0,r.kt)("inlineCode",{parentName:"li"},"db_host_endpoint")," to the ",(0,r.kt)("inlineCode",{parentName:"li"},"rds_endpoint")," value output from the rds-cluster deployment."),(0,r.kt)("li",{parentName:"ul"},"Set the value of ",(0,r.kt)("inlineCode",{parentName:"li"},"rds_security_group_id")," to the ",(0,r.kt)("inlineCode",{parentName:"li"},"security_group_id")," value output from the rds-cluster deployment."),(0,r.kt)("li",{parentName:"ul"},"You may change ",(0,r.kt)("inlineCode",{parentName:"li"},"source")," to an alternate release. If local, make sure it is within the scope of the container.")))),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-bash"},"cd ../cumulus-tf\nterraform init\nterraform plan\nterraform apply\n")),(0,r.kt)("a",{name:"redirect-definition"}),(0,r.kt)("ul",null,(0,r.kt)("li",{parentName:"ul"},"Go to ",(0,r.kt)("a",{parentName:"li",href:"https://uat.urs.earthdata.nasa.gov/profile"},"https://uat.urs.earthdata.nasa.gov/profile")),(0,r.kt)("li",{parentName:"ul"},"Applications -> My Applications"),(0,r.kt)("li",{parentName:"ul"},"Click on the Edit button for your application."),(0,r.kt)("li",{parentName:"ul"},"Click on Manage -> Redirect Uris"),(0,r.kt)("li",{parentName:"ul"},"Add http://localhost:3000/auth and the ",(0,r.kt)("inlineCode",{parentName:"li"},"archive_api_redirect_uri")," and ",(0,r.kt)("inlineCode",{parentName:"li"},"distribution_redirect_uri")," output from ",(0,r.kt)("inlineCode",{parentName:"li"},"terraform apply"),".")))}d.isMDXComponent=!0}}]);