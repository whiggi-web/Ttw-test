import * as THREE from 'three';
import { loadArena } from './assets/wrestling-arena/arena-loader.js';
import { loadWrestler } from './assets/ttw-master-wrestler/loader.js';
import { loadPack } from './assets/ttw-wrestlers/loader.js';

// TTW level foundation. Keep the world independent of wrestling mechanics.
// Claude's arena will be mounted at (0,0,0) when its asset is ready.
const scene=new THREE.Scene();
scene.background=new THREE.Color(0x10131c);
scene.fog=new THREE.Fog(0x10131c,85,180);
const camera=new THREE.PerspectiveCamera(55,innerWidth/innerHeight,.1,300);
const renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

scene.add(new THREE.HemisphereLight(0xa8c8ff,0x32313a,2.2));
const keyLight=new THREE.DirectionalLight(0xffffff,3);
keyLight.position.set(-20,35,25);
keyLight.castShadow=true;
keyLight.shadow.mapSize.set(2048,2048);
keyLight.shadow.camera.left=-45;
keyLight.shadow.camera.right=45;
keyLight.shadow.camera.top=45;
keyLight.shadow.camera.bottom=-45;
scene.add(keyLight);

// Temporary ground is a test reference, not the wrestling arena.
const testFloor=new THREE.Mesh(
 new THREE.PlaneGeometry(80,80),
 new THREE.MeshStandardMaterial({color:0x252a36,roughness:.95})
);
testFloor.rotation.x=-Math.PI/2;
testFloor.receiveShadow=true;
scene.add(testFloor);
const grid=new THREE.GridHelper(80,40,0x59647b,0x394354);
grid.position.y=.012;
scene.add(grid);
const arenaMount=new THREE.Group();
arenaMount.name='TTW_ARENA_MOUNT';
scene.add(arenaMount);
const marker=new THREE.Mesh(new THREE.CylinderGeometry(.7,.7,.08,32),new THREE.MeshStandardMaterial({color:0x63e4ac}));
marker.position.y=.05;
arenaMount.add(marker);

// The arena asset can replace the temporary floor/grid and marker.
export function attachArena(object,{hideTestFloor=true}={}){
 arenaMount.clear();
 arenaMount.add(object);
 if(hideTestFloor){testFloor.visible=false;grid.visible=false;}
}
window.TTWLevel={scene,camera,renderer,arenaMount,attachArena,testFloor,grid};




// TTW Wrestling Ring v0.5: playable raised ring, ropes, posts and arena surround.
const ring=new THREE.Group();
ring.name='TTW_WRESTLING_RING';
scene.add(ring);
function ringBox(w,h,d,color,x,y,z,metalness=0){
 const mesh=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),new THREE.MeshStandardMaterial({color,roughness:.68,metalness}));
 mesh.position.set(x,y,z);mesh.castShadow=true;mesh.receiveShadow=true;ring.add(mesh);return mesh;
}
ringBox(17,.75,17,0x161b28,0,.38,0);
ringBox(16.3,.2,16.3,0xe4e8f0,0,.86,0);
for(let i=-1;i<=1;i++){
 ringBox(16.7,.26,.13,0xd12439,0,.64,i*8.45);
 ringBox(.13,.26,16.7,0xd12439,i*8.45,.64,0);
}
const postMat=new THREE.MeshStandardMaterial({color:0x30343e,metalness:.7,roughness:.3});
const ropeMat=new THREE.MeshStandardMaterial({color:0xe7edf7,roughness:.48});
for(const x of [-8.3,8.3])for(const z of [-8.3,8.3]){
 const post=new THREE.Mesh(new THREE.CylinderGeometry(.16,.2,3.15,12),postMat);
 post.position.set(x,2.05,z);post.castShadow=true;ring.add(post);
 for(const y of [1.5,2.15,2.8]){
  const pad=ringBox(.68,.32,.68,0xc71d35,x,y,z);
 }
}
function rope(a,b,y){
 const delta=new THREE.Vector3().subVectors(b,a);
 const mesh=new THREE.Mesh(new THREE.CylinderGeometry(.052,.052,delta.length(),10),ropeMat);
 mesh.position.copy(a).add(b).multiplyScalar(.5);
 mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),delta.normalize());
 mesh.castShadow=true;ring.add(mesh);
}
for(const y of [1.5,2.15,2.8]){
 for(const z of [-8.3,8.3])rope(new THREE.Vector3(-8.3,y,z),new THREE.Vector3(8.3,y,z),y);
 for(const x of [-8.3,8.3])rope(new THREE.Vector3(x,y,-8.3),new THREE.Vector3(x,y,8.3),y);
}
for(const z of [-13,13])ringBox(27,1.1,1.7,0x252c3d,0,.55,z);
for(const x of [-13,13])ringBox(1.7,1.1,27,0x252c3d,x,.55,0);
const entrySteps=ringBox(3,.35,3,0x596170,0,.18,10.2);
ringBox(3,.35,2,0x737c8a,0,.53,8.6);
testFloor.visible=true;grid.visible=false;
marker.visible=false;


// TTW Arena v0.6: low-poly stadium seating, crowd, entry stage and lighting.
const stadium=new THREE.Group();stadium.name='TTW_STADIUM';scene.add(stadium);
const arenaMaterial=(color,metalness=0)=>new THREE.MeshStandardMaterial({color,roughness:.75,metalness});
function stadiumBox(w,h,d,x,y,z,color){
 const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),arenaMaterial(color));
 m.position.set(x,y,z);m.receiveShadow=true;stadium.add(m);return m;
}
stadiumBox(86,.35,86,0,-.24,0,0x171b24);
for(let tier=0;tier<7;tier++){
 const outer=19+tier*3.05, height=1.2+tier*1.15;
 for(const side of [-1,1]){
  stadiumBox(outer*2,.48,2.75,0,height,side*outer,0x303747);
  stadiumBox(2.75,.48,outer*2,side*outer,height,0,0x303747);
 }
}
// Central entrance ramp and illuminated stage.
stadiumBox(8,.32,19,0,.18,-28,0x4a5061);
stadiumBox(14,1.2,4,0,.65,-39,0x1b2232);
stadiumBox(12,7,.6,0,4.5,-41,0x111622);
const screenCanvas=document.createElement('canvas');screenCanvas.width=512;screenCanvas.height=256;
const sctx=screenCanvas.getContext('2d');sctx.fillStyle='#151b2b';sctx.fillRect(0,0,512,256);
sctx.fillStyle='#f43f5e';sctx.font='bold 118px sans-serif';sctx.textAlign='center';sctx.fillText('TTW',256,155);
sctx.fillStyle='#e9eefa';sctx.font='bold 29px sans-serif';sctx.fillText('WRESTLING ARENA',256,210);
const screen=new THREE.Mesh(new THREE.PlaneGeometry(11.6,5.7),new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(screenCanvas)}));
screen.position.set(0,4.5,-40.65);stadium.add(screen);
for(const x of [-34,34])for(const z of [-34,34]){
 const light=new THREE.PointLight(0xa5c9ff,35,65,2);light.position.set(x,16,z);stadium.add(light);
}
const spotPositions=[[-15,18,-15],[15,18,-15],[-15,18,15],[15,18,15]];
for(const [x,y,z] of spotPositions){
 const spot=new THREE.SpotLight(0xffffff,110,65,Math.PI/5,.7,1.4);
 spot.position.set(x,y,z);spot.target.position.set(0,0,0);stadium.add(spot,spot.target);
}
// Instancing keeps hundreds of audience members cheap on mobile GPUs.
const audienceCount=840;
const torsoGeo=new THREE.CapsuleGeometry(.3,.55,2,4);
const headGeo=new THREE.SphereGeometry(.23,5,4);
const audienceMat=new THREE.MeshLambertMaterial({color:0xffffff});
const torsos=new THREE.InstancedMesh(torsoGeo,audienceMat,audienceCount);
const heads=new THREE.InstancedMesh(headGeo,audienceMat,audienceCount);
const dummy=new THREE.Object3D();const color=new THREE.Color();
const palette=[0x3565b7,0xc83d4e,0xe0bd54,0x52a884,0xb8a4c5,0xd9d9e0,0x323b50];
for(let i=0;i<audienceCount;i++){
 const tier=Math.floor(i/120),index=i%120,side=Math.floor(index/30),pos=index%30;
 const distance=19+tier*3.05,along=(pos-14.5)*1.32;
 const x=side===0?along:side===1?distance:side===2?along:-distance;
 const z=side===0?-distance:side===1?along:side===2?distance:along;
 const y=1.8+tier*1.15;
 dummy.position.set(x,y,z);dummy.rotation.set(0,0,0);dummy.scale.set(.8,.85,.8);dummy.updateMatrix();
 torsos.setMatrixAt(i,dummy.matrix);
 dummy.position.y+=.65;dummy.scale.set(1,1,1);dummy.updateMatrix();heads.setMatrixAt(i,dummy.matrix);
 color.setHex(palette[(i*13+Math.floor(i/17))%palette.length]);torsos.setColorAt(i,color);
 heads.setColorAt(i,new THREE.Color().setHex([0xf0c9a0,0xa86b4e,0x7d5039,0xd8ac8c][i%4]));
}
torsos.instanceMatrix.needsUpdate=true;heads.instanceMatrix.needsUpdate=true;
stadium.add(torsos,heads);

