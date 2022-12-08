"use strict";(self.webpackChunkorca_website=self.webpackChunkorca_website||[]).push([[277,2083],{3622:function(e,t,a){a.r(t),a.d(t,{assets:function(){return m},contentTitle:function(){return c},default:function(){return g},frontMatter:function(){return d},metadata:function(){return u},toc:function(){return h}});var n=a(7462),o=a(3366),i=(a(7294),a(3905)),r=a(4079),s=a(4996),l=["components"],d={id:"research-orca-delete-functionality",title:"Research Notes on ORCA delete functionality.",description:"Research Notes on implementing delete functionality for ORCA."},c=void 0,u={unversionedId:"developer/research/research-orca-delete-functionality",id:"developer/research/research-orca-delete-functionality",title:"Research Notes on ORCA delete functionality.",description:"Research Notes on implementing delete functionality for ORCA.",source:"@site/docs/developer/research/research-orca-delete-functionality.mdx",sourceDirName:"developer/research",slug:"/developer/research/research-orca-delete-functionality",permalink:"/cumulus-orca/docs/developer/research/research-orca-delete-functionality",draft:!1,editUrl:"https://github.com/nasa/cumulus-orca/edit/develop/website/docs/developer/research/research-orca-delete-functionality.mdx",tags:[],version:"current",frontMatter:{id:"research-orca-delete-functionality",title:"Research Notes on ORCA delete functionality.",description:"Research Notes on implementing delete functionality for ORCA."},sidebar:"dev_guide",previous:{title:"Using Lambda functions as container research Notes",permalink:"/cumulus-orca/docs/developer/research/research-lambda-container"},next:{title:"Research Notes on running integration tests in bamboo CI/CD",permalink:"/cumulus-orca/docs/developer/research/research-bamboo-integration-tests"}},m={},h=[{value:"Delete functionality use cases",id:"delete-functionality-use-cases",level:2},{value:"Initial ORCA Delete Functionality Architecture",id:"initial-orca-delete-functionality-architecture",level:2},{value:"User Interface",id:"user-interface",level:3},{value:"API gateway",id:"api-gateway",level:3},{value:"Lambda function",id:"lambda-function",level:3},{value:"Deleting objects from AWS S3",id:"deleting-objects-from-aws-s3",level:3},{value:"Example Using delete_objects",id:"example-using-delete_objects",level:4},{value:"Logging for Auditing",id:"logging-for-auditing",level:3},{value:"Open Questions yet to be answered",id:"open-questions-yet-to-be-answered",level:2},{value:"Future directions",id:"future-directions",level:2},{value:"References",id:"references",level:5}],p={toc:h};function g(e){var t=e.components,a=(0,o.Z)(e,l);return(0,i.kt)("wrapper",(0,n.Z)({},p,a,{components:t,mdxType:"MDXLayout"}),(0,i.kt)("h2",{id:"delete-functionality-use-cases"},"Delete functionality use cases"),(0,i.kt)("p",null,"Some use cases for delete functionality are as follows:"),(0,i.kt)("ul",null,(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("p",{parentName:"li"},"As a DAAC, I would like to remove data from ORCA that is invalid or expired in order to maintain a clean data archive.\nThis can be achieved by a two-step process- an initial soft delete initiated by user, and a physical delete to permanently delete the data from S3 and database.\nIt is assumed that the process is not automated and must be initiated by the user with an API call for both steps.")),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("p",{parentName:"li"},"As a DAAC, I would like to remove data from ORCA only if it has been in glacier for more than 90 days from initial ingest to keep from incurring additional cost for early removal."),(0,i.kt)("p",{parentName:"li"},"  This can be implemented by using soft delete. We can either flag the data in the database with a new column named ",(0,i.kt)("inlineCode",{parentName:"p"},"Pending Deletion")," or we can create a separate table that contains those data marked for deletion. Then after 90 days, we can permanently delete from the DB as well as the glacier bucket.\nIf the data is stored in standard it would be 90 days but for deep glacier, it would be 180 days. If the time the data stays in ORCA is less than the initial (90/180) days from ingest, any kind of delete operation will not be allowed. Some business logic should be added to the code to execute this rule."))),(0,i.kt)("ul",null,(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("p",{parentName:"li"},"As a DAAC, I would like to configure the amount of time data remains in ORCA after being signaled to be deleted.\t"),(0,i.kt)("p",{parentName:"li"},"  This should be configurable by each DAAC that is using ORCA. The number of days it would stay in ORCA would be based off of the soft delete date. Once the data stays in ORCA for greater than 90/180 days based on the glacier storage type used, that data would be eligible for a soft delete.\nThe data would be eligible for a physical delete after the configured x days after the soft delete date.\nThe data should stay in ORCA for x number of days for safety reasons. The configuration should be done using an environment variable during deployment. It is assumed that the configuration cannot be overridden except with a new deployment.\nAdditionally, ORCA should prevent deletion of any kind from certain data like Level 0 or base data sets that\nare static. Some ways to implement this would be to have a configuration parameter we capture that says\nwe are not able to delete from this collection or use an S3 bucket having bucket policies that prevents any\ndeletes from happening."))),(0,i.kt)("ul",null,(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("p",{parentName:"li"},"As a DAAC, I would like only authorized personnel to be able to remove data from ORCA in a controlled way to minimize risk of accidental or malicious deletions."),(0,i.kt)("p",{parentName:"li"},"  This could be implemented with the use of NASA launchpad authentication since other teams such as Cumulus are already using this approach. This ",(0,i.kt)("a",{parentName:"p",href:"https://idmax.nasa.gov/nams/asset/255115"},"link")," is used to submit a new GSFC workflow request and most probably will be used to only allow specific users to perform the deletes. Contact ",(0,i.kt)("inlineCode",{parentName:"p"},"robert.a.meredith@nasa.gov")," and ",(0,i.kt)("inlineCode",{parentName:"p"},"tadd.buffington@nasa.gov")," with any issues regarding launchpad integration.\nThe api gateway resource policy can be used to restrict certain users from accessing the api endpoint. For more information, see ",(0,i.kt)("a",{parentName:"p",href:"https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-resource-policies.html"},"Controlling access to an API with API Gateway resource policies"),".\nAnother technology to look into would be AWS Cognito which can be used to create customizable authentication and authorization solutions for the REST API. Amazon Cognito user pools are used to control who can invoke REST API methods. For more information, see ",(0,i.kt)("a",{parentName:"p",href:"https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-integrate-with-cognito.html"},"Control access to a REST API using Amazon Cognito user pools as authorizer"),"."))),(0,i.kt)("div",{className:"admonition admonition-note alert alert--secondary"},(0,i.kt)("div",{parentName:"div",className:"admonition-heading"},(0,i.kt)("h5",{parentName:"div"},(0,i.kt)("span",{parentName:"h5",className:"admonition-icon"},(0,i.kt)("svg",{parentName:"span",xmlns:"http://www.w3.org/2000/svg",width:"14",height:"16",viewBox:"0 0 14 16"},(0,i.kt)("path",{parentName:"svg",fillRule:"evenodd",d:"M6.3 5.69a.942.942 0 0 1-.28-.7c0-.28.09-.52.28-.7.19-.18.42-.28.7-.28.28 0 .52.09.7.28.18.19.28.42.28.7 0 .28-.09.52-.28.7a1 1 0 0 1-.7.3c-.28 0-.52-.11-.7-.3zM8 7.99c-.02-.25-.11-.48-.31-.69-.2-.19-.42-.3-.69-.31H6c-.27.02-.48.13-.69.31-.2.2-.3.44-.31.69h1v3c.02.27.11.5.31.69.2.2.42.31.69.31h1c.27 0 .48-.11.69-.31.2-.19.3-.42.31-.69H8V7.98v.01zM7 2.3c-3.14 0-5.7 2.54-5.7 5.68 0 3.14 2.56 5.7 5.7 5.7s5.7-2.55 5.7-5.7c0-3.15-2.56-5.69-5.7-5.69v.01zM7 .98c3.86 0 7 3.14 7 7s-3.14 7-7 7-7-3.12-7-7 3.14-7 7-7z"}))),"note")),(0,i.kt)("div",{parentName:"div",className:"admonition-content"},(0,i.kt)("p",{parentName:"div"},"Authentication and authorization piece of this functionality needs further research to make sure only authorized users can perform deletes."))),(0,i.kt)("div",{className:"admonition admonition-warning alert alert--danger"},(0,i.kt)("div",{parentName:"div",className:"admonition-heading"},(0,i.kt)("h5",{parentName:"div"},(0,i.kt)("span",{parentName:"h5",className:"admonition-icon"},(0,i.kt)("svg",{parentName:"span",xmlns:"http://www.w3.org/2000/svg",width:"12",height:"16",viewBox:"0 0 12 16"},(0,i.kt)("path",{parentName:"svg",fillRule:"evenodd",d:"M5.05.31c.81 2.17.41 3.38-.52 4.31C3.55 5.67 1.98 6.45.9 7.98c-1.45 2.05-1.7 6.53 3.53 7.7-2.2-1.16-2.67-4.52-.3-6.61-.61 2.03.53 3.33 1.94 2.86 1.39-.47 2.3.53 2.27 1.67-.02.78-.31 1.44-1.13 1.81 3.42-.59 4.78-3.42 4.78-5.56 0-2.84-2.53-3.22-1.25-5.61-1.52.13-2.03 1.13-1.89 2.75.09 1.08-1.02 1.8-1.86 1.33-.67-.41-.66-1.19-.06-1.78C8.18 5.31 8.68 2.45 5.05.32L5.03.3l.02.01z"}))),"warning")),(0,i.kt)("div",{parentName:"div",className:"admonition-content"},(0,i.kt)("p",{parentName:"div"},"Currently AWS Cognito has some restrictions from use in production environments and should be avoided for now."))),(0,i.kt)("ul",null,(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("p",{parentName:"li"},"As a DAAC, I would like duplicate data to be versioned in ORCA in order to recover the proper version of the data based on the type of failure.\t"),(0,i.kt)("p",{parentName:"li"},"  Versioning can be enabled at the bucket level by configuring the bucket properties via terraform or AWS console. After versioning is enabled in a bucket, it can never return to an unversioned state but can only be suspended on that bucket. Versioning can help recover objects from accidental deletion or overwrite. For example, if an object is deleted, Amazon S3 inserts a delete marker instead of removing the object permanently. The delete marker becomes the current object version. If the object is overwritten, it results in a new object version in the bucket. The previous version can always be restored. For more information, see ",(0,i.kt)("a",{parentName:"p",href:"https://docs.aws.amazon.com/AmazonS3/latest/userguide/DeletingObjectVersions.html"},"Deleting object versions from a versioning-enabled bucket"),".\nThe drawback of using versioning is the additional cost of storage for that versioned object. This can be solved by using object versioning with S3 Lifecycle policy. After a certain period of time defined, the versioned object will be marked as expired and automatically deleted from S3 bucket. This can be configured in bucket management via terraform. For more information, see ",(0,i.kt)("a",{parentName:"p",href:"https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html"},"S3 lifecycle policy"),"\n"))),(0,i.kt)("ul",null,(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("p",{parentName:"li"},"Perform a check with CMR and/or Cumulus to verify that the granule has been deleted from those locations prior to allowing the delete to proceed in ORCA."),(0,i.kt)("p",{parentName:"li"},"  This can be implemented in the existing lambda function that will be used to delete the data from ORCA.\nBefore deleting from CMR and Cumulus, the UI should show a warning message to the user for additional confirmation. Additional items need to be discussed on this rule to determine when and how it would be implemented and to address corner cases like versioned file removal."))),(0,i.kt)("h2",{id:"initial-orca-delete-functionality-architecture"},"Initial ORCA Delete Functionality Architecture"),(0,i.kt)("p",null,"The following is a potential architecture for ORCA delete functionality. Note that this could possibly change after discussing open questions with other teams."),(0,i.kt)(r.default,{imageSource:(0,s.Z)("img/ORCA-Delete-Functionality-Architecture-Initial.png"),imageAlt:"System Context",zoomInPic:(0,s.Z)("img/zoom-in.png"),zoomOutPic:(0,s.Z)("img/zoom-out.png"),resetPic:(0,s.Z)("img/zoom-pan-reset.png"),mdxType:"MyImage"}),(0,i.kt)("h3",{id:"user-interface"},"User Interface"),(0,i.kt)("p",null,"The user interface is used to show warning messages to end user while performing the deletes. The UI should be able to interact with Cumulus dashboard and other apps as needed.\nIt also makes api calls to the API gateway for delete operations."),(0,i.kt)("h3",{id:"api-gateway"},"API gateway"),(0,i.kt)("p",null,"API gateway is currently used by end users for creating reconciliation reports and getting status update of recovery granules and jobs. This can be used for creating API calls made by end users for deletion.\nThe API gateway should act as a trigger to the lambda functions that actually perform the deletion in the backend. In addition, it should also trigger a login lambda function that gets the authentication token from Launchpad possibly for user login and verification.\nAn API gateway with two different resources need to be created- one for the soft delete API call and one for the hard delete API call. In order to deploy this via terraform, a private rest api with two resources need to be created. In case of using private API, the vpc endpoint ID for the gateway will be required.\nThe REST API should use a ",(0,i.kt)("inlineCode",{parentName:"p"},"POST")," http method and the integration type should be ",(0,i.kt)("inlineCode",{parentName:"p"},"AWS"),".\nIf lambda function is used with the API, a lambda permission resource should be created in terraform giving access to ",(0,i.kt)("inlineCode",{parentName:"p"},"lambda:InvokeFunction")," action so that the API can trigger the lambda. In addition, the api gateway resource policy can be used to restrict certain IP addresses and VPC if needed from accessing the API endpoint. Check API gateway ",(0,i.kt)("a",{parentName:"p",href:"https://github.com/nasa/cumulus-orca/tree/develop/modules/api-gateway"},"examples")," currently used by ORCA. "),(0,i.kt)("h3",{id:"lambda-function"},"Lambda function"),(0,i.kt)("p",null,"The delete functionality can be performed by two lambda functions based on initial research. One of the lambda functions will be used to perform soft delete- only flag the granule in the database for deletion after 90 days in case of standard glacier or 180 days in case of deep glacier. The lambda should also verify with CMR and/or Cumulus that the granule has been deleted from those locations prior to allowing the delete to proceed in ORCA. The lambda will be triggered by an API call made by the user once the user is authenticated with Launchpad."),(0,i.kt)("p",null,"The other lambda function can be used to perform a physical delete- delete from S3 glacier as well as from the database.\nThe lambda code should addresses the rule that the data cannot be physically deleted until the DAAC configured x number of days. This will require further discussions with ORCA team and ORCA Working group before performing the actual work."),(0,i.kt)("h3",{id:"deleting-objects-from-aws-s3"},"Deleting objects from AWS S3"),(0,i.kt)("p",null,"To delete an object from an S3 bucket, the ",(0,i.kt)("a",{parentName:"p",href:"https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_objects"},"delete_objects"),"\ncan be used from the boto3 library. An example of the usage can be seen below.\nSome notable items if this library is used includes the following."),(0,i.kt)("ul",null,(0,i.kt)("li",{parentName:"ul"},"It can be used to delete up to 1000 objects from a bucket using a single API call."),(0,i.kt)("li",{parentName:"ul"},"When performing this action on an MFA Delete enabled bucket that attempts to delete any versioned objects, an MFA token must be included or else it will fail."),(0,i.kt)("li",{parentName:"ul"},"If the object specified in the request is not found, Amazon S3 returns the result as deleted."),(0,i.kt)("li",{parentName:"ul"},"Each DeleteObjects API incurs a little cost of $0.05/10000 requests.")),(0,i.kt)("h4",{id:"example-using-delete_objects"},"Example Using delete_objects"),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-python"},'import boto3\n\ns3_client = boto3.client(\'s3\')\nbucket = "riz-orca"\nresponse = s3_client.delete_objects(\n    Bucket=bucket,\n    Delete={\n        \'Objects\': [\n            {\n                \'Key\': \'MOD09A1.006/MOD09A1.A2019025.h07v03.006.2019037205734.hdf\',\n            }\n        ]\n    }\n)\nprint(response)\n\n# Results\n{\n   "ResponseMetadata":{\n      "RequestId":"KJCZAPM0RWMJNNC7",\n      "HostId":"z2fRlgMxT10ApzcyDOLp3REn3PjM71OSgdH0oPpe4v2pHchmSTPCfEjBjTx00PyTL55wgmQ7gF4=",\n      "HTTPStatusCode":200,\n      "HTTPHeaders":{\n         "x-amz-id-2":"z2fRlgMxT10ApzcyDOLp3REn3PjM71OSgdH0oPpe4v2pHchmSTPCfEjBjTx00PyTL55wgmQ7gF4=",\n         "x-amz-request-id":"KJCZAPM0RWMJNNC7",\n         "date":"Tue, 08 Mar 2022 05:19:07 GMT",\n         "content-type":"application/xml",\n         "transfer-encoding":"chunked",\n         "server":"AmazonS3",\n         "connection":"close"\n      },\n      "RetryAttempts":0\n   },\n   "Deleted":[\n      {\n         "Key":"MOD09A1.006/MOD09A1.A2019025.h07v03.006.2019037205734.hdf"\n      }\n   ]\n}\n')),(0,i.kt)("h3",{id:"logging-for-auditing"},"Logging for Auditing"),(0,i.kt)("p",null,"Additional logging should be collected during the deletion process to keep records for safety and security purposes. Some logging to capture might include who deleted the data, when how many granules were deleted over a particular timespan, from which collections was it deleted, and what workflow was used to delete them."),(0,i.kt)("p",null,"Cloudwatch logs and cloudtrail can be used to collect logging information. In addition, S3 server access logging can be used at the bucket level which would provide detailed records for the requests that are made to a bucket. The log information can be useful in security and access audits. AWS will collect access log records, add the records in log files, and then upload log files to the target bucket as log objects. There is no extra charge for using the service except the cost for storing the log files in S3."),(0,i.kt)("h2",{id:"open-questions-yet-to-be-answered"},"Open Questions yet to be answered"),(0,i.kt)("p",null,"The following questions should be discussed with the broader team before implementing the work."),(0,i.kt)("ul",null,(0,i.kt)("li",{parentName:"ul"},"Regarding user authentication and authorization for deletes, do we have to pass any temporary tokens? How will this integrate with Cumulus calls to our API? Do we utilize an authentication token from API gateway?"),(0,i.kt)("li",{parentName:"ul"},"Since",(0,i.kt)("inlineCode",{parentName:"li"},"deleteObjects")," boto3 API call is limited to 1000 deletes per call, can we batch this up? Are there better ways to do batch deletes? What are the rules this has to follow?"),(0,i.kt)("li",{parentName:"ul"},"What information should we capture from the delete logs? Do we delete the records, move them to an audit table or store them in S3 like in server access logging? How long do we keep them?"),(0,i.kt)("li",{parentName:"ul"},"How do we handle situations like deleting a version of a granule and not the complete granule?"),(0,i.kt)("li",{parentName:"ul"},"When removing versioned data granule, do we remove all the versions or do we remove all but the last and keep the delete marked version for longer?")),(0,i.kt)("h2",{id:"future-directions"},"Future directions"),(0,i.kt)("p",null,"Few cards have been created to perform the ORCA delete functionality work based on initial research. It can be assumed that some of these cards will get modified once we have more discussion with other teams. This should be revisited during PI planning/team meetings to confirm the use cases/requirements before starting the work.\nSome of the cards created to finish the task include:"),(0,i.kt)("ul",null,(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("a",{parentName:"li",href:"https://bugs.earthdata.nasa.gov/browse/ORCA-394-"},"https://bugs.earthdata.nasa.gov/browse/ORCA-394-")," Create Lambda function for performing soft deletes from ORCA"),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("a",{parentName:"li",href:"https://bugs.earthdata.nasa.gov/browse/ORCA-395-"},"https://bugs.earthdata.nasa.gov/browse/ORCA-395-")," Create Lambda function for performing physical/hard deletes from ORCA"),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("a",{parentName:"li",href:"https://bugs.earthdata.nasa.gov/browse/ORCA-396-"},"https://bugs.earthdata.nasa.gov/browse/ORCA-396-")," Create API gateway resource for performing ORCA delete functionality"),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("a",{parentName:"li",href:"https://bugs.earthdata.nasa.gov/browse/ORCA-397-"},"https://bugs.earthdata.nasa.gov/browse/ORCA-397-")," Integrate ORCA delete API gateways with Launchpad and add users who can perform the deletion."),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("a",{parentName:"li",href:"https://bugs.earthdata.nasa.gov/browse/ORCA-398-"},"https://bugs.earthdata.nasa.gov/browse/ORCA-398-")," Investigate logging for ORCA delete functionality."),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("a",{parentName:"li",href:"https://bugs.earthdata.nasa.gov/browse/ORCA-402-"},"https://bugs.earthdata.nasa.gov/browse/ORCA-402-")," Discuss the open questions regarding the delete functionality with the larger team (Cumulus IX,OX/GHRC).")),(0,i.kt)("h5",{id:"references"},"References"),(0,i.kt)("ul",null,(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("a",{parentName:"li",href:"https://wiki.earthdata.nasa.gov/display/CUMULUS/ORCA+Data+Management+Use+Cases"},"https://wiki.earthdata.nasa.gov/display/CUMULUS/ORCA+Data+Management+Use+Cases")),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("a",{parentName:"li",href:"https://wiki.earthdata.nasa.gov/display/CUMULUS/ORCA+Prevention+Use+Cases"},"https://wiki.earthdata.nasa.gov/display/CUMULUS/ORCA+Prevention+Use+Cases")),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("a",{parentName:"li",href:"https://wiki.earthdata.nasa.gov/display/CUMULUS/2022-03-02+ORCA+Meeting+notes"},"https://wiki.earthdata.nasa.gov/display/CUMULUS/2022-03-02+ORCA+Meeting+notes")),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("a",{parentName:"li",href:"https://docs.aws.amazon.com/AmazonS3/latest/userguide/ServerLogs.html"},"https://docs.aws.amazon.com/AmazonS3/latest/userguide/ServerLogs.html")),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("a",{parentName:"li",href:"https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_objects"},"https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_objects")),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("a",{parentName:"li",href:"https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-control-access-to-api.html"},"https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-control-access-to-api.html")),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("a",{parentName:"li",href:"https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html"},"https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html")),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("a",{parentName:"li",href:"https://www.sumologic.com/insight/s3-cost-optimization/"},"https://www.sumologic.com/insight/s3-cost-optimization/")),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("a",{parentName:"li",href:"https://aws.amazon.com/premiumsupport/knowledge-center/s3-undelete-configuration/"},"https://aws.amazon.com/premiumsupport/knowledge-center/s3-undelete-configuration/"))))}g.isMDXComponent=!0},4079:function(e,t,a){a.r(t),a.d(t,{assets:function(){return h},contentTitle:function(){return u},default:function(){return f},frontMatter:function(){return c},metadata:function(){return m},toc:function(){return p}});var n=a(7462),o=a(3366),i=a(7294),r=a(3905),s=a(6126),l=["components"],d=["zoomIn","zoomOut","resetTransform"],c={},u=void 0,m={unversionedId:"templates/pan-zoom-image",id:"templates/pan-zoom-image",title:"pan-zoom-image",description:"The image below can be panned and zoomed using your mouse or the provided buttons.",source:"@site/docs/templates/pan-zoom-image.mdx",sourceDirName:"templates",slug:"/templates/pan-zoom-image",permalink:"/cumulus-orca/docs/templates/pan-zoom-image",draft:!1,editUrl:"https://github.com/nasa/cumulus-orca/edit/develop/website/docs/templates/pan-zoom-image.mdx",tags:[],version:"current",frontMatter:{}},h={},p=[],g={toc:p};function f(e){var t=e.components,a=(0,o.Z)(e,l);return(0,r.kt)("wrapper",(0,n.Z)({},g,a,{components:t,mdxType:"MDXLayout"}),(0,r.kt)("div",{className:"admonition admonition-note alert alert--secondary"},(0,r.kt)("div",{parentName:"div",className:"admonition-heading"},(0,r.kt)("h5",{parentName:"div"},(0,r.kt)("span",{parentName:"h5",className:"admonition-icon"},(0,r.kt)("svg",{parentName:"span",xmlns:"http://www.w3.org/2000/svg",width:"14",height:"16",viewBox:"0 0 14 16"},(0,r.kt)("path",{parentName:"svg",fillRule:"evenodd",d:"M6.3 5.69a.942.942 0 0 1-.28-.7c0-.28.09-.52.28-.7.19-.18.42-.28.7-.28.28 0 .52.09.7.28.18.19.28.42.28.7 0 .28-.09.52-.28.7a1 1 0 0 1-.7.3c-.28 0-.52-.11-.7-.3zM8 7.99c-.02-.25-.11-.48-.31-.69-.2-.19-.42-.3-.69-.31H6c-.27.02-.48.13-.69.31-.2.2-.3.44-.31.69h1v3c.02.27.11.5.31.69.2.2.42.31.69.31h1c.27 0 .48-.11.69-.31.2-.19.3-.42.31-.69H8V7.98v.01zM7 2.3c-3.14 0-5.7 2.54-5.7 5.68 0 3.14 2.56 5.7 5.7 5.7s5.7-2.55 5.7-5.7c0-3.15-2.56-5.69-5.7-5.69v.01zM7 .98c3.86 0 7 3.14 7 7s-3.14 7-7 7-7-3.12-7-7 3.14-7 7-7z"}))),"Interactive Image")),(0,r.kt)("div",{parentName:"div",className:"admonition-content"},(0,r.kt)("p",{parentName:"div"},"The image below can be panned and zoomed using your mouse or the provided buttons.\nTo reset the image to the original size on the page click ",(0,r.kt)("img",{width:"12px",height:"12px",src:a.resetPic,alt:"Reset Image"}),".\nIf you wish to view the full image on a separate page, click this ",(0,r.kt)("a",{href:a.imageSource,target:"_blank",rel:"noopener noreferrer"},"link"),"."))),(0,r.kt)(s.d$,{defaultScale:1,mdxType:"TransformWrapper"},(function(e){var t=e.zoomIn,n=e.zoomOut,l=e.resetTransform;(0,o.Z)(e,d);return(0,r.kt)(i.Fragment,null,(0,r.kt)("div",{className:"tools"},(0,r.kt)("button",{onClick:function(){return t()}},(0,r.kt)("img",{width:"15px",height:"15px",src:a.zoomInPic,alt:"Zoom In"})),(0,r.kt)("button",{onClick:function(){return n()}},(0,r.kt)("img",{width:"15px",height:"15px",src:a.zoomOutPic,alt:"Zoom Out"})),(0,r.kt)("button",{onClick:function(){return l()}},(0,r.kt)("img",{width:"15px",height:"15px",src:a.resetPic,alt:"Reset Image"}))),(0,r.kt)(s.Uv,{mdxType:"TransformComponent"},(0,r.kt)("img",{src:a.imageSource,alt:a.imageAlt})))})))}f.isMDXComponent=!0}}]);