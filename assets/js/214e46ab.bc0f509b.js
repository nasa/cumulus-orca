"use strict";(self.webpackChunkorca_website=self.webpackChunkorca_website||[]).push([[6059],{3905:function(e,t,r){r.d(t,{Zo:function(){return l},kt:function(){return m}});var n=r(7294);function o(e,t,r){return t in e?Object.defineProperty(e,t,{value:r,enumerable:!0,configurable:!0,writable:!0}):e[t]=r,e}function i(e,t){var r=Object.keys(e);if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(e);t&&(n=n.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),r.push.apply(r,n)}return r}function a(e){for(var t=1;t<arguments.length;t++){var r=null!=arguments[t]?arguments[t]:{};t%2?i(Object(r),!0).forEach((function(t){o(e,t,r[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(r)):i(Object(r)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(r,t))}))}return e}function c(e,t){if(null==e)return{};var r,n,o=function(e,t){if(null==e)return{};var r,n,o={},i=Object.keys(e);for(n=0;n<i.length;n++)r=i[n],t.indexOf(r)>=0||(o[r]=e[r]);return o}(e,t);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);for(n=0;n<i.length;n++)r=i[n],t.indexOf(r)>=0||Object.prototype.propertyIsEnumerable.call(e,r)&&(o[r]=e[r])}return o}var u=n.createContext({}),s=function(e){var t=n.useContext(u),r=t;return e&&(r="function"==typeof e?e(t):a(a({},t),e)),r},l=function(e){var t=s(e.components);return n.createElement(u.Provider,{value:t},e.children)},d={inlineCode:"code",wrapper:function(e){var t=e.children;return n.createElement(n.Fragment,{},t)}},p=n.forwardRef((function(e,t){var r=e.components,o=e.mdxType,i=e.originalType,u=e.parentName,l=c(e,["components","mdxType","originalType","parentName"]),p=s(r),m=o,f=p["".concat(u,".").concat(m)]||p[m]||d[m]||i;return r?n.createElement(f,a(a({ref:t},l),{},{components:r})):n.createElement(f,a({ref:t},l))}));function m(e,t){var r=arguments,o=t&&t.mdxType;if("string"==typeof e||o){var i=r.length,a=new Array(i);a[0]=p;var c={};for(var u in t)hasOwnProperty.call(t,u)&&(c[u]=t[u]);c.originalType=e,c.mdxType="string"==typeof e?e:o,a[1]=c;for(var s=2;s<i;s++)a[s]=r[s];return n.createElement.apply(null,a)}return n.createElement.apply(null,r)}p.displayName="MDXCreateElement"},6157:function(e,t,r){r.r(t),r.d(t,{assets:function(){return l},contentTitle:function(){return u},default:function(){return m},frontMatter:function(){return c},metadata:function(){return s},toc:function(){return d}});var n=r(7462),o=r(3366),i=(r(7294),r(3905)),a=["components"],c={id:"orca-intro",title:"Introduction to ORCA",description:"Initial document describing what ORCA is and resources available."},u=void 0,s={unversionedId:"about/introduction/orca-intro",id:"about/introduction/orca-intro",title:"Introduction to ORCA",description:"Initial document describing what ORCA is and resources available.",source:"@site/docs/about/introduction/orca-intro.md",sourceDirName:"about/introduction",slug:"/about/introduction/orca-intro",permalink:"/cumulus-orca/docs/about/introduction/orca-intro",draft:!1,editUrl:"https://github.com/nasa/cumulus-orca/edit/develop/website/docs/about/introduction/orca-intro.md",tags:[],version:"current",frontMatter:{id:"orca-intro",title:"Introduction to ORCA",description:"Initial document describing what ORCA is and resources available."},sidebar:"about_orca",next:{title:"Navigating the ORCA Documents",permalink:"/cumulus-orca/docs/about/introduction/intro-navigating"}},l={},d=[{value:"What is ORCA?",id:"what-is-orca",level:2},{value:"How do I implement or use ORCA?",id:"how-do-i-implement-or-use-orca",level:2}],p={toc:d};function m(e){var t=e.components,r=(0,o.Z)(e,a);return(0,i.kt)("wrapper",(0,n.Z)({},p,r,{components:t,mdxType:"MDXLayout"}),(0,i.kt)("h2",{id:"what-is-orca"},"What is ORCA?"),(0,i.kt)("p",null,"The Operational Recovery Cloud Archive (ORCA) provides a baseline solution for\ncreating, and managing operational backups in the cloud. In addition, best\npractices and recovery code that manages common baseline recovery scenarios is\nalso maintained. Requirements and use cases for ORCA are derived from the\nORCA Working Group."),(0,i.kt)("h2",{id:"how-do-i-implement-or-use-orca"},"How do I implement or use ORCA?"),(0,i.kt)("p",null,"Information on implementing ORCA is located ",(0,i.kt)("a",{parentName:"p",href:"/cumulus-orca/docs/developer/deployment-guide/deployment"},"here"),"."),(0,i.kt)("p",null,"Information on ORCA use for Operators and Data Managers is located ",(0,i.kt)("a",{parentName:"p",href:"/cumulus-orca/docs/operator/operator-intro"},"here"),"."))}m.isMDXComponent=!0}}]);