// Load Claude's authored stadium and wrestler; retain existing scene as fallback if an asset fails.
let loadedArena=null;
try{
 loadedArena=await loadArena('./assets/wrestling-arena/arena.json');
 scene.add(loadedArena.group);
 ring.visible=false;stadium.visible=false;testFloor.visible=false;grid.visible=false;
 console.info('TTW: Claude wrestling arena loaded');
}catch(error){console.error('TTW arena asset failed:',error);}
// Live jumbotron countdown. Uses Claude's existing arena screen textures.
let jumbotronCountdown=-1;
let jumbotronLastSecond=null;
const jumbotronButton=document.createElement('button');
jumbotronButton.textContent='⏱ JUMBOTRON COUNTDOWN';
jumbotronButton.style.cssText='position:fixed;top:148px;left:16px;z-index:15;padding:10px 14px;background:#163c69;color:white;border:1px solid #83baff;border-radius:8px;font:700 13px system-ui;cursor:pointer';
document.body.appendChild(jumbotronButton);
function setJumbotron(text,sub,colors){
 if(!loadedArena)return;
 loadedArena.setScreen('screen_main',{text,sub,colors});
}
function setSideAdvertising(){
 if(!loadedArena)return;
 loadedArena.setScreen('screen_side',{text:'FREE TO PLAY',sub:'FOLLOW FOR MORE',colors:['#11245d','#e12b4a']});
}
setSideAdvertising();
let countdownResumeCamera=false;
jumbotronButton.addEventListener('click',()=>{
 // Show the countdown on the main screen only, then resume the live action feed.
 countdownResumeCamera=actionFeedEnabled;
 if(actionFeedEnabled)setActionFeed(false);
 jumbotronCountdown=10;
 jumbotronLastSecond=null;
 jumbotronButton.textContent='⏱ RESTART COUNTDOWN';
});
function updateJumbotron(dt){
 if(jumbotronCountdown<0)return;
 jumbotronCountdown=Math.max(0,jumbotronCountdown-dt);
 const second=Math.ceil(jumbotronCountdown);
 if(second!==jumbotronLastSecond){
  jumbotronLastSecond=second;
  if(second>0)setJumbotron(String(second),'GET READY',['#07162c','#d52943']);
  else setJumbotron('TTW','LET\'S WRESTLE!',['#410c1e','#ffb522']);
 }
 if(jumbotronCountdown===0){
  jumbotronCountdown=-1;
  jumbotronButton.textContent='⏱ JUMBOTRON COUNTDOWN';
  if(countdownResumeCamera)setActionFeed(true);
  countdownResumeCamera=false;
 }
}
// Action-camera broadcast rendered directly onto the existing arena jumbotron.
const actionCamera=new THREE.PerspectiveCamera(48,16/9,.1,130);
const actionFeed=new THREE.WebGLRenderTarget(640,360,{depthBuffer:true});
actionFeed.texture.colorSpace=THREE.SRGBColorSpace;
const actionScreens=[];
if(loadedArena){
 for(const id of ['screen_main']){
  for(const group of loadedArena.byId(id)){
   group.traverse(obj=>{
    if(obj.isMesh&&obj.name==='screen_surface'){
     actionScreens.push({mesh:obj,original:obj.material.map});
    }
   });
  }
 }
}
let actionFeedEnabled=false,actionFeedClock=0;
const actionFeedButton=document.createElement('button');
actionFeedButton.textContent='📹 LIVE ACTION CAM';
actionFeedButton.style.cssText='position:fixed;top:193px;left:16px;z-index:15;padding:10px 14px;background:#175b54;color:white;border:1px solid #86e7d5;border-radius:8px;font:700 13px system-ui;cursor:pointer';
document.body.appendChild(actionFeedButton);
function setActionFeed(enabled){
 actionFeedEnabled=enabled&&actionScreens.length>0;
 for(const s of actionScreens){
  s.mesh.material.map=actionFeedEnabled?actionFeed.texture:s.original;
  s.mesh.material.needsUpdate=true;
 }
 actionFeedButton.textContent=actionFeedEnabled?'📹 STOP ACTION CAM':'📹 LIVE ACTION CAM';
}
actionFeedButton.addEventListener('click',()=>{jumbotronCountdown=-1;countdownResumeCamera=false;jumbotronButton.textContent='⏱ JUMBOTRON COUNTDOWN';setActionFeed(!actionFeedEnabled);});
function renderActionFeed(dt){
 if(!actionFeedEnabled)return;
 actionFeedClock+=dt;
 if(actionFeedClock<1/15)return;
 actionFeedClock=0;
 // Track both wrestlers when connected, or the local wrestler when alone.
 const centre=player.position.clone();
 if(remoteConnected&&remote.visible)centre.lerp(remote.position,.5);
 const separation=remoteConnected&&remote.visible?player.position.distanceTo(remote.position):0;
 const spread=Math.min(12,Math.max(5.5,5.5+separation*.7));
 const desired=centre.clone().add(new THREE.Vector3(spread*.7,spread*.55,spread));
 actionCamera.position.lerp(desired,.22);
 actionCamera.lookAt(centre.x,centre.y+1.3,centre.z);
 // Hide screen panels while capturing to prevent recursive video feedback.
 for(const s of actionScreens)s.mesh.visible=false;
 renderer.setRenderTarget(actionFeed);
 renderer.clear();
 renderer.render(scene,actionCamera);
 renderer.setRenderTarget(null);
 for(const s of actionScreens)s.mesh.visible=true;
}
let loadedWrestler=null;
let remoteWrestler=null;
let usingBatchOne=false;
let wrestlerPack=null;
try{
 const pack=await loadPack('./assets/ttw-wrestlers/manifest.json');
 wrestlerPack=pack;
 loadedWrestler=pack.createWrestler('wrestler-01');
 remoteWrestler=pack.createWrestler('wrestler-02');
 usingBatchOne=true;
 console.info('TTW: Batch 1 loaded, Rex and Nova');
}catch(error){
 console.error('TTW Batch 1 failed, retaining master wrestler fallback:',error);
 try{
  loadedWrestler=await loadWrestler('./assets/ttw-master-wrestler/wrestler.json');
  remoteWrestler=await loadWrestler('./assets/ttw-master-wrestler/wrestler.json');
 }catch(fallbackError){console.error('TTW wrestler fallback failed:',fallbackError);}
}
const playTTWAnimation=(w,state,fade=.2)=>{
 if(!w)return;
 const name=usingBatchOne?({idle:'movement.idle',run:'movement.run',punch:'striking.punch',fall:'falls.fall-backward',ropeLean:'ropes.rope-lean',ropeRebound:'ropes.rope-rebound'}[state]||'movement.idle'):state;
 w.play(name,{fade,restart:true});
};
// Arena collision v0.8: Claude's collider data drives movement and walkable elevation.
const solidArenaBoxes=(loadedArena?.colliders||[]).filter(c=>
 c.id==='ring_apron' || (c.tags||[]).includes('rope') || (c.tags||[]).some(t=>['wall','barrier','stand','post','table','chair','rig','suites'].includes(t))
);
const arenaWalkables=[];
if(loadedArena){
 for(const obj of loadedArena.group.children){
  obj.traverse(child=>{
   if(!child.isMesh)return;
   let parent=child, walkable=false;
   while(parent&&parent!==loadedArena.group){
    const tags=parent.userData?.tags||[];
    if(tags.includes('walkable')||parent.userData?.arenaId==='ring_apron')walkable=true;
    parent=parent.parent;
   }
   if(walkable)arenaWalkables.push(child);
  });
 }
}
const floorRay=new THREE.Raycaster();
function arenaFloorAt(x,z,currentY){
 if(!loadedArena)return .97;
 floorRay.set(new THREE.Vector3(x,30,z),new THREE.Vector3(0,-1,0));
 const hits=floorRay.intersectObjects(arenaWalkables,false);
 // Ignore overhead surfaces and prevent stepping directly onto tall structures.
 const eligible=hits.filter(h=>h.point.y<=currentY+.42);
 return eligible.length?Math.max(0,eligible[0].point.y):0;
}
// Springy ring ropes: slight give, visible bending and a short recoil burst.
const ropeEdge=3.5, ropeGive=.38;
const ropeSides=['north','south','east','west'];
const ropeSprings=Object.fromEntries(ropeSides.map(side=>[side,{bend:0,velocity:0,impact:0,contact:0}]));
const ropeMeshes=[];
if(loadedArena){
 loadedArena.group.traverse(obj=>{
  if(!obj.isMesh||!obj.parent?.userData?.tags?.includes('rope'))return;
  obj.updateWorldMatrix(true,false);
  const center=new THREE.Vector3();obj.getWorldPosition(center);
  const side=Math.abs(center.z)>Math.abs(center.x)?(center.z>0?'north':'south'):(center.x>0?'east':'west');
  const geom=obj.geometry.clone();obj.geometry=geom;
  const pos=geom.attributes.position;
  const original=new Float32Array(pos.array);
  // Deform away from the ring centre on every side, including mirrored ropes.
  const outward=new THREE.Vector3(side==='west'?-1:side==='east'?1:0,0,side==='north'?1:side==='south'?-1:0);
  // Inverse world matrix includes mirrored negative scales; quaternion inversion does not.
  const localInward=outward.transformDirection(obj.matrixWorld.clone().invert());
  const halfLength=(geom.parameters?.height||7)/2;
  ropeMeshes.push({side,pos,original,localInward,halfLength,mesh:obj});
 });
}
function ropeSideAt(x,z){
 const ax=Math.abs(x),az=Math.abs(z);
 if(Math.max(ax,az)<2.6||Math.max(ax,az)>4.1)return null;
 return az>ax?(z>0?'north':'south'):(x>0?'east':'west');
}
function ropeCollision(x,z,dt){
 if(player.position.y<.7||player.position.y>1.7)return {x,z};
 const edge=3.5, radius=.38, give=.24;
 const side=ropeSideAt(x,z);
 if(!side)return {x,z};
 const axis=side==='east'||side==='west'?'x':'z';
 const sign=side==='east'||side==='north'?1:-1;
 const current=player.position[axis]*sign;
 const proposed=(axis==='x'?x:z)*sign;
 // Wrestlers on the ring side compress the ropes before springing backward.
 if(current<edge+radius&&proposed>edge-radius){
  const spring=ropeSprings[side];
  const compression=Math.max(0,proposed-(edge-radius));
  spring.contact=axis==='x'?player.position.z:player.position.x;
  spring.bend=Math.max(spring.bend,Math.min(.7,compression*2.5));
  if(proposed>=edge-radius+give){
   if(spring.impact<=0){
    spring.velocity+=3;
    spring.impact=.45;
    ropeRecoil.set(axis==='x'?-sign*5:0,0,axis==='z'?-sign*5:0);
    ropeRecoilTime=.38;
    registerRopeBounce(new THREE.Vector3(axis==='x'?-sign:0,0,axis==='z'?-sign:0));
   }
   if(axis==='x')x=sign*(edge-radius+give);
   else z=sign*(edge-radius+give);
  }
 }
 return {x,z};
}
function updateRopes(dt){
 for(const side of ropeSides){
  const s=ropeSprings[side];
  s.velocity+=(-s.bend*62-s.velocity*12)*dt;
  s.bend+=s.velocity*dt;
  if(Math.abs(s.bend)<.0005&&Math.abs(s.velocity)<.005){s.bend=0;s.velocity=0;}
  s.impact=Math.max(0,s.impact-dt);
 }
 for(const r of ropeMeshes){
  const spring=ropeSprings[r.side];
  const bend=spring.bend;
  const worldCenter=new THREE.Vector3();r.mesh.getWorldPosition(worldCenter);
  const contactOffset=THREE.MathUtils.clamp(spring.contact-(r.side==='north'||r.side==='south'?worldCenter.x:worldCenter.z),-3.2,3.2);
  for(let i=0;i<r.pos.count;i++){
   const k=i*3;
   const along=r.original[k+1]/r.halfLength*3.5;
   const proximity=Math.max(0,1-Math.abs(along-contactOffset)/3.6);
   const offset=bend*proximity*proximity;
   r.pos.array[k]=r.original[k]+r.localInward.x*offset;
   r.pos.array[k+1]=r.original[k+1]+r.localInward.y*offset;
   r.pos.array[k+2]=r.original[k+2]+r.localInward.z*offset;
  }
  r.pos.needsUpdate=true;
  r.mesh.geometry.computeBoundingSphere();
 }
}
let ropeRecoil=new THREE.Vector3(),ropeRecoilTime=0;
let ropeSpeedMultiplier=1,ropeFacingTime=0;
let ropeAnimationTime=0,ropeBounceDelay=0,ropeMovementLock=0;
const ropeLeanDuration=.7,ropeReboundDuration=.8;
function registerRopeBounce(inward){
 ropeSpeedMultiplier=Math.min(1.30,Math.round((ropeSpeedMultiplier+.10)*100)/100);
 ropeFacingTime=1;
 ropeBounceDelay=1;
 ropeMovementLock=1.10;
 if(usingBatchOne)ropeAnimationTime=ropeLeanDuration+ropeReboundDuration;
 player.rotation.y=Math.atan2(-inward.x,-inward.z);
}
function blockedByArena(x,z,feetY){
 const radius=.32;
 if(feetY>=.75&&feetY<=1.65){
  const side=ropeSideAt(x,z);
  const inside=Math.abs(player.position.x)<ropeEdge&&Math.abs(player.position.z)<ropeEdge;
  if(side&&inside){
   const inward=side==='east'?new THREE.Vector3(-1,0,0):side==='west'?new THREE.Vector3(1,0,0):side==='north'?new THREE.Vector3(0,0,-1):new THREE.Vector3(0,0,1);
   const outwardDistance=side==='east'?x:side==='west'?-x:side==='north'?z:-z;
   if(outwardDistance>ropeEdge-.44){
    const spring=ropeSprings[side];
    spring.contact=side==='east'||side==='west'?player.position.z:player.position.x;
    spring.bend=Math.max(spring.bend,Math.min(.7,(outwardDistance-(ropeEdge-.44))*2));
    if(outwardDistance>=ropeEdge-.32+ropeGive){
     if(spring.impact<=0){
      spring.velocity+=2.2;
      spring.impact=.35;
      ropeRecoil.copy(inward).multiplyScalar(3.5);
      ropeRecoilTime=.28;
      registerRopeBounce(inward);
     }
     return true;
    }
   }
  }
  // Keep the outer side solid too.
  const outside=Math.abs(player.position.x)>ropeEdge+.32||Math.abs(player.position.z)>ropeEdge+.32;
  if(side&&outside&&Math.abs(x)<ropeEdge+.32&&Math.abs(z)<ropeEdge+.32)return true;
 }
 return solidArenaBoxes.some(c=>{
  if((c.tags||[]).includes('rope'))return false; // Spring boundary replaces thin rope AABBs.
  const b=c.box;
  if(c.id==='ring_apron'&&feetY>=1.05)return false;
  if(feetY>b.max.y-.08||feetY+1.65<b.min.y+.08)return false;
  const cx=THREE.MathUtils.clamp(x,b.min.x,b.max.x);
  const cz=THREE.MathUtils.clamp(z,b.min.z,b.max.z);
  return (x-cx)**2+(z-cz)**2<radius**2;
 });
}

