"use strict";(self.webpackChunkorca_website=self.webpackChunkorca_website||[]).push([[592,2083],{9578:(t,e,o)=>{o.r(e),o.d(e,{assets:()=>m,contentTitle:()=>c,default:()=>h,frontMatter:()=>s,metadata:()=>u,toc:()=>l});var r=o(7462),a=(o(7294),o(3905)),i=o(4079),n=o(4996);const s={id:"architecture-intro",title:"ORCA Architecture Introduction",description:"High level overview of ORCA architecture."},c=void 0,u={unversionedId:"about/architecture/architecture-intro",id:"about/architecture/architecture-intro",title:"ORCA Architecture Introduction",description:"High level overview of ORCA architecture.",source:"@site/docs/about/architecture/architecture-intro.mdx",sourceDirName:"about/architecture",slug:"/about/architecture/architecture-intro",permalink:"/cumulus-orca/docs/about/architecture/architecture-intro",draft:!1,editUrl:"https://github.com/nasa/cumulus-orca/edit/develop/website/docs/about/architecture/architecture-intro.mdx",tags:[],version:"current",frontMatter:{id:"architecture-intro",title:"ORCA Architecture Introduction",description:"High level overview of ORCA architecture."},sidebar:"about_orca",previous:{title:"Glossary",permalink:"/cumulus-orca/docs/about/introduction/intro-glossary"},next:{title:"Software System Architecture",permalink:"/cumulus-orca/docs/about/architecture/architecture-software-system"}},m={},l=[],d={toc:l};function h(t){let{components:e,...o}=t;return(0,a.kt)("wrapper",(0,r.Z)({},d,o,{components:e,mdxType:"MDXLayout"}),(0,a.kt)("p",null,"ORCA relies heavily on Cumulus and integrates with Cumulus messaging,\nfunctionality, and UI elements. The diagram below provides insight into how the\nsoftware systems interact along with the network and OU boundaries that are\ncrossed using the ORCA system. From a security standpoint, ORCA is generally not\ninteracted directly but instead is acted on by the existing Cumulus systems APIs\nand Dashboard UI. Note that the actual archive storage for ORCA is maintained in\na separate account and VPC. This is done to better separate costs and\npermissions related to this secondary archive copy."),(0,a.kt)("p",null,"A copy of the architecture drawings in this section are available in\n",(0,a.kt)("a",{parentName:"p",href:"https://app.diagrams.net/"},"draw.io")," format ",(0,a.kt)("a",{href:(0,n.Z)("files/ORCA-Architecture.drawio"),target:"_blank",download:!0},"here"),"."),(0,a.kt)(i.default,{imageSource:(0,n.Z)("img/ORCA-Architecture-System-Context.svg"),imageAlt:"System Context",zoomInPic:(0,n.Z)("img/zoom-in.svg"),zoomOutPic:(0,n.Z)("img/zoom-out.svg"),resetPic:(0,n.Z)("img/zoom-pan-reset.svg"),mdxType:"MyImage"}))}h.isMDXComponent=!0},4079:(t,e,o)=>{o.r(e),o.d(e,{assets:()=>m,contentTitle:()=>c,default:()=>h,frontMatter:()=>s,metadata:()=>u,toc:()=>l});var r=o(7462),a=o(7294),i=o(3905),n=o(6126);const s={},c=void 0,u={unversionedId:"templates/pan-zoom-image",id:"templates/pan-zoom-image",title:"pan-zoom-image",description:"The image below can be panned and zoomed using your mouse or the provided buttons.",source:"@site/docs/templates/pan-zoom-image.mdx",sourceDirName:"templates",slug:"/templates/pan-zoom-image",permalink:"/cumulus-orca/docs/templates/pan-zoom-image",draft:!1,editUrl:"https://github.com/nasa/cumulus-orca/edit/develop/website/docs/templates/pan-zoom-image.mdx",tags:[],version:"current",frontMatter:{}},m={},l=[],d={toc:l};function h(t){let{components:e,...o}=t;return(0,i.kt)("wrapper",(0,r.Z)({},d,o,{components:e,mdxType:"MDXLayout"}),(0,i.kt)("admonition",{title:"Interactive Image",type:"note"},(0,i.kt)("p",{parentName:"admonition"},"The image below can be panned and zoomed using your mouse or the provided buttons.\nTo reset the image to the original size on the page click ",(0,i.kt)("img",{width:"12px",height:"12px",src:o.resetPic,alt:"Reset Image"}),".\nIf you wish to view the full image on a separate page, click this ",(0,i.kt)("a",{href:o.imageSource,target:"_blank",rel:"noopener noreferrer"},"link"),".")),(0,i.kt)(n.d$,{defaultScale:1,mdxType:"TransformWrapper"},(t=>{let{zoomIn:e,zoomOut:r,resetTransform:s,...c}=t;return(0,i.kt)(a.Fragment,null,(0,i.kt)("div",{className:"tools"},(0,i.kt)("button",{onClick:()=>e()},(0,i.kt)("img",{width:"15px",height:"15px",src:o.zoomInPic,alt:"Zoom In"})),(0,i.kt)("button",{onClick:()=>r()},(0,i.kt)("img",{width:"15px",height:"15px",src:o.zoomOutPic,alt:"Zoom Out"})),(0,i.kt)("button",{onClick:()=>s()},(0,i.kt)("img",{width:"15px",height:"15px",src:o.resetPic,alt:"Reset Image"}))),(0,i.kt)(n.Uv,{mdxType:"TransformComponent"},(0,i.kt)("img",{src:o.imageSource,alt:o.imageAlt})))})))}h.isMDXComponent=!0}}]);