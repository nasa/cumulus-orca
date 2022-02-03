"use strict";(self.webpackChunkorca_website=self.webpackChunkorca_website||[]).push([[9762],{3905:function(e,t,n){n.d(t,{Zo:function(){return d},kt:function(){return m}});var r=n(7294);function o(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function a(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function i(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?a(Object(n),!0).forEach((function(t){o(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):a(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function l(e,t){if(null==e)return{};var n,r,o=function(e,t){if(null==e)return{};var n,r,o={},a=Object.keys(e);for(r=0;r<a.length;r++)n=a[r],t.indexOf(n)>=0||(o[n]=e[n]);return o}(e,t);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);for(r=0;r<a.length;r++)n=a[r],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(o[n]=e[n])}return o}var s=r.createContext({}),c=function(e){var t=r.useContext(s),n=t;return e&&(n="function"==typeof e?e(t):i(i({},t),e)),n},d=function(e){var t=c(e.components);return r.createElement(s.Provider,{value:t},e.children)},p={inlineCode:"code",wrapper:function(e){var t=e.children;return r.createElement(r.Fragment,{},t)}},u=r.forwardRef((function(e,t){var n=e.components,o=e.mdxType,a=e.originalType,s=e.parentName,d=l(e,["components","mdxType","originalType","parentName"]),u=c(n),m=o,f=u["".concat(s,".").concat(m)]||u[m]||p[m]||a;return n?r.createElement(f,i(i({ref:t},d),{},{components:n})):r.createElement(f,i({ref:t},d))}));function m(e,t){var n=arguments,o=t&&t.mdxType;if("string"==typeof e||o){var a=n.length,i=new Array(a);i[0]=u;var l={};for(var s in t)hasOwnProperty.call(t,s)&&(l[s]=t[s]);l.originalType=e,l.mdxType="string"==typeof e?e:o,i[1]=l;for(var c=2;c<a;c++)i[c]=n[c];return r.createElement.apply(null,i)}return r.createElement.apply(null,n)}u.displayName="MDXCreateElement"},7943:function(e,t,n){n.r(t),n.d(t,{frontMatter:function(){return s},contentTitle:function(){return c},metadata:function(){return d},toc:function(){return p},default:function(){return m}});var r=n(7462),o=n(3366),a=(n(7294),n(3905)),i=n(4996),l=["components"],s={id:"best-practices",title:"Best Practices",description:"Best practices for coding in ORCA."},c=void 0,d={unversionedId:"developer/development-guide/code/best-practices",id:"developer/development-guide/code/best-practices",title:"Best Practices",description:"Best practices for coding in ORCA.",source:"@site/docs/developer/development-guide/code/best-practices.mdx",sourceDirName:"developer/development-guide/code",slug:"/developer/development-guide/code/best-practices",permalink:"/cumulus-orca/docs/developer/development-guide/code/best-practices",editUrl:"https://github.com/nasa/cumulus-orca/edit/develop/website/docs/developer/development-guide/code/best-practices.mdx",tags:[],version:"current",frontMatter:{id:"best-practices",title:"Best Practices",description:"Best practices for coding in ORCA."},sidebar:"dev_guide",previous:{title:"Setting Up a Dev Environment",permalink:"/cumulus-orca/docs/developer/development-guide/code/setup-dev-env"},next:{title:"ORCA Versioning and Releases",permalink:"/cumulus-orca/docs/developer/development-guide/code/versioning-releases"}},p=[{value:"Unit Testing",id:"unit-testing",children:[],level:2},{value:"Code Style",id:"code-style",children:[],level:2},{value:"Stop on Failure",id:"stop-on-failure",children:[],level:2}],u={toc:p};function m(e){var t=e.components,n=(0,o.Z)(e,l);return(0,a.kt)("wrapper",(0,r.Z)({},u,n,{components:t,mdxType:"MDXLayout"}),(0,a.kt)("h2",{id:"unit-testing"},"Unit Testing"),(0,a.kt)("p",null,"All code should reach minimum 80% coverage through ",(0,a.kt)("a",{parentName:"p",href:"/cumulus-orca/docs/developer/development-guide/code/unit-tests"},"Unit Tests"),"."),(0,a.kt)("h2",{id:"code-style"},"Code Style"),(0,a.kt)("p",null,"We use the ",(0,a.kt)("a",{parentName:"p",href:"https://google.github.io/styleguide/pyguide.html"},"Google Style Guide")," for style elements such as documentation, titling, and structure."),(0,a.kt)("h2",{id:"stop-on-failure"},"Stop on Failure"),(0,a.kt)("p",null,"Failures within ORCA break through to the Cumulus workflow they are a part of.\nTo this end, raising an error is preferred over catching the error and returning a null value or error message.\nThe code examples below exemplify this idea by showing how to raise an error using python in different contexts."),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-python"},"try:\n    value = function(param)\nexcept requests_db.DatabaseError as err:\n    logging.error(err)\n    raise\n")),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-python"},'if not success:\n    logging.error(f"You may log additional information if desired. "\n                  f"param: {param}")\n    raise DescriptiveErrorType(f\'Error message to be raised info Cumulus workflow.\')\n')),(0,a.kt)("p",null,"Retries can then be configured in the workflow json if desired. See\n",(0,a.kt)("a",{parentName:"p",href:"https://docs.aws.amazon.com/step-functions/latest/dg/concepts-error-handling.html"},"documentation"),"\nand\n",(0,a.kt)("a",{parentName:"p",href:"https://aws.amazon.com/getting-started/hands-on/handle-serverless-application-errors-step-functions-lambda/"},"tutorials"),"\nfor more information.\nThe following snippet from the copy_to_glacier lambda demonstrates usage of retries for a lambda in an ingest workflow.\n",(0,a.kt)("inlineCode",{parentName:"p"},"MaxAttempts")," is set to 6, meaning that it will run the function a maximum of 7 times before transitioning to the ",(0,a.kt)("inlineCode",{parentName:"p"},"WorkflowFailed")," state.\n",(0,a.kt)("inlineCode",{parentName:"p"},"IntervalSeconds")," determines how many seconds the workflow will sleep between retries.\nA ",(0,a.kt)("inlineCode",{parentName:"p"},"BackOffRate")," of 2 means that the ",(0,a.kt)("inlineCode",{parentName:"p"},"IntervalSeconds")," will be doubled on each failure beyond the first."),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-json"},'"CopyToGlacier": {\n  ...\n  "Type": "Task",\n  "Resource": "${copy_to_glacier_task_arn}",\n  "Retry": [\n    {\n      "ErrorEquals": [\n        "Lambda.ServiceException",\n        "Lambda.AWSLambdaException",\n        "Lambda.SdkClientException"\n      ],\n      "IntervalSeconds": 2,\n      "MaxAttempts": 6,\n      "BackoffRate": 2\n    }\n  ],\n  "Catch": [\n    {\n      "ErrorEquals": [\n        "States.ALL"\n      ],\n      "ResultPath": "$.exception",\n      "Next": "WorkflowFailed"\n    }\n  ],\n  "Next": "WorkflowSucceeded"\n},\n')),(0,a.kt)("p",null,"If the retries are exceeded and the error is caught, then the workflow will show that it jumped to the ",(0,a.kt)("inlineCode",{parentName:"p"},"WorkflowFailed")," state."),(0,a.kt)("img",{alt:"Workflow Failed",src:(0,i.Z)("img/Workflow Failed.png")}),(0,a.kt)("p",null,"If the 'WorkflowFailed' state was not triggered, then the workflow will move on to the step defined in ",(0,a.kt)("inlineCode",{parentName:"p"},"Next"),"."),(0,a.kt)("img",{alt:"Workflow Succeeded",src:(0,i.Z)("img/Workflow Succeeded.png")}),(0,a.kt)("div",{className:"admonition admonition-note alert alert--secondary"},(0,a.kt)("div",{parentName:"div",className:"admonition-heading"},(0,a.kt)("h5",{parentName:"div"},(0,a.kt)("span",{parentName:"h5",className:"admonition-icon"},(0,a.kt)("svg",{parentName:"span",xmlns:"http://www.w3.org/2000/svg",width:"14",height:"16",viewBox:"0 0 14 16"},(0,a.kt)("path",{parentName:"svg",fillRule:"evenodd",d:"M6.3 5.69a.942.942 0 0 1-.28-.7c0-.28.09-.52.28-.7.19-.18.42-.28.7-.28.28 0 .52.09.7.28.18.19.28.42.28.7 0 .28-.09.52-.28.7a1 1 0 0 1-.7.3c-.28 0-.52-.11-.7-.3zM8 7.99c-.02-.25-.11-.48-.31-.69-.2-.19-.42-.3-.69-.31H6c-.27.02-.48.13-.69.31-.2.2-.3.44-.31.69h1v3c.02.27.11.5.31.69.2.2.42.31.69.31h1c.27 0 .48-.11.69-.31.2-.19.3-.42.31-.69H8V7.98v.01zM7 2.3c-3.14 0-5.7 2.54-5.7 5.68 0 3.14 2.56 5.7 5.7 5.7s5.7-2.55 5.7-5.7c0-3.15-2.56-5.69-5.7-5.69v.01zM7 .98c3.86 0 7 3.14 7 7s-3.14 7-7 7-7-3.12-7-7 3.14-7 7-7z"}))),"note")),(0,a.kt)("div",{parentName:"div",className:"admonition-content"},(0,a.kt)("p",{parentName:"div"},"In the event that an error may be transient, and failing would cause a large amount of redundant work for other objects, retrying a failing operation in code is acceptable with a strictly limited number of retries.\nYou will likely want to log each individual error for analytics and debugging."))))}m.isMDXComponent=!0}}]);