// Temporary player capsule fallback. Hidden when the original wrestler is loaded.
const player=new THREE.Group();
player.name='TTW_TEST_PLAYER';
const capsule=new THREE.Mesh(new THREE.CapsuleGeometry(.45,1.1,6,12),new THREE.MeshStandardMaterial({color:0x4fa8ff,roughness:.55}));
capsule.position.y=1;
capsule.castShadow=true;
player.add(capsule);
const facing=new THREE.Mesh(new THREE.ConeGeometry(.18,.42,12),new THREE.MeshStandardMaterial({color:0xffffff}));
facing.rotation.x=Math.PI/2;
facing.position.set(0,1.25,-.48);
player.add(facing);
player.position.set(0,.97,0);
scene.add(player);
if(loadedWrestler){
 capsule.visible=false;facing.visible=false;
 player.add(loadedWrestler.object);
 loadedWrestler.object.position.set(0,0,0);
 playTTWAnimation(loadedWrestler,'idle');
}
// Two-player online test: state is relayed through the companion WebSocket server.
const remote=new THREE.Group();remote.name='TTW_REMOTE_PLAYER';remote.visible=false;remote.position.set(1.5,1.2,0);
if(remoteWrestler){remote.add(remoteWrestler.object);playTTWAnimation(remoteWrestler,'idle');remoteWrestler._ttwState='idle';}
else{const m=new THREE.Mesh(new THREE.CapsuleGeometry(.4,1.1,6,12),new THREE.MeshStandardMaterial({color:0xee5533}));m.position.y=1;remote.add(m);}
scene.add(remote);
let playerHP=100,remoteHP=100,playerPunchImpact=-1,remoteConnected=false,playerSlot=null,network=null,sendClock=0,remoteAnim='idle',remoteHasTarget=false;
const remoteTarget=new THREE.Vector3();
let remoteTargetRotation=0;
const combatHud=document.createElement('div');
combatHud.style.cssText='position:fixed;right:16px;top:16px;z-index:12;color:white;font:700 16px system-ui;text-shadow:0 2px 5px black;pointer-events:none;text-align:right';
document.body.appendChild(combatHud);
const networkStatus=document.createElement('div');
networkStatus.style.cssText='position:fixed;right:16px;top:46px;z-index:12;color:#bcd0e4;font:12px system-ui;text-shadow:0 1px 3px black;pointer-events:none';
document.body.appendChild(networkStatus);
function refreshCombatHud(){combatHud.textContent='YOU '+playerHP+' HP | '+(remoteConnected?'OPPONENT '+remoteHP+' HP':'WAITING FOR PLAYER 2');}
refreshCombatHud();
const damagePopups=[];
function showDamage(position,value,color){
 const canvas=document.createElement('canvas');canvas.width=256;canvas.height=128;
 const ctx=canvas.getContext('2d');ctx.font='bold 80px system-ui';ctx.textAlign='center';ctx.fillStyle=color;ctx.strokeStyle='#111';ctx.lineWidth=9;
 ctx.strokeText(value,128,88);ctx.fillText(value,128,88);
 const tex=new THREE.CanvasTexture(canvas),mat=new THREE.SpriteMaterial({map:tex,transparent:true,depthTest:false});
 const sprite=new THREE.Sprite(mat);sprite.position.copy(position);sprite.position.y+=2.7;sprite.scale.set(1.5,.75,1);scene.add(sprite);
 damagePopups.push({sprite,mat,tex,life:.85});
}
const params=new URLSearchParams(location.search);
const wsUrl=params.get('server')||(['localhost','127.0.0.1'].includes(location.hostname)?'ws://'+location.hostname+':8765':'');
function sendNetwork(data){if(network?.readyState===WebSocket.OPEN)network.send(JSON.stringify(data));}
function startMultiplayer(){
 if(network)return;
 if(!wsUrl){networkStatus.textContent='Multiplayer server not configured';return;}
 networkStatus.textContent='Connecting…';
 try{network=new WebSocket(wsUrl);}catch{networkStatus.textContent='Invalid server URL';return;}
 network.onopen=()=>sendNetwork({type:'join',name:window.TTWPlayerName||'Wrestler'});
 network.onmessage=e=>{
  let m;try{m=JSON.parse(e.data);}catch{return;}
  if(m.type==='welcome'){playerSlot=m.slot;player.position.set(m.slot===1?-1.4:1.4,1.2,0);playerHP=m.hp??100;refreshCombatHud();}
  if(m.type==='waiting'||m.type==='peer_left'){remoteHasTarget=false;remoteConnected=false;remote.visible=false;remoteHP=100;networkStatus.textContent='Waiting for player 2…';refreshCombatHud();}
  if(m.type==='joined'){remoteHasTarget=false;remoteConnected=true;remote.visible=true;remoteHP=m.hp??100;networkStatus.textContent='Two players connected';refreshCombatHud();}
  if(m.type==='full'){networkStatus.textContent='Ring full (2 players maximum)';}
  if(m.type==='state'&&m.slot!==playerSlot&&remoteConnected){
   const p=m.position||{};
   if([p.x,p.y,p.z,m.rotation].every(Number.isFinite)){remoteTarget.set(p.x,p.y,p.z);remoteTargetRotation=m.rotation;
    if(!remoteHasTarget){remote.position.copy(remoteTarget);remote.rotation.y=remoteTargetRotation;remoteHasTarget=true;}}
   remoteAnim=['idle','run','punch','fall'].includes(m.animation)?m.animation:'idle';
  }
  if(m.type==='health'){
   playerHP=m.self;remoteHP=m.other;refreshCombatHud();
   if(m.hit==='self')showDamage(player.position,'-'+(m.damage??11),'#ff6969');
   if(m.hit==='other')showDamage(remote.position,'-'+(m.damage??11),'#ffdf55');
  }
 };
 network.onclose=()=>{network=null;playerSlot=null;remoteHasTarget=false;remoteConnected=false;remote.visible=false;networkStatus.textContent='Disconnected. Refresh to reconnect.';refreshCombatHud();};
 network.onerror=()=>{networkStatus.textContent='Cannot reach multiplayer server';};
}
window.addEventListener('ttw:player-name',startMultiplayer);
if(document.getElementById('home').hidden)startMultiplayer();
function combatTick(dt){
 for(let i=damagePopups.length-1;i>=0;i--){
  const p=damagePopups[i];p.life-=dt;p.sprite.position.y+=dt*1.1;p.mat.opacity=Math.max(0,p.life/.85);
  if(p.life<=0){scene.remove(p.sprite);p.mat.dispose();p.tex.dispose();damagePopups.splice(i,1);}
 }
 if(remoteConnected&&remoteHasTarget){
  // Render every frame between network updates instead of teleporting at 20Hz.
  const blend=1-Math.exp(-dt*16);
  remote.position.lerp(remoteTarget,blend);
  let delta=THREE.MathUtils.euclideanModulo(remoteTargetRotation-remote.rotation.y+Math.PI,Math.PI*2)-Math.PI;
  remote.rotation.y+=delta*blend;
 }
 if(remoteWrestler&&remoteConnected){
  const state=remoteHP<=0?'fall':remoteAnim;
  if(remoteWrestler._ttwState!==state){playTTWAnimation(remoteWrestler,state,.12);remoteWrestler._ttwState=state;}
  remoteWrestler.update(dt);
 }
 sendClock+=dt;
 if(sendClock>=.05&&playerSlot!==null){
  sendClock-=.05;
  sendNetwork({type:'state',position:{x:player.position.x,y:player.position.y,z:player.position.z},rotation:player.rotation.y,animation:playerHP<=0?'fall':punchRemaining>0?'punch':heldKeys.size||movement.active?'run':'idle'});
 }
}
// Floating nameplate follows the test wrestler; text is drawn locally and never interpreted as HTML.
const labelCanvas=document.createElement('canvas');
labelCanvas.width=512;labelCanvas.height=128;
const labelContext=labelCanvas.getContext('2d');
const labelTexture=new THREE.CanvasTexture(labelCanvas);
const labelMaterial=new THREE.SpriteMaterial({map:labelTexture,transparent:true,depthTest:false});
const nameplate=new THREE.Sprite(labelMaterial);
nameplate.position.set(0,2.65,0);
nameplate.scale.set(2.8,.7,1);
player.add(nameplate);
function updateNameplate(name){
 labelContext.clearRect(0,0,512,128);
 labelContext.fillStyle='rgba(9,14,23,.82)';
 labelContext.beginPath();labelContext.roundRect(10,18,492,92,18);labelContext.fill();
 labelContext.font='bold 54px system-ui,sans-serif';
 labelContext.textAlign='center';labelContext.textBaseline='middle';
 labelContext.fillStyle='#fff';labelContext.fillText(name,256,64,460);
 labelTexture.needsUpdate=true;
}
updateNameplate(window.TTWPlayerName||'WRESTLER');
window.addEventListener('ttw:player-name',e=>updateNameplate(e.detail.name));
const controllerSlot=document.getElementById('controllerSlot');
const pad=window.GameController.mount(controllerSlot,{mode:'auto'});
const movement=pad.state.joysticks.controlMOVEMENT;
const clock=new THREE.Clock();
const heldKeys=new Set();
let punchRemaining=0;
window.addEventListener('keydown',e=>{
 if(['KeyW','KeyA','KeyS','KeyD','ShiftLeft','ShiftRight'].includes(e.code)){
  if(e.target instanceof HTMLElement&&e.target.closest('input,textarea,[contenteditable="true"]'))return;
  heldKeys.add(e.code);
  e.preventDefault();
 }
});
window.addEventListener('keyup',e=>heldKeys.delete(e.code));
window.addEventListener('blur',()=>heldKeys.clear());
// Listen at window level: the game HUD can sit above the WebGL canvas.
window.addEventListener('pointerdown',e=>{
 if(e.button!==0||document.getElementById('home').hidden===false)return;
 if(e.target instanceof Element&&e.target.closest('button,input,textarea,select,a,#controllerSlot'))return;
 if(punchRemaining>0||playerHP<=0||!remoteConnected)return;
 punchRemaining=.8;
 playerPunchImpact=.3; // Match Claude's 0.8-second punch animation.
},{capture:true});

