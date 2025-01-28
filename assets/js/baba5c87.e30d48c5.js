"use strict";(self.webpackChunkorca_website=self.webpackChunkorca_website||[]).push([[2120],{6234:(e,n,s)=>{s.r(n),s.d(n,{assets:()=>c,contentTitle:()=>o,default:()=>u,frontMatter:()=>i,metadata:()=>r,toc:()=>d});const r=JSON.parse('{"id":"developer/development-guide/code/clean-architecture","title":"Clean Architecture","description":"Overview of Clean Architecture for ORCA","source":"@site/docs/developer/development-guide/code/clean-architecture.mdx","sourceDirName":"developer/development-guide/code","slug":"/developer/development-guide/code/clean-architecture","permalink":"/cumulus-orca/docs/developer/development-guide/code/clean-architecture","draft":false,"unlisted":false,"editUrl":"https://github.com/nasa/cumulus-orca/edit/develop/website/docs/developer/development-guide/code/clean-architecture.mdx","tags":[],"version":"current","frontMatter":{"id":"clean-architecture","title":"Clean Architecture","description":"Overview of Clean Architecture for ORCA"},"sidebar":"dev_guide","previous":{"title":"Best Practices","permalink":"/cumulus-orca/docs/developer/development-guide/code/best-practices"},"next":{"title":"ORCA Versioning and Releases","permalink":"/cumulus-orca/docs/developer/development-guide/code/versioning-releases"}}');var a=s(4848),t=s(8453),l=s(6025);const i={id:"clean-architecture",title:"Clean Architecture",description:"Overview of Clean Architecture for ORCA"},o=void 0,c={},d=[{value:"Broad Strokes",id:"broad-strokes",level:3},{value:"Layers",id:"layers",level:2},{value:"Reasons for Layers",id:"reasons-for-layers",level:3},{value:"&quot;Frameworks and Drivers&quot; Layer",id:"frameworks-and-drivers-layer",level:3},{value:"Orca Examples",id:"orca-examples",level:4},{value:"&quot;Interface Adapters&quot; Layer",id:"interface-adapters-layer",level:3},{value:"Resource Examples",id:"resource-examples",level:4},{value:"Code Examples",id:"code-examples",level:4},{value:"&quot;Use Cases&quot; Layer",id:"use-cases-layer",level:3},{value:"Resource Examples",id:"resource-examples-1",level:4},{value:"Code Examples",id:"code-examples-1",level:4},{value:"&quot;Entities&quot; Layer",id:"entities-layer",level:3},{value:"Resource Examples",id:"resource-examples-2",level:4},{value:"Code Examples",id:"code-examples-2",level:4},{value:"Additional Thoughts",id:"additional-thoughts",level:2}];function h(e){const n={a:"a",code:"code",h2:"h2",h3:"h3",h4:"h4",li:"li",p:"p",ul:"ul",...(0,t.R)(),...e.components};return(0,a.jsxs)(a.Fragment,{children:[(0,a.jsxs)(n.p,{children:["Our definition of Clean Architecture, including images used in this file,\ncome from the ",(0,a.jsx)(n.a,{href:"https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html",children:"Clean Coder blog"}),"."]}),"\n",(0,a.jsx)("img",{alt:"Clean Architecture Overview",src:(0,l.Ay)("img/CleanArchitecture.jpg")}),"\n",(0,a.jsx)(n.p,{children:"While the broad strokes remain the same as the Clean Coder definitions, this document will tie into our current architecture for realistic examples."}),"\n",(0,a.jsx)(n.h3,{id:"broad-strokes",children:"Broad Strokes"}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsxs)(n.li,{children:["Layers in Clean Architecture are ordered such that outer layers are dependent on inner layers.","\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsx)(n.li,{children:"The opposite should never be the case, or at least as little as possible."}),"\n",(0,a.jsx)(n.li,{children:"The ideal state is that if an element in an outer layer changes it should change none of the layers within it."}),"\n"]}),"\n"]}),"\n",(0,a.jsx)(n.li,{children:"The closer you get to the innermost layer, the closer you are to the raw business logic that acts on raw data."}),"\n",(0,a.jsx)(n.li,{children:"The number and labels of layers are not important, and are simply used as shorthand for the types of resources present at deeper/higher levels."}),"\n"]}),"\n",(0,a.jsx)(n.h2,{id:"layers",children:"Layers"}),"\n",(0,a.jsx)(n.h3,{id:"reasons-for-layers",children:"Reasons for Layers"}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsx)(n.li,{children:"Isolating layers reduces the chance for changes to that layer to affect other layers.\nFor example, if the Database code is isolated from the business logic, then changes to database technology will not require rewriting business logic."}),"\n",(0,a.jsx)(n.li,{children:"Allows development and testing of individual components without an understanding of the tech stack beyond that component."}),"\n"]}),"\n",(0,a.jsx)("a",{name:"frameworks-and-drivers"}),"\n",(0,a.jsx)(n.h3,{id:"frameworks-and-drivers-layer",children:'"Frameworks and Drivers" Layer'}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsx)(n.li,{children:"The outermost layer, often components external to the central product."}),"\n",(0,a.jsx)(n.li,{children:"May change based on changes from inner layers."}),"\n"]}),"\n",(0,a.jsx)(n.h4,{id:"orca-examples",children:"Orca Examples"}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsx)(n.li,{children:"API Gateway"}),"\n",(0,a.jsx)(n.li,{children:"Postgres Database"}),"\n",(0,a.jsx)(n.li,{children:"S3 Buckets"}),"\n",(0,a.jsx)(n.li,{children:"SQS Queues"}),"\n",(0,a.jsx)(n.li,{children:"Lambda API"}),"\n",(0,a.jsx)(n.li,{children:"Step Functions"}),"\n"]}),"\n",(0,a.jsx)("a",{name:"interface"}),"\n",(0,a.jsx)(n.h3,{id:"interface-adapters-layer",children:'"Interface Adapters" Layer'}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsxs)(n.li,{children:["Best viewed as a sub-section of the ",(0,a.jsx)(n.a,{href:"#frameworks-and-drivers",children:'"Frameworks and Drivers" layer'}),".","\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsx)(n.li,{children:"Changes to the database change this layer as well, which would otherwise contradict the dependency chain of Clean Architecture."}),"\n"]}),"\n"]}),"\n",(0,a.jsxs)(n.li,{children:["Translates data between the forms required for the external components above it, and the internal components beneath it.","\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsx)(n.li,{children:"All technical details from the above layer should be stripped before handing down to the lower layer."}),"\n"]}),"\n"]}),"\n",(0,a.jsx)(n.li,{children:"Receives calls from the layer above it and/or the layer beneath it."}),"\n"]}),"\n",(0,a.jsx)(n.h4,{id:"resource-examples",children:"Resource Examples"}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsx)(n.li,{children:"Centralized code for contacting the Postgres Database"}),"\n",(0,a.jsx)(n.li,{children:"Centralized code for posting events to SQS Queues"}),"\n",(0,a.jsxs)(n.li,{children:["Pulling relevant information out of parameters passed to Lambda ",(0,a.jsx)(n.code,{children:"handler"})," functions before calling additional logic"]}),"\n"]}),"\n",(0,a.jsx)(n.h4,{id:"code-examples",children:"Code Examples"}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsxs)(n.li,{children:[(0,a.jsxs)(n.a,{href:"https://github.com/nasa/cumulus-orca/blob/master/tasks/internal_reconcile_report_orphan/src/adapters/storage/rdbms.py",children:["Storage adapter ",(0,a.jsx)(n.code,{children:"rdbms.py"})]}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsx)(n.li,{children:"Provides access to database without requiring knowledge of database outside of constructor."}),"\n",(0,a.jsx)(n.li,{children:"Implements single-purpose interface to allow future features to use different storage adapters as needed."}),"\n",(0,a.jsx)(n.li,{children:"Allows additional layer between RDBMS database technologies by isolating technology-specific SQL to abstract methods."}),"\n"]}),"\n"]}),"\n"]}),"\n",(0,a.jsx)("a",{name:"use-cases"}),"\n",(0,a.jsx)(n.h3,{id:"use-cases-layer",children:'"Use Cases" Layer'}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsxs)(n.li,{children:["The business logic of the application, often analogous to user stories.","\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsx)(n.li,{children:"Larger features and flows may consist of several Use Cases chained together by SQS Queues or Step Functions."}),"\n"]}),"\n"]}),"\n",(0,a.jsx)(n.li,{children:"May call higher or lower components as needed, though neither should need to know the details of the other."}),"\n"]}),"\n",(0,a.jsx)(n.h4,{id:"resource-examples-1",children:"Resource Examples"}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsxs)(n.li,{children:[(0,a.jsx)(n.code,{children:"task"})," functions in Lambdas that perform a series of operations."]}),"\n"]}),"\n",(0,a.jsx)(n.h4,{id:"code-examples-1",children:"Code Examples"}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsxs)(n.li,{children:[(0,a.jsxs)(n.a,{href:"https://github.com/nasa/cumulus-orca/blob/master/tasks/internal_reconcile_report_orphan/src/use_cases/get_orphans_page.py",children:["Use case ",(0,a.jsx)(n.code,{children:"get_orphans_page.py"})]}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsx)(n.li,{children:"Performs the underlying flow of getting results from the database adapter, and passing them out to the caller."}),"\n",(0,a.jsx)(n.li,{children:"Accepts adapters for specific purposes."}),"\n"]}),"\n"]}),"\n"]}),"\n",(0,a.jsx)("a",{name:"entities"}),"\n",(0,a.jsx)(n.h3,{id:"entities-layer",children:'"Entities" Layer'}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsx)(n.li,{children:"Simple, reusable objects and functions."}),"\n",(0,a.jsxs)(n.li,{children:["Can only communicate with the ",(0,a.jsx)(n.a,{href:"#use-cases",children:"Use Cases layer"}),"."]}),"\n"]}),"\n",(0,a.jsx)(n.h4,{id:"resource-examples-2",children:"Resource Examples"}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsx)(n.li,{children:"Shared helper libraries without external dependencies"}),"\n",(0,a.jsx)(n.li,{children:"Individual Lambda functions"}),"\n"]}),"\n",(0,a.jsx)(n.h4,{id:"code-examples-2",children:"Code Examples"}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsxs)(n.li,{children:[(0,a.jsxs)(n.a,{href:"https://github.com/nasa/cumulus-orca/blob/master/tasks/internal_reconcile_report_orphan/src/entities/orphan.py",children:["Entity ",(0,a.jsx)(n.code,{children:"orphan.py"})]}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsx)(n.li,{children:"Simple data classes."}),"\n",(0,a.jsx)(n.li,{children:"Standardizes information transfer between classes without the need for dictionary keys."}),"\n"]}),"\n"]}),"\n"]}),"\n",(0,a.jsx)(n.h2,{id:"additional-thoughts",children:"Additional Thoughts"}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsxs)(n.li,{children:["\n",(0,a.jsx)(n.p,{children:"Categorization of some resources are blurred."}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsx)(n.li,{children:"I have attempted to place each resource type type in its highest possible layer to encourage viewing that type's availability as mutable."}),"\n",(0,a.jsx)(n.li,{children:"StepFunctions are analogous to user stories, but are AWS reliant components and require a translation layer."}),"\n",(0,a.jsx)(n.li,{children:"The Lambda API (parameters for the handler) are dictated by AWS.\nLambdas also contain business logic, and should therefore contain their own translation layer between API and business logic."}),"\n"]}),"\n"]}),"\n",(0,a.jsxs)(n.li,{children:["\n",(0,a.jsx)(n.p,{children:"Orca does currently have some architecture that does not follow these principles."}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsx)(n.li,{children:"Database code is mixed into some of our lambdas, and the Postgres return structure in particular is used frequently rather than reformatting to avoid entanglement."}),"\n",(0,a.jsx)(n.li,{children:"We hope to clean some of this up, and to use these aforementioned practices going forward."}),"\n"]}),"\n"]}),"\n"]})]})}function u(e={}){const{wrapper:n}={...(0,t.R)(),...e.components};return n?(0,a.jsx)(n,{...e,children:(0,a.jsx)(h,{...e})}):h(e)}},8453:(e,n,s)=>{s.d(n,{R:()=>l,x:()=>i});var r=s(6540);const a={},t=r.createContext(a);function l(e){const n=r.useContext(t);return r.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function i(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(a):e.components||a:l(e.components),r.createElement(t.Provider,{value:n},e.children)}}}]);