"""Restore catalogue image pixels into the first photographic scene.

The photograph supplies one shared floor, camera, light and contact shadows.
Original RGBA packshots are projected into the matching photographed package
faces with a homography. No package text or artwork is generated or retyped.
"""
from pathlib import Path
import json, base64
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/product-wallpapers-2026-11-07'
DEST=OUT/'realistic-shared-surface'
DEST.mkdir(exist_ok=True)
inventory=json.loads((OUT/'references/high-res-manifest.json').read_text())['products']
products={p['id']:p for p in inventory}
def uri(p):
    return 'data:image/png;base64,'+base64.b64encode(Path(p).read_bytes()).decode()

placements=[
    ('kotlety-kurinye',[[-124,-60],[136,74],[83,163],[-196,54]]),
    ('naggetsy-kurinye-s-syrom',[[-143,191],[77,382],[-4,469],[-254,315]]),
    ('kotlety-pikantnye',[[-129,452],[104,631],[-13,802],[-265,622]]),
    ('stripsy',[[-75,834],[228,940],[161,1120],[-175,988]]),
    ('bitochki-kurinye-s-ovoshchami',[[347,840],[572,896],[534,1070],[259,993]]),
    ('naggetsy-s-indeykoy-fitnes',[[766,941],[954,887],[1090,1049],[840,1121]]),
    ('kotlety-kurinye',[[1216,856],[1438,858],[1478,1050],[1164,1045]]),
    ('naggetsy-ostrye',[[1631,231],[1846,130],[1940,270],[1708,400]]),
    ('naggetsy-kurinye-s-syrom',[[1518,915],[1749,866],[1832,1030],[1501,1085]]),
    ('kotlety-kurinye',[[103,153],[316,100],[393,257],[152,307]]),
    ('bitochki-kurinye-s-ovoshchami',[[350,72],[560,20],[647,153],[402,218]]),
    ('ezhiki-iz-tsyplenka-s-risom',[[685,78],[931,79],[950,238],[663,237]]),
    ('popsy',[[978,35],[1184,-13],[1263,159],[1000,212]]),
    ('stripsy',[[1290,109],[1488,131],[1498,322],[1225,258]]),
    ('naggetsy-dinozavry',[[1458,42],[1643,-22],[1720,111],[1532,190]]),
    ('kotlety-po-domashnemu',[[77,378],[321,344],[375,519],[71,571]]),
    ('kurinyj-popkorn',[[377,294],[609,237],[688,396],[429,456]]),
    ('naggetsy-kurinye-s-syrom',[[700,338],[945,345],[966,539],[670,526]]),
    ('naggetsy-kurinye',[[941,276],[1171,236],[1257,394],[992,450]]),
    ('naggetsy-s-indeykoy-fitnes',[[346,541],[577,479],[659,634],[389,713]]),
    ('naggetsy-ostrye',[[1387,381],[1612,326],[1700,490],[1451,550]]),
    ('kotlety-pikantnye',[[94,648],[311,620],[375,791],[85,836]]),
    ('lulia-mini',[[604,688],[817,674],[884,846],[578,866]]),
    ('kotlety-po-italyanski',[[861,650],[1091,596],[1187,779],[898,836]]),
    ('frikadelki-klassicheskie',[[1128,478],[1368,457],[1414,644],[1122,652]]),
    ('fibriki',[[1418,621],[1668,606],[1690,799],[1388,805]]),
]

assets=[]
for pid,q in placements:
    p=products[pid]
    x0,y0,x1,y1=p['alpha_bbox_64']
    w,h=x1-x0,y1-y0
    # Back corners of the bowed paper sleeve and its two front corners.
    source=[[x0+.06*w,y0-.025*h],[x1-.06*w,y0-.025*h],
            [x1,y0+.77*h],[x0,y0+.77*h]]
    with Image.open(p['path']) as im:
        colors=[]
        for yy in range(int(y0+.08*h),int(y0+.70*h),8):
            for xx in range(int(x0+.12*w),int(x1-.12*w),8):
                r,g,b,a=im.getpixel((xx,yy))
                if a>240 and r>190 and g>175 and b>140 and 0<r-g<30 and 5<g-b<45:
                    colors.append((r,g,b))
        paper=[sorted(c[i] for c in colors)[int(len(colors)*.70)]/255 for i in range(3)]
    assets.append(dict(id=pid,url=uri(p['path']),source=source,target=q,paper=paper))