// Standalone cinematic entrance test. The bot is visual-only and does not join multiplayer.
const entranceBot=new THREE.Group();
entranceBot.name='TTW_ENTRANCE_BOT';
entranceBot.visible=false;
scene.add(entranceBot);
let entranceActor=null;
if(wrestlerPack){
 try{entranceActor=wrestlerPack.createWrestler('wrestler-02');entranceBot.add(entranceActor.object);}
 catch(e){console.warn('Entrance wrestler unavailable',e);}
}
if(!entranceActor){
 const placeholder=new THREE.Mesh(new THREE.CapsuleGeometry(.42,1.2,8,12),new THREE.MeshStandardMaterial({color:0xffad42}));
 placeholder.position.y=1;entranceBot.add(placeholder);
}
const entranceButton=document.createElement('button');
entranceButton.textContent='🎬 BOT ENTRANCE';
entranceButton.style.cssText='position:fixed;top:58px;left:16px;z-index:15;padding:10px 14px;background:#9e274d;color:white;border:1px solid #f9b1c8;border-radius:8px;font:700 13px system-ui;cursor:pointer';
document.body.appendChild(entranceButton);
let entranceTime=-1;
// Timed entrance choreography: slow stage walk, crowd acknowledgements, then sprint.
// Simple low-poly stage fireworks, played before the entrance.
const stagePyro=new THREE.Group();scene.add(stagePyro);
const pyroPieces=[];
for(const x of [-8,-5,-2,2,5,8]){
 for(let j=0;j<12;j++){
  const mat=new THREE.MeshBasicMaterial({color:j%3===0?0xffffff:j%2?0xff9625:0xffda46,transparent:true,opacity:0,depthWrite:false});
  const mesh=new THREE.Mesh(new THREE.ConeGeometry(.14,.85,3),mat);
  stagePyro.add(mesh);
  const angle=j*Math.PI/6;
  pyroPieces.push({mesh,x,j,vx:Math.cos(angle)*(1+j%3),vz:Math.sin(angle)*(1+j%3),vy:3+j%4});
 }
}
function resetStagePyro(){for(const p of pyroPieces){p.mesh.visible=false;p.mesh.material.opacity=0;}}
function updateStagePyro(t){
 for(const p of pyroPieces){
  const age=t-(p.j%4)*.12-(Math.abs(p.x)%2)*.3;
  p.mesh.visible=age>=0&&age<2.3;
  if(p.mesh.visible){
   p.mesh.position.set(p.x+p.vx*age,1.25+p.vy*age-2.6*age*age,-27.1+p.vz*age);
   p.mesh.rotation.z=age*4;
   p.mesh.material.opacity=Math.min(1,age*7)*Math.max(0,1-age/2.3);
  }
 }
}
const entranceKeyframes=[
 {t:3,x:0,y:1.2,z:-37.5,anim:'movement.walk',face:Math.PI},
 {t:5.5,x:0,y:1.2,z:-31,anim:'movement.walk',face:Math.PI},
 {t:8.5,x:-7,y:1.2,z:-29.5,anim:'movement.walk',face:Math.PI/2},
 {t:10.5,x:-7,y:1.2,z:-29.5,anim:'movement.idle',face:-Math.PI/2},
 {t:13,x:-7,y:1.2,z:-29.5,anim:'movement.idle',face:-Math.PI/2},
 {t:16,x:7,y:1.2,z:-29.5,anim:'movement.walk',face:-Math.PI/2},
 {t:18,x:7,y:1.2,z:-29.5,anim:'movement.idle',face:Math.PI/2},
 {t:21,x:7,y:1.2,z:-29.5,anim:'movement.idle',face:Math.PI/2},
 {t:23,x:0,y:1.2,z:-29,anim:'movement.walk',face:Math.PI},
 {t:26,x:0,y:.8,z:-18,anim:'movement.run',face:Math.PI},
 {t:29,x:0,y:.06,z:-9,anim:'movement.run',face:Math.PI},
 {t:31,x:0,y:.06,z:-6,anim:'movement.run',face:Math.PI},
 {t:33,x:0,y:.06,z:-6,anim:'movement.idle',face:Math.PI}
];
const entranceDuration=33;
const entranceV=(x,y,z)=>new THREE.Vector3(x,y,z);
function entrancePose(t){
 const next=entranceKeyframes.findIndex((k,j)=>j>0&&t<=k.t);
 const i=next<0?entranceKeyframes.length-2:Math.max(0,next-1);
 const a=entranceKeyframes[i],b=entranceKeyframes[Math.min(i+1,entranceKeyframes.length-1)];
 const p=a===b?0:THREE.MathUtils.clamp((t-a.t)/(b.t-a.t),0,1);
 const pos=entranceV(THREE.MathUtils.lerp(a.x,b.x,p),THREE.MathUtils.lerp(a.y,b.y,p),THREE.MathUtils.lerp(a.z,b.z,p));
 // Destination keyframe specifies movement type for each segment.
 const moving=t>=3&&pos.distanceToSquared(entranceV(b.x,b.y,b.z))>.00001;
 const anim=moving?(b.anim==='movement.run'?'movement.run':'movement.walk'):'movement.idle';
 return {pos,anim,face:b.face};
}
entranceButton.addEventListener('click',()=>{
 entranceTime=0;entranceBot.visible=false;resetStagePyro();
 entranceBot.position.set(0,1.2,-37.5);entranceBot.rotation.y=Math.PI;
 if(entranceActor){entranceActor._entranceState=null;entranceActor.play('movement.idle',{fade:.15,restart:true});}
 entranceButton.textContent='🎬 RESTART ENTRANCE';
});
function updateEntrance(dt){
 if(entranceTime<0)return false;
 entranceTime=Math.min(entranceDuration,entranceTime+dt);
 const t=entranceTime,pose=entrancePose(t);
 updateStagePyro(t);
 entranceBot.visible=t>=3;
 entranceBot.position.copy(pose.pos);
 // Look outward during each crowd acknowledgement, face the direction of travel otherwise.
 if(t>=8.5&&t<13)entranceBot.rotation.y=Math.PI/2;
 else if(t>=16&&t<21)entranceBot.rotation.y=-Math.PI/2;
 else{
  const ahead=entrancePose(Math.min(entranceDuration,t+.05)).pos;
  if(ahead.distanceToSquared(pose.pos)>.00001)
   entranceBot.rotation.y=Math.atan2(-(ahead.x-pose.pos.x),-(ahead.z-pose.pos.z));
 }
 if(entranceActor){
  if(entranceActor._entranceState!==pose.anim){
   entranceActor.play(pose.anim,{fade:.22,restart:true});
   entranceActor._entranceState=pose.anim;
  }
  entranceActor.update(dt);
 }
 // Directed television coverage: each shot has its own camera and focal point.
 let eye,focus;
 if(t<3){ // fireworks before the curtain opens
  eye=entranceV(-11,6,-19);focus=entranceV(0,3,-30);
 }else if(t<5.5){ // curtain reveal
  eye=entranceV(-5,3.2,-28);focus=pose.pos.clone().add(entranceV(0,1.1,0));
 }else if(t<8.5){ // track left across stage
  eye=pose.pos.clone().add(entranceV(-2.5,2.2,5.5));focus=pose.pos.clone().add(entranceV(0,1.2,0));
 }else if(t<10.5){ // wrestler acknowledges left crowd
  eye=entranceV(-11,3.3,-25);focus=pose.pos.clone().add(entranceV(0,1.2,0));
 }else if(t<13){ // panoramic right-side audience, independent of wrestler
  const p=(t-10.5)/2.5;
  eye=entranceV(8+p*10,5.5,-16+p*3);
  focus=entranceV(22+p*9,5,-17+p*7);
 }else if(t<16){ // cross stage to the right
  eye=pose.pos.clone().add(entranceV(2.8,2.4,5.2));focus=pose.pos.clone().add(entranceV(0,1.2,0));
 }else if(t<18){ // look out over right-side crowd
  eye=entranceV(11,3.1,-25);focus=pose.pos.clone().add(entranceV(0,1.2,0));
 }else if(t<21){ // close-up of the human player already in the ring
  const faceDir=entranceV(-Math.sin(player.rotation.y),0,-Math.cos(player.rotation.y));
  eye=player.position.clone().addScaledVector(faceDir,1.7).add(entranceV(0,1.65,0));
  focus=player.position.clone().add(entranceV(0,1.55,0));
 }else if(t<23){ // dramatic low-angle stage departure
  eye=entranceV(-3,1.5,-23);focus=pose.pos.clone().add(entranceV(0,1.1,0));
 }else if(t<25){ // head-on tracking run
  eye=pose.pos.clone().add(entranceV(0,1.6,5.5));focus=pose.pos.clone().add(entranceV(0,1.1,0));
 }else if(t<27){ // sweeping side shot
  eye=pose.pos.clone().add(entranceV(-6,3.4,1));focus=pose.pos.clone().add(entranceV(0,1.1,0));
 }else if(t<29){ // high angle looking down the ramp
  eye=pose.pos.clone().add(entranceV(4.5,8,4));focus=pose.pos.clone().add(entranceV(0,1,0));
 }else{ // ringside finish
  eye=entranceV(-6,3.6,2);focus=pose.pos.clone().add(entranceV(0,1.1,0));
 }
 camera.position.lerp(eye,Math.min(1,dt*12));
 camera.lookAt(focus);
 if(t>=entranceDuration){entranceTime=-1;entranceButton.textContent='🎬 BOT ENTRANCE';}
 return true;
}

