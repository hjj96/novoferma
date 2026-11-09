// Normalize ImageGen outputs and build read-only color/comparison evidence.
const sharp=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const fs=require('fs');
const dir='output/research/novelty-color-match/',assets='output/concept/assets/';
const items=[['fibriki',8,'Фибрики'],['lulia-mini',3,'Люля мини']];
const median=a=>a.sort((a,b)=>a-b)[Math.floor(a.length/2)];
async function normalize(slug,version){
 const source=dir+`${slug}-pack-v${version}.png`,out=assets+`novelty-packaging/${slug}-pack-v${version}.webp`;
 const {data,info}=await sharp(source).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 let x0=info.width,y0=info.height,x1=0,y1=0;
 for(let y=0;y<info.height;y++)for(let x=0;x<info.width;x++)if(data[(y*info.width+x)*4+3]>=64){x0=Math.min(x0,x);x1=Math.max(x1,x);y0=Math.min(y0,y);y1=Math.max(y1,y);}
 const scale=Math.min(736/(x1-x0+1),640/(y1-y0+1)),pad=6;
 const left=Math.max(0,x0-pad),top=Math.max(0,y0-pad),right=Math.min(info.width,x1+pad+1),bottom=Math.min(info.height,y1+pad+1);
 const width=Math.round((right-left)*scale),height=Math.round((bottom-top)*scale);
 const im=await sharp(source).extract({left,top,width:right-left,height:bottom-top}).resize(width,height).png().toBuffer();
 await sharp({create:{width:800,height:800,channels:4,background:{r:0,g:0,b:0,alpha:0}}}).composite([{input:im,left:Math.round(400-width/2),top:Math.round(390-height/2)}]).webp({lossless:true,effort:6}).toFile(out);
 for(const [theme,background]of[['cream','#fff5e3'],['dark','#402111']])await sharp(out).flatten({background}).png().toFile(dir+`${slug}-pack-v${version}-${theme}.png`);
 return out;
}
async function sheet(name,list,columns=list.length,cell=440){
 const parts=[];
 for(let i=0;i<list.length;i++){
  const [label,file]=list[i],x=(i%columns)*cell,y=Math.floor(i/columns)*(cell+36);
  parts.push({input:await sharp(file).resize(cell,cell).png().toBuffer(),left:x,top:y+36});
  parts.push({input:Buffer.from(`<svg width="${cell}" height="36"><text x="16" y="25" font-family="Arial" font-size="17" fill="#402111">${label.replaceAll('&','&amp;')}</text></svg>`),left:x,top:y});
 }
 await sharp({create:{width:cell*columns,height:(cell+36)*Math.ceil(list.length/columns),channels:3,background:'#fff5e3'}}).composite(parts).png().toFile(dir+name+'.png');
}
async function sample(file){
 const {data,info}=await sharp(file).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 const region=(box,match)=>{const rgb=[[],[],[]];for(let y=box[1];y<box[3];y++)for(let x=box[0];x<box[2];x++){const i=(y*info.width+x)*4,r=data[i],g=data[i+1],b=data[i+2];if(data[i+3]>250&&match(r,g,b))for(let c=0;c<3;c++)rgb[c].push(data[i+c]);}return{pixels:rgb[0].length,rgb:rgb.map(median)};};
 return {file,paper:region([345,305,395,380],(r,g,b)=>r>180&&g>170&&b>135),logo:region([270,105,550,155],(r,g,b)=>r>180&&g<180&&b<100),type:region([80,165,705,235],(r,g,b)=>r<150&&g<120&&b<80)};
}
(async()=>{
 const outputs=[];
 for(const[slug,v,name]of items){const out=await normalize(slug,v);outputs.push({name,...await sample(out)});}
 const f=assets+'novelty-packaging/fibriki-pack-v8.webp',l=assets+'novelty-packaging/lulia-mini-pack-v3.webp';
 await sheet('family-lineup',[
  ['Стрипсы',assets+'catalogue-clean-v2/stripsy.webp'],['Фрикадельки',assets+'catalogue-clean-v2/frikadelki-klassicheskie.webp'],['Фибрики',f],['Котлеты по-домашнему',assets+'catalogue-clean-v2/kotlety-po-domashnemu.webp'],['Люля мини',l]
 ]);
 await sheet('before-after',[
  ['Фибрики — до',assets+'novelty-packaging/fibriki-pack-v6.webp'],['Фибрики — после',f],['Люля мини — до',assets+'novelty-packaging/lulia-mini-pack-v2.webp'],['Люля мини — после',l]
 ],2,600);
 await sheet('two-packages',[['Фибрики',f],['Люля мини',l]],2,700);
 const products=JSON.parse(fs.readFileSync('output/concept/products.json'));
 await sheet('all-sixteen-packages',products.map(p=>[p.displayName,assets+`catalogue-clean-v2/${p.slug}.webp`]).concat([['Фибрики',f],['Люля мини',l]]),4,400);
 fs.writeFileSync(dir+'color-analysis-after.json',JSON.stringify(outputs,null,2)+'\n');
 console.log(JSON.stringify(outputs));
})().catch(e=>{console.error(e);process.exit(1)});
