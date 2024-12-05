"use strict";(self.webpackChunkorca_website=self.webpackChunkorca_website||[]).push([[739],{4684:(e,s,t)=>{t.r(s),t.d(s,{assets:()=>l,contentTitle:()=>o,default:()=>h,frontMatter:()=>r,metadata:()=>c,toc:()=>a});var n=t(4848),i=t(8453);const r={id:"unit-tests",title:"Unit Tests",description:"Instructions on running unit tests."},o=void 0,c={id:"developer/development-guide/code/unit-tests",title:"Unit Tests",description:"Instructions on running unit tests.",source:"@site/docs/developer/development-guide/code/unit-tests.md",sourceDirName:"developer/development-guide/code",slug:"/developer/development-guide/code/unit-tests",permalink:"/cumulus-orca/docs/developer/development-guide/code/unit-tests",draft:!1,unlisted:!1,editUrl:"https://github.com/nasa/cumulus-orca/edit/develop/website/docs/developer/development-guide/code/unit-tests.md",tags:[],version:"current",frontMatter:{id:"unit-tests",title:"Unit Tests",description:"Instructions on running unit tests."},sidebar:"dev_guide",previous:{title:"Local Debugging with AWS Resources",permalink:"/cumulus-orca/docs/developer/development-guide/code/local-debugging"},next:{title:"Integration Tests",permalink:"/cumulus-orca/docs/developer/development-guide/code/integration-tests"}},l={},a=[{value:"Running Unit Tests and Coverage Checks",id:"running-unit-tests-and-coverage-checks",level:2},{value:"Writing Unit Tests",id:"writing-unit-tests",level:2},{value:"Unit Test Standards and Tips",id:"unit-test-standards-and-tips",level:3}];function d(e){const s={a:"a",admonition:"admonition",code:"code",h2:"h2",h3:"h3",li:"li",ol:"ol",p:"p",pre:"pre",ul:"ul",...(0,i.R)(),...e.components};return(0,n.jsxs)(n.Fragment,{children:[(0,n.jsx)(s.admonition,{type:"tip",children:(0,n.jsxs)(s.p,{children:["Run through the steps in ",(0,n.jsx)(s.a,{href:"/cumulus-orca/docs/developer/development-guide/code/setup-dev-env",children:"Setting Up a Dev Environment"})," prior to modifying/testing code."]})}),"\n",(0,n.jsx)(s.h2,{id:"running-unit-tests-and-coverage-checks",children:"Running Unit Tests and Coverage Checks"}),"\n",(0,n.jsxs)(s.ol,{children:["\n",(0,n.jsxs)(s.li,{children:["\n",(0,n.jsx)(s.p,{children:"Navigate to the task's base folder."}),"\n"]}),"\n",(0,n.jsxs)(s.li,{children:["\n",(0,n.jsx)(s.p,{children:"Activate the virtual environment."}),"\n"]}),"\n",(0,n.jsxs)(s.li,{children:["\n",(0,n.jsx)(s.p,{children:"Run"}),"\n",(0,n.jsx)(s.pre,{children:(0,n.jsx)(s.code,{className:"language-commandline",children:"coverage run --source [name of lambda] -m pytest\n"})}),"\n"]}),"\n",(0,n.jsxs)(s.li,{children:["\n",(0,n.jsx)(s.p,{children:"Output the coverage results to the file system by running"}),"\n",(0,n.jsx)(s.pre,{children:(0,n.jsx)(s.code,{className:"language-commandline",children:"coverage html\n"})}),"\n"]}),"\n"]}),"\n",(0,n.jsx)(s.admonition,{type:"tip",children:(0,n.jsxs)(s.p,{children:["For error-free running of postgres tests, see ",(0,n.jsx)(s.a,{href:"postgres-tests",children:"Postgres Tests"}),"."]})}),"\n",(0,n.jsx)(s.h2,{id:"writing-unit-tests",children:"Writing Unit Tests"}),"\n",(0,n.jsxs)(s.p,{children:["Any written code should have a minimum of 80% ",(0,n.jsx)(s.a,{href:"#coverage",children:"coverage"}),", with higher coverage ideal.\nThis is a requirement for any new code, and will apply retroactively to old code as we have time to create/update tests."]}),"\n",(0,n.jsxs)(s.p,{children:["As described above, we use ",(0,n.jsx)(s.a,{href:"https://docs.pytest.org/en/stable/",children:"pytest"})," for running unit tests.\nIf pytest reports new or existing tests failing, then this must be resolved before a PR can be completed."]}),"\n",(0,n.jsxs)(s.p,{children:["Familiarize yourself with ",(0,n.jsx)(s.a,{href:"https://docs.python.org/3/library/unittest.mock.html",children:"Mock and Patch"})," as they are vital for testing components in isolation."]}),"\n",(0,n.jsx)(s.h3,{id:"unit-test-standards-and-tips",children:"Unit Test Standards and Tips"}),"\n",(0,n.jsxs)(s.ul,{children:["\n",(0,n.jsxs)(s.li,{children:["\n",(0,n.jsx)(s.p,{children:"Title your testing class with the format"}),"\n",(0,n.jsx)(s.pre,{children:(0,n.jsx)(s.code,{className:"language-python",children:"class Test[class name](unittest.TestCase):\n"})}),"\n"]}),"\n",(0,n.jsxs)(s.li,{children:["\n",(0,n.jsx)(s.p,{children:"Test a single piece of functionality at a time, such as a single path through a function.\nThis will make tests more valuable as diagnostic tools."}),"\n"]}),"\n",(0,n.jsxs)(s.li,{children:["\n",(0,n.jsx)(s.p,{children:"Title tests with the format"}),"\n",(0,n.jsx)(s.pre,{children:(0,n.jsx)(s.code,{className:"language-python",children:"def test_[function name]_[conditions]_[expected result](self):\n"})}),"\n"]}),"\n",(0,n.jsxs)(s.li,{children:["\n",(0,n.jsx)(s.p,{children:"Avoid using assignments to mock functions and objects."}),"\n",(0,n.jsx)(s.pre,{children:(0,n.jsx)(s.code,{className:"language-python",children:"class.func = Mock() # This is dangerous\n"})}),"\n",(0,n.jsx)(s.p,{children:"These Mocks will persist between tests, potentially causing failures at best, and false-positives at worst."}),"\n"]}),"\n",(0,n.jsxs)(s.li,{children:["\n",(0,n.jsxs)(s.p,{children:["Create mocks using ",(0,n.jsx)(s.a,{href:"https://docs.python.org/3/library/unittest.mock.html#patch",children:"patch"})]}),"\n",(0,n.jsx)(s.pre,{children:(0,n.jsx)(s.code,{className:"language-python",children:"@patch('class.first_func')\n@patch('class.second_func')\ndef test_name(self,\n              second_func_mock: MagicMock,\n              first_func_mock: MagicMock):\n"})}),"\n",(0,n.jsx)(s.admonition,{type:"note",children:(0,n.jsx)(s.p,{children:"Decorators reverse in order when passed to parameters."})}),"\n",(0,n.jsxs)(s.admonition,{type:"tip",children:[(0,n.jsx)(s.p,{children:"You can assign Mocks to Mock properties without your Mocks persisting between tests.\nThese Mocks will persist for the duration of the test, then will be removed."}),(0,n.jsx)(s.pre,{children:(0,n.jsx)(s.code,{className:"language-python",children:"func_mock = Mock()\nclass_mock.func = func_mock # This is fine\n"})})]}),"\n"]}),"\n",(0,n.jsxs)(s.li,{children:["\n",(0,n.jsxs)(s.p,{children:["Tests should ",(0,n.jsx)(s.a,{href:"https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_called",children:"assert"})," any effects that go outside the test's scope.\nDepending on the size of your test, this could be"]}),"\n",(0,n.jsxs)(s.ul,{children:["\n",(0,n.jsx)(s.li,{children:"Calls to external classes"}),"\n",(0,n.jsx)(s.li,{children:"Calls within the class to different functions"}),"\n"]}),"\n"]}),"\n",(0,n.jsxs)(s.li,{children:["\n",(0,n.jsxs)(s.p,{children:["Tests should ",(0,n.jsx)(s.a,{href:"https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_called",children:"assert"})," that affects you DO NOT expect do not occur.\nFor example, if 2/3 values in an array are passed through to another function then your test should assert that only the two values in question were passed.\nSimilarly, if the conditions in your test bypass an external effect, Mock that effect and make sure it is not called."]}),"\n"]}),"\n",(0,n.jsxs)(s.li,{children:["\n",(0,n.jsxs)(s.p,{children:["Generally speaking, any Mock you create should have at least one ",(0,n.jsx)(s.a,{href:"https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_called",children:"assert"})," statement.\nThe main exception is logging messages, particularly verbose or debug messages."]}),"\n"]}),"\n",(0,n.jsxs)(s.li,{children:["\n",(0,n.jsxs)(s.p,{children:["A different group of ",(0,n.jsx)(s.a,{href:"https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertEqual",children:"asserts"})," are used to check raw values, such as the return value of the function under test."]}),"\n",(0,n.jsx)(s.pre,{children:(0,n.jsx)(s.code,{className:"language-python",children:'self.assertEqual(expected_result, result, "Message to be displayed when assert fails.")\n'})}),"\n"]}),"\n"]})]})}function h(e={}){const{wrapper:s}={...(0,i.R)(),...e.components};return s?(0,n.jsx)(s,{...e,children:(0,n.jsx)(d,{...e})}):d(e)}},8453:(e,s,t)=>{t.d(s,{R:()=>o,x:()=>c});var n=t(6540);const i={},r=n.createContext(i);function o(e){const s=n.useContext(r);return n.useMemo((function(){return"function"==typeof e?e(s):{...s,...e}}),[s,e])}function c(e){let s;return s=e.disableParentContext?"function"==typeof e.components?e.components(i):e.components||i:o(e.components),n.createElement(r.Provider,{value:s},e.children)}}}]);