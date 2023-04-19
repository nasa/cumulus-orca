"use strict";(self.webpackChunkorca_website=self.webpackChunkorca_website||[]).push([[4814],{3905:(e,t,r)=>{r.d(t,{Zo:()=>c,kt:()=>g});var n=r(7294);function o(e,t,r){return t in e?Object.defineProperty(e,t,{value:r,enumerable:!0,configurable:!0,writable:!0}):e[t]=r,e}function s(e,t){var r=Object.keys(e);if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(e);t&&(n=n.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),r.push.apply(r,n)}return r}function a(e){for(var t=1;t<arguments.length;t++){var r=null!=arguments[t]?arguments[t]:{};t%2?s(Object(r),!0).forEach((function(t){o(e,t,r[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(r)):s(Object(r)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(r,t))}))}return e}function i(e,t){if(null==e)return{};var r,n,o=function(e,t){if(null==e)return{};var r,n,o={},s=Object.keys(e);for(n=0;n<s.length;n++)r=s[n],t.indexOf(r)>=0||(o[r]=e[r]);return o}(e,t);if(Object.getOwnPropertySymbols){var s=Object.getOwnPropertySymbols(e);for(n=0;n<s.length;n++)r=s[n],t.indexOf(r)>=0||Object.prototype.propertyIsEnumerable.call(e,r)&&(o[r]=e[r])}return o}var p=n.createContext({}),l=function(e){var t=n.useContext(p),r=t;return e&&(r="function"==typeof e?e(t):a(a({},t),e)),r},c=function(e){var t=l(e.components);return n.createElement(p.Provider,{value:t},e.children)},d="mdxType",u={inlineCode:"code",wrapper:function(e){var t=e.children;return n.createElement(n.Fragment,{},t)}},m=n.forwardRef((function(e,t){var r=e.components,o=e.mdxType,s=e.originalType,p=e.parentName,c=i(e,["components","mdxType","originalType","parentName"]),d=l(r),m=o,g=d["".concat(p,".").concat(m)]||d[m]||u[m]||s;return r?n.createElement(g,a(a({ref:t},c),{},{components:r})):n.createElement(g,a({ref:t},c))}));function g(e,t){var r=arguments,o=t&&t.mdxType;if("string"==typeof e||o){var s=r.length,a=new Array(s);a[0]=m;var i={};for(var p in t)hasOwnProperty.call(t,p)&&(i[p]=t[p]);i.originalType=e,i[d]="string"==typeof e?e:o,a[1]=i;for(var l=2;l<s;l++)a[l]=r[l];return n.createElement.apply(null,a)}return n.createElement.apply(null,r)}m.displayName="MDXCreateElement"},2156:(e,t,r)=>{r.r(t),r.d(t,{assets:()=>p,contentTitle:()=>a,default:()=>d,frontMatter:()=>s,metadata:()=>i,toc:()=>l});var n=r(7462),o=(r(7294),r(3905));const s={id:"postgres-tests",title:"Postgres Tests",description:"Instructions on running 'postgres' tests."},a=void 0,i={unversionedId:"developer/development-guide/code/postgres-tests",id:"developer/development-guide/code/postgres-tests",title:"Postgres Tests",description:"Instructions on running 'postgres' tests.",source:"@site/docs/developer/development-guide/code/postgres-tests.md",sourceDirName:"developer/development-guide/code",slug:"/developer/development-guide/code/postgres-tests",permalink:"/cumulus-orca/docs/developer/development-guide/code/postgres-tests",draft:!1,editUrl:"https://github.com/nasa/cumulus-orca/edit/develop/website/docs/developer/development-guide/code/postgres-tests.md",tags:[],version:"current",frontMatter:{id:"postgres-tests",title:"Postgres Tests",description:"Instructions on running 'postgres' tests."},sidebar:"dev_guide",previous:{title:"Integration Tests",permalink:"/cumulus-orca/docs/developer/development-guide/code/integration-tests"},next:{title:"ORCA Logs",permalink:"/cumulus-orca/docs/developer/development-guide/code/orca-logging"}},p={},l=[{value:"Preparing to Run Postgres Tests",id:"preparing-to-run-postgres-tests",level:2}],c={toc:l};function d(e){let{components:t,...r}=e;return(0,o.kt)("wrapper",(0,n.Z)({},c,r,{components:t,mdxType:"MDXLayout"}),(0,o.kt)("admonition",{type:"tip"},(0,o.kt)("p",{parentName:"admonition"},"Run through the steps in ",(0,o.kt)("a",{parentName:"p",href:"/cumulus-orca/docs/developer/development-guide/code/setup-dev-env"},"Setting Up a Dev Environment")," prior to modifying/testing code.")),(0,o.kt)("h2",{id:"preparing-to-run-postgres-tests"},"Preparing to Run Postgres Tests"),(0,o.kt)("p",null,"Test files ending in '_postgres.py' require a postgres database to be accessible."),(0,o.kt)("ol",null,(0,o.kt)("li",{parentName:"ol"},"Make sure you have Docker running on your machine."),(0,o.kt)("li",{parentName:"ol"},"Open a command prompt and run",(0,o.kt)("pre",{parentName:"li"},(0,o.kt)("code",{parentName:"pre",className:"language-commandline"},"docker run -it --rm --name some-postgres -v [path to repository]/database/ddl/base:/docker-entrypoint-initdb.d/ -p 5432:5432 -e POSTGRES_PASSWORD=[your db password here] postgres\n"))),(0,o.kt)("li",{parentName:"ol"},"The running database can now be accessed at localhost:5432"),(0,o.kt)("li",{parentName:"ol"},"Use the username 'postgres', and your new db password to access the db, and set the password for 'druser'.",(0,o.kt)("pre",{parentName:"li"},(0,o.kt)("code",{parentName:"pre",className:"language-commandline"},"docker run -it --rm --network host -e POSTGRES_PASSWORD=[your user password here] postgres psql -h localhost -U postgres`\n"))),(0,o.kt)("li",{parentName:"ol"},"Place a file called 'private_config.json' in the postgres' test folder and give it the information for your database.",(0,o.kt)("pre",{parentName:"li"},(0,o.kt)("code",{parentName:"pre",className:"language-json"},'{"DATABASE_HOST": "localhost",\n"DATABASE_PORT": "5432",\n"DATABASE_NAME": "orca",\n"DATABASE_USER": "druser",\n"DATABASE_PW": "[your user password here]",\n"MASTER_USER_PW": "[your db password here]"}\n')),"These values will be injected into your environment variables before the test is run."),(0,o.kt)("li",{parentName:"ol"},"You may now run postgres tests the same way you would ",(0,o.kt)("a",{parentName:"li",href:"unit-tests"},"unit tests"),".")))}d.isMDXComponent=!0}}]);