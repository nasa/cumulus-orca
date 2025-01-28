"use strict";(self.webpackChunkorca_website=self.webpackChunkorca_website||[]).push([[9878],{8356:(e,t,r)=>{r.r(t),r.d(t,{assets:()=>u,contentTitle:()=>s,default:()=>d,frontMatter:()=>i,metadata:()=>o,toc:()=>h});const o=JSON.parse('{"id":"about/architecture/architecture-recover-container","title":"Recover Container Architecture","description":"High level overview of ORCA recover container architecture.","source":"@site/docs/about/architecture/architecture-restore-container.mdx","sourceDirName":"about/architecture","slug":"/about/architecture/architecture-recover-container","permalink":"/cumulus-orca/docs/about/architecture/architecture-recover-container","draft":false,"unlisted":false,"editUrl":"https://github.com/nasa/cumulus-orca/edit/develop/website/docs/about/architecture/architecture-restore-container.mdx","tags":[],"version":"current","frontMatter":{"id":"architecture-recover-container","title":"Recover Container Architecture","description":"High level overview of ORCA recover container architecture."},"sidebar":"about_orca","previous":{"title":"Archive Container Architecture","permalink":"/cumulus-orca/docs/about/architecture/architecture-archive-container"},"next":{"title":"API Container Architecture","permalink":"/cumulus-orca/docs/about/architecture/architecture-api-container"}}');var c=r(4848),n=r(8453),a=r(6025);const i={id:"architecture-recover-container",title:"Recover Container Architecture",description:"High level overview of ORCA recover container architecture."},s=void 0,u={},h=[];function l(e){const t={p:"p",...(0,n.R)(),...e.components};return(0,c.jsxs)(c.Fragment,{children:[(0,c.jsx)(t.p,{children:"The ORCA recover data container contains all the components used in the recovery\nof data from the secondary archive. The diagram below shows the various\ninteractions of these components. Recovery processes are kicked off manually\nby an operator through the Cumulus Dashboard. The dashboard calls an API which\nkicks off a recovery workflow. Recovery is an asynchronous operation since data\nrequested from the archive can take up to 4 hours or more to reconstitute in most\nscenarios. Since it is asynchronous, the recovery container relies on a database\nto maintain the status of the request and event driven triggers to restore the\ndata once it has been reconstituted from the archive into an S3 bucket. Currently\ndata is copied back to the Cumulus S3 primary data bucket as the final restore\nstep. Determining the status of the recovery job is done by either checking the\nstatus on the Cumulus Dashboard or manually by accessing the ORCA API or querying\nthe database directly."}),"\n",(0,c.jsx)("img",{src:(0,a.Ay)("/img/ORCA-Architecture-Recovery-Container-Component.svg"),imageAlt:"ORCA Recover Data Container Context",zoomInPic:(0,a.Ay)("img/zoom-in.svg"),zoomOutPic:(0,a.Ay)("img/zoom-out.svg"),resetPic:(0,a.Ay)("img/zoom-pan-reset.svg")})]})}function d(e={}){const{wrapper:t}={...(0,n.R)(),...e.components};return t?(0,c.jsx)(t,{...e,children:(0,c.jsx)(l,{...e})}):l(e)}},8453:(e,t,r)=>{r.d(t,{R:()=>a,x:()=>i});var o=r(6540);const c={},n=o.createContext(c);function a(e){const t=o.useContext(n);return o.useMemo((function(){return"function"==typeof e?e(t):{...t,...e}}),[t,e])}function i(e){let t;return t=e.disableParentContext?"function"==typeof e.components?e.components(c):e.components||c:a(e.components),o.createElement(n.Provider,{value:t},e.children)}}}]);