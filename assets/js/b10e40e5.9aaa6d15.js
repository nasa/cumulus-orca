"use strict";(self.webpackChunkorca_website=self.webpackChunkorca_website||[]).push([[6615,2083],{1932:function(t,e,a){a.r(e),a.d(e,{assets:function(){return l},contentTitle:function(){return m},default:function(){return g},frontMatter:function(){return u},metadata:function(){return d},toc:function(){return p}});var n=a(7462),o=a(3366),i=(a(7294),a(3905)),r=a(4079),c=a(4996),s=["components"],u={id:"architecture-database-container",title:"Database Container Architecture",description:"ORCA database schema information."},m=void 0,d={unversionedId:"about/architecture/architecture-database-container",id:"about/architecture/architecture-database-container",title:"Database Container Architecture",description:"ORCA database schema information.",source:"@site/docs/about/architecture/architecture-database-container.mdx",sourceDirName:"about/architecture",slug:"/about/architecture/architecture-database-container",permalink:"/cumulus-orca/docs/about/architecture/architecture-database-container",draft:!1,editUrl:"https://github.com/nasa/cumulus-orca/edit/develop/website/docs/about/architecture/architecture-database-container.mdx",tags:[],version:"current",frontMatter:{id:"architecture-database-container",title:"Database Container Architecture",description:"ORCA database schema information."},sidebar:"about_orca",previous:{title:"API Container Architecture",permalink:"/cumulus-orca/docs/about/architecture/architecture-api-container"},next:{title:"ORCA Tips",permalink:"/cumulus-orca/docs/about/tips"}},l={},p=[],h={toc:p};function g(t){var e=t.components,a=(0,o.Z)(t,s);return(0,i.kt)("wrapper",(0,n.Z)({},h,a,{components:e,mdxType:"MDXLayout"}),(0,i.kt)("p",null,"ORCA utilizes a PostgreSQL compatible database instance in AWS. The ORCA database\nis used to order to track and manage the status of a recovery in a typical recover\ndata workflow and to maintain a catalog of ORCA data stored in the S3 Glacier\narchive. The diagram below provides details on the tables and the services that\naccess them. The data within the ORCA Recovery Status tables is considered transient\nand is typically no longer useful after a recovery has reached completion in a\nsuccessful state. The data within the ORCA Metadata Catalog tables points to the\nlatest version of the data stored in ORCA and provides a files association to a\ngranule, collection, and provider objects information. The ORCA Metadata Catalog\ntables data are also used by ORCA services to perform vital ORCA data management\nfunctions like reconciliation. The Schema Version Tracking table is used internally\nby ORCA to know if any schema migrations are needed for the ORCA code to function\nand provides an audit record of the installed ORCA schema."),(0,i.kt)(r.default,{imageSource:(0,c.Z)("img/ORCA-Architecture-Database-Container-Component.svg"),imageAlt:"ORCA Database Container Context",zoomInPic:(0,c.Z)("img/zoom-in.svg"),zoomOutPic:(0,c.Z)("img/zoom-out.svg"),resetPic:(0,c.Z)("img/zoom-pan-reset.svg"),mdxType:"MyImage"}))}g.isMDXComponent=!0},4079:function(t,e,a){a.r(e),a.d(e,{assets:function(){return p},contentTitle:function(){return d},default:function(){return f},frontMatter:function(){return m},metadata:function(){return l},toc:function(){return h}});var n=a(7462),o=a(3366),i=a(7294),r=a(3905),c=a(6126),s=["components"],u=["zoomIn","zoomOut","resetTransform"],m={},d=void 0,l={unversionedId:"templates/pan-zoom-image",id:"templates/pan-zoom-image",title:"pan-zoom-image",description:"The image below can be panned and zoomed using your mouse or the provided buttons.",source:"@site/docs/templates/pan-zoom-image.mdx",sourceDirName:"templates",slug:"/templates/pan-zoom-image",permalink:"/cumulus-orca/docs/templates/pan-zoom-image",draft:!1,editUrl:"https://github.com/nasa/cumulus-orca/edit/develop/website/docs/templates/pan-zoom-image.mdx",tags:[],version:"current",frontMatter:{}},p={},h=[],g={toc:h};function f(t){var e=t.components,a=(0,o.Z)(t,s);return(0,r.kt)("wrapper",(0,n.Z)({},g,a,{components:e,mdxType:"MDXLayout"}),(0,r.kt)("div",{className:"admonition admonition-note alert alert--secondary"},(0,r.kt)("div",{parentName:"div",className:"admonition-heading"},(0,r.kt)("h5",{parentName:"div"},(0,r.kt)("span",{parentName:"h5",className:"admonition-icon"},(0,r.kt)("svg",{parentName:"span",xmlns:"http://www.w3.org/2000/svg",width:"14",height:"16",viewBox:"0 0 14 16"},(0,r.kt)("path",{parentName:"svg",fillRule:"evenodd",d:"M6.3 5.69a.942.942 0 0 1-.28-.7c0-.28.09-.52.28-.7.19-.18.42-.28.7-.28.28 0 .52.09.7.28.18.19.28.42.28.7 0 .28-.09.52-.28.7a1 1 0 0 1-.7.3c-.28 0-.52-.11-.7-.3zM8 7.99c-.02-.25-.11-.48-.31-.69-.2-.19-.42-.3-.69-.31H6c-.27.02-.48.13-.69.31-.2.2-.3.44-.31.69h1v3c.02.27.11.5.31.69.2.2.42.31.69.31h1c.27 0 .48-.11.69-.31.2-.19.3-.42.31-.69H8V7.98v.01zM7 2.3c-3.14 0-5.7 2.54-5.7 5.68 0 3.14 2.56 5.7 5.7 5.7s5.7-2.55 5.7-5.7c0-3.15-2.56-5.69-5.7-5.69v.01zM7 .98c3.86 0 7 3.14 7 7s-3.14 7-7 7-7-3.12-7-7 3.14-7 7-7z"}))),"Interactive Image")),(0,r.kt)("div",{parentName:"div",className:"admonition-content"},(0,r.kt)("p",{parentName:"div"},"The image below can be panned and zoomed using your mouse or the provided buttons.\nTo reset the image to the original size on the page click ",(0,r.kt)("img",{width:"12px",height:"12px",src:a.resetPic,alt:"Reset Image"}),".\nIf you wish to view the full image on a separate page, click this ",(0,r.kt)("a",{href:a.imageSource,target:"_blank",rel:"noopener noreferrer"},"link"),"."))),(0,r.kt)(c.d$,{defaultScale:1,mdxType:"TransformWrapper"},(function(t){var e=t.zoomIn,n=t.zoomOut,s=t.resetTransform;(0,o.Z)(t,u);return(0,r.kt)(i.Fragment,null,(0,r.kt)("div",{className:"tools"},(0,r.kt)("button",{onClick:function(){return e()}},(0,r.kt)("img",{width:"15px",height:"15px",src:a.zoomInPic,alt:"Zoom In"})),(0,r.kt)("button",{onClick:function(){return n()}},(0,r.kt)("img",{width:"15px",height:"15px",src:a.zoomOutPic,alt:"Zoom Out"})),(0,r.kt)("button",{onClick:function(){return s()}},(0,r.kt)("img",{width:"15px",height:"15px",src:a.resetPic,alt:"Reset Image"}))),(0,r.kt)(c.Uv,{mdxType:"TransformComponent"},(0,r.kt)("img",{src:a.imageSource,alt:a.imageAlt})))})))}f.isMDXComponent=!0}}]);