"use strict";(self.webpackChunkorca_website=self.webpackChunkorca_website||[]).push([[6597],{83:(e,n,i)=>{i.r(n),i.d(n,{assets:()=>o,contentTitle:()=>l,default:()=>p,frontMatter:()=>t,metadata:()=>s,toc:()=>c});const s=JSON.parse('{"id":"developer/development-guide/code/parallel-scripting","title":"Parallel Scripting","description":"Instructions on running multiple functions in a script in Parallel.","source":"@site/docs/developer/development-guide/code/parallel-scripting.md","sourceDirName":"developer/development-guide/code","slug":"/developer/development-guide/code/parallel-scripting","permalink":"/cumulus-orca/docs/developer/development-guide/code/parallel-scripting","draft":false,"unlisted":false,"editUrl":"https://github.com/nasa/cumulus-orca/edit/develop/website/docs/developer/development-guide/code/parallel-scripting.md","tags":[],"version":"current","frontMatter":{"id":"parallel-scripting","title":"Parallel Scripting","description":"Instructions on running multiple functions in a script in Parallel."},"sidebar":"dev_guide","previous":{"title":"ORCA Logs","permalink":"/cumulus-orca/docs/developer/development-guide/code/orca-logging"},"next":{"title":"Postgres Paging","permalink":"/cumulus-orca/docs/developer/development-guide/code/postgres-tips"}}');var r=i(4848),a=i(8453);const t={id:"parallel-scripting",title:"Parallel Scripting",description:"Instructions on running multiple functions in a script in Parallel."},l=void 0,o={},c=[{value:"Installation",id:"installation",level:2},{value:"Scripting Basics",id:"scripting-basics",level:2},{value:"Demo",id:"demo",level:4},{value:"Alternatives",id:"alternatives",level:2},{value:"Background and Wait (&amp;)",id:"background-and-wait-",level:3},{value:"Cons",id:"cons",level:4},{value:"Demo",id:"demo-1",level:4},{value:"Xargs",id:"xargs",level:3},{value:"Cons",id:"cons-1",level:4},{value:"Demo",id:"demo-2",level:4}];function d(e){const n={a:"a",admonition:"admonition",code:"code",h2:"h2",h3:"h3",h4:"h4",li:"li",p:"p",pre:"pre",ul:"ul",...(0,a.R)(),...e.components};return(0,r.jsxs)(r.Fragment,{children:[(0,r.jsxs)(n.p,{children:[(0,r.jsx)(n.a,{href:"https://www.gnu.org/software/parallel/man.html",children:"Parallel"})," is a means of running a function multiple times in different processes.\nThis can significantly increase the performance of scripts that loop with significant wait time.\nFor example, in cases with network calls such as package installation."]}),"\n",(0,r.jsx)(n.h2,{id:"installation",children:"Installation"}),"\n",(0,r.jsxs)(n.p,{children:["For development, install via ",(0,r.jsx)(n.a,{href:"https://formulae.brew.sh/formula/parallel",children:"brew"}),"."]}),"\n",(0,r.jsx)(n.h2,{id:"scripting-basics",children:"Scripting Basics"}),"\n",(0,r.jsxs)(n.p,{children:["Using parallel will run multiple instances of the command in different processes.\nStandard output for each process will be buffered, and shown all at once when the process completes.\nAfter all processes exit, execution of the main script will continue.\n",(0,r.jsx)(n.code,{children:"$?"})," will contain how many tasks exited with a non-0 exit code."]}),"\n",(0,r.jsx)(n.h4,{id:"demo",children:"Demo"}),"\n",(0,r.jsxs)(n.ul,{children:["\n",(0,r.jsxs)(n.li,{children:[(0,r.jsx)(n.code,{children:"--jobs 0"})," indicates that as many processes as possible should run at once."]}),"\n",(0,r.jsxs)(n.li,{children:[(0,r.jsx)(n.code,{children:"-n 1"})," limits the number of parameters per process to 1."]}),"\n",(0,r.jsxs)(n.li,{children:[(0,r.jsx)(n.code,{children:"-X"})," distributes the parameters among the new processes."]}),"\n",(0,r.jsxs)(n.li,{children:[(0,r.jsx)(n.code,{children:"--halt now,fail=1"})," is used to halt all ongoing processes once 1 process exits with a non-0 exit code. Modifies ",(0,r.jsx)(n.code,{children:"$?"})," to return the failing process' exit code instead of how many processes failed.","\n",(0,r.jsx)(n.admonition,{type:"tip",children:(0,r.jsx)(n.p,{children:"Since the exit code does not indicate which process failed, logging for individual processes should be robust."})}),"\n"]}),"\n"]}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{className:"language-bash",children:'parallel --jobs 0 -n 1 -X --halt now,fail=1 function_name ::: $parameter_array\nprocess_return_code=$?\nif [ $process_return_code -ne 0 ]; then\n  echo "ERROR: process failed with code $process_return_code."\n  failure=1\nfi\n'})}),"\n",(0,r.jsx)(n.h2,{id:"alternatives",children:"Alternatives"}),"\n",(0,r.jsx)(n.p,{children:"Some alternatives were researched, but found to be more limited."}),"\n",(0,r.jsx)(n.h3,{id:"background-and-wait-",children:"Background and Wait (&)"}),"\n",(0,r.jsxs)(n.p,{children:["If a function is run with a ",(0,r.jsx)(n.code,{children:"&"})," suffix, it will start in a new process.\nThe process ID can then be captured, and used to track progress and exit codes."]}),"\n",(0,r.jsx)(n.h4,{id:"cons",children:"Cons"}),"\n",(0,r.jsxs)(n.ul,{children:["\n",(0,r.jsx)(n.li,{children:"Requires extra code for managing processes."}),"\n",(0,r.jsx)(n.li,{children:"Logging is not grouped by function invocation."}),"\n"]}),"\n",(0,r.jsx)(n.h4,{id:"demo-1",children:"Demo"}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{className:"language-bash",children:'declare -A pids\nfor param in $parameter_array\ndo\nfunction_name $param &\npids[${param}]=$!  # This assumes that all parameters are unique.\ndone\n\nfailure=0\nfor param in "${!pids[@]}"\ndo\n  wait ${pids[$param]}\n  process_return_code=$?\n  if [ $process_return_code -ne 0 ]; then\n    echo "ERROR: $param failed."\n    failure=1\n  fi\ndone\n'})}),"\n",(0,r.jsx)(n.h3,{id:"xargs",children:(0,r.jsx)(n.a,{href:"https://www.man7.org/linux/man-pages/man1/xargs.1.html",children:"Xargs"})}),"\n",(0,r.jsx)(n.p,{children:"Xargs has several useful performance optimization parameters, but is more difficult to use."}),"\n",(0,r.jsx)(n.h4,{id:"cons-1",children:"Cons"}),"\n",(0,r.jsxs)(n.ul,{children:["\n",(0,r.jsx)(n.li,{children:"Logging is not grouped by function invocation."}),"\n",(0,r.jsx)(n.li,{children:"Parameters are passed in via a single string, split on a separator character, which is rather brittle."}),"\n",(0,r.jsx)(n.li,{children:"Exit codes are not passed out to main process."}),"\n"]}),"\n",(0,r.jsx)(n.h4,{id:"demo-2",children:"Demo"}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{className:"language-bash",children:'echo "${parameter_array[@]}" | xargs -n 1 -P 0 bash -c \'function_name "$@"\' _\n'})})]})}function p(e={}){const{wrapper:n}={...(0,a.R)(),...e.components};return n?(0,r.jsx)(n,{...e,children:(0,r.jsx)(d,{...e})}):d(e)}},8453:(e,n,i)=>{i.d(n,{R:()=>t,x:()=>l});var s=i(6540);const r={},a=s.createContext(r);function t(e){const n=s.useContext(a);return s.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function l(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(r):e.components||r:t(e.components),s.createElement(a.Provider,{value:n},e.children)}}}]);