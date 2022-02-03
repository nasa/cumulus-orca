"use strict";(self.webpackChunkorca_website=self.webpackChunkorca_website||[]).push([[6427,2083],{8560:function(e,t,o){o.r(t),o.d(t,{frontMatter:function(){return u},contentTitle:function(){return m},metadata:function(){return d},toc:function(){return h},default:function(){return p}});var r=o(7462),n=o(3366),i=(o(7294),o(3905)),a=o(4079),s=o(4996),c=["components"],u={id:"architecture-software-system",title:"Software System Architecture",description:"High level overview of ORCA software system architecture."},m=void 0,d={unversionedId:"about/architecture/architecture-software-system",id:"about/architecture/architecture-software-system",title:"Software System Architecture",description:"High level overview of ORCA software system architecture.",source:"@site/docs/about/architecture/architecture-software-system.mdx",sourceDirName:"about/architecture",slug:"/about/architecture/architecture-software-system",permalink:"/cumulus-orca/docs/about/architecture/architecture-software-system",editUrl:"https://github.com/nasa/cumulus-orca/edit/develop/website/docs/about/architecture/architecture-software-system.mdx",tags:[],version:"current",frontMatter:{id:"architecture-software-system",title:"Software System Architecture",description:"High level overview of ORCA software system architecture."},sidebar:"about_orca",previous:{title:"ORCA Architecture Introduction",permalink:"/cumulus-orca/docs/about/architecture/architecture-intro"},next:{title:"Archive Container Architecture",permalink:"/cumulus-orca/docs/about/architecture/architecture-archive-container"}},h=[],l={toc:h};function p(e){var t=e.components,o=(0,n.Z)(e,c);return(0,i.kt)("wrapper",(0,r.Z)({},l,o,{components:t,mdxType:"MDXLayout"}),(0,i.kt)("p",null,"The ORCA software system is currently made up of three primary functions. The\nfirst function is to archive a secondary copy of the data. This is done by\ncapitalizing on Cumulus Workflows and AWS Lambda. An end user would only need to\nadd the proper ORCA components to their ingest workflow in order to use the feature.\nThe second function is recovery of data from the secondary copy. Adding this functionality\nis more involved but requires the user to add the proper components and\nconfiguration to Cumulus to utilize. The final function is to provide end users\ninsight into the ORCA system for monitoring and data management. This is done by\nproviding the end user with an API to access information on the ORCA system. The\ndiagram below gives a software system view of ORCA and the various containers and\nprotocols used within the system. The following pages go into further details on\neach container."),(0,i.kt)(a.default,{imageSource:(0,s.Z)("img/ORCA-Architecture-ORCA-System.svg"),imageAlt:"ORCA System Architecture",zoomInPic:(0,s.Z)("img/zoom-in.svg"),zoomOutPic:(0,s.Z)("img/zoom-out.svg"),resetPic:(0,s.Z)("img/zoom-pan-reset.svg"),mdxType:"MyImage"}))}p.isMDXComponent=!0},4079:function(e,t,o){o.r(t),o.d(t,{frontMatter:function(){return m},contentTitle:function(){return d},metadata:function(){return h},toc:function(){return l},default:function(){return f}});var r=o(7462),n=o(3366),i=o(7294),a=o(3905),s=o(6126),c=["components"],u=["zoomIn","zoomOut","resetTransform"],m={},d=void 0,h={unversionedId:"templates/pan-zoom-image",id:"templates/pan-zoom-image",title:"pan-zoom-image",description:"The image below can be panned and zoomed using your mouse or the provided buttons.",source:"@site/docs/templates/pan-zoom-image.mdx",sourceDirName:"templates",slug:"/templates/pan-zoom-image",permalink:"/cumulus-orca/docs/templates/pan-zoom-image",editUrl:"https://github.com/nasa/cumulus-orca/edit/develop/website/docs/templates/pan-zoom-image.mdx",tags:[],version:"current",frontMatter:{}},l=[],p={toc:l};function f(e){var t=e.components,o=(0,n.Z)(e,c);return(0,a.kt)("wrapper",(0,r.Z)({},p,o,{components:t,mdxType:"MDXLayout"}),(0,a.kt)("div",{className:"admonition admonition-note alert alert--secondary"},(0,a.kt)("div",{parentName:"div",className:"admonition-heading"},(0,a.kt)("h5",{parentName:"div"},(0,a.kt)("span",{parentName:"h5",className:"admonition-icon"},(0,a.kt)("svg",{parentName:"span",xmlns:"http://www.w3.org/2000/svg",width:"14",height:"16",viewBox:"0 0 14 16"},(0,a.kt)("path",{parentName:"svg",fillRule:"evenodd",d:"M6.3 5.69a.942.942 0 0 1-.28-.7c0-.28.09-.52.28-.7.19-.18.42-.28.7-.28.28 0 .52.09.7.28.18.19.28.42.28.7 0 .28-.09.52-.28.7a1 1 0 0 1-.7.3c-.28 0-.52-.11-.7-.3zM8 7.99c-.02-.25-.11-.48-.31-.69-.2-.19-.42-.3-.69-.31H6c-.27.02-.48.13-.69.31-.2.2-.3.44-.31.69h1v3c.02.27.11.5.31.69.2.2.42.31.69.31h1c.27 0 .48-.11.69-.31.2-.19.3-.42.31-.69H8V7.98v.01zM7 2.3c-3.14 0-5.7 2.54-5.7 5.68 0 3.14 2.56 5.7 5.7 5.7s5.7-2.55 5.7-5.7c0-3.15-2.56-5.69-5.7-5.69v.01zM7 .98c3.86 0 7 3.14 7 7s-3.14 7-7 7-7-3.12-7-7 3.14-7 7-7z"}))),"Interactive Image")),(0,a.kt)("div",{parentName:"div",className:"admonition-content"},(0,a.kt)("p",{parentName:"div"},"The image below can be panned and zoomed using your mouse or the provided buttons.\nTo reset the image to the original size on the page click ",(0,a.kt)("img",{width:"12px",height:"12px",src:o.resetPic,alt:"Reset Image"}),".\nIf you wish to view the full image on a separate page, click this ",(0,a.kt)("a",{href:o.imageSource,target:"_blank",rel:"noopener noreferrer"},"link"),"."))),(0,a.kt)(s.d$,{defaultScale:1,mdxType:"TransformWrapper"},(function(e){var t=e.zoomIn,r=e.zoomOut,c=e.resetTransform;(0,n.Z)(e,u);return(0,a.kt)(i.Fragment,null,(0,a.kt)("div",{className:"tools"},(0,a.kt)("button",{onClick:function(){return t()}},(0,a.kt)("img",{width:"15px",height:"15px",src:o.zoomInPic,alt:"Zoom In"})),(0,a.kt)("button",{onClick:function(){return r()}},(0,a.kt)("img",{width:"15px",height:"15px",src:o.zoomOutPic,alt:"Zoom Out"})),(0,a.kt)("button",{onClick:function(){return c()}},(0,a.kt)("img",{width:"15px",height:"15px",src:o.resetPic,alt:"Reset Image"}))),(0,a.kt)(s.Uv,{mdxType:"TransformComponent"},(0,a.kt)("img",{src:o.imageSource,alt:o.imageAlt})))})))}f.isMDXComponent=!0}}]);