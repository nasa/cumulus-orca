"use strict";(self.webpackChunkorca_website=self.webpackChunkorca_website||[]).push([[6566],{4153:(e,n,r)=>{r.r(n),r.d(n,{assets:()=>c,contentTitle:()=>o,default:()=>d,frontMatter:()=>a,metadata:()=>t,toc:()=>l});const t=JSON.parse('{"id":"developer/research/research-multipart-chunksize","title":"Multipart Chunksize Research Notes","description":"Research Notes on Modifying Multipart-Chunksize for copy_to_archive.","source":"@site/docs/developer/research/research-multipart-chunksize.md","sourceDirName":"developer/research","slug":"/developer/research/research-multipart-chunksize","permalink":"/cumulus-orca/docs/developer/research/research-multipart-chunksize","draft":false,"unlisted":false,"editUrl":"https://github.com/nasa/cumulus-orca/edit/develop/website/docs/developer/research/research-multipart-chunksize.md","tags":[],"version":"current","frontMatter":{"id":"research-multipart-chunksize","title":"Multipart Chunksize Research Notes","description":"Research Notes on Modifying Multipart-Chunksize for copy_to_archive."},"sidebar":"dev_guide","previous":{"title":"GraphQL Research Notes","permalink":"/cumulus-orca/docs/developer/research/research-graphql"},"next":{"title":"Bamboo specs Research Notes","permalink":"/cumulus-orca/docs/developer/research/research-bamboo"}}');var s=r(4848),i=r(8453);const a={id:"research-multipart-chunksize",title:"Multipart Chunksize Research Notes",description:"Research Notes on Modifying Multipart-Chunksize for copy_to_archive."},o=void 0,c={},l=[{value:"Overview",id:"overview",level:2},{value:"Implementation Details",id:"implementation-details",level:3},{value:"Future Direction",id:"future-direction",level:3}];function h(e){const n={a:"a",code:"code",h2:"h2",h3:"h3",li:"li",p:"p",pre:"pre",ul:"ul",...(0,i.R)(),...e.components};return(0,s.jsxs)(s.Fragment,{children:[(0,s.jsx)(n.h2,{id:"overview",children:"Overview"}),"\n",(0,s.jsxs)(n.p,{children:[(0,s.jsx)(n.a,{href:"https://github.com/nasa/cumulus-orca/blob/2f2600a2edd85e0af216d78180c5d46ebda03060/tasks/copy_to_glacier/copy_to_glacier.py#L50",children:"copy_to_archive"}),"\nuses a copy command that has a chunk-size for multi-part transfers.\nWe currently are using the default value of 8mb, which will cause problems when transferring large files, sometimes exceeding 120Gb."]}),"\n",(0,s.jsx)(n.h3,{id:"implementation-details",children:"Implementation Details"}),"\n",(0,s.jsxs)(n.ul,{children:["\n",(0,s.jsxs)(n.li,{children:[(0,s.jsx)(n.a,{href:"https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.copy",children:"Docs for the copy command"})," mention a ",(0,s.jsx)(n.code,{children:"Config"})," parameter of type ",(0,s.jsx)(n.code,{children:"TransferConfig"}),"."]}),"\n",(0,s.jsxs)(n.li,{children:[(0,s.jsx)(n.a,{href:"https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/s3.html#boto3.s3.transfer.TransferConfig",children:"Docs for TransferConfig"})," state that it has a property"]}),"\n",(0,s.jsxs)(n.li,{children:["Given the above, we can modify the ",(0,s.jsx)(n.code,{children:"s3.copy"})," command to","\n",(0,s.jsx)(n.pre,{children:(0,s.jsx)(n.code,{className:"language-python",children:"s3.copy(\n  copy_source,\n  destination_bucket, destination_key,\n  ExtraArgs={\n      'StorageClass': 'GLACIER',\n      'MetadataDirective': 'COPY',\n      'ContentType': s3.head_object(Bucket=source_bucket_name, Key=source_key)['ContentType'],\n  },\n  Config=TransferConfig(multipart_chunksize=multipart_chunksize_mb * MB)\n)\n"})}),"\n"]}),"\n",(0,s.jsxs)(n.li,{children:["This will require a variable passed into the lambda.","\n",(0,s.jsxs)(n.ul,{children:["\n",(0,s.jsxs)(n.li,{children:["Could be set at the collection level under ",(0,s.jsx)(n.code,{children:"config['collection']['s3MultipartChunksizeMb']"})," with a default value in the lambdas/main.tf entry for ",(0,s.jsx)(n.code,{children:"copy_to_archive"})," defined as","\n",(0,s.jsx)(n.pre,{children:(0,s.jsx)(n.code,{children:"environment {\n  variables = {\n    ORCA_DEFAULT_BUCKET = var.orca_default_bucket,\n    DEFAULT_ORCA_COPY_CHUNK_SIZE_MB = var.orca_copy_chunk_size\n  }\n}\n"})}),"\n"]}),"\n",(0,s.jsxs)(n.li,{children:["Could also be an overall environment variable, though this is less flexible. In the lambdas/main.tf entry for ",(0,s.jsx)(n.code,{children:"copy_to_archive"})," this would look like","\n",(0,s.jsx)(n.pre,{children:(0,s.jsx)(n.code,{children:"environment {\n  variables = {\n    ORCA_DEFAULT_BUCKET = var.orca_default_bucket,\n    ORCA_COPY_CHUNK_SIZE_MB = var.orca_copy_chunk_size\n  }\n}\n"})}),"\n"]}),"\n"]}),"\n"]}),"\n",(0,s.jsx)(n.li,{children:"The above should be added to other TF files such as terraform.tfvars, orca/main.tf, orca/variables.tf, and lambdas/variables.tf as well as documentation."}),"\n"]}),"\n",(0,s.jsx)(n.h3,{id:"future-direction",children:"Future Direction"}),"\n",(0,s.jsxs)(n.ul,{children:["\n",(0,s.jsxs)(n.li,{children:["Recommend adding the environment variable ",(0,s.jsx)(n.code,{children:"ORCA_COPY_CHUNK_SIZE_MB"})," to TF and Lambda.","\n",(0,s.jsxs)(n.ul,{children:["\n",(0,s.jsx)(n.li,{children:"Worth waiting to use the same name as Cumulus, as they are going through a similar change."}),"\n"]}),"\n"]}),"\n",(0,s.jsxs)(n.li,{children:["I have read in a couple of sources that increasing ",(0,s.jsx)(n.code,{children:"io_chunksize"})," can also have a significant impact on performance. May be worth looking into if more improvements are desired.","\n",(0,s.jsxs)(n.ul,{children:["\n",(0,s.jsx)(n.li,{children:"The other variables should be considered as well."}),"\n"]}),"\n"]}),"\n"]})]})}function d(e={}){const{wrapper:n}={...(0,i.R)(),...e.components};return n?(0,s.jsx)(n,{...e,children:(0,s.jsx)(h,{...e})}):h(e)}},8453:(e,n,r)=>{r.d(n,{R:()=>a,x:()=>o});var t=r(6540);const s={},i=t.createContext(s);function a(e){const n=t.useContext(i);return t.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function o(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(s):e.components||s:a(e.components),t.createElement(i.Provider,{value:n},e.children)}}}]);