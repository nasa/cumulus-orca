"use strict";(self.webpackChunkorca_website=self.webpackChunkorca_website||[]).push([[2647],{1809:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>d,contentTitle:()=>r,default:()=>u,frontMatter:()=>s,metadata:()=>l,toc:()=>c});var a=n(4848),o=n(8453),i=n(6025);const s={id:"research-orca-delete-functionality",title:"Research Notes on ORCA delete functionality.",description:"Research Notes on implementing delete functionality for ORCA."},r=void 0,l={id:"developer/research/research-orca-delete-functionality",title:"Research Notes on ORCA delete functionality.",description:"Research Notes on implementing delete functionality for ORCA.",source:"@site/docs/developer/research/research-orca-delete-functionality.mdx",sourceDirName:"developer/research",slug:"/developer/research/research-orca-delete-functionality",permalink:"/cumulus-orca/docs/developer/research/research-orca-delete-functionality",draft:!1,unlisted:!1,editUrl:"https://github.com/nasa/cumulus-orca/edit/develop/website/docs/developer/research/research-orca-delete-functionality.mdx",tags:[],version:"current",frontMatter:{id:"research-orca-delete-functionality",title:"Research Notes on ORCA delete functionality.",description:"Research Notes on implementing delete functionality for ORCA."},sidebar:"dev_guide",previous:{title:"Bamboo specs Research Notes",permalink:"/cumulus-orca/docs/developer/research/research-bamboo"},next:{title:"Research Notes on running integration tests in bamboo CI/CD",permalink:"/cumulus-orca/docs/developer/research/research-bamboo-integration-tests"}},d={},c=[{value:"Delete functionality use cases",id:"delete-functionality-use-cases",level:2},{value:"Initial ORCA Delete Functionality Architecture",id:"initial-orca-delete-functionality-architecture",level:2},{value:"User Interface",id:"user-interface",level:3},{value:"API gateway",id:"api-gateway",level:3},{value:"Lambda function",id:"lambda-function",level:3},{value:"Deleting objects from AWS S3",id:"deleting-objects-from-aws-s3",level:3},{value:"Example Using delete_objects",id:"example-using-delete_objects",level:4},{value:"Logging for Auditing",id:"logging-for-auditing",level:3},{value:"Open Questions yet to be answered",id:"open-questions-yet-to-be-answered",level:2},{value:"Future directions",id:"future-directions",level:2},{value:"References",id:"references",level:5}];function h(e){const t={a:"a",admonition:"admonition",code:"code",h2:"h2",h3:"h3",h4:"h4",h5:"h5",li:"li",p:"p",pre:"pre",ul:"ul",...(0,o.R)(),...e.components};return(0,a.jsxs)(a.Fragment,{children:[(0,a.jsx)(t.h2,{id:"delete-functionality-use-cases",children:"Delete functionality use cases"}),"\n",(0,a.jsx)(t.p,{children:"Some use cases for delete functionality are as follows:"}),"\n",(0,a.jsxs)(t.ul,{children:["\n",(0,a.jsxs)(t.li,{children:["\n",(0,a.jsx)(t.p,{children:"As a DAAC, I would like to remove data from ORCA that is invalid or expired in order to maintain a clean data archive.\nThis can be achieved by a two-step process- an initial soft delete initiated by user, and a physical delete to permanently delete the data from S3 and database.\nIt is assumed that the process is not automated and must be initiated by the user with an API call for both steps."}),"\n"]}),"\n",(0,a.jsxs)(t.li,{children:["\n",(0,a.jsx)(t.p,{children:"As a DAAC, I would like to remove data from ORCA only if it has been in archive for more than x days from initial ingest to keep from incurring additional cost for early removal."}),"\n",(0,a.jsxs)(t.p,{children:["This can be implemented by using soft delete. We can either flag the data in the database with a new column named ",(0,a.jsx)(t.code,{children:"Pending Deletion"})," or we can create a separate table that contains those data marked for deletion. Then after 90 days, we can permanently delete from the DB as well as the glacier bucket.\nIf the data is stored in standard it would be 90 days but for deep archive, it would be 180 days. If the time the data stays in ORCA is less than the initial (90/180) days from ingest, any kind of delete operation will not be allowed. Some business logic should be added to the code to execute this rule."]}),"\n"]}),"\n",(0,a.jsxs)(t.li,{children:["\n",(0,a.jsx)(t.p,{children:"As a DAAC, I would like to configure the amount of time data remains in ORCA after being signaled to be deleted."}),"\n",(0,a.jsx)(t.p,{children:"This should be configurable by each DAAC that is using ORCA. The number of days it would stay in ORCA would be based off of the soft delete date. Once the data stays in ORCA for greater than 90/180 days based on the glacier storage type used, that data would be eligible for a soft delete.\nThe data would be eligible for a physical delete after the configured x days after the soft delete date.\nThe data should stay in ORCA for x number of days for safety reasons. The configuration should be done using an environment variable during deployment. It is assumed that the configuration cannot be overridden except with a new deployment.\nAdditionally, ORCA should prevent deletion of any kind from certain data like Level 0 or base data sets that\nare static. Some ways to implement this would be to have a configuration parameter we capture that says\nwe are not able to delete from this collection or use an S3 bucket having bucket policies that prevents any\ndeletes from happening."}),"\n"]}),"\n",(0,a.jsxs)(t.li,{children:["\n",(0,a.jsx)(t.p,{children:"As a DAAC, I would like only authorized personnel to be able to remove data from ORCA in a controlled way to minimize risk of accidental or malicious deletions."}),"\n",(0,a.jsxs)(t.p,{children:["This could be implemented with the use of NASA launchpad authentication since other teams such as Cumulus are already using this approach. This ",(0,a.jsx)(t.a,{href:"https://idmax.nasa.gov/nams/asset/255115",children:"link"})," is used to submit a new GSFC workflow request and most probably will be used to only allow specific users to perform the deletes. Contact ",(0,a.jsx)(t.code,{children:"robert.a.meredith@nasa.gov"})," and ",(0,a.jsx)(t.code,{children:"tadd.buffington@nasa.gov"})," with any issues regarding launchpad integration.\nThe api gateway resource policy can be used to restrict certain users from accessing the api endpoint. For more information, see ",(0,a.jsx)(t.a,{href:"https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-resource-policies.html",children:"Controlling access to an API with API Gateway resource policies"}),".\nAnother technology to look into would be AWS Cognito which can be used to create customizable authentication and authorization solutions for the REST API. Amazon Cognito user pools are used to control who can invoke REST API methods. For more information, see ",(0,a.jsx)(t.a,{href:"https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-integrate-with-cognito.html",children:"Control access to a REST API using Amazon Cognito user pools as authorizer"}),"."]}),"\n"]}),"\n"]}),"\n",(0,a.jsx)(t.admonition,{type:"note",children:(0,a.jsx)(t.p,{children:"Authentication and authorization piece of this functionality needs further research to make sure only authorized users can perform deletes."})}),"\n",(0,a.jsx)(t.admonition,{type:"warning",children:(0,a.jsx)(t.p,{children:"Currently AWS Cognito has some restrictions from use in production environments and should be avoided for now."})}),"\n",(0,a.jsxs)(t.ul,{children:["\n",(0,a.jsxs)(t.li,{children:["\n",(0,a.jsx)(t.p,{children:"As a DAAC, I would like duplicate data to be versioned in ORCA in order to recover the proper version of the data based on the type of failure."}),"\n",(0,a.jsxs)(t.p,{children:["Versioning can be enabled at the bucket level by configuring the bucket properties via terraform or AWS console. After versioning is enabled in a bucket, it can never return to an unversioned state but can only be suspended on that bucket. Versioning can help recover objects from accidental deletion or overwrite. For example, if an object is deleted, Amazon S3 inserts a delete marker instead of removing the object permanently. The delete marker becomes the current object version. If the object is overwritten, it results in a new object version in the bucket. The previous version can always be restored. For more information, see ",(0,a.jsx)(t.a,{href:"https://docs.aws.amazon.com/AmazonS3/latest/userguide/DeletingObjectVersions.html",children:"Deleting object versions from a versioning-enabled bucket"}),".\nThe drawback of using versioning is the additional cost of storage for that versioned object. This can be solved by using object versioning with S3 Lifecycle policy. After a certain period of time defined, the versioned object will be marked as expired and automatically deleted from S3 bucket. This can be configured in bucket management via terraform. For more information, see ",(0,a.jsx)(t.a,{href:"https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html",children:"S3 lifecycle policy"})]}),"\n"]}),"\n",(0,a.jsxs)(t.li,{children:["\n",(0,a.jsx)(t.p,{children:"Perform a check with CMR and/or Cumulus to verify that the granule has been deleted from those locations prior to allowing the delete to proceed in ORCA."}),"\n",(0,a.jsx)(t.p,{children:"This can be implemented in the existing lambda function that will be used to delete the data from ORCA.\nBefore deleting from CMR and Cumulus, the UI should show a warning message to the user for additional confirmation. Additional items need to be discussed on this rule to determine when and how it would be implemented and to address corner cases like versioned file removal."}),"\n"]}),"\n"]}),"\n",(0,a.jsx)(t.h2,{id:"initial-orca-delete-functionality-architecture",children:"Initial ORCA Delete Functionality Architecture"}),"\n",(0,a.jsx)(t.p,{children:"The following is a potential architecture for ORCA delete functionality. Note that this could possibly change after discussing open questions with other teams."}),"\n",(0,a.jsx)("img",{src:(0,i.Ay)("img/ORCA-Delete-Functionality-Architecture-Initial.png"),zoomInPic:(0,i.Ay)("img/zoom-in.svg"),zoomOutPic:(0,i.Ay)("img/zoom-out.svg"),resetPic:(0,i.Ay)("img/zoom-pan-reset.svg")}),"\n",(0,a.jsx)(t.h3,{id:"user-interface",children:"User Interface"}),"\n",(0,a.jsx)(t.p,{children:"The user interface is used to show warning messages to end user while performing the deletes. The UI should be able to interact with Cumulus dashboard and other apps as needed.\nIt also makes api calls to the API gateway for delete operations."}),"\n",(0,a.jsx)(t.h3,{id:"api-gateway",children:"API gateway"}),"\n",(0,a.jsxs)(t.p,{children:["API gateway is currently used by end users for creating reconciliation reports and getting status update of recovery granules and jobs. This can be used for creating API calls made by end users for deletion.\nThe API gateway should act as a trigger to the lambda functions that actually perform the deletion in the backend. In addition, it should also trigger a login lambda function that gets the authentication token from Launchpad possibly for user login and verification.\nAn API gateway with two different resources need to be created- one for the soft delete API call and one for the hard delete API call. In order to deploy this via terraform, a private rest api with two resources need to be created. In case of using private API, the vpc endpoint ID for the gateway will be required.\nThe REST API should use a ",(0,a.jsx)(t.code,{children:"POST"})," http method and the integration type should be ",(0,a.jsx)(t.code,{children:"AWS"}),".\nIf lambda function is used with the API, a lambda permission resource should be created in terraform giving access to ",(0,a.jsx)(t.code,{children:"lambda:InvokeFunction"})," action so that the API can trigger the lambda. In addition, the api gateway resource policy can be used to restrict certain IP addresses and VPC if needed from accessing the API endpoint. Check API gateway ",(0,a.jsx)(t.a,{href:"https://github.com/nasa/cumulus-orca/tree/develop/modules/api-gateway",children:"examples"})," currently used by ORCA."]}),"\n",(0,a.jsx)(t.h3,{id:"lambda-function",children:"Lambda function"}),"\n",(0,a.jsx)(t.p,{children:"The delete functionality can be performed by two lambda functions based on initial research. One of the lambda functions will be used to perform soft delete- only flag the granule in the database for deletion after 90 days in case of standard glacier or 180 days in case of deep glacier. The lambda should also verify with CMR and/or Cumulus that the granule has been deleted from those locations prior to allowing the delete to proceed in ORCA. The lambda will be triggered by an API call made by the user once the user is authenticated with Launchpad."}),"\n",(0,a.jsx)(t.p,{children:"The other lambda function can be used to perform a physical delete from S3 archive as well as from the database.\nThe lambda code should addresses the rule that the data cannot be physically deleted until the DAAC configured x number of days. This will require further discussions with ORCA team and ORCA Working group before performing the actual work."}),"\n",(0,a.jsx)(t.h3,{id:"deleting-objects-from-aws-s3",children:"Deleting objects from AWS S3"}),"\n",(0,a.jsxs)(t.p,{children:["To delete an object from an S3 bucket, the ",(0,a.jsx)(t.a,{href:"https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_objects",children:"delete_objects"}),"\ncan be used from the boto3 library. An example of the usage can be seen below.\nSome notable items if this library is used includes the following."]}),"\n",(0,a.jsxs)(t.ul,{children:["\n",(0,a.jsx)(t.li,{children:"It can be used to delete up to 1000 objects from a bucket using a single API call."}),"\n",(0,a.jsx)(t.li,{children:"When performing this action on an MFA Delete enabled bucket that attempts to delete any versioned objects, an MFA token must be included or else it will fail."}),"\n",(0,a.jsx)(t.li,{children:"If the object specified in the request is not found, Amazon S3 returns the result as deleted."}),"\n",(0,a.jsx)(t.li,{children:"Each DeleteObjects API incurs a little cost of $0.05/10000 requests."}),"\n"]}),"\n",(0,a.jsx)(t.h4,{id:"example-using-delete_objects",children:"Example Using delete_objects"}),"\n",(0,a.jsx)(t.pre,{children:(0,a.jsx)(t.code,{className:"language-python",children:'import boto3\n\ns3_client = boto3.client(\'s3\')\nbucket = "riz-orca"\nresponse = s3_client.delete_objects(\n    Bucket=bucket,\n    Delete={\n        \'Objects\': [\n            {\n                \'Key\': \'MOD09A1.006/MOD09A1.A2019025.h07v03.006.2019037205734.hdf\',\n            }\n        ]\n    }\n)\nprint(response)\n\n# Results\n{\n   "ResponseMetadata":{\n      "RequestId":"KJCZAPM0RWMJNNC7",\n      "HostId":"z2fRlgMxT10ApzcyDOLp3REn3PjM71OSgdH0oPpe4v2pHchmSTPCfEjBjTx00PyTL55wgmQ7gF4=",\n      "HTTPStatusCode":200,\n      "HTTPHeaders":{\n         "x-amz-id-2":"z2fRlgMxT10ApzcyDOLp3REn3PjM71OSgdH0oPpe4v2pHchmSTPCfEjBjTx00PyTL55wgmQ7gF4=",\n         "x-amz-request-id":"KJCZAPM0RWMJNNC7",\n         "date":"Tue, 08 Mar 2022 05:19:07 GMT",\n         "content-type":"application/xml",\n         "transfer-encoding":"chunked",\n         "server":"AmazonS3",\n         "connection":"close"\n      },\n      "RetryAttempts":0\n   },\n   "Deleted":[\n      {\n         "Key":"MOD09A1.006/MOD09A1.A2019025.h07v03.006.2019037205734.hdf"\n      }\n   ]\n}\n'})}),"\n",(0,a.jsx)(t.h3,{id:"logging-for-auditing",children:"Logging for Auditing"}),"\n",(0,a.jsx)(t.p,{children:"Additional logging should be collected during the deletion process to keep records for safety and security purposes. Some logging to capture might include who deleted the data, when how many granules were deleted over a particular timespan, from which collections was it deleted, and what workflow was used to delete them."}),"\n",(0,a.jsx)(t.p,{children:"Cloudwatch logs and cloudtrail can be used to collect logging information. In addition, S3 server access logging can be used at the bucket level which would provide detailed records for the requests that are made to a bucket. The log information can be useful in security and access audits. AWS will collect access log records, add the records in log files, and then upload log files to the target bucket as log objects. There is no extra charge for using the service except the cost for storing the log files in S3."}),"\n",(0,a.jsx)(t.h2,{id:"open-questions-yet-to-be-answered",children:"Open Questions yet to be answered"}),"\n",(0,a.jsx)(t.p,{children:"The following questions should be discussed with the broader team before implementing the work."}),"\n",(0,a.jsxs)(t.ul,{children:["\n",(0,a.jsx)(t.li,{children:"Regarding user authentication and authorization for deletes, do we have to pass any temporary tokens? How will this integrate with Cumulus calls to our API? Do we utilize an authentication token from API gateway?"}),"\n",(0,a.jsxs)(t.li,{children:["Since",(0,a.jsx)(t.code,{children:"deleteObjects"})," boto3 API call is limited to 1000 deletes per call, can we batch this up? Are there better ways to do batch deletes? What are the rules this has to follow?"]}),"\n",(0,a.jsx)(t.li,{children:"What information should we capture from the delete logs? Do we delete the records, move them to an audit table or store them in S3 like in server access logging? How long do we keep them?"}),"\n",(0,a.jsx)(t.li,{children:"How do we handle situations like deleting a version of a granule and not the complete granule?"}),"\n",(0,a.jsx)(t.li,{children:"When removing versioned data granule, do we remove all the versions or do we remove all but the last and keep the delete marked version for longer?"}),"\n"]}),"\n",(0,a.jsx)(t.h2,{id:"future-directions",children:"Future directions"}),"\n",(0,a.jsx)(t.p,{children:"Few cards have been created to perform the ORCA delete functionality work based on initial research. It can be assumed that some of these cards will get modified once we have more discussion with other teams. This should be revisited during PI planning/team meetings to confirm the use cases/requirements before starting the work.\nSome of the cards created to finish the task include:"}),"\n",(0,a.jsxs)(t.ul,{children:["\n",(0,a.jsxs)(t.li,{children:[(0,a.jsx)(t.a,{href:"https://bugs.earthdata.nasa.gov/browse/ORCA-394-",children:"https://bugs.earthdata.nasa.gov/browse/ORCA-394-"})," Create Lambda function for performing soft deletes from ORCA"]}),"\n",(0,a.jsxs)(t.li,{children:[(0,a.jsx)(t.a,{href:"https://bugs.earthdata.nasa.gov/browse/ORCA-395-",children:"https://bugs.earthdata.nasa.gov/browse/ORCA-395-"})," Create Lambda function for performing physical/hard deletes from ORCA"]}),"\n",(0,a.jsxs)(t.li,{children:[(0,a.jsx)(t.a,{href:"https://bugs.earthdata.nasa.gov/browse/ORCA-396-",children:"https://bugs.earthdata.nasa.gov/browse/ORCA-396-"})," Create API gateway resource for performing ORCA delete functionality"]}),"\n",(0,a.jsxs)(t.li,{children:[(0,a.jsx)(t.a,{href:"https://bugs.earthdata.nasa.gov/browse/ORCA-397-",children:"https://bugs.earthdata.nasa.gov/browse/ORCA-397-"})," Integrate ORCA delete API gateways with Launchpad and add users who can perform the deletion."]}),"\n",(0,a.jsxs)(t.li,{children:[(0,a.jsx)(t.a,{href:"https://bugs.earthdata.nasa.gov/browse/ORCA-398-",children:"https://bugs.earthdata.nasa.gov/browse/ORCA-398-"})," Investigate logging for ORCA delete functionality."]}),"\n",(0,a.jsxs)(t.li,{children:[(0,a.jsx)(t.a,{href:"https://bugs.earthdata.nasa.gov/browse/ORCA-402-",children:"https://bugs.earthdata.nasa.gov/browse/ORCA-402-"})," Discuss the open questions regarding the delete functionality with the larger team (Cumulus IX,OX/GHRC)."]}),"\n"]}),"\n",(0,a.jsx)(t.h5,{id:"references",children:"References"}),"\n",(0,a.jsxs)(t.ul,{children:["\n",(0,a.jsx)(t.li,{children:(0,a.jsx)(t.a,{href:"https://wiki.earthdata.nasa.gov/display/CUMULUS/ORCA+Data+Management+Use+Cases",children:"https://wiki.earthdata.nasa.gov/display/CUMULUS/ORCA+Data+Management+Use+Cases"})}),"\n",(0,a.jsx)(t.li,{children:(0,a.jsx)(t.a,{href:"https://wiki.earthdata.nasa.gov/display/CUMULUS/ORCA+Prevention+Use+Cases",children:"https://wiki.earthdata.nasa.gov/display/CUMULUS/ORCA+Prevention+Use+Cases"})}),"\n",(0,a.jsx)(t.li,{children:(0,a.jsx)(t.a,{href:"https://wiki.earthdata.nasa.gov/display/CUMULUS/2022-03-02+ORCA+Meeting+notes",children:"https://wiki.earthdata.nasa.gov/display/CUMULUS/2022-03-02+ORCA+Meeting+notes"})}),"\n",(0,a.jsx)(t.li,{children:(0,a.jsx)(t.a,{href:"https://docs.aws.amazon.com/AmazonS3/latest/userguide/ServerLogs.html",children:"https://docs.aws.amazon.com/AmazonS3/latest/userguide/ServerLogs.html"})}),"\n",(0,a.jsx)(t.li,{children:(0,a.jsx)(t.a,{href:"https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_objects",children:"https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_objects"})}),"\n",(0,a.jsx)(t.li,{children:(0,a.jsx)(t.a,{href:"https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-control-access-to-api.html",children:"https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-control-access-to-api.html"})}),"\n",(0,a.jsx)(t.li,{children:(0,a.jsx)(t.a,{href:"https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html",children:"https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html"})}),"\n",(0,a.jsx)(t.li,{children:(0,a.jsx)(t.a,{href:"https://www.sumologic.com/insight/s3-cost-optimization/",children:"https://www.sumologic.com/insight/s3-cost-optimization/"})}),"\n",(0,a.jsx)(t.li,{children:(0,a.jsx)(t.a,{href:"https://aws.amazon.com/premiumsupport/knowledge-center/s3-undelete-configuration/",children:"https://aws.amazon.com/premiumsupport/knowledge-center/s3-undelete-configuration/"})}),"\n"]})]})}function u(e={}){const{wrapper:t}={...(0,o.R)(),...e.components};return t?(0,a.jsx)(t,{...e,children:(0,a.jsx)(h,{...e})}):h(e)}},8453:(e,t,n)=>{n.d(t,{R:()=>s,x:()=>r});var a=n(6540);const o={},i=a.createContext(o);function s(e){const t=a.useContext(i);return a.useMemo((function(){return"function"==typeof e?e(t):{...t,...e}}),[t,e])}function r(e){let t;return t=e.disableParentContext?"function"==typeof e.components?e.components(o):e.components||o:s(e.components),a.createElement(i.Provider,{value:t},e.children)}}}]);