base=uri(DEST/'blank-photographic-plate.png')
payload=json.dumps(dict(base=base,assets=assets))
doc='''<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;width:3840px;height:2160px;overflow:hidden;background:#f8ecd6}
canvas{display:block;width:3840px;height:2160px}
</style></head><body><canvas width="3840" height="2160"></canvas><script>
const DATA=PAYLOAD;
const canvas=document.querySelector('canvas');
const gl=canvas.getContext('webgl',{alpha:false,antialias:true,preserveDrawingBuffer:true});
function shader(type,code){const s=gl.createShader(type);gl.shaderSource(s,code);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw gl.getShaderInfoLog(s);return s;}
const program=gl.createProgram();
gl.attachShader(program,shader(gl.VERTEX_SHADER,`attribute vec2 p;attribute vec2 uv;attribute vec2 local;uniform mat3 h;uniform vec2 screen;varying vec2 tex;varying vec2 st;void main(){vec3 q=h*vec3(p,1.);gl_Position=vec4(2.*q.x/screen.x-q.z,q.z-2.*q.y/screen.y,0.,q.z);tex=uv;st=local;}`));
gl.attachShader(program,shader(gl.FRAGMENT_SHADER,`precision highp float;uniform sampler2D image;uniform float face;uniform vec3 paper;varying vec2 tex;varying vec2 st;void main(){vec4 c=texture2D(image,tex);if(face<.5){gl_FragColor=c;return;}float edge=min(min(st.x,1.-st.x),min(st.y,1.-st.y));float a=c.a;float d=.006;for(int i=-1;i<=1;i++){for(int j=-1;j<=1;j++){a=min(a,texture2D(image,tex+vec2(float(i),float(j))*d).a);}}float mask=smoothstep(0.,.018,edge)*smoothstep(.90,.999,a);vec3 rgb=c.rgb/max(c.a,.001);vec3 ink=clamp(rgb/paper,0.,1.);gl_FragColor=vec4(mix(vec3(1.),ink,mask),1.);}`));
gl.linkProgram(program);gl.useProgram(program);
const aP=gl.getAttribLocation(program,'p'),aUV=gl.getAttribLocation(program,'uv');
const aLocal=gl.getAttribLocation(program,'local');gl.enableVertexAttribArray(aP);gl.enableVertexAttribArray(aUV);gl.enableVertexAttribArray(aLocal);
const uH=gl.getUniformLocation(program,'h');gl.uniform2f(gl.getUniformLocation(program,'screen'),1672,941);
gl.enable(gl.BLEND);gl.blendFunc(gl.ONE,gl.ONE_MINUS_SRC_ALPHA);
gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,true);
function solve(A,b){const n=b.length;for(let i=0;i<n;i++){let k=i;for(let j=i+1;j<n;j++)if(Math.abs(A[j][i])>Math.abs(A[k][i]))k=j;[A[i],A[k]]=[A[k],A[i]];[b[i],b[k]]=[b[k],b[i]];const d=A[i][i];for(let c=i;c<n;c++)A[i][c]/=d;b[i]/=d;for(let r=0;r<n;r++){if(r===i)continue;const m=A[r][i];for(let c=i;c<n;c++)A[r][c]-=m*A[i][c];b[r]-=m*b[i];}}return b;}
function homography(src,dst){const A=[],b=[];for(let i=0;i<4;i++){const [x,y]=src[i],[u,v]=dst[i];A.push([x,y,1,0,0,0,-u*x,-u*y]);b.push(u);A.push([0,0,0,x,y,1,-v*x,-v*y]);b.push(v);}const h=solve(A,b);return [h[0],h[3],h[6],h[1],h[4],h[7],h[2],h[5],1];}
async function load(url){return new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=reject;im.src=url;});}
function draw(im,h,quad=null,paper=[1,1,1]){const w=im.width,hg=im.height;const corners=quad||[[0,0],[w,0],[w,hg],[0,hg]],st=[[0,0],[1,0],[1,1],[0,1]],data=[];for(const i of [0,1,3,3,1,2])data.push(...corners[i],corners[i][0]/w,corners[i][1]/hg,...st[i]);const verts=new Float32Array(data);const buf=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buf);gl.bufferData(gl.ARRAY_BUFFER,verts,gl.STATIC_DRAW);gl.vertexAttribPointer(aP,2,gl.FLOAT,false,24,0);gl.vertexAttribPointer(aUV,2,gl.FLOAT,false,24,8);gl.vertexAttribPointer(aLocal,2,gl.FLOAT,false,24,16);gl.uniformMatrix3fv(uH,false,new Float32Array(h));gl.uniform1f(gl.getUniformLocation(program,'face'),quad?1:0);gl.uniform3fv(gl.getUniformLocation(program,'paper'),paper);gl.blendFunc(quad?gl.DST_COLOR:gl.ONE,quad?gl.ZERO:gl.ONE_MINUS_SRC_ALPHA);const t=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,t);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,im);gl.drawArrays(gl.TRIANGLES,0,6);gl.deleteTexture(t);gl.deleteBuffer(buf);}
(async()=>{gl.viewport(0,0,canvas.width,canvas.height);gl.clearColor(1,1,1,1);gl.clear(gl.COLOR_BUFFER_BIT);const base=await load(DATA.base);draw(base,[1672/base.width,0,0,0,941/base.height,0,0,0,1]);for(const a of DATA.assets){const im=await load(a.url);draw(im,homography(a.source,a.target),a.source,a.paper);}document.body.dataset.ready='true';window.RENDER_COMPLETE=true;gl.finish();})().catch(e=>{document.body.dataset.error=String(e);console.error(e);});
</script></body></html>'''.replace('PAYLOAD',payload)
(DEST/'novoferma-cream-shared-surface.html').write_text(doc)
(DEST/'placements.json').write_text(json.dumps([{k:v for k,v in a.items() if k!='url'} for a in assets],ensure_ascii=False,indent=2))
print('Built photographic scene with all 17 products and cropped edge repeats.')
