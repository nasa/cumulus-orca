"use strict";(self.webpackChunkorca_website=self.webpackChunkorca_website||[]).push([[6578],{3101:(e,t,r)=>{r.r(t),r.d(t,{assets:()=>u,contentTitle:()=>c,default:()=>d,frontMatter:()=>n,metadata:()=>a,toc:()=>h});var o=r(4848),i=r(8453),s=r(6025);const n={id:"architecture-software-system",title:"Software System Architecture",description:"High level overview of ORCA software system architecture."},c=void 0,a={id:"about/architecture/architecture-software-system",title:"Software System Architecture",description:"High level overview of ORCA software system architecture.",source:"@site/docs/about/architecture/architecture-software-system.mdx",sourceDirName:"about/architecture",slug:"/about/architecture/architecture-software-system",permalink:"/cumulus-orca/docs/about/architecture/architecture-software-system",draft:!1,unlisted:!1,editUrl:"https://github.com/nasa/cumulus-orca/edit/develop/website/docs/about/architecture/architecture-software-system.mdx",tags:[],version:"current",frontMatter:{id:"architecture-software-system",title:"Software System Architecture",description:"High level overview of ORCA software system architecture."},sidebar:"about_orca",previous:{title:"ORCA Architecture Introduction",permalink:"/cumulus-orca/docs/about/architecture/architecture-intro"},next:{title:"Archive Container Architecture",permalink:"/cumulus-orca/docs/about/architecture/architecture-archive-container"}},u={},h=[];function m(e){const t={p:"p",...(0,i.R)(),...e.components};return(0,o.jsxs)(o.Fragment,{children:[(0,o.jsx)(t.p,{children:"The ORCA software system is currently made up of three primary functions. The\nfirst function is to archive a secondary copy of the data. This is done by\ncapitalizing on Cumulus Workflows and AWS Lambda. An end user would only need to\nadd the proper ORCA components to their ingest workflow in order to use the feature.\nThe second function is recovery of data from the secondary copy. Adding this functionality\nis more involved but requires the user to add the proper components and\nconfiguration to Cumulus to utilize. The final function is to provide end users\ninsight into the ORCA system for monitoring and data management. This is done by\nproviding the end user with an API to access information on the ORCA system. The\ndiagram below gives a software system view of ORCA and the various containers and\nprotocols used within the system. The following pages go into further details on\neach container."}),"\n",(0,o.jsx)("img",{src:(0,s.A)("/img/ORCA-Architecture-ORCA-System.svg"),imageAlt:"ORCA System Architecture",zoomInPic:(0,s.A)("img/zoom-in.svg"),zoomOutPic:(0,s.A)("img/zoom-out.svg"),resetPic:(0,s.A)("img/zoom-pan-reset.svg")})]})}function d(e={}){const{wrapper:t}={...(0,i.R)(),...e.components};return t?(0,o.jsx)(t,{...e,children:(0,o.jsx)(m,{...e})}):m(e)}},8453:(e,t,r)=>{r.d(t,{R:()=>n,x:()=>c});var o=r(6540);const i={},s=o.createContext(i);function n(e){const t=o.useContext(s);return o.useMemo((function(){return"function"==typeof e?e(t):{...t,...e}}),[t,e])}function c(e){let t;return t=e.disableParentContext?"function"==typeof e.components?e.components(i):e.components||i:n(e.components),o.createElement(s.Provider,{value:t},e.children)}}}]);