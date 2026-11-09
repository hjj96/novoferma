const sharp=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const fs=require('fs');
const dir='output/research/novelty-color-match/';
fs.mkdirSync(dir,{recursive:true});
const median=a=>a.sort((a,b)=>a-b)[Math.floor(a.length/2)];
async function sample(file){
 const {data,info}=await sharp(file).resize(800,800).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 const region=(box,match)=>{const rgb=[[],[],[]];for(let y=box[1];y<box[3];y++)for(let x=box[0];x<box[2];x++){const i=(y*info.width+x)*4,r=data[i],g=data[i+1],b=data[i+2];if(data[i+3]>250&&match(r,g,b))for(let c=0;c<3;c++)rgb[c].push(data[i+c]);}return{pixels:rgb[0].length,rgb:rgb.map(median)};};
 return {file,paper:region([345,305,395,380],(r,g,b)=>r>180&&g>170&&b>135),logo:region([270,105,550,155],(r,g,b)=>r>180&&g<180&&b<100),type:region([80,165,705,235],(r,g,b)=>r<150&&g<120&&b<80)};
}
(async()=>{
 const products=JSON.parse(fs.readFileSync('output/concept/products.json'));
 const records=[];
 for(const p of products)records.push({name:p.displayName,kind:'reference',...await sample(`output/concept/assets/catalogue-clean-v2/${p.slug}.webp`)});
 for(const [name,file]of[['Фибрики v6','fibriki-pack-v6.webp'],['Люля мини v2','lulia-mini-pack-v2.webp']])records.push({name,kind:'before',...await sample('output/concept/assets/novelty-packaging/'+file)});
 fs.writeFileSync(dir+'color-analysis-before.json',JSON.stringify(records,null,2)+'\n');
 console.log(JSON.stringify(records.map(r=>({name:r.name,paper:r.paper.rgb,logo:r.logo.rgb,type:r.type.rgb})),null,2));
 for(const [slug,label]of[['frikadelki-klassicheskie','meatballs'],['kotlety-po-domashnemu','homestyle'],['stripsy','strips']])await sharp(`output/concept/assets/catalogue-clean-v2/${slug}.webp`).flatten({background:'#fff5e3'}).png().toFile(dir+label+'-color-reference.png');
})();