// Alternative entrance #2: arena establishing shot, blackout, huge stage blasts,
// then a deliberate low-angle walk down the full ramp.
const slowEntranceButton=document.createElement('button');
slowEntranceButton.textContent='🎬 EPIC WALK ENTRANCE';
slowEntranceButton.style.cssText=entranceButton.style.cssText+';top:103px;background:#51359b;border-color:#bcb1ff';
document.body.appendChild(slowEntranceButton);
const cinematicBlackout=document.createElement('div');
cinematicBlackout.style.cssText='position:fixed;inset:0;z-index:14;background:#000;pointer-events:none;opacity:0';
document.body.appendChild(cinematicBlackout);
const epicPyro=new THREE.Group();scene.add(epicPyro);
const epicShards=[];
for(const x of [-9,-5,-1,1,5,9]){
 for(let j=0;j<28;j++){
  const a=j*Math.PI*2/28, speed=3+(j%5)*.8;
  const mat=new THREE.MeshBasicMaterial({color:j%4===0?0xffffff:j%3===0?0xff3b17:j%2?0xffb22b:0xffe95d,transparent:true,opacity:0,depthWrite:false,side:THREE.DoubleSide});
  const mesh=new THREE.Mesh(new THREE.ConeGeometry(.3,2.6,4),mat);
  epicPyro.add(mesh);
  epicShards.push({mesh,x,delay:(j%4)*.08,vx:Math.cos(a)*speed,vy:9+j%6*1.4,vz:Math.sin(a)*speed});
 }
}
function updateEpicPyro(t){
 for(const p of epicShards){
  const age=t-4-p.delay;
  p.mesh.visible=age>=0&&age<3;
  if(p.mesh.visible){
   p.mesh.position.set(p.x+p.vx*age,6+p.vy*age-5*age*age,-32+p.vz*age);
   p.mesh.rotation.z=age*3.5;
   p.mesh.scale.setScalar(1+age*.65);
   p.mesh.material.opacity=Math.min(1,age*8)*Math.max(0,1-age/3);
  }
 }
}
let epicEntranceTime=-1;
slowEntranceButton.addEventListener('click',()=>{
 entranceTime=-1;
 resetStagePyro();
 epicEntranceTime=0;
 entranceBot.visible=false;
 slowEntranceButton.textContent='🎬 RESTART EPIC WALK';
 if(entranceActor)entranceActor._entranceState=null;
});
entranceButton.addEventListener('click',()=>{
 epicEntranceTime=-1;
 cinematicBlackout.style.opacity='0';
 for(const p of epicShards)p.mesh.visible=false;
});
function updateEpicEntrance(dt){
 if(epicEntranceTime<0)return false;
 epicEntranceTime+=dt;
 const t=epicEntranceTime;
 // Arena view for 2s, full black for the following 2s.
 cinematicBlackout.style.opacity=t>=2&&t<4?'1':'0';
 updateEpicPyro(t);
 const walking=t>=7&&t<29;
 entranceBot.visible=t>=7;
 const p=THREE.MathUtils.clamp((t-7)/22,0,1);
 // Walk slowly from stage curtain, across the stage and all the way down the ramp.
 const route=[
  entranceV(0,1.2,-34),entranceV(0,1.2,-26),
  entranceV(0,.06,-9),entranceV(0,.06,-6)
 ];
 const lengths=[8,Math.hypot(17,1.14),3];
 let remaining=p*lengths.reduce((a,b)=>a+b,0);
 let pos=route[3].clone();
 for(let i=0;i<3;i++){
  if(remaining<=lengths[i]){
   pos=route[i].clone().lerp(route[i+1],remaining/lengths[i]);
   break;
  }
  remaining-=lengths[i];
 }
 entranceBot.position.copy(pos);
 entranceBot.rotation.y=Math.PI;
 if(entranceActor){
  const anim=walking?'movement.walk':'movement.idle';
  if(entranceActor._entranceState!==anim){entranceActor.play(anim,{fade:.25,restart:true});entranceActor._entranceState=anim;}
  entranceActor.update(dt);
 }
 let eye,focus;
 if(t<2){ // wide establishing shot of the full arena
  eye=entranceV(18,17,22);focus=entranceV(0,3,-16);
 }else if(t<4){ // blackout holds the establishing angle
  eye=entranceV(18,17,22);focus=entranceV(0,3,-16);
 }else if(t<7){ // reveal huge pyrotechnics high above the stage
  eye=entranceV(-13,2.5,-20);focus=entranceV(0,10,-32);
 }else if(t>=16&&t<19){ // front-facing reaction close-up of the wrestler in the ring
  const faceDir=entranceV(-Math.sin(player.rotation.y),0,-Math.cos(player.rotation.y));
  eye=player.position.clone().addScaledVector(faceDir,1.65).add(entranceV(0,1.65,0));
  focus=player.position.clone().add(entranceV(0,1.55,0));
 }else if(t<13){ // very low tracking shot looking up
  eye=pos.clone().add(entranceV(-2.4,.5,4.3));
  focus=pos.clone().add(entranceV(0,2.15,0));
 }else if(t<23){ // front-on ground-level dolly
  eye=pos.clone().add(entranceV(0,.35,5.2));
  focus=pos.clone().add(entranceV(0,2.2,0));
 }else{ // dramatic low side shot as the bot approaches the ring
  eye=pos.clone().add(entranceV(3,.45,3.4));
  focus=pos.clone().add(entranceV(0,2.1,0));
 }
 camera.position.lerp(eye,Math.min(1,dt*10));
 camera.lookAt(focus);
 if(t>=31){
  epicEntranceTime=-1;
  slowEntranceButton.textContent='🎬 EPIC WALK ENTRANCE';
  cinematicBlackout.style.opacity='0';
 }
 return true;
}
// Third entrance test: sprint down the ramp, slide under the bottom rope.
const slideEntranceButton=document.createElement('button');
slideEntranceButton.textContent='🏃 RUN & SLIDE ENTRANCE';
slideEntranceButton.style.cssText=entranceButton.style.cssText+';top:238px;background:#176e83;border-color:#9be6f5';
document.body.appendChild(slideEntranceButton);
let slideEntranceTime=-1;
slideEntranceButton.addEventListener('click',()=>{
 entranceTime=-1;epicEntranceTime=-1;
 cinematicBlackout.style.opacity='0';
 resetStagePyro();
 for(const p of epicShards)p.mesh.visible=false;
 slideEntranceTime=0;
 entranceBot.visible=true;
 entranceBot.position.set(0,1.2,-34);
 entranceBot.rotation.set(0,Math.PI,0);
 if(entranceActor){entranceActor.object.rotation.set(0,0,0);entranceActor._entranceState=null;}
 slideEntranceButton.textContent='🏃 RESTART RUN & SLIDE';
});
entranceButton.addEventListener('click',()=>{slideEntranceTime=-1;if(entranceActor)entranceActor.object.rotation.set(0,0,0);});
slowEntranceButton.addEventListener('click',()=>{slideEntranceTime=-1;if(entranceActor)entranceActor.object.rotation.set(0,0,0);});
function updateSlideEntrance(dt){
 if(slideEntranceTime<0)return false;
 slideEntranceTime+=dt;
 const t=slideEntranceTime;
 let animation='movement.run';
 let pos;
 let tilt=0;
 if(t<1.5){pos=entranceV(0,1.2,-34);animation='movement.idle';}
 else if(t<7){
  const p=(t-1.5)/5.5;
  const z=THREE.MathUtils.lerp(-34,-6,p);
  const y=z<-26?1.2:z<-9?THREE.MathUtils.lerp(1.2,.06,(-26-z)/17):.06;
  pos=entranceV(0,y,z);
 }else if(t<8.5){
  // Dive and slide from ringside under the bottom rope.
  const p=(t-7)/1.5;
  pos=entranceV(0,THREE.MathUtils.lerp(.5,1.45,p),THREE.MathUtils.lerp(-6,-1.7,p));
  tilt=-Math.PI/2*Math.min(1,p*4);
  animation='movement.idle';
 }else{
  const p=Math.min(1,(t-8.5)/1.2);
  pos=entranceV(0,1.45,-1.7);
  tilt=-Math.PI/2*(1-p);
  animation='movement.idle';
 }
 entranceBot.visible=true;
 entranceBot.position.copy(pos);
 entranceBot.rotation.y=Math.PI;
 if(entranceActor){
  if(entranceActor._entranceState!==animation){
   entranceActor.play(animation,{fade:.15,restart:true});
   entranceActor._entranceState=animation;
  }
  entranceActor.object.rotation.x=tilt;
  entranceActor.update(dt);
 }
 let eye,focus;
 if(t<1.5){eye=entranceV(-8,3,-24);focus=entranceV(0,2,-33);}
 else if(t<5.5){
  eye=pos.clone().add(entranceV(-3,1.15,5.5));
  focus=pos.clone().add(entranceV(0,1.2,0));
 }else if(t<7.2){
  eye=entranceV(-6,2.2,-1.8);focus=pos.clone().add(entranceV(0,1.1,0));
 }else{
  eye=entranceV(-5,2.6,2.5);focus=pos.clone().add(entranceV(0,.5,0));
 }
 camera.position.lerp(eye,Math.min(1,dt*12));
 camera.lookAt(focus);
 if(t>=10){
  slideEntranceTime=-1;
  slideEntranceButton.textContent='🏃 RUN & SLIDE ENTRANCE';
  if(entranceActor)entranceActor.object.rotation.set(0,0,0);
 }
 return true;
}
let yaw=Math.PI/4,pitch=.06,distance=11;
const target=new THREE.Vector3(0,1.7,0);
const pointers=new Map();
let lastPinch=null;
renderer.domElement.addEventListener('pointerdown',e=>{
 renderer.domElement.setPointerCapture(e.pointerId);
 pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
});
renderer.domElement.addEventListener('pointermove',e=>{
 if(!pointers.has(e.pointerId))return;
 const prev=pointers.get(e.pointerId);
 pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
 if(pointers.size===1){
  yaw-=(e.clientX-prev.x)*.006;
  pitch=THREE.MathUtils.clamp(pitch+(e.clientY-prev.y)*.006,.02,1.35);
 }else if(pointers.size===2){
  const [a,b]=[...pointers.values()];
  const pinch=Math.hypot(a.x-b.x,a.y-b.y);
  if(lastPinch!==null)distance=THREE.MathUtils.clamp(distance*lastPinch/pinch,9,90);
  lastPinch=pinch;
 }
});
for(const eventName of ['pointerup','pointercancel','lostpointercapture']){
 renderer.domElement.addEventListener(eventName,e=>{pointers.delete(e.pointerId);lastPinch=null;});
}
renderer.domElement.addEventListener('wheel',e=>{
 e.preventDefault();
 distance=THREE.MathUtils.clamp(distance*Math.exp(e.deltaY*.001),9,90);
},{passive:false});
window.addEventListener('resize',()=>{
 camera.aspect=innerWidth/innerHeight;
 camera.updateProjectionMatrix();
 renderer.setSize(innerWidth,innerHeight);
});
renderer.setAnimationLoop(()=>{
 const dt=Math.min(clock.getDelta(),.05);
 updateJumbotron(dt);
 ropeFacingTime=Math.max(0,ropeFacingTime-dt);
 ropeBounceDelay=Math.max(0,ropeBounceDelay-dt);
 ropeMovementLock=Math.max(0,ropeMovementLock-dt);
 ropeAnimationTime=Math.max(0,ropeAnimationTime-dt);
 updateRopes(dt);
 if(!document.getElementById('home').hidden){camera.position.set(22,20,22);camera.lookAt(target);renderer.render(scene,camera);return;}
 let isWalking=false;
 const keyboardX=Number(heldKeys.has('KeyD'))-Number(heldKeys.has('KeyA'));
 const keyboardZ=Number(heldKeys.has('KeyS'))-Number(heldKeys.has('KeyW'));
 const inputX=keyboardX||keyboardZ?keyboardX:movement.active?movement.x:0;
 const inputZ=keyboardX||keyboardZ?keyboardZ:movement.active?movement.y:0;
 const sprint=heldKeys.has('ShiftLeft')||heldKeys.has('ShiftRight');
 // Losing continuous movement resets all accumulated rope momentum.
 if(playerHP<=0||Math.abs(inputX)+Math.abs(inputZ)<=.001){ropeSpeedMultiplier=1;}
 if(playerHP>0&&ropeMovementLock<=0&&Math.abs(inputX)+Math.abs(inputZ)>.001){
  const forward=new THREE.Vector3(-Math.sin(yaw),0,-Math.cos(yaw));
  const right=new THREE.Vector3(Math.cos(yaw),0,-Math.sin(yaw));
  const move=right.multiplyScalar(inputX).add(forward.multiplyScalar(-inputZ));
  if(move.lengthSq()>.0001){
   move.clampLength(0,1);
   isWalking=true;
   const step=move.multiplyScalar((sprint?8:5)*ropeSpeedMultiplier*dt);
   if(loadedArena){
    const tryAxis=(axis,amount)=>{
     const nx=player.position.x+(axis==='x'?amount:0);
     const nz=player.position.z+(axis==='z'?amount:0);
     const adjusted=ropeCollision(nx,nz,dt);
     const tx=adjusted.x,tz=adjusted.z;
     const floor=arenaFloorAt(tx,tz,player.position.y);
     if(floor>=player.position.y-.65 && floor<=player.position.y+.42 && !blockedByArena(tx,tz,floor)){
      player.position[axis]=axis==='x'?tx:tz;
      player.position.y=floor;
     }else if(floor<player.position.y-.65 && !blockedByArena(tx,tz,player.position.y)){
      player.position[axis]+=amount;
      player.position.y=Math.max(floor,player.position.y-3*dt);
     }
    };
    tryAxis('x',step.x);tryAxis('z',step.z);
   }else{
    player.position.add(step);
    player.position.x=THREE.MathUtils.clamp(player.position.x,-7.65,7.65);
    player.position.z=THREE.MathUtils.clamp(player.position.z,-7.65,7.65);
   }
   if(ropeFacingTime<=0)player.rotation.y=Math.atan2(-move.x,-move.z);
  }
 }

 if(playerHP>0&&ropeBounceDelay<=0&&ropeRecoilTime>0){
  ropeRecoilTime=Math.max(0,ropeRecoilTime-dt);
  const amount=dt*(ropeRecoilTime/.28);
  const nx=player.position.x+ropeRecoil.x*amount,nz=player.position.z+ropeRecoil.z*amount;
  if(!blockedByArena(nx,nz,player.position.y)){player.position.x=nx;player.position.z=nz;}
 }
 if(playerPunchImpact>=0){playerPunchImpact-=dt;if(playerPunchImpact<0&&remoteConnected&&playerHP>0)sendNetwork({type:'punch',momentum:ropeSpeedMultiplier});}
 combatTick(dt);
 if(loadedWrestler){
  if(punchRemaining>0)punchRemaining=Math.max(0,punchRemaining-dt);
  const nextAnimation=playerHP<=0?'fall':punchRemaining>0?'punch':ropeAnimationTime>ropeReboundDuration?'ropeLean':ropeAnimationTime>0?'ropeRebound':isWalking?'run':'idle';
  if(loadedWrestler._ttwState!==nextAnimation){
   playTTWAnimation(loadedWrestler,nextAnimation,.2);
   loadedWrestler._ttwState=nextAnimation;
  }
  loadedWrestler.update(dt);
 }
 target.lerp(new THREE.Vector3(player.position.x,player.position.y+1.25,player.position.z),Math.min(1,dt*6));
 const cinematicActive=slideEntranceTime>=0?updateSlideEntrance(dt):epicEntranceTime>=0?updateEpicEntrance(dt):updateEntrance(dt);
 if(!cinematicActive){
 camera.position.set(
 target.x+Math.sin(yaw)*Math.cos(pitch)*distance,
 target.y+Math.sin(pitch)*distance,
 target.z+Math.cos(yaw)*Math.cos(pitch)*distance
 );
 // Aim below the wrestler so the character is framed in the centre of the gameplay view.
 camera.lookAt(target.x,target.y-2.7,target.z);
 }
 renderActionFeed(dt);
 renderer.render(scene,camera);
});
