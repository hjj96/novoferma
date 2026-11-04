// Read-only VM probe. No browser, navigation, email, network or source modification.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const events={};
const input={value:'Москва',setCustomValidity(s){this.validity=s},addEventListener(k,f){events['city:'+k]=f}};
const wanted={options:[{value:'all'},{value:'fibriki'}],selectedOptions:[{text:'Весь ассортимент'}]};
const form={reportValidity(){return true},addEventListener(k,f){events['form:'+k]=f}};
const feedback={hidden:true,children:[],replaceChildren(...x){this.children=x},append(x){this.children.push(x)}};
const selectors={'#city-form':form,'#city':input,'#wanted-product':wanted,'.form-feedback':feedback};
const context={
 matchMedia:()=>({matches:true,addEventListener(){}}),
 document:{querySelector:s=>selectors[s]??null,querySelectorAll:()=>[],addEventListener(){},body:{classList:{contains:()=>true}},createTextNode:s=>({textContent:s}),createElement:t=>({tagName:t,style:{}})},
 location:{search:'',href:''},addEventListener(){},URLSearchParams,encodeURIComponent,console,
};
vm.runInNewContext(fs.readFileSync(__dirname+'/snapshot/script.js','utf8'),context);
events['form:submit']({preventDefault(){}});
const first=feedback.children.at(-1).href;
input.value='Казань';wanted.selectedOptions=[{text:'Фибрики — новинка'}];
events['city:input']({target:input});
const afterEdit=feedback.children.at(-1).href;
assert.equal(afterEdit,first);
assert(decodeURIComponent(afterEdit).includes('Город: Москва'));
assert(!decodeURIComponent(afterEdit).includes('Казань'));
const output={test:'Change city/product after composing first draft',before:{city:'Москва',product:'Весь ассортимент'},after:{city:input.value,product:wanted.selectedOptions[0].text},feedbackStillVisible:!feedback.hidden,retryDraftStillOld:afterEdit===first,decodedRetry:decodeURIComponent(afterEdit),realNavigation:false};
fs.writeFileSync(__dirname+'/technical-form-check.json',JSON.stringify(output,null,2));
console.log(output);
