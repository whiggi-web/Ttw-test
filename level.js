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
 const originalManifest=await (await fetch('./assets/ttw-wrestlers/manifest-batch2.json')).json();
 const coreIds=originalManifest.animations.filter(a=>a.status==='ready').map(a=>a.id);
 const pack=await loadPack('./assets/ttw-wrestlers/manifest-master.json',{animations:[...coreIds,'throws.powerbomb-attacker','throws.powerbomb-defender']});
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
const attackMoves={punch:{anim:'striking.punch',reaction:'reactions.hit-front',duration:.8,impact:.3},jab:{anim:'striking.jab',reaction:'reactions.hit-front',duration:.65,impact:.23},hook:{anim:'striking.hook-right',reaction:'reactions.hit-left',duration:.85,impact:.35},uppercut:{anim:'striking.uppercut',reaction:'reactions.knocked-back',duration:1,impact:.42},kick:{anim:'striking.roundhouse',reaction:'reactions.hit-kick',duration:1.05,impact:.48},clothesline:{anim:'striking.clothesline',reaction:'reactions.hit-clothesline',duration:1.1,impact:.5}};
const playTTWAnimation=(w,state,fade=.2)=>{
 if(!w)return;
 const name=usingBatchOne?({idle:'movement.idle',run:'movement.run',punch:'striking.punch',fall:'falls.fall-backward',ropeLean:'ropes.rope-lean',ropeRebound:'ropes.rope-rebound'}[state]||attackMoves[state]?.anim||(state.startsWith('reactions.')?state:'movement.idle')):state;
 const safeName=usingBatchOne&&w.library?.defs?.[name]?name:(usingBatchOne?'movement.idle':name);
 try{w.play(safeName,{fade,restart:true});}catch(error){console.warn('TTW animation unavailable:',name,error);if(safeName!=='movement.idle')try{w.play('movement.idle',{fade:0,restart:true});}catch{}}
};
// Gameplay position belongs to the player/remote network group, never to an animation.
// Batch 2 baked reactions can otherwise commit hip motion into the child model,
// leaving the visible wrestler offset from the actual hitbox.
function lockGameplayWrestler(w){
 if(!w)return;
 w.autoRootMotion=false;
 w.commitRootMotion=()=>false;
 w.object.position.set(0,0,0);
}
lockGameplayWrestler(loadedWrestler);
lockGameplayWrestler(remoteWrestler);
function keepWrestlerAtHitbox(w){
 if(!w)return;
 w.object.position.set(0,0,0);
}
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
let botMode=true,botRecover=0,botMoveClock=0,botStrikeClock=2.5;
let playerHP=100,remoteHP=100,playerPunchImpact=-1,remoteConnected=false,playerSlot=null,network=null,sendClock=0,remoteAnim='idle',remoteHasTarget=false;
const remoteTarget=new THREE.Vector3();
let remoteTargetRotation=0;
const combatHud=document.createElement('div');
combatHud.style.cssText='position:fixed;right:16px;top:16px;z-index:12;color:white;font:700 16px system-ui;text-shadow:0 2px 5px black;pointer-events:none;text-align:right';
document.body.appendChild(combatHud);
const networkStatus=document.createElement('div');
networkStatus.style.cssText='position:fixed;right:16px;top:46px;z-index:12;color:#bcd0e4;font:12px system-ui;text-shadow:0 1px 3px black;pointer-events:none';
document.body.appendChild(networkStatus);
function refreshCombatHud(){combatHud.textContent='YOU '+playerHP+' HP | '+(botMode?'SPARRING BOT '+remoteHP+' HP':remoteConnected?'OPPONENT '+remoteHP+' HP':'WAITING FOR PLAYER 2');}
refreshCombatHud();
remote.visible=true;remote.position.set(1.8,1.2,-.6);
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
 if(!wsUrl){networkStatus.textContent='Offline sparring bot active';return;}
 networkStatus.textContent='Connecting…';
 try{network=new WebSocket(wsUrl);}catch{networkStatus.textContent='Invalid server URL';return;}
 network.onopen=()=>sendNetwork({type:'join',name:window.TTWPlayerName||'Wrestler'});
 network.onmessage=e=>{
  let m;try{m=JSON.parse(e.data);}catch{return;}
  if(m.type==='welcome'){playerSlot=m.slot;player.position.set(m.slot===1?-1.4:1.4,1.2,0);playerHP=m.hp??100;refreshCombatHud();}
  if(m.type==='waiting'||m.type==='peer_left'){botMode=true;remote.visible=true;remote.position.set(1.8,1.2,-.6);remoteHasTarget=false;remoteConnected=false;remote.visible=true;remoteHP=100;networkStatus.textContent='Sparring bot active';refreshCombatHud();}
  if(m.type==='joined'){botMode=false;remoteHasTarget=false;remoteConnected=true;remote.visible=true;remoteHP=m.hp??100;networkStatus.textContent='Two players connected';refreshCombatHud();}
  if(m.type==='full'){networkStatus.textContent='Ring full (2 players maximum)';}
  if(m.type==='state'&&m.slot!==playerSlot&&remoteConnected){
   const p=m.position||{};
   if([p.x,p.y,p.z,m.rotation].every(Number.isFinite)){remoteTarget.set(p.x,p.y,p.z);remoteTargetRotation=m.rotation;
    if(!remoteHasTarget){remote.position.copy(remoteTarget);remote.rotation.y=remoteTargetRotation;remoteHasTarget=true;}}
   remoteAnim=['idle','run','fall',...Object.keys(attackMoves)].includes(m.animation)?m.animation:'idle';
  }
  if(m.type==='health'){
   playerHP=m.self;remoteHP=m.other;refreshCombatHud();
   if(m.hit==='self'){showDamage(player.position,'-'+(m.damage??11),'#ff6969');hitReaction=m.reaction||'reactions.hit-front';hitReactionTime=.72;}
   if(m.hit==='other'){showDamage(remote.position,'-'+(m.damage??11),'#ffdf55');remoteReaction=m.reaction||'reactions.hit-front';remoteReactionTime=.72;}
  }
 };
 network.onclose=()=>{botMode=true;remote.visible=true;remote.position.set(1.8,1.2,-.6);network=null;playerSlot=null;remoteHasTarget=false;remoteConnected=false;remote.visible=true;networkStatus.textContent='Disconnected. Refresh to reconnect.';refreshCombatHud();};
 network.onerror=()=>{networkStatus.textContent='Cannot reach multiplayer server';};
}
window.addEventListener('ttw:player-name',startMultiplayer);
if(document.getElementById('home').hidden)startMultiplayer();
function hitSparringBot(move){
 if(!botMode||remoteHP<=0)return;
 const dx=remote.position.x-player.position.x,dz=remote.position.z-player.position.z;
 if(Math.hypot(dx,dz)>2.2)return;
 const damage=Math.round(({punch:11,jab:7,hook:13,uppercut:16,kick:15,clothesline:18}[move]||11)*ropeSpeedMultiplier);
 remoteHP=Math.max(0,remoteHP-damage);
 remoteReaction=remoteHP<=0?'falls.fall-backward':(attackMoves[move]?.reaction||'reactions.hit-front');
 remoteReactionTime=.8;
 showDamage(remote.position,'-'+damage,'#ffdf55');
 refreshCombatHud();
 if(remoteHP<=0){botRecover=10;remoteAnim='fall';}
}
function updateSparringBot(dt){
 if(!botMode||grappleMove||document.getElementById('home').hidden===false)return;
 if(remoteHP<=0){
  botRecover-=dt;
  if(botRecover<=0){remoteHP=100;remoteAnim='idle';remoteReactionTime=0;remote.position.set(1.8,1.2,-.6);refreshCombatHud();}
  return;
 }
 const dx=player.position.x-remote.position.x,dz=player.position.z-remote.position.z;
 const dist=Math.hypot(dx,dz);
 remote.rotation.y=Math.atan2(-dx,-dz);
 botMoveClock-=dt;
 if(dist>1.45&&botMoveClock<=0){
  const step=Math.min(dist-1.45,dt*1.75);
  const nx=remote.position.x+dx/dist*step,nz=remote.position.z+dz/dist*step;
  if(Math.abs(nx)<3.05&&Math.abs(nz)<3.05){remote.position.x=nx;remote.position.z=nz;}
  remoteAnim='run';
 }else remoteAnim='idle';
 botStrikeClock-=dt;
 if(dist<2&&botStrikeClock<=0&&playerHP>0){
  botStrikeClock=3.2;
  hitReaction='reactions.hit-front';hitReactionTime=.65;
  playerHP=Math.max(0,playerHP-2);
  showDamage(player.position,'-2','#ff6969');
  refreshCombatHud();
 }
}
function combatTick(dt){
 updateSparringBot(dt);
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
 if(remoteWrestler&&(remoteConnected||botMode)&&!grappleMove){
  remoteReactionTime=Math.max(0,remoteReactionTime-dt);
  const state=remoteHP<=0?'fall':remoteReactionTime>0?remoteReaction:remoteAnim;
  if(remoteWrestler._ttwState!==state){playTTWAnimation(remoteWrestler,state,.12);remoteWrestler._ttwState=state;}
  remoteWrestler.update(dt);
  keepWrestlerAtHitbox(remoteWrestler);
 }
 sendClock+=dt;
 if(sendClock>=.05&&playerSlot!==null){
  sendClock-=.05;
  sendNetwork({type:'state',position:{x:player.position.x,y:player.position.y,z:player.position.z},rotation:player.rotation.y,animation:playerHP<=0?'fall':punchRemaining>0?activeAttack:heldKeys.size||movement.active?'run':'idle'});
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
let punchRemaining=0,activeAttack='punch',hitReactionTime=0,hitReaction='reactions.hit-front',remoteReactionTime=0,remoteReaction='reactions.hit-front';
const attackPanel=document.createElement('div');
attackPanel.style.cssText='position:fixed;bottom:120px;right:12px;z-index:16;display:flex;flex-wrap:wrap;gap:5px;max-width:320px;justify-content:flex-end';
document.body.appendChild(attackPanel);
const contextMessage=document.createElement('div');
contextMessage.style.cssText='position:fixed;bottom:190px;right:12px;z-index:16;color:#fff;background:#14243bd9;padding:7px 10px;border-radius:6px;font:12px system-ui;pointer-events:none;display:none';
document.body.appendChild(contextMessage);
let contextMessageUntil=0;
function showContextMessage(message){contextMessage.textContent=message;contextMessage.style.display='block';contextMessageUntil=performance.now()+2000;}
let attackSequence=0;
function performAttack(move){
 if(grappleMove||traversal||punchRemaining>0||playerHP<=0||!(remoteConnected||botMode)||document.getElementById('home').hidden===false)return;
 const attack=attackMoves[move];if(!attack)return;
 activeAttack=move;punchRemaining=attack.duration;playerPunchImpact=attack.impact;
}
function tapAttack(){
 const moves=['punch','jab','hook','kick','uppercut'];
 performAttack(moves[attackSequence++%moves.length]);
}
// Temporary scripted traversal until Claude's planned rope/aerial clips are supplied.
let traversal=null;
function beginTraversal(kind){
 if(traversal||playerHP<=0)return;
 const x=player.position.x,z=player.position.z;
 if(kind==='ring'){
  const side=Math.abs(x)>Math.abs(z)?'x':'z';
  const sign=Math.sign(player.position[side])||1;
  const distance=Math.abs(player.position[side]);
  if(distance<2.6||distance>4.15)return showContextMessage('Stand beside the ropes to enter or exit');
  const outside=distance>3.6;
  const start=player.position.clone(),end=start.clone();
  end[side]=sign*(outside?2.55:3.98);
  end.y=1.2;
  traversal={kind,start,end,time:0,duration:1.65};
  showContextMessage(outside?'Climbing into the ring':'Climbing out of the ring');
 }else if(kind==='climb'){
  if(Math.abs(x)<2.15||Math.abs(z)<2.15)return showContextMessage('Move into a ring corner to climb');
  const corner=new THREE.Vector3(Math.sign(x)*3.1,1.2,Math.sign(z)*3.1);
  traversal={kind,start:player.position.clone(),end:corner,time:0,duration:1.8};
  showContextMessage('Climbing the turnbuckle');
 }else if(kind==='dive'){
  if(!traversal||traversal.kind!=='perched')return;
 }
}
function swanDive(){
 if(!traversal||traversal.kind!=='perched')return showContextMessage('Climb a turnbuckle first');
 traversal={kind:'dive',start:player.position.clone(),end:new THREE.Vector3(0,1.2,0),time:0,duration:1.45};
 showContextMessage('SWAN DIVE!');
}
function updateTraversal(dt){
 if(!traversal)return false;
 if(traversal.kind==='perched'){player.position.copy(traversal.end);return true;}
 traversal.time+=dt;
 const p=Math.min(1,traversal.time/traversal.duration);
 const eased=p*p*(3-2*p);
 player.position.lerpVectors(traversal.start,traversal.end,eased);
 if(traversal.kind==='ring'){
  player.position.y=1.2+Math.sin(Math.PI*p)*.18;
  if(loadedWrestler)loadedWrestler.object.rotation.x=-Math.sin(Math.PI*p)*.28;
 }else if(traversal.kind==='climb'){
  player.position.y=THREE.MathUtils.lerp(traversal.start.y,2.55,eased);
 }else if(traversal.kind==='dive'){
  player.position.y=THREE.MathUtils.lerp(traversal.start.y,1.2,eased)+Math.sin(Math.PI*p)*1.4;
  if(loadedWrestler)loadedWrestler.object.rotation.x=-Math.sin(Math.PI*p)*1.2;
 }
 if(p>=1){
  if(traversal.kind==='climb'){traversal={kind:'perched',end:player.position.clone()};showContextMessage('Press SPECIAL (F) to swan dive');}
  else{traversal=null;if(loadedWrestler)loadedWrestler.object.rotation.x=0;}
 }
 return true;
}
// Shared-clock, offline two-person grapple. The player/remote groups remain authoritative.
let grappleMove=null;
const POWERBOMB_DURATION=2.3,POWERBOMB_IMPACT=1.55;
function beginPowerbomb(){
 if(grappleMove||traversal||punchRemaining>0||playerHP<=0||remoteHP<=0)return;
 if(!botMode)return showContextMessage('Powerbomb currently available against the offline bot');
 if(!loadedWrestler?.library?.defs?.['throws.powerbomb-attacker']||!remoteWrestler?.library?.defs?.['throws.powerbomb-defender'])return showContextMessage('Powerbomb assets not loaded');
 const dx=remote.position.x-player.position.x,dz=remote.position.z-player.position.z;
 if(Math.hypot(dx,dz)>2.2)return showContextMessage('Move closer to grapple');
 // Keep the pair in the ring, away from the ropes.
 const x=THREE.MathUtils.clamp(player.position.x,-2.3,2.3);
 const z=THREE.MathUtils.clamp(player.position.z,-2.3,2.3);
 player.position.set(x,1.2,z);
 const yaw=Math.atan2(-dx,-dz);
 player.rotation.y=yaw;
 remote.rotation.y=yaw-Math.PI;
 const ahead=new THREE.Vector3(0,0,-.55).applyAxisAngle(new THREE.Vector3(0,1,0),yaw);
 remote.position.copy(player.position).add(ahead);
 remote.position.y=1.2;
 botStrikeClock=99;
 remoteReactionTime=0;
 punchRemaining=0;playerPunchImpact=-1;
 grappleMove={time:0,impact:false,origin:player.position.clone(),yaw,offset:ahead};
 try{
  loadedWrestler.play('throws.powerbomb-attacker',{fade:0,restart:true});
  remoteWrestler.play('throws.powerbomb-defender',{fade:0,restart:true});
  loadedWrestler._ttwState='throws.powerbomb-attacker';
  remoteWrestler._ttwState='throws.powerbomb-defender';
 }catch(error){console.error('TTW powerbomb failed',error);grappleMove=null;showContextMessage('Powerbomb animation error');return;}
 showContextMessage('POWERBOMB!');
}
function updatePowerbomb(dt){
 if(!grappleMove)return;
 const g=grappleMove;
 g.time=Math.min(POWERBOMB_DURATION,g.time+dt);
 // Freeze AI and gameplay movement, while retaining the paired asset's poses.
 const forward=new THREE.Vector3(0,0,-1).applyAxisAngle(new THREE.Vector3(0,1,0),g.yaw);
 const travel=THREE.MathUtils.smoothstep(g.time,0,POWERBOMB_DURATION)*.2;
 player.position.copy(g.origin).addScaledVector(forward,travel);
 remote.position.copy(g.origin).add(g.offset);
 remote.rotation.y=g.yaw-Math.PI;
 remote.position.y=1.2;
 if(!g.impact&&g.time>=POWERBOMB_IMPACT){
  g.impact=true;
  remoteHP=Math.max(0,remoteHP-30);
  showDamage(remote.position,'-30','#ffdf55');
  refreshCombatHud();
 }
 if(g.time>=POWERBOMB_DURATION){
  grappleMove=null;
  remoteReaction=remoteHP<=0?'fall':'reactions.stunned';
  remoteReactionTime=remoteHP<=0?0:1.5;
  botStrikeClock=3.2;
  if(remoteHP<=0){botRecover=10;remoteAnim='fall';}
  loadedWrestler._ttwState='';
  remoteWrestler._ttwState='';
 }
}
const contextActions=[
 ['GRAPPLE','KeyG',()=>{
  if(!(remoteConnected||botMode)||playerHP<=0||remoteHP<=0)return showContextMessage('Grapple requires an active opponent');
  if(player.position.distanceTo(remote.position)>2.2)return showContextMessage('Move closer to grapple');
  beginPowerbomb();
 }],
 ['ROPES','KeyR',()=>{
  const near=Math.min(Math.abs(Math.abs(player.position.x)-3.5),Math.abs(Math.abs(player.position.z)-3.5));
  if(near>.9)return showContextMessage('Move closer to the ropes');
  showContextMessage('Rope interaction: lean and rebound');
  ropeAnimationTime=1.5;
 }],
 ['ENTER / EXIT','KeyE',()=>beginTraversal('ring')],
 ['TURNBUCKLE','KeyT',()=>beginTraversal('climb')],
 ['SPECIAL','KeyF',()=>{
  if(traversal?.kind==='perched')return swanDive();
  if(!(remoteConnected||botMode)||player.position.distanceTo(remote.position)>2.2)return showContextMessage('Get closer to use a special');
  performAttack('uppercut');showContextMessage('Special test: uppercut');
 }]
];
for(const [label,key,action] of contextActions){
 const btn=document.createElement('button');btn.textContent=label+' ('+key.slice(3)+')';btn.style.cssText='background:#222c42;color:#fff;border:1px solid #8ca9d5;border-radius:7px;padding:9px;font:700 11px system-ui;cursor:pointer';btn.addEventListener('pointerdown',e=>e.stopPropagation());btn.addEventListener('click',action);attackPanel.appendChild(btn);
}
window.addEventListener('keydown',e=>{
 if(e.repeat||e.target instanceof HTMLElement&&e.target.closest('input,textarea,[contenteditable="true"]'))return;
 const action=contextActions.find(item=>item[1]===e.code);
 if(action){action[2]();e.preventDefault();}
});
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
 tapAttack();
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
  // The authored ramp slopes DOWN from stage z=-26 to floor z=-9.
  const p=(t-1.5)/5.5;
  const z=THREE.MathUtils.lerp(-34,-5.15,p);
  const y=z<-26?1.2:z<-9?THREE.MathUtils.lerp(1.2,.06,(z+26)/17):.06;
  pos=entranceV(0,y,z);
 }else if(t<8.5){
  // The ring apron begins near z=-4; climb onto the ring surface,
  // then travel along the canvas, not through the underside of the ring.
  const p=(t-7)/1.5;
  pos=entranceV(0,THREE.MathUtils.lerp(.75,1.42,Math.min(1,p*3)),THREE.MathUtils.lerp(-5.15,-1.65,p));
  tilt=-Math.PI*.42*Math.min(1,p*5);
  animation='movement.idle';
 }else{
  const p=Math.min(1,(t-8.5)/1.2);
  pos=entranceV(0,1.42,-1.65);
  tilt=-Math.PI*.42*(1-p);
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

/* TTW v0.60: The Royal Procession, a four-person theatrical entrance. */
const processionButton=document.createElement('button');
processionButton.textContent='👑 ROYAL PROCESSION';
processionButton.style.cssText=entranceButton.style.cssText+';top:283px;background:#68420f;border-color:#ffe18b';
document.body.appendChild(processionButton);
let processionTime=-1;
const processionActors=[];
const processionColors=[0xffd25b,0x3355aa,0x992f6b,0x336c61];
for(let i=0;i<4;i++){
 const group=new THREE.Group();group.visible=false;group.name='TTW_PROCESSION_'+i;scene.add(group);
 let actor=null;
 if(wrestlerPack){
  try{
   actor=wrestlerPack.createWrestler('wrestler-'+String([3,7,12,18][i]).padStart(2,'0'));
   group.add(actor.object);
  }catch(e){console.warn('Procession actor unavailable',i,e);}
 }
 if(!actor){
  const mesh=new THREE.Mesh(new THREE.CapsuleGeometry(.38,1.15,6,10),new THREE.MeshStandardMaterial({color:processionColors[i]}));
  mesh.position.y=1;group.add(mesh);
 }
 const marker=new THREE.Mesh(new THREE.TorusGeometry(.52,.065,6,24),new THREE.MeshBasicMaterial({color:processionColors[i]}));
 marker.rotation.x=Math.PI/2;marker.position.y=.06;group.add(marker);
 processionActors.push({group,actor,state:''});
}
const processionCrown=new THREE.Group();scene.add(processionCrown);
const crownGold=new THREE.MeshStandardMaterial({color:0xffd23b,metalness:.75,roughness:.2,emissive:0x5b3500});
const crownBase=new THREE.Mesh(new THREE.CylinderGeometry(.43,.42,.21,9,1,true),crownGold);
processionCrown.add(crownBase);
for(let j=0;j<9;j++){
 const a=j*Math.PI*2/9;
 const tip=new THREE.Mesh(new THREE.ConeGeometry(.11,.44,4),crownGold);
 tip.position.set(Math.cos(a)*.39,.27,Math.sin(a)*.39);
 processionCrown.add(tip);
}
processionCrown.visible=false;
const processionLight=new THREE.SpotLight(0xffd989,140,38,Math.PI/6,.55,1.2);
processionLight.position.set(0,12,-26);processionLight.target.position.set(0,0,-27);
scene.add(processionLight,processionLight.target);
processionLight.visible=false;
const processionBanner=document.createElement('div');
processionBanner.style.cssText='position:fixed;top:13%;left:50%;transform:translateX(-50%);z-index:15;pointer-events:none;text-align:center;font:900 clamp(18px,4vw,46px) system-ui;letter-spacing:.13em;color:#ffe09a;text-shadow:0 0 18px #e0a83a,0 3px 6px #000;opacity:0;transition:opacity .3s';
processionBanner.textContent='THE ROYAL PROCESSION';
document.body.appendChild(processionBanner);
const processionConfetti=[];
for(let i=0;i<110;i++){
 const mat=new THREE.MeshBasicMaterial({color:i%3===0?0xffffff:i%2?0xffca35:0x8d4ad0,side:THREE.DoubleSide});
 const mesh=new THREE.Mesh(new THREE.PlaneGeometry(.12,.24),mat);
 mesh.visible=false;scene.add(mesh);
 processionConfetti.push({mesh,seed:i*2.39996,speed:1.3+(i%7)*.19});
}
function stopProcession(){
 processionTime=-1;
 processionLight.visible=false;
 processionCrown.visible=false;
 processionBanner.style.opacity='0';
 for(const p of processionActors){p.group.visible=false;p.state='';}
 for(const c of processionConfetti)c.mesh.visible=false;
 processionButton.textContent='👑 ROYAL PROCESSION';
}
processionButton.addEventListener('click',()=>{
 entranceTime=-1;epicEntranceTime=-1;slideEntranceTime=-1;
 resetStagePyro();for(const p of epicShards)p.mesh.visible=false;
 cinematicBlackout.style.opacity='0';
 if(entranceActor)entranceActor.object.rotation.set(0,0,0);
 entranceBot.visible=false;
 stopProcession();
 processionTime=0;
 processionLight.visible=true;
 processionButton.textContent='👑 RESTART PROCESSION';
});
for(const b of [entranceButton,slowEntranceButton,slideEntranceButton]){
 b.addEventListener('click',stopProcession);
}
function updateProcession(dt){
 if(processionTime<0)return false;
 processionTime+=dt;
 const t=processionTime;
 const smooth=p=>{p=THREE.MathUtils.clamp(p,0,1);return p*p*(3-2*p);};
 // The champion enters last, flanked by two hype wrestlers and a bodyguard.
 const reveal=smooth((t-2.8)/1.8);
 const travel=smooth((t-7.5)/17);
 const z=THREE.MathUtils.lerp(-33,-7,travel);
 const y=z< -26?1.2:z< -9?THREE.MathUtils.lerp(1.2,.06,(z+26)/17):.06;
 for(let i=0;i<processionActors.length;i++){
  const p=processionActors[i],g=p.group;
  g.visible=t>(i===0?3.2:i===3?2:2.6);
  let x=0,zz=z,yy=y;
  if(i===1){x=-2.15;zz=z+2.1;}
  if(i===2){x=2.15;zz=z+2.1;}
  if(i===3){x=0;zz=z+4.2;}
  if(t<7.5){zz=-33+(i===1||i===2?2:i===3?4:0);yy=1.2;}
  if(t>=24&&i>0){x+=(i===1?-1:i===2?1:0)*smooth((t-24)/2);zz+=smooth((t-24)/2)*1.4;}
  g.position.set(x,yy,zz);
  g.rotation.y=Math.PI;
  const state=t<7.5?'movement.idle':t<24?'movement.walk':'movement.idle';
  if(p.actor){
   if(p.state!==state){try{p.actor.play(state,{fade:.25,restart:true});}catch(e){console.warn('Procession clip unavailable',e);}p.state=state;}
   p.actor.update(dt);
   p.actor.object.position.set(0,0,0);
  }
 }
 // The crown descends dramatically over the champion's head.
 const leader=processionActors[0].group;
 processionCrown.visible=t>=4.5&&t<25;
 processionCrown.position.set(leader.position.x,leader.position.y+2.45+(t<6?(6-t)*.8:0),leader.position.z);
 processionCrown.rotation.y+=dt*.45;
 processionLight.position.set(leader.position.x,12,leader.position.z+1);
 processionLight.target.position.set(leader.position.x,leader.position.y+1,leader.position.z);
 processionBanner.style.opacity=t>4&&t<9||t>23&&t<28?'1':'0';
 for(let i=0;i<processionConfetti.length;i++){
  const c=processionConfetti[i],p=c.mesh;
  const age=t-24-(i%11)*.09;
  p.visible=age>=0&&age<5;
  if(p.visible){
   const a=c.seed;
   p.position.set(Math.sin(a)*((i%8)*.5+.5)+Math.sin(age*1.4+a)*.45,6.8-age*c.speed, -7+Math.cos(a)*((i%7)*.52+.3));
   p.rotation.set(age*2+a,age*1.3,age*3);
  }
 }
 let eye,focus;
 if(t<3){eye=entranceV(15,11,-10);focus=entranceV(0,3,-33);}
 else if(t<7.5){eye=entranceV(-4.5,2.1,-25.5);focus=entranceV(0,3,-32);}
 else if(t<12){eye=entranceV(-5,3,z+8);focus=entranceV(0,y+1.5,z);}
 else if(t<17){eye=entranceV(6,4,z+5);focus=entranceV(0,y+1.3,z);}
 else if(t<22){eye=entranceV(0,2.4,z+7);focus=entranceV(0,y+1.6,z);}
 else if(t<25){eye=entranceV(-9,5,-2);focus=entranceV(0,1.8,-7);}
 else{eye=entranceV(0,2.2,1);focus=entranceV(0,1.8,-7);}
 camera.position.lerp(eye,Math.min(1,dt*8));
 camera.lookAt(focus);
 if(t>=30)stopProcession();
 return true;
}



/* v0.63: Tiny Invasion. Fifteen lightweight half-sized wrestlers chase a full-sized star. */
const tinyButton=document.createElement('button');
tinyButton.textContent='🐜 TINY INVASION';
tinyButton.type='button';
let tinyTime=-1;
const tinyMob=[];
const tinyMatColors=[0xed455c,0x47b8e8,0xf4b33b,0x80d66d,0x9c76e8];
for(let i=0;i<15;i++){
 const group=new THREE.Group();group.name='TTW_TINY_'+(i+1);group.scale.setScalar(.5);group.visible=false;scene.add(group);
 const suit=new THREE.MeshStandardMaterial({color:tinyMatColors[i%5],roughness:.72});
 const skin=new THREE.MeshStandardMaterial({color:0xe8b58b,roughness:.8});
 const torso=new THREE.Mesh(new THREE.CapsuleGeometry(.35,.68,4,8),suit);torso.position.y=1.1;group.add(torso);
 const head=new THREE.Mesh(new THREE.SphereGeometry(.29,8,6),skin);head.position.y=1.94;group.add(head);
 const limbs=[];
 for(const side of [-1,1]){
  const arm=new THREE.Group();arm.position.set(side*.4,1.46,0);
  const armMesh=new THREE.Mesh(new THREE.CapsuleGeometry(.105,.52,3,6),skin);armMesh.position.y=-.3;arm.add(armMesh);group.add(arm);limbs.push(arm);
  const leg=new THREE.Group();leg.position.set(side*.19,.75,0);
  const legMesh=new THREE.Mesh(new THREE.CapsuleGeometry(.13,.57,3,6),suit);legMesh.position.y=-.32;leg.add(legMesh);group.add(leg);limbs.push(leg);
 }
 tinyMob.push({group,limbs,position:new THREE.Vector3(0,0,-40),last:new THREE.Vector3(0,0,-40)});
}
function tinyFloor(z){return z< -26?1.2:z< -9?THREE.MathUtils.lerp(1.2,.06,(z+26)/17):z> -4.4&&z<4.4?1.2:.06;}
function tinyPath(points,p){
 const u=THREE.MathUtils.clamp(p,0,1)*(points.length-1),i=Math.min(points.length-2,Math.floor(u));
 return new THREE.Vector3().lerpVectors(new THREE.Vector3(...points[i]),new THREE.Vector3(...points[i+1]),u-i);
}
function stopTiny(){
 tinyTime=-1;
 for(const m of tinyMob)m.group.visible=false;
 tinyButton.textContent='🐜 TINY INVASION';
 if(entranceActor)entranceActor.object.rotation.set(0,0,0);
}
tinyButton.addEventListener('click',()=>{
 entranceTime=-1;epicEntranceTime=-1;slideEntranceTime=-1;
 if(typeof stopProcession==='function')stopProcession();
 resetStagePyro();for(const p of epicShards)p.mesh.visible=false;
 cinematicBlackout.style.opacity='0';
 entranceBot.visible=true;
 if(entranceActor){entranceActor.object.rotation.set(0,0,0);entranceActor._entranceState=null;}
 stopTiny();tinyTime=0;tinyButton.textContent='🐜 RESTART TINY INVASION';
});
for(const b of [entranceButton,slowEntranceButton,slideEntranceButton,processionButton])b.addEventListener('click',stopTiny);
function updateTiny(dt){
 if(tinyTime<0)return false;
 tinyTime+=dt;
 const t=tinyTime;
 // Star: stroll down ramp, spot the mob, flee around right side of ring, slide into ring.
 let hero,anim='movement.walk',tilt=0;
 if(t<8){
  const z=THREE.MathUtils.lerp(-34,-18,THREE.MathUtils.clamp(t/8,0,1));
  hero=new THREE.Vector3(0,tinyFloor(z),z);
 }else if(t<9.4){
  hero=new THREE.Vector3(0,tinyFloor(-18),-18);anim='movement.idle';
 }else if(t<16){
  const p=(t-9.4)/6.6;
  hero=tinyPath([[0,0,-18],[0,0,-7],[6,0,-6],[7,0,0],[6,0,5],[3.8,0,6]],p);
  hero.y=tinyFloor(hero.z);anim='movement.run';
 }else if(t<19.2){
  const p=(t-16)/3.2;
  hero=tinyPath([[3.8,0,6],[2,0,5],[0,0,4.2],[0,0,2.2]],p);
  hero.y=THREE.MathUtils.lerp(.06,1.2,THREE.MathUtils.clamp((p-.34)*3,0,1));
  tilt=-Math.sin(Math.PI*THREE.MathUtils.clamp((p-.28)*1.5,0,1))*1.05;
  anim='movement.idle';
 }else{hero=new THREE.Vector3(0,1.2,2.2);anim='movement.idle';}
 entranceBot.visible=true;
 const prev=entranceBot.position.clone();
 entranceBot.position.copy(hero);
 if(hero.distanceToSquared(prev)>.00002)entranceBot.rotation.y=Math.atan2(-(hero.x-prev.x),-(hero.z-prev.z));
 if(entranceActor){
  if(entranceActor._entranceState!==anim){
   try{entranceActor.play(anim,{fade:.18,restart:true});}catch(e){console.warn('Tiny Invasion hero clip',e);}
   entranceActor._entranceState=anim;
  }
  entranceActor.object.rotation.x=tilt;
  entranceActor.update(dt);
 }
 // Mob: delayed wave, seven circle the left, eight circle the right.
 // They stay on the arena floor, never cut across the ring or its ropes.
 for(let i=0;i<tinyMob.length;i++){
  const m=tinyMob[i],g=m.group,delay=(i%5)*.23+Math.floor(i/5)*.17;
  const age=t-7.2-delay;
  g.visible=age>=0&&age<27;
  if(!g.visible)continue;
  let pos;
  const lane=(i%5-2)*.32;
  const side=i<7?-1:1;
  const ringRoute=[
   [lane,0,-30],[lane,0,-18],[side*(2.3+Math.abs(lane)),0,-8],
   [side*6.5,0,-6],[side*7.1,0,0],[side*6.4,0,5.6],
   [side*3.4,0,6.6],[side*1.4,0,5.3]
  ];
  if(age<12.7){
   pos=tinyPath(ringRoute,age/12.7);
  }else if(age<15.1){
   pos=tinyPath(ringRoute,1);
  }else{
   // Comically flee in reverse, back to the curtain.
   pos=tinyPath([...ringRoute].reverse(),(age-15.1)/11.9);
  }
  pos.y=tinyFloor(pos.z);
  m.last.copy(m.position);m.position.copy(pos);
  g.position.copy(pos);
  const delta=pos.clone().sub(m.last);
  if(delta.lengthSq()>.000001)g.rotation.y=Math.atan2(-delta.x,-delta.z);
  const running=age<12.7||age>=15.1;
  for(let j=0;j<m.limbs.length;j++)m.limbs[j].rotation.x=running?Math.sin(t*14+i*1.2+(j%2)*Math.PI)*.75:0;
 }
 // Broadcast coverage: reveal, shock, chase tracking, split-screen-style overhead, ring escape.
 let eye,focus;
 if(t<7){eye=entranceV(-5,3.1,hero.z+6);focus=hero.clone().add(entranceV(0,1.2,0));}
 else if(t<10){eye=entranceV(6,5,-12);focus=entranceV(0,1,-20);}
 else if(t<13){eye=hero.clone().add(entranceV(5,3,6));focus=hero.clone().add(entranceV(0,1,0));}
 else if(t<16){eye=entranceV(0,17,12);focus=entranceV(0,0,0);}
 else if(t<20){eye=entranceV(9,4,10);focus=hero.clone().add(entranceV(0,.8,0));}
 else if(t<25){eye=entranceV(0,13,12);focus=entranceV(0,1,2);}
 else{eye=entranceV(-7,6,-5);focus=entranceV(0,1,-15);}
 camera.position.lerp(eye,Math.min(1,dt*9));
 camera.lookAt(focus);
 if(t>=36){stopTiny();entranceBot.visible=false;}
 return true;
}



/* v0.66: Model photo entrance and the slow silver-toned Omen. */
const showcaseNames=['📸 The Perfect Entrance','🌑 The Omen'];
const showcaseButtons=showcaseNames.map(name=>{const b=document.createElement('button');b.type='button';b.textContent=name;return b;});
let showcaseMode=-1,showcaseTime=-1,showcaseFreeze=false,omenSlow=false;
const showcaseOverlay=document.createElement('div');
showcaseOverlay.style.cssText='position:fixed;inset:0;z-index:14;pointer-events:none;opacity:0;display:grid;place-items:center;color:#fff;font:900 clamp(24px,7vw,78px) system-ui;text-align:center;text-shadow:0 4px 20px #000;letter-spacing:.1em';
document.body.appendChild(showcaseOverlay);
const showcaseFlash=document.createElement('div');
showcaseFlash.style.cssText='position:fixed;inset:0;z-index:19;pointer-events:none;background:#fff;opacity:0';
document.body.appendChild(showcaseFlash);
const showcaseGrayscale=document.createElement('div');
showcaseGrayscale.style.cssText='position:fixed;inset:0;z-index:18;pointer-events:none;backdrop-filter:grayscale(1) contrast(1.35);-webkit-backdrop-filter:grayscale(1) contrast(1.35);opacity:0';
document.body.appendChild(showcaseGrayscale);
const omenVeil=document.createElement('div');
omenVeil.style.cssText='position:fixed;inset:0;z-index:13;pointer-events:none;opacity:0;background:linear-gradient(110deg,#c2c9d022,#12182766 48%,#dce0e622);box-shadow:inset 0 0 190px 75px #05070b9c;transition:opacity .8s';
document.body.appendChild(omenVeil);
const omenTitle=document.createElement('div');
omenTitle.style.cssText='position:fixed;top:18%;left:0;width:100%;text-align:center;z-index:15;pointer-events:none;color:#cbd1d7;font:300 clamp(24px,5vw,54px) Georgia,serif;letter-spacing:.55em;text-shadow:0 0 22px #b7c0cb;opacity:0;transition:opacity 1s';
omenTitle.textContent='THE OMEN';document.body.appendChild(omenTitle);
const omenLight=new THREE.SpotLight(0xcbd5e5,85,30,Math.PI/7,.75,1.2);
omenLight.visible=false;scene.add(omenLight,omenLight.target);
const omenWaypoints=[
 [0,1.2,-34],[0,1.2,-26],[0,.06,-9],[0,.06,-6],
 [-6,.06,-6],[-7,.06,0],[-6,.06,6],[0,.06,7],
 [6,.06,6],[7,.06,0],[6,.06,-6],[0,.06,-7]
];
const omenStops=[{t:12,d:2.5},{t:23,d:3},{t:34,d:3.5},{t:47,d:4},{t:60,d:4.5}];
function stopShowcase(){
 showcaseMode=-1;showcaseTime=-1;showcaseFreeze=false;omenSlow=false;
 showcaseOverlay.style.opacity='0';showcaseFlash.style.opacity='0';showcaseGrayscale.style.opacity='0';
 omenVeil.style.opacity='0';omenTitle.style.opacity='0';omenLight.visible=false;
 if(entranceActor)entranceActor.object.rotation.set(0,0,0);
 showcaseButtons.forEach((b,i)=>b.textContent=showcaseNames[i]);
}
showcaseButtons.forEach((button,i)=>button.addEventListener('click',()=>{
 entranceTime=-1;epicEntranceTime=-1;slideEntranceTime=-1;
 stopTiny();stopProcession();resetStagePyro();
 for(const p of epicShards)p.mesh.visible=false;
 cinematicBlackout.style.opacity='0';
 stopShowcase();showcaseMode=i;showcaseTime=0;entranceBot.visible=true;
 if(entranceActor)entranceActor._entranceState=null;
 button.textContent='↻ RESTART '+showcaseNames[i];
}));
for(const b of [entranceButton,slowEntranceButton,slideEntranceButton,processionButton,tinyButton])b.addEventListener('click',stopShowcase);
function updateShowcase(dt){
 if(showcaseMode<0)return false;
 showcaseTime+=dt;
 const t=showcaseTime;
 const clamp=THREE.MathUtils.clamp,lerp=THREE.MathUtils.lerp;
 const smooth=u=>{u=clamp(u,0,1);return u*u*(3-2*u);};
 let pos,anim='movement.walk',face=Math.PI;
 showcaseFreeze=false;omenSlow=false;
 if(showcaseMode===0){
  const poses=[6.2,11.1,16.2,21.2];
  const freeze=poses.find(v=>t>=v&&t<v+.8);
  showcaseFreeze=freeze!==undefined;
  const walkTime=t-poses.reduce((n,v)=>n+Math.min(.8,Math.max(0,t-v)),0);
  const z=lerp(-34,-6,smooth(walkTime/22));
  const y=z< -26?1.2:z< -9?lerp(1.2,.06,(z+26)/17):.06;
  pos=new THREE.Vector3(Math.sin(t*.7)*.55,y,z);
  anim=showcaseFreeze?'movement.idle':'movement.walk';
  face=showcaseFreeze?Math.PI+(poses.indexOf(freeze)-1.5)*.28:Math.PI;
  const snap=poses.reduce((v,p)=>Math.max(v,Math.max(0,1-Math.abs(t-p-.15)/.16)),0);
  showcaseFlash.style.opacity=String(snap*.92);
  showcaseGrayscale.style.opacity=showcaseFreeze?'1':'0';
  showcaseOverlay.textContent=showcaseFreeze?'✦ PERFECT ✦':'';
  showcaseOverlay.style.opacity=showcaseFreeze?'.9':'0';
 }else{
  // Storytelling through restraint: a long circuit, pauses and slow-motion stares.
  const total=76;
  const paused=omenStops.find(stop=>t>=stop.t&&t<stop.t+stop.d);
  showcaseFreeze=!!paused;
  const effective=t-omenStops.reduce((sum,stop)=>sum+clamp(t-stop.t,0,stop.d),0);
  const walk=smooth(effective/58);
  const segments=omenWaypoints.length-1;
  const u=walk*segments,i=Math.min(segments-1,Math.floor(u)),f=u-i;
  pos=new THREE.Vector3(...omenWaypoints[i]).lerp(new THREE.Vector3(...omenWaypoints[i+1]),f);
  const aheadU=Math.min(segments,u+.05),ai=Math.min(segments-1,Math.floor(aheadU));
  const ahead=new THREE.Vector3(...omenWaypoints[ai]).lerp(new THREE.Vector3(...omenWaypoints[ai+1]),aheadU-ai);
  const d=ahead.sub(pos);
  if(d.lengthSq()>.000001)face=Math.atan2(-d.x,-d.z);
  if(paused)face+=Math.sin((t-paused.t)/paused.d*Math.PI)*.48;
  omenSlow=paused!==undefined||[9,20,32,44,57].some(v=>t>=v&&t<v+2);
  anim=showcaseFreeze?'movement.idle':'movement.walk';
  omenVeil.style.opacity=t<2?String(t*.36):t>total-3?String((total-t)/3*.7):'.7';
  omenTitle.style.opacity=t>2&&t<7?'1':t>65&&t<71?'.8':'0';
  omenLight.visible=true;
  omenLight.position.set(pos.x-2,pos.y+8,pos.z+1);
  omenLight.target.position.set(pos.x,pos.y+1.1,pos.z);
  // Low silver lighting follows him rather than lighting the whole arena.
  showcaseGrayscale.style.opacity=t>3?'.35':'0';
 }
 entranceBot.position.copy(pos);entranceBot.rotation.y=face;
 if(entranceActor){
  if(entranceActor._entranceState!==anim){
   try{entranceActor.play(anim,{fade:.35,restart:true});}catch(e){console.warn('Entrance animation unavailable',e);}
   entranceActor._entranceState=anim;
  }
  if(!showcaseFreeze)entranceActor.update(showcaseMode===1&&omenSlow?dt*.35:dt);
 }
 let eye,focus=pos.clone().add(new THREE.Vector3(0,1.45,0));
 if(showcaseMode===0){
  eye=showcaseFreeze?pos.clone().add(new THREE.Vector3(2.3,1.9,3.1)):pos.clone().add(new THREE.Vector3(Math.sin(t*.7)*3.6,1.9,5));
 }else if(t<10){
  eye=pos.clone().add(new THREE.Vector3(-4,1.2,6));focus.y+=.4;
 }else if(t<24){
  eye=pos.clone().add(new THREE.Vector3(5,.7,3.5));
 }else if(t<37){
  eye=new THREE.Vector3(-12,8,11);focus=pos.clone().add(new THREE.Vector3(0,1,0));
 }else if(t<50){
  eye=pos.clone().add(new THREE.Vector3(-3,1,5));focus.y+=.35;
 }else if(t<64){
  eye=new THREE.Vector3(0,15,13);
 }else{
  eye=pos.clone().add(new THREE.Vector3(3,1.3,4));
 }
 camera.position.lerp(eye,Math.min(1,dt*(showcaseMode===1?3.5:10)));
 camera.lookAt(focus);
 if(t>=(showcaseMode===0?28:76)){stopShowcase();entranceBot.visible=false;}
 return true;
}


/* v0.67: Arrogant jumbotron entrance with two towering close-formation bodyguards. */
const betterButton=document.createElement('button');
betterButton.textContent='😎 BETTER THAN YOU';
betterButton.type='button';
let betterTime=-1,betterPreviousFeed=false,betterLastCard=-1;
const betterGuards=[];
for(let i=0;i<2;i++){
 const group=new THREE.Group();group.name='TTW_BODYGUARD_'+i;group.visible=false;group.scale.setScalar(1.5);scene.add(group);
 let actor=null;
 if(wrestlerPack){
  try{actor=wrestlerPack.createWrestler('wrestler-'+(i===0?'07':'12'));group.add(actor.object);}
  catch(e){console.warn('Bodyguard wrestler unavailable',e);}
 }
 if(!actor){
  const mesh=new THREE.Mesh(new THREE.CapsuleGeometry(.42,1.2,8,10),new THREE.MeshStandardMaterial({color:i?0x222b3a:0x292a2d,roughness:.65}));
  mesh.position.y=1;group.add(mesh);
 }
 betterGuards.push({group,actor,state:''});
}
function stopBetter(){
 if(betterTime<0)return;
 betterTime=-1;betterLastCard=-1;
 for(const g of betterGuards){g.group.visible=false;g.state='';}
 if(entranceActor)entranceActor.object.rotation.set(0,0,0);
 if(betterPreviousFeed)setActionFeed(true);
 betterPreviousFeed=false;
 betterButton.textContent='😎 BETTER THAN YOU';
}
betterButton.addEventListener('click',()=>{
 entranceTime=-1;epicEntranceTime=-1;slideEntranceTime=-1;
 stopTiny();stopProcession();stopShowcase();
 resetStagePyro();for(const p of epicShards)p.mesh.visible=false;
 cinematicBlackout.style.opacity='0';
 stopBetter();
 betterPreviousFeed=actionFeedEnabled;
 if(actionFeedEnabled)setActionFeed(false);
 jumbotronCountdown=-1;
 betterTime=0;betterLastCard=-1;
 entranceBot.visible=false;
 if(entranceActor)entranceActor._entranceState=null;
 betterButton.textContent='😎 RESTART BETTER THAN YOU';
});
for(const b of [entranceButton,slowEntranceButton,slideEntranceButton,processionButton,tinyButton,...showcaseButtons])b.addEventListener('click',stopBetter);
function updateBetter(dt){
 if(betterTime<0)return false;
 betterTime+=dt;
 const t=betterTime;
 // The screen gets the opening line, then the punchline.
 const card=t<4?0:t<8?1:t<10?2:3;
 if(card!==betterLastCard){
  betterLastCard=card;
  if(card===0)setJumbotron("I'M BETTER","THAN YOU",['#07090e','#c5ced8']);
  if(card===1)setJumbotron('AND I','KNOW IT.',['#12131b','#e7bd65']);
  if(card===2)setJumbotron('','',['#05070b','#101722']);
  if(card===3)setJumbotron('TTW','THE MAIN EVENT',['#12151c','#8e98a8']);
 }
 // No giant particles. All the drama comes from the giant men and the slow approach.
 const u=THREE.MathUtils.clamp((t-9)/23,0,1);
 const p=u*u*(3-2*u);
 const z=THREE.MathUtils.lerp(-34,-7,p);
 const y=z< -26?1.2:z< -9?THREE.MathUtils.lerp(1.2,.06,(z+26)/17):.06;
 entranceBot.visible=t>=9;
 entranceBot.position.set(0,y,z);
 entranceBot.rotation.y=Math.PI;
 const state=t<9||t>32?'movement.idle':'movement.walk';
 if(entranceActor&&t>=9){
  if(entranceActor._entranceState!==state){
   try{entranceActor.play(state,{fade:.3,restart:true});}catch(e){console.warn('Main event clip',e);}
   entranceActor._entranceState=state;
  }
  entranceActor.update(dt);
 }
 for(let i=0;i<betterGuards.length;i++){
  const guard=betterGuards[i],g=guard.group;
  g.visible=t>=9.4;
  // Larger characters, shoulder-to-shoulder behind the star with only 0.9m of separation.
  const gz=THREE.MathUtils.lerp(-34,-7,Math.max(0,Math.min(1,(t-9.45)/23))**2*(3-2*Math.max(0,Math.min(1,(t-9.45)/23))));
  const gy=gz< -26?1.2:gz< -9?THREE.MathUtils.lerp(1.2,.06,(gz+26)/17):.06;
  g.position.set(i===0?-1.12:1.12,gy,gz-1.25);
  g.rotation.y=Math.PI;
  if(guard.actor&&g.visible){
   if(guard.state!==state){try{guard.actor.play(state,{fade:.25,restart:true});}catch(e){console.warn('Bodyguard clip',e);}guard.state=state;}
   guard.actor.update(dt);
   guard.actor.object.position.set(0,0,0);
  }
 }
 let eye,focus;
 if(t<8){
  // Pull back to reveal the enormous main screen at the end of the arena.
  const pull=THREE.MathUtils.clamp(t/7,0,1);
  eye=entranceV(THREE.MathUtils.lerp(0,5,pull),THREE.MathUtils.lerp(11,15,pull),THREE.MathUtils.lerp(-12,6,pull));
  focus=entranceV(0,9.4,-34.6);
 }else if(t<12){
  eye=entranceV(-9,4,-22);focus=entranceV(0,2,-33);
 }else if(t<19){
  eye=entranceV(0,2.4,z+7);focus=entranceV(0,y+1.5,z);
 }else if(t<25){
  eye=entranceV(5,2.2,z+4.8);focus=entranceV(0,y+1.5,z-1);
 }else if(t<32){
  eye=entranceV(-4,3.1,z+5.5);focus=entranceV(0,y+1.6,z);
 }else{
  eye=entranceV(0,2.2,0);focus=entranceV(0,1.7,-7);
 }
 camera.position.lerp(eye,Math.min(1,dt*6));
 camera.lookAt(focus);
 if(t>=37){stopBetter();entranceBot.visible=false;}
 return true;
}


/* TTW v0.68: A God Was Born, ten synchronised carriers beneath a living throne. */
const godButton=document.createElement('button');
godButton.type='button';godButton.textContent='👑 A GOD WAS BORN';
let godTime=-1,godLastCard=-1,godResumeFeed=false;
const godProcession=new THREE.Group();godProcession.name='TTW_GOD_PROCESSION';godProcession.visible=false;scene.add(godProcession);
const godWood=new THREE.MeshStandardMaterial({color:0x624126,roughness:.92,metalness:.04});
const godGold=new THREE.MeshStandardMaterial({color:0xb49a55,roughness:.35,metalness:.6});
const godPlatform=new THREE.Mesh(new THREE.BoxGeometry(2.9,.22,4.45),godWood);
godPlatform.position.y=3.18;godProcession.add(godPlatform);
for(const x of [-1.27,1.27]){
 const trim=new THREE.Mesh(new THREE.BoxGeometry(.12,.18,4.55),godGold);
 trim.position.set(x,3.22,0);godProcession.add(trim);
}
for(const z of [-2.12,2.12]){
 const trim=new THREE.Mesh(new THREE.BoxGeometry(2.75,.18,.12),godGold);
 trim.position.set(0,3.22,z);godProcession.add(trim);
}
const godCarriers=[];
for(let i=0;i<10;i++){
 const g=new THREE.Group();godProcession.add(g);
 const col=i%2,row=Math.floor(i/2);
 g.position.set(col===0?-.68:.68,0,(row-2)*.86);
 const cloth=new THREE.MeshStandardMaterial({color:i%2?0x413b38:0x594b3d,roughness:.9});
 const skin=new THREE.MeshStandardMaterial({color:[0xb57e59,0xc69a72,0x906347,0xd0a27c][i%4],roughness:.85});
 const torso=new THREE.Mesh(new THREE.CapsuleGeometry(.3,.8,4,8),cloth);torso.position.y=1.37;g.add(torso);
 const head=new THREE.Mesh(new THREE.SphereGeometry(.24,10,8),skin);head.position.y=2.19;g.add(head);
 const arms=[],legs=[];
 for(const side of [-1,1]){
  const arm=new THREE.Group();arm.position.set(side*.39,1.77,0);
  const upper=new THREE.Mesh(new THREE.CapsuleGeometry(.11,.7,3,6),skin);
  upper.position.y=.34;arm.add(upper);g.add(arm);arms.push(arm);
  const leg=new THREE.Group();leg.position.set(side*.17,.89,0);
  const lower=new THREE.Mesh(new THREE.CapsuleGeometry(.13,.55,3,6),cloth);
  lower.position.y=-.37;leg.add(lower);g.add(leg);legs.push(leg);
 }
 // The wooden beams visibly rest over the ten carriers' raised hands.
 const beam=new THREE.Mesh(new THREE.BoxGeometry(.4,.13,.65),godWood);
 beam.position.set(0,3.01,0);g.add(beam);
 godCarriers.push({g,arms,legs});
}
const godThrone=new THREE.Group();godThrone.position.set(0,3.32,0);godProcession.add(godThrone);
let godActor=null;
if(wrestlerPack){
 try{godActor=wrestlerPack.createWrestler('wrestler-03');godThrone.add(godActor.object);godActor.play('movement.idle',{fade:0});}
 catch(e){console.warn('God king wrestler fallback',e);}
}
if(!godActor){
 const body=new THREE.Mesh(new THREE.CapsuleGeometry(.39,1.2,6,10),new THREE.MeshStandardMaterial({color:0x202126,metalness:.4,roughness:.65}));
 body.position.y=1.05;godThrone.add(body);
 const head=new THREE.Mesh(new THREE.SphereGeometry(.29,12,8),new THREE.MeshStandardMaterial({color:0xd2a17d}));
 head.position.y=2.05;godThrone.add(head);
}
const godMantle=new THREE.Mesh(new THREE.BoxGeometry(1.5,.16,.5),godGold);
godMantle.position.set(0,2.12,.18);godThrone.add(godMantle);
function stopGod(){
 if(godTime<0)return;
 godTime=-1;godLastCard=-1;godProcession.visible=false;
 godThrone.position.set(0,3.32,0);godThrone.rotation.set(0,0,0);
 if(godResumeFeed)setActionFeed(true);
 godResumeFeed=false;godButton.textContent='👑 A GOD WAS BORN';
}
godButton.addEventListener('click',()=>{
 entranceTime=-1;epicEntranceTime=-1;slideEntranceTime=-1;
 stopTiny();stopProcession();stopShowcase();stopBetter();
 resetStagePyro();for(const p of epicShards)p.mesh.visible=false;
 cinematicBlackout.style.opacity='0';
 stopGod();
 godResumeFeed=actionFeedEnabled;
 if(actionFeedEnabled)setActionFeed(false);
 jumbotronCountdown=-1;godTime=0;godLastCard=-1;
 godThrone.position.set(0,3.32,0);godThrone.rotation.set(0,0,0);
 entranceBot.visible=false;godProcession.visible=false;
 godButton.textContent='👑 RESTART A GOD WAS BORN';
});
for(const b of [entranceButton,slowEntranceButton,slideEntranceButton,processionButton,tinyButton,betterButton,...showcaseButtons])b.addEventListener('click',stopGod);
function updateGod(dt){
 if(godTime<0)return false;
 godTime+=dt;const t=godTime;
 const card=t<3?0:t<7?1:t<10?2:3;
 if(card!==godLastCard){
  godLastCard=card;
  if(card===0)setJumbotron('A GOD','WAS BORN',['#050506','#b2a07c']);
  else if(card===1)setJumbotron('BOW','BEFORE HIM',['#0b0a09','#b99b58']);
  else if(card===2)setJumbotron('','',['#070707','#111111']);
  else setJumbotron('THE GOD KING','TTW',['#17120b','#d0b16b']);
 }
 godProcession.visible=t>=10;
 // All ten carry the same rigid structure, so nobody slips off the ramp.
 const u=THREE.MathUtils.clamp((t-10)/33,0,1);
 const smooth=u*u*(3-2*u);
 const z=THREE.MathUtils.lerp(-34,-7,smooth);
 const y=z< -26?1.2:z< -9?THREE.MathUtils.lerp(1.2,.06,(z+26)/17):.06;
 godProcession.position.set(0,y,z);
 godProcession.rotation.y=Math.PI;
 for(let i=0;i<godCarriers.length;i++){
  const c=godCarriers[i];
  // Marching legs are in unison; the platform and motionless king never bob.
  const step=Math.sin((t-10)*5.4+(i%2)*Math.PI);
  for(let j=0;j<2;j++){
   c.legs[j].rotation.x=t>=10&&t<43?step*(j===0?1:-1)*.32:0;
   c.arms[j].rotation.x=-.18;
  }
 }
 // He remains perfectly still until the carriers halt. Then he sprints
 // toward the near end of the platform and launches over the front rope.
 const dash=THREE.MathUtils.clamp((t-44)/2,0,1);
 const flight=THREE.MathUtils.clamp((t-46)/2.15,0,1);
 if(t<44){
  godThrone.position.set(0,3.32,0);
  godThrone.rotation.set(0,0,0);
 }else if(t<46){
  godThrone.position.set(0,3.32,-1.85*dash);
  godThrone.rotation.set(0,0,0);
 }else if(t<48.15){
  const arc=Math.sin(Math.PI*flight)*2.4;
  godThrone.position.set(0,THREE.MathUtils.lerp(3.32,1.14,flight)+arc,-1.85-5.3*flight);
  godThrone.rotation.x=-Math.sin(Math.PI*flight)*.28;
 }else{
  godThrone.position.set(0,1.14,-7.15);
  godThrone.rotation.set(0,0,0);
 }
 if(godActor){
  const kingState=t<44?'movement.idle':t<48.15?'movement.run':'movement.idle';
  if(godActor._godState!==kingState){
   try{godActor.play(kingState,{fade:.12,restart:true});}catch(e){console.warn('God king leap animation',e);}
   godActor._godState=kingState;
  }
  if(t>=44)godActor.update(dt);
 }
 let eye,focus;
 if(t<10){
  const pull=THREE.MathUtils.clamp(t/8,0,1);
  eye=entranceV(THREE.MathUtils.lerp(0,6,pull),THREE.MathUtils.lerp(11,15,pull),THREE.MathUtils.lerp(-12,4,pull));
  focus=entranceV(0,9.4,-34.6);
 }else if(t<17){
  // Reveal the marching feet first, then tilt up to the immobile ruler.
  const reveal=THREE.MathUtils.clamp((t-11)/5,0,1);
  eye=entranceV(3.3,1.05,z+6);
  focus=entranceV(0,y+.65+reveal*4.7,z);
 }else if(t<27){
  eye=entranceV(-5,3.1,z+7);focus=entranceV(0,y+4.6,z);
 }else if(t<37){
  eye=entranceV(6,5.2,z+9);focus=entranceV(0,y+4,z);
 }else if(t<44){
  eye=entranceV(0,2.1,4);focus=entranceV(0,y+4.3,z);
 }else if(t<46){
  eye=entranceV(5,4,-2);focus=entranceV(0,y+3.7,z+1.8);
 }else if(t<49){
  eye=entranceV(7,4,5);focus=godThrone.getWorldPosition(new THREE.Vector3()).add(new THREE.Vector3(0,1,0));
 }else{
  eye=entranceV(5,3,6);focus=entranceV(0,2,-.2);
 }
 camera.position.lerp(eye,Math.min(1,dt*4));
 camera.lookAt(focus);
 if(t>=54){stopGod();}
 return true;
}


/* TTW v0.70: The Convoy, an SUV arrival with animated door and retreat. */
const convoyButton=document.createElement('button');
convoyButton.type='button';convoyButton.textContent='🚙 THE CONVOY';
let convoyTime=-1;
const convoyCar=new THREE.Group();convoyCar.name='TTW_CONVOY_SUV';convoyCar.visible=false;scene.add(convoyCar);
const convoyPaint=new THREE.MeshStandardMaterial({color:0x39443c,metalness:.3,roughness:.63});
const convoyDark=new THREE.MeshStandardMaterial({color:0x10171b,metalness:.12,roughness:.3});
const convoySteel=new THREE.MeshStandardMaterial({color:0x9da4a2,metalness:.72,roughness:.3});
const convoyLights=new THREE.MeshBasicMaterial({color:0xe8e5c8});
function convoyBox(w,h,d,x,y,z,mat,parent=convoyCar){
 const mesh=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat);
 mesh.position.set(x,y,z);parent.add(mesh);return mesh;
}
convoyBox(2.45,.72,4.15,0,.98,0,convoyPaint);
convoyBox(2.16,.9,2.6,0,1.76,-.15,convoyPaint);
convoyBox(2.2,.19,2.8,0,2.26,-.15,convoyPaint);
convoyBox(2.19,.53,.045,0,1.82,1.17,convoyDark);
convoyBox(2.19,.53,.045,0,1.82,-1.45,convoyDark);
for(const side of [-1,1]){
 convoyBox(.045,.5,1.1,side*1.11,1.82,.2,convoyDark);
 convoyBox(.045,.5,1.05,side*1.11,1.82,-.94,convoyDark);
 for(const z of [-1.44,1.44]){
  const wheel=new THREE.Mesh(new THREE.CylinderGeometry(.48,.48,.32,16),new THREE.MeshStandardMaterial({color:0x151617,roughness:.95}));
  wheel.rotation.z=Math.PI/2;wheel.position.set(side*1.25,.54,z);convoyCar.add(wheel);
 }
 convoyBox(.24,.22,.18,side*.9,1.2,2.09,convoyLights);
 convoyBox(.26,.21,.15,side*.9,1.2,-2.09,new THREE.MeshBasicMaterial({color:0xbb3030}));
}
convoyBox(1.9,.34,.16,0,.96,2.12,convoySteel);
convoyBox(1.9,.34,.16,0,.96,-2.12,convoySteel);
const convoyDoorPivot=new THREE.Group();
convoyDoorPivot.position.set(-1.23,1.54,.75);convoyCar.add(convoyDoorPivot);
convoyBox(.08,1.08,1.1,0,0,-.55,convoyPaint,convoyDoorPivot);
convoyBox(.095,.39,.91,-.015,.29,-.55,convoyDark,convoyDoorPivot);
convoyBox(.12,.075,.18,-.09,-.1,-.4,convoySteel,convoyDoorPivot);
const convoyPassenger=new THREE.Group();convoyPassenger.visible=false;scene.add(convoyPassenger);
let convoyActor=null;
if(wrestlerPack){
 try{convoyActor=wrestlerPack.createWrestler('wrestler-05');convoyPassenger.add(convoyActor.object);}
 catch(e){console.warn('Convoy wrestler fallback',e);}
}
if(!convoyActor){
 const body=new THREE.Mesh(new THREE.CapsuleGeometry(.38,1.05,6,10),new THREE.MeshStandardMaterial({color:0x4a3430}));
 body.position.y=1.02;convoyPassenger.add(body);
 const head=new THREE.Mesh(new THREE.SphereGeometry(.28,10,8),new THREE.MeshStandardMaterial({color:0xd5a17a}));
 head.position.y=1.96;convoyPassenger.add(head);
}
function stopConvoy(){
 if(convoyTime<0)return;
 convoyTime=-1;convoyCar.visible=false;convoyPassenger.visible=false;
 convoyDoorPivot.rotation.y=0;convoyButton.textContent='🚙 THE CONVOY';
}
convoyButton.addEventListener('click',()=>{
 entranceTime=-1;epicEntranceTime=-1;slideEntranceTime=-1;
 stopTiny();stopProcession();stopShowcase();stopBetter();stopGod();
 resetStagePyro();for(const p of epicShards)p.mesh.visible=false;
 cinematicBlackout.style.opacity='0';
 stopConvoy();convoyTime=0;entranceBot.visible=false;
 convoyButton.textContent='🚙 RESTART THE CONVOY';
 if(convoyActor)convoyActor._convoyState=null;
});
for(const b of [entranceButton,slowEntranceButton,slideEntranceButton,processionButton,tinyButton,betterButton,godButton,...showcaseButtons])b.addEventListener('click',stopConvoy);
function updateConvoy(dt){
 if(convoyTime<0)return false;
 convoyTime+=dt;const t=convoyTime;
 const clamp=THREE.MathUtils.clamp,lerp=THREE.MathUtils.lerp;
 const smooth=p=>{p=clamp(p,0,1);return p*p*(3-2*p);};
 // Centered on the ramp, descending from stage height to arena floor.
 let z;
 if(t<13)z=lerp(-35,-8.1,smooth((t-2)/11));
 else if(t<25)z=-8.1;
 else z=lerp(-8.1,-36,smooth((t-25)/12));
 const y=z< -26?1.2:z< -9?lerp(1.2,.06,(z+26)/17):.06;
 convoyCar.visible=t>=2&&t<38;
 convoyCar.position.set(0,y,z);
 convoyCar.rotation.y=Math.PI;
 const doorOpen=smooth((t-14)/1.6)*(1-smooth((t-22)/1.3));
 convoyDoorPivot.rotation.y=-doorOpen*1.35;
 convoyPassenger.visible=t>=16.3;
 if(convoyPassenger.visible){
  const walk=smooth((t-16.3)/4.1);
  const x=lerp(-.6,-3.05,walk);
  const wz=lerp(-8.3,-5.7,walk);
  convoyPassenger.position.set(x,.06,wz);
  convoyPassenger.rotation.y=lerp(-Math.PI/2,Math.PI,walk);
  if(convoyActor){
   const state=t<20.4?'movement.walk':'movement.idle';
   if(convoyActor._convoyState!==state){
    try{convoyActor.play(state,{fade:.2,restart:true});}catch(e){console.warn('Convoy passenger animation',e);}
    convoyActor._convoyState=state;
   }
   convoyActor.update(dt);convoyActor.object.position.set(0,0,0);
  }
 }
 let eye,focus;
 if(t<7){eye=entranceV(-6,3.5,-16);focus=entranceV(0,2,z);}
 else if(t<13){eye=entranceV(4,2.8,z+9);focus=entranceV(0,y+1.4,z);}
 else if(t<20){eye=entranceV(-5,2.2,-3);focus=entranceV(-1.3,1.2,-8);}
 else if(t<25){eye=entranceV(-3,2.2,1);focus=entranceV(-2.5,1.3,-6);}
 else if(t<33){eye=entranceV(5,4,-2);focus=entranceV(0,y+1.2,z);}
 else{eye=entranceV(-6,2.4,-8);focus=entranceV(-2.5,1.3,-6);}
 camera.position.lerp(eye,Math.min(1,dt*5));
 camera.lookAt(focus);
 if(t>=40)stopConvoy();
 return true;
}


/* TTW v0.71: Seven distinct story-driven wrestling entrances. */
const storyNames=["⚰️ The Undertaker's Apprentice","📸 The Hollywood Superstar","👑 The King Who Refuses to Walk","👁️ The Invisible Opponent","👴 The Old Timer","👥 The Clone Army","🎬 The False Start"];
const storyButtons=storyNames.map(name=>{const b=document.createElement('button');b.type='button';b.textContent=name;return b;});
let storyMode=-1,storyTime=0,storyCard=-1,storySavedFeed=false;
const storyStage=new THREE.Group();scene.add(storyStage);
const storyMaterials={
 black:new THREE.MeshStandardMaterial({color:0x15141b,roughness:.88}),
 gray:new THREE.MeshStandardMaterial({color:0x68616a,roughness:.8}),
 skin:new THREE.MeshStandardMaterial({color:0xd3a17e,roughness:.85}),
 gold:new THREE.MeshStandardMaterial({color:0xc5a45a,metalness:.48,roughness:.4}),
 red:new THREE.MeshStandardMaterial({color:0x982c3d,roughness:.85}),
 wood:new THREE.MeshStandardMaterial({color:0x59402b,roughness:.9}),
 white:new THREE.MeshStandardMaterial({color:0xe9e5d8,roughness:.85}),
 blue:new THREE.MeshStandardMaterial({color:0x334f79,roughness:.8})
};
function storyBlock(parent,w,h,d,x,y,z,mat){
 const o=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat);
 o.position.set(x,y,z);parent.add(o);return o;
}
function storyPerson(parent,mat=storyMaterials.black,scale=1){
 const g=new THREE.Group();g.scale.setScalar(scale);parent.add(g);
 storyBlock(g,.75,1.08,.44,0,1.33,0,mat);
 const head=new THREE.Mesh(new THREE.SphereGeometry(.27,12,9),storyMaterials.skin);
 head.position.y=2.13;g.add(head);
 const arms=[],legs=[];
 for(const side of [-1,1]){
  const arm=new THREE.Group();arm.position.set(side*.49,1.77,0);
  storyBlock(arm,.22,.82,.24,0,-.38,0,mat);g.add(arm);arms.push(arm);
  const leg=new THREE.Group();leg.position.set(side*.2,.8,0);
  storyBlock(leg,.27,.78,.31,0,-.39,0,mat);g.add(leg);legs.push(leg);
 }
 return {g,arms,legs};
}
const storyActors=Array.from({length:12},(_,i)=>storyPerson(storyStage,[storyMaterials.black,storyMaterials.red,storyMaterials.gold,storyMaterials.gray,storyMaterials.blue][i%5]));
const storyCoffin=new THREE.Group();storyStage.add(storyCoffin);
storyBlock(storyCoffin,1.45,.65,3.2,0,.6,0,storyMaterials.wood);
const coffinLid=new THREE.Group();coffinLid.position.set(-.75,.94,0);storyCoffin.add(coffinLid);
storyBlock(coffinLid,1.45,.15,3.2,.75,0,0,storyMaterials.wood);
const storyCarpet=storyBlock(storyStage,2.8,.025,25,0,.045,-20,storyMaterials.red);
const storyCane=storyBlock(storyStage,.09,1.45,.09,-.6,.74,0,storyMaterials.wood);
const storyThrone=new THREE.Group();storyStage.add(storyThrone);
storyBlock(storyThrone,1.6,.3,1.4,0,.8,0,storyMaterials.gold);
storyBlock(storyThrone,1.6,1.6,.25,0,1.65,-.58,storyMaterials.gold);
for(const x of [-.83,.83])storyBlock(storyThrone,.19,.7,1.3,x,1.18,0,storyMaterials.wood);
const storyCameras=[];
for(let i=0;i<5;i++){
 const g=new THREE.Group();storyStage.add(g);
 storyBlock(g,.35,.27,.35,0,1.38,0,storyMaterials.gray);
 storyBlock(g,.22,.17,.24,0,1.48,.32,storyMaterials.black);
 storyCameras.push(g);
}
const storySign=storyBlock(storyStage,1.9,.78,.12,0,2.1,0,storyMaterials.white);
const storyText=document.createElement('canvas');storyText.width=512;storyText.height=256;
const storyCtx=storyText.getContext('2d');storyCtx.fillStyle='#f2eee0';storyCtx.fillRect(0,0,512,256);
storyCtx.fillStyle='#222';storyCtx.font='bold 48px sans-serif';storyCtx.textAlign='center';
storyCtx.fillText('WRONG',256,110);storyCtx.fillText('GUY!',256,172);
const storyTex=new THREE.CanvasTexture(storyText);
storySign.material=new THREE.MeshBasicMaterial({map:storyTex});
function storyPlace(a,x,z,y=0,rotation=Math.PI){
 a.g.position.set(x,y,z);a.g.rotation.y=rotation;a.g.visible=true;
}
function storyWalk(a,t,speed=6){
 const phase=Math.sin(t*speed);
 a.legs[0].rotation.x=phase*.37;a.legs[1].rotation.x=-phase*.37;
 a.arms[0].rotation.x=-phase*.24;a.arms[1].rotation.x=phase*.24;
}
function storyReset(){
 storyActors.forEach(a=>{a.g.visible=false;a.g.scale.setScalar(1);a.g.rotation.set(0,0,0);a.arms.forEach(v=>v.rotation.set(0,0,0));a.legs.forEach(v=>v.rotation.set(0,0,0));});
 storyCoffin.visible=false;coffinLid.rotation.z=0;
 storyCarpet.visible=false;storyThrone.visible=false;storySign.visible=false;storyCane.visible=false;
 storyCameras.forEach(g=>g.visible=false);
}
function stopStory(){
 if(storyMode<0)return;
 storyMode=-1;storyTime=0;storyCard=-1;storyReset();
 if(storySavedFeed)setActionFeed(true);
 storySavedFeed=false;
}
storyButtons.forEach((b,i)=>b.addEventListener('click',()=>{
 entranceTime=-1;epicEntranceTime=-1;slideEntranceTime=-1;
 stopTiny();stopProcession();stopShowcase();stopBetter();stopGod();stopConvoy();
 resetStagePyro();for(const p of epicShards)p.mesh.visible=false;
 cinematicBlackout.style.opacity='0';
 stopStory();storyMode=i;storyTime=0;storyCard=-1;
 storySavedFeed=actionFeedEnabled;if(actionFeedEnabled)setActionFeed(false);
 jumbotronCountdown=-1;entranceBot.visible=false;
}));
for(const b of [entranceButton,slowEntranceButton,slideEntranceButton,processionButton,tinyButton,betterButton,godButton,convoyButton,...showcaseButtons])b.addEventListener('click',stopStory);
function updateStory(dt){
 if(storyMode<0)return false;
 storyTime+=dt;const t=storyTime;
 const clamp=THREE.MathUtils.clamp,lerp=THREE.MathUtils.lerp;
 const ease=p=>{p=clamp(p,0,1);return p*p*(3-2*p);};
 const rampY=z=>z< -26?1.2:z< -9?lerp(1.2,.06,(z+26)/17):.06;
 const approach=p=>lerp(-34,-7,ease(p));
 storyReset();
 let eye=entranceV(5,4,-8),look=entranceV(0,2,-18);
 const card=Math.floor(t/5);
 if(card!==storyCard){
  storyCard=card;
  const title=["THE LAST RITE","THE HOLLYWOOD STAR","HIS MAJESTY","ALREADY HERE","THE OLD TIMER","WE ARE ONE","WRONG GUY"][storyMode];
  const sub=["THE COFFIN IS EMPTY","CAMERAS READY","DO NOT MAKE HIM WALK","LOOK BEHIND YOU","NEVER JUDGE A BOOK","WHICH ONE IS REAL?","TRY AGAIN"][storyMode];
  setJumbotron(title,sub,['#0a0a0d','#ab9973']);
 }
 if(storyMode===0){
  // Four pallbearers deliver a coffin. The reveal is empty; the wrestler is already in the crowd.
  storyCoffin.visible=true;
  const cz=approach((t-2)/17);storyCoffin.position.set(0,rampY(cz),cz);
  for(let i=0;i<4;i++){
   const x=i%2?1.15:-1.15,z=cz+(i<2?-1:1)*1.05;
   storyPlace(storyActors[i],x,z,rampY(z));if(t<19)storyWalk(storyActors[i],t);
  }
  if(t>=20)coffinLid.rotation.z=lerp(0,-1.5,ease((t-20)/3));
  if(t>=25){
   // Enter from the audience side, not the ramp.
   const z=lerp(12,3.1,ease((t-25)/8));
   storyPlace(storyActors[4],7,z,.06,-Math.PI/2);
   storyWalk(storyActors[4],t,8);
  }
  if(t<20){eye=entranceV(5,4,cz+8);look=entranceV(0,1.5,cz);}
  else if(t<25){eye=entranceV(2,2,-4);look=entranceV(0,1,-7);}
  else{eye=entranceV(11,3,7);look=entranceV(7,1.5,lerp(12,3,ease((t-25)/8)));}
 }else if(storyMode===1){
  // Paparazzi swarm the red carpet, star poses and takes a selfie.
  storyCarpet.visible=true;
  const z=approach((t-2)/19);storyPlace(storyActors[0],0,z,rampY(z));
  if(t<23)storyWalk(storyActors[0],t,5);
  for(let i=0;i<5;i++){
   const p=storyCameras[i];p.visible=true;
   p.position.set((i%2?1:-1)*(2.5+i*.27),rampY(z),z+[-2,-.4,1.5,3,4][i]);
   p.rotation.y=(i%2?-.7:.7);
   storyPlace(storyActors[i+1],p.position.x,p.position.z,p.position.y);
  }
  if(t>=23){storyActors[0].arms[0].rotation.x=-1.6;storyActors[0].arms[0].rotation.z=-.8;}
  eye=t<23?entranceV(-4,2.8,z+7):entranceV(1.4,2.5,-4);
  look=entranceV(0,rampY(z)+1.6,z);
 }else if(storyMode===2){
  // Four attendants carry the throne; the king refuses to get off at the ring.
  const z=approach((t-2)/18);storyThrone.visible=true;
  storyThrone.position.set(0,rampY(z)+1.3,z);
  storyPlace(storyActors[0],0,z,rampY(z)+2.18);
  storyActors[0].arms[0].rotation.z=-.7;
  for(let i=1;i<=4;i++){
   const x=i%2?-.9:.9,zz=z+(i<3?-1:1)*.55;
   storyPlace(storyActors[i],x,zz,rampY(z));
   storyActors[i].arms[0].rotation.z=-1.2;storyActors[i].arms[1].rotation.z=1.2;
   if(t<20)storyWalk(storyActors[i],t,5);
  }
  if(t>=22&&t<29){
   const struggle=Math.sin(t*8)*.13;
   storyThrone.position.y+=struggle;
   storyActors[1].g.rotation.z=struggle;storyActors[2].g.rotation.z=-struggle;
  }
  if(t>=30){storyActors[0].arms[1].rotation.z=1.5;storyActors[0].g.rotation.y=Math.PI+.2;}
  eye=t<22?entranceV(5,3,z+8):entranceV(-4,3,-3);
  look=entranceV(0,rampY(z)+2.4,z);
 }else if(storyMode===3){
  // Search the empty ramp and ring. Reveal wrestler behind the player.
  if(t>=18){
   const x=player.position.x+Math.sin(player.rotation.y)*2.3;
   const z=player.position.z+Math.cos(player.rotation.y)*2.3;
   storyPlace(storyActors[0],x,z,player.position.y-.97,player.rotation.y+Math.PI);
  }
  if(t<8){eye=entranceV(2,5,-10);look=entranceV(0,2,-34);}
  else if(t<18){eye=entranceV(8,5,7);look=entranceV(0,1.5,0);}
  else{eye=entranceV(player.position.x+5,3,player.position.z+5);look=entranceV(player.position.x,1.5,player.position.z);}
 }else if(storyMode===4){
  // Slow cane-assisted shuffle followed by an impossible athletic flip.
  const z=approach((t-2)/22);storyPlace(storyActors[0],0,z,rampY(z));
  if(t<25){storyActors[0].g.rotation.x=.3;storyWalk(storyActors[0],t,2.4);}
  storyCane.position.set(-.6,rampY(z)+.74,z+.2);storyCane.visible=t<25;
  if(t>=25&&t<28){
   const p=ease((t-25)/3);
   storyActors[0].g.rotation.x=p*Math.PI*2;
   storyActors[0].g.position.y=rampY(z)+Math.sin(Math.PI*p)*1.5;
  }
  if(t>=28){storyActors[0].g.rotation.x=0;storyActors[0].g.position.y=rampY(z);}
  eye=t<25?entranceV(3,2,z+5):entranceV(5,3,-3);look=entranceV(0,1.6,z);
 }else if(storyMode===5){
  // Eight identical wrestlers appear one by one, march together, turn in perfect sync.
  const z=approach((t-4)/20);
  for(let i=0;i<8;i++){
   if(t<2+i*.7)continue;
   const x=(i%4-1.5)*1.25,zz=z+Math.floor(i/4)*1.25;
   storyPlace(storyActors[i],x,zz,rampY(zz),t>=27?0:Math.PI);
   storyActors[i].g.scale.setScalar(1);
   if(t<27)storyWalk(storyActors[i],t,6);
   if(t>=27&&i===3){storyActors[i].g.rotation.y=Math.PI;storyActors[i].g.position.z=lerp(zz,1.5,ease((t-27)/7));}
   if(t>=27&&i!==3)storyActors[i].g.position.z=lerp(zz,-23,ease((t-27)/8));
  }
  eye=t<27?entranceV(6,4,z+9):entranceV(-7,5,-2);look=entranceV(0,2,z);
 }else if(storyMode===6){
  // First performer is publicly rejected; real headliner calmly passes him.
  const z1=t<15?approach((t-2)/12):lerp(-7,-34,ease((t-19)/9));
  storyPlace(storyActors[0],0,z1,rampY(z1),t>=19?0:Math.PI);
  if(t<15||t>=19)storyWalk(storyActors[0],t);
  if(t>=15&&t<19){
   storySign.visible=true;storySign.position.set(0,2.8,-8);
   storyActors[0].arms[0].rotation.z=1.2;
  }
  if(t>=24){
   const z2=approach((t-24)/12);
   storyPlace(storyActors[1],.8,z2,rampY(z2));storyWalk(storyActors[1],t,5);
  }
  eye=t<15?entranceV(5,3,z1+7):t<24?entranceV(-3,3,-3):entranceV(5,3,-12);
  look=t<24?entranceV(0,1.8,z1):entranceV(.8,1.8,approach((t-24)/12));
 }
 camera.position.lerp(eye,Math.min(1,dt*4));
 camera.lookAt(look);
 const duration=[38,32,36,27,33,37,40][storyMode];
 if(t>=duration)stopStory();
 return true;
}


/* TTW v0.72: The Magician, stage illusion, assistant, exploding box and ring reveal. */
const magicianButton=document.createElement('button');
magicianButton.type='button';magicianButton.textContent='🎩 THE MAGICIAN';
let magicianTime=-1,magicianCard=-1,magicianResumeFeed=false;
const magicStage=new THREE.Group();scene.add(magicStage);
const magicBlack=new THREE.MeshStandardMaterial({color:0x171023,roughness:.72});
const magicPurple=new THREE.MeshStandardMaterial({color:0x4e2079,roughness:.55,metalness:.25});
const magicGold=new THREE.MeshStandardMaterial({color:0xd7ad5a,metalness:.65,roughness:.35});
const magicSkin=new THREE.MeshStandardMaterial({color:0xd1a082,roughness:.85});
const magicWhite=new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:.55,depthWrite:false});
function magicBox(parent,w,h,d,x,y,z,mat){
 const o=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat);o.position.set(x,y,z);parent.add(o);return o;
}
function magicHuman(parent,coat,hat){
 const g=new THREE.Group();parent.add(g);
 magicBox(g,.77,1.06,.47,0,1.34,0,coat);
 magicBox(g,.22,.83,.25,-.5,1.35,0,coat);
 magicBox(g,.22,.83,.25,.5,1.35,0,coat);
 magicBox(g,.29,.81,.32,-.2,.43,0,magicBlack);
 magicBox(g,.29,.81,.32,.2,.43,0,magicBlack);
 const head=new THREE.Mesh(new THREE.SphereGeometry(.27,12,8),magicSkin);
 head.position.y=2.13;g.add(head);
 if(hat){
  const brim=new THREE.Mesh(new THREE.CylinderGeometry(.44,.44,.055,16),magicBlack);
  brim.position.y=2.46;g.add(brim);
  const top=new THREE.Mesh(new THREE.CylinderGeometry(.28,.28,.55,16),magicBlack);
  top.position.y=2.76;g.add(top);
  magicBox(g,.82,.1,.08,0,1.92,.3,magicGold);
 }
 return g;
}
const magician=magicHuman(magicStage,magicPurple,true);
const magicAssistant=magicHuman(magicStage,magicGold,false);
const magicCabinet=new THREE.Group();magicStage.add(magicCabinet);
magicBox(magicCabinet,2.0,.18,1.6,0,.17,0,magicGold);
magicBox(magicCabinet,.13,2.5,1.6,-1,1.47,0,magicPurple);
magicBox(magicCabinet,.13,2.5,1.6,1,1.47,0,magicPurple);
magicBox(magicCabinet,2.0,.16,1.6,0,2.77,0,magicGold);
magicBox(magicCabinet,2,.12,.12,0,1.65,-.8,magicGold);
const magicDoors=[];
for(const side of [-1,1]){
 const hinge=new THREE.Group();hinge.position.set(side*1,1.45,.82);magicCabinet.add(hinge);
 magicBox(hinge,.96,2.38,.09,-side*.48,0,0,magicPurple);
 magicBox(hinge,.08,2.18,.13,-side*.88,0,.04,magicGold);
 magicDoors.push({hinge,side});
}
const magicShards=[];
for(let i=0;i<20;i++){
 const shard=magicBox(magicStage,.25+(i%4)*.12,.12+(i%3)*.16,.12,0,0,0,i%3?magicPurple:magicGold);
 shard.visible=false;magicShards.push(shard);
}
const magicSmoke=[];
for(let i=0;i<32;i++){
 const material=magicWhite.clone();
 const puff=new THREE.Mesh(new THREE.SphereGeometry(.36+(i%4)*.13,8,6),material);
 puff.visible=false;magicStage.add(puff);magicSmoke.push(puff);
}
const magicSparks=[];
for(let i=0;i<28;i++){
 const spark=new THREE.Mesh(new THREE.BoxGeometry(.035,.24,.035),new THREE.MeshBasicMaterial({color:i%2?0xffd56e:0xffffff}));
 spark.visible=false;magicStage.add(spark);magicSparks.push(spark);
}
function stopMagician(){
 if(magicianTime<0)return;
 magicianTime=-1;magicianCard=-1;magicStage.visible=false;
 if(magicianResumeFeed)setActionFeed(true);
 magicianResumeFeed=false;
}
magicianButton.addEventListener('click',()=>{
 entranceTime=-1;epicEntranceTime=-1;slideEntranceTime=-1;
 stopTiny();stopProcession();stopShowcase();stopBetter();stopGod();stopConvoy();stopStory();
 resetStagePyro();for(const p of epicShards)p.mesh.visible=false;
 cinematicBlackout.style.opacity='0';
 stopMagician();magicianTime=0;magicianCard=-1;
 magicianResumeFeed=actionFeedEnabled;
 if(actionFeedEnabled)setActionFeed(false);
 jumbotronCountdown=-1;entranceBot.visible=false;magicStage.visible=true;
});
for(const b of [entranceButton,slowEntranceButton,slideEntranceButton,processionButton,tinyButton,betterButton,godButton,convoyButton,...storyButtons,...showcaseButtons])b.addEventListener('click',stopMagician);
function updateMagician(dt){
 if(magicianTime<0)return false;
 magicianTime+=dt;const t=magicianTime;
 const clamp=THREE.MathUtils.clamp,lerp=THREE.MathUtils.lerp;
 const ease=v=>{v=clamp(v,0,1);return v*v*(3-2*v);};
 magicStage.visible=true;
 const card=t<6?0:t<19?1:t<26?2:3;
 if(card!==magicianCard){
  magicianCard=card;
  if(card===0)setJumbotron('THE','MAGICIAN',['#1c1030','#cba3fa']);
  else if(card===1)setJumbotron('WATCH','CLOSELY',['#160e26','#b89aeb']);
  else if(card===2)setJumbotron('NOW YOU SEE ME','NOW YOU DON\'T',['#0c0816','#eee0ff']);
  else setJumbotron('TA-DA!','THE MAGICIAN',['#31184d','#e4b5ff']);
 }
 const magZ=-30.6;
 const walk=ease((t-2)/5);
 const stepIn=ease((t-13)/3);
 const inBox=t>=16&&t<26;
 const ring=t>=26;
 magician.visible=!inBox&&(t<22||ring);
 if(t<13)magician.position.set(lerp(-4.8,-1.9,walk),1.2,magZ);
 else if(t<16)magician.position.set(lerp(-1.9,0,stepIn),1.2,magZ);
 else if(ring)magician.position.set(0,1.2,0);
 else magician.position.set(0,1.2,magZ);
 magician.rotation.set(0,t>=26?0:Math.PI,0);
 if(t>=7&&t<13){
  magician.rotation.y=Math.PI+Math.sin((t-7)*1.4)*.6;
  magician.rotation.z=Math.sin((t-7)*2.2)*.09;
 }else magician.rotation.z=0;
 if(ring){
  magician.rotation.y=Math.PI*2*ease((t-26)/2);
  magician.rotation.z=t>29?.08:0;
 }
 magicAssistant.visible=t>=10&&t<26;
 magicAssistant.position.set(t<17?2.6:lerp(2.6,1.9,ease((t-17)/2)),1.2,magZ+.3);
 magicAssistant.rotation.y=Math.PI;
 magicCabinet.visible=t>=9&&t<25;
 magicCabinet.position.set(0,1.2,magZ);
 const door=ease((t-17)/1.4);
 for(const d of magicDoors)d.hinge.rotation.y=-d.side*(1-door)*1.4;
 for(let i=0;i<magicShards.length;i++){
  const o=magicShards[i];const age=t-22.7;
  o.visible=age>=0&&age<2.2;
  if(o.visible){
   const angle=i*2.39996;
   const distance=age*(2.1+(i%5)*.47);
   o.position.set(Math.cos(angle)*distance,2.4+Math.sin(i*3.7)*distance*.6+age*1.5-age*age*1.3,magZ+Math.sin(angle)*distance);
   o.rotation.set(age*(i%3+1)*3,age*(i%4+1)*2,age*4);
  }
 }
 for(let i=0;i<magicSmoke.length;i++){
  const o=magicSmoke[i];const inRing=i>=16;
  const start=inRing?25.7:22.4;
  const age=t-start-(i%4)*.06;
  o.visible=age>=0&&age<3.2;
  if(o.visible){
   const angle=i*2.39996;
   const radius=(.25+age*.68)*(1+(i%4)*.17);
   o.position.set(Math.cos(angle)*radius,(inRing?1.2:1.2)+.5+age*.55, (inRing?0:magZ)+Math.sin(angle)*radius);
   o.material.opacity=.65*(1-age/3.2);
   o.scale.setScalar(.5+age*.65);
  }
 }
 for(let i=0;i<magicSparks.length;i++){
  const o=magicSparks[i];
  const start=i<14?2:22.6;
  const age=t-start;
  o.visible=age>=0&&age<(i<14?5:1.7);
  if(o.visible){
   const angle=i*2.39996;
   const radius=i<14?2.9:1.7;
   o.position.set(Math.cos(angle)*radius,1.2+((age*(3+i%4)+i*.19)%3),magZ+Math.sin(angle)*radius);
   o.rotation.z=angle;
  }
 }
 let eye,look;
 if(t<7){eye=entranceV(-7,4,-22);look=entranceV(-2,3,magZ);}
 else if(t<13){eye=entranceV(3.5,2.7,-24);look=entranceV(-1.9,2.9,magZ);}
 else if(t<19){eye=entranceV(-4.5,3.1,-25);look=entranceV(0,2.5,magZ);}
 else if(t<24){eye=entranceV(4,3.3,-24);look=entranceV(0,2.5,magZ);}
 else if(t<26){eye=entranceV(6,5,-13);look=entranceV(0,2.2,magZ);}
 else if(t<29){eye=entranceV(7,4,7);look=entranceV(0,2,0);}
 else{eye=entranceV(4,2.6,5);look=entranceV(0,2.5,0);}
 camera.position.lerp(eye,Math.min(1,dt*5));
 camera.lookAt(look);
 if(t>=34)stopMagician();
 return true;
}


/* TTW v0.73: The Swinging Entrance, a suspended aerial ring arrival. */
const swingButton=document.createElement('button');
swingButton.type='button';swingButton.textContent='🪢 THE SWINGING ENTRANCE';
let swingTime=-1,swingResumeFeed=false,swingCard=-1;
const swingRig=new THREE.Group();scene.add(swingRig);
const swingPerson=new THREE.Group();swingRig.add(swingPerson);
let swingActor=null;
if(wrestlerPack){
 try{swingActor=wrestlerPack.createWrestler('wrestler-09');swingPerson.add(swingActor.object);}
 catch(e){console.warn('Swing entrance wrestler fallback',e);}
}
if(!swingActor){
 const suit=new THREE.MeshStandardMaterial({color:0x8b252c,roughness:.7});
 const skin=new THREE.MeshStandardMaterial({color:0xc89170,roughness:.8});
 const torso=new THREE.Mesh(new THREE.CapsuleGeometry(.36,.95,5,10),suit);torso.position.y=1.25;swingPerson.add(torso);
 const head=new THREE.Mesh(new THREE.SphereGeometry(.27,12,8),skin);head.position.y=2.1;swingPerson.add(head);
 for(const side of [-1,1]){
  const arm=new THREE.Mesh(new THREE.CapsuleGeometry(.12,.7,4,7),skin);
  arm.position.set(side*.47,1.88,0);arm.rotation.z=side*.45;swingPerson.add(arm);
  const leg=new THREE.Mesh(new THREE.CapsuleGeometry(.14,.7,4,7),suit);
  leg.position.set(side*.19,.55,0);swingPerson.add(leg);
 }
}
const swingRopeMaterial=new THREE.MeshStandardMaterial({color:0xc9b68a,roughness:1});
const swingRope=new THREE.Mesh(new THREE.CylinderGeometry(.052,.052,1,10),swingRopeMaterial);
swingRig.add(swingRope);
const swingGrip=new THREE.Mesh(new THREE.TorusGeometry(.25,.05,7,14),new THREE.MeshStandardMaterial({color:0x8b9299,metalness:.7,roughness:.4}));
swingGrip.rotation.x=Math.PI/2;swingRig.add(swingGrip);
const swingAnchor=new THREE.Vector3(-3.8,17,0);
const swingFrom=new THREE.Vector3(-16,7.3,0);
const swingRelease=new THREE.Vector3(-.6,5.2,0);
const swingLanding=new THREE.Vector3(0,1.2,0);
function stopSwing(){
 if(swingTime<0)return;
 swingTime=-1;swingCard=-1;swingRig.visible=false;
 if(swingResumeFeed)setActionFeed(true);
 swingResumeFeed=false;
}
swingButton.addEventListener('click',()=>{
 entranceTime=-1;epicEntranceTime=-1;slideEntranceTime=-1;
 stopTiny();stopProcession();stopShowcase();stopBetter();stopGod();stopConvoy();stopStory();stopMagician();
 resetStagePyro();for(const p of epicShards)p.mesh.visible=false;
 cinematicBlackout.style.opacity='0';
 stopSwing();swingTime=0;swingCard=-1;
 swingResumeFeed=actionFeedEnabled;if(actionFeedEnabled)setActionFeed(false);
 jumbotronCountdown=-1;entranceBot.visible=false;swingRig.visible=true;
 if(swingActor)swingActor._swingState='';
});
for(const b of [entranceButton,slowEntranceButton,slideEntranceButton,processionButton,tinyButton,betterButton,godButton,convoyButton,magicianButton,...storyButtons,...showcaseButtons])b.addEventListener('click',stopSwing);
function updateSwing(dt){
 if(swingTime<0)return false;
 swingTime+=dt;const t=swingTime;
 const clamp=THREE.MathUtils.clamp,lerp=THREE.MathUtils.lerp;
 const ease=v=>{v=clamp(v,0,1);return v*v*(3-2*v);};
 if(swingCard!==Math.floor(t/5)){
  swingCard=Math.floor(t/5);
  if(t<5)setJumbotron('HERE HE','COMES!',['#122333','#e0bb74']);
  else setJumbotron('THE','SWINGING ENTRANCE',['#1d2434','#d6b56d']);
 }
 let p;
 if(t<3)p=swingFrom.clone();
 else if(t<10){
  // Arc passes high above the outside ropes, descending toward ring centre.
  const u=ease((t-3)/7);
  p=swingFrom.clone().lerp(swingRelease,u);
  p.y=lerp(7.3,5.2,u)-Math.sin(Math.PI*u)*1.1;
 }else if(t<12.2){
  const u=ease((t-10)/2.2);
  p=swingRelease.clone().lerp(swingLanding,u);
  p.y+=Math.sin(Math.PI*u)*1.15;
 }else p=swingLanding.clone();
 swingPerson.position.copy(p);
 if(t<10){
  swingPerson.rotation.set(0,Math.PI/2,Math.sin(Math.PI*clamp((t-3)/7,0,1))*.17);
 }else if(t<12.2){
  swingPerson.rotation.set(-.22*Math.sin(Math.PI*(t-10)/2.2),0,0);
 }else swingPerson.rotation.set(0,0,0);
 // The rope is attached to the roof throughout the swing and releases in flight.
 const ropeEnd=p.clone().add(new THREE.Vector3(0,2.1,0));
 swingRope.visible=t<10;
 swingGrip.visible=t<10;
 if(t<10){
  const diff=swingAnchor.clone().sub(ropeEnd);
  swingRope.position.copy(swingAnchor).add(ropeEnd).multiplyScalar(.5);
  swingRope.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),diff.clone().normalize());
  swingRope.scale.set(1,diff.length(),1);
  swingGrip.position.copy(ropeEnd);
 }
 if(swingActor){
  const state=t<10?'movement.idle':t<12.2?'movement.run':'movement.idle';
  if(swingActor._swingState!==state){
   try{swingActor.play(state,{fade:.16,restart:true});}catch(e){console.warn('Swing animation',e);}
   swingActor._swingState=state;
  }
  swingActor.update(dt);
  swingActor.object.position.set(0,0,0);
 }
 let eye,look;
 if(t<3){eye=entranceV(7,10,14);look=entranceV(-12,8,0);}
 else if(t<9){eye=entranceV(8,6,9);look=p.clone().add(new THREE.Vector3(0,1,0));}
 else if(t<12.5){eye=entranceV(5,4,6);look=p.clone().add(new THREE.Vector3(0,1,0));}
 else{eye=entranceV(3.5,2.5,5);look=entranceV(0,2.2,0);}
 camera.position.lerp(eye,Math.min(1,dt*5));
 camera.lookAt(look);
 if(t>=18)stopSwing();
 return true;
}

// Retired theatrical entrance sets must never remain visible in the playable ring.
// Keep their source for later editing, but remove their props from the scene entirely.
stopMagician();
storyReset();
magicStage.visible=false;
scene.remove(magicStage);
scene.remove(storyStage);
stopSwing();swingRig.visible=false;scene.remove(swingRig);
stopGod();godProcession.visible=false;scene.remove(godProcession);
stopConvoy();
stopTiny();
stopProcession();
stopShowcase();
stopBetter();
// Single compact, scrollable entrance selector for desktop and mobile.
const scenesButton=document.createElement('button');
scenesButton.textContent='🎬 SCENES ▾';
scenesButton.type='button';
scenesButton.setAttribute('aria-expanded','false');
scenesButton.style.cssText='position:fixed;top:58px;left:16px;z-index:17;padding:11px 16px;background:#763c91;color:white;border:1px solid #dfb7ff;border-radius:9px;font:700 13px system-ui;cursor:pointer;box-shadow:0 4px 16px #0008';
document.body.appendChild(scenesButton);
const scenesMenu=document.createElement('div');
scenesMenu.style.cssText='position:fixed;top:106px;left:16px;z-index:18;width:min(300px,calc(100vw - 32px));max-height:min(52vh,390px);overflow-y:auto;overscroll-behavior:contain;background:#151c2df5;border:1px solid #8d73a7;border-radius:11px;padding:8px;box-shadow:0 12px 30px #000b;display:none';
document.body.appendChild(scenesMenu);
function closeScenesMenu(){scenesMenu.style.display='none';scenesButton.setAttribute('aria-expanded','false');scenesButton.textContent='🎬 SCENES ▾';}
scenesButton.addEventListener('click',()=>{
 const open=scenesMenu.style.display!=='none';
 scenesMenu.style.display=open?'none':'flex';
 scenesMenu.style.flexDirection='column';
 scenesMenu.style.gap='7px';
 scenesButton.setAttribute('aria-expanded',String(!open));
 scenesButton.textContent=open?'🎬 SCENES ▾':'🎬 SCENES ▴';
});
// Keep only straightforward stage/ramp entrances. Experimental ring-prop scenes are retired.
for(const [button,title] of [
 [entranceButton,'🎬 Bot Entrance'],
 [slowEntranceButton,'✨ Epic Walk Entrance'],
 [slideEntranceButton,'🏃 Run & Slide Entrance']
]){
 button.textContent=title;
 button.style.cssText='position:relative;inset:auto;top:auto;left:auto;width:100%;flex:none;text-align:left;z-index:auto;padding:13px 12px;background:#30324c;color:#fff;border:1px solid #656987;border-radius:8px;font:700 13px system-ui;cursor:pointer';
 scenesMenu.appendChild(button);
 button.addEventListener('click',()=>{closeScenesMenu();button.textContent=title;});
}
document.addEventListener('pointerdown',e=>{
 if(scenesMenu.style.display!=='none'&&!scenesMenu.contains(e.target)&&!scenesButton.contains(e.target))closeScenesMenu();
});

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
 if(playerHP>0&&!grappleMove&&!traversal&&ropeMovementLock<=0&&Math.abs(inputX)+Math.abs(inputZ)>.001){
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

 if(playerHP>0&&!grappleMove&&!traversal&&ropeBounceDelay<=0&&ropeRecoilTime>0){
  ropeRecoilTime=Math.max(0,ropeRecoilTime-dt);
  const amount=dt*(ropeRecoilTime/.28);
  const nx=player.position.x+ropeRecoil.x*amount,nz=player.position.z+ropeRecoil.z*amount;
  if(!blockedByArena(nx,nz,player.position.y)){player.position.x=nx;player.position.z=nz;}
 }
 updateTraversal(dt);
 updatePowerbomb(dt);
 if(contextMessageUntil&&performance.now()>contextMessageUntil){contextMessage.style.display='none';contextMessageUntil=0;}
 if(playerPunchImpact>=0){playerPunchImpact-=dt;if(playerPunchImpact<0&&playerHP>0){if(botMode)hitSparringBot(activeAttack);else if(remoteConnected)sendNetwork({type:'punch',move:activeAttack,momentum:ropeSpeedMultiplier});}}
 combatTick(dt);
 if(loadedWrestler){
  if(punchRemaining>0)punchRemaining=Math.max(0,punchRemaining-dt);
  hitReactionTime=Math.max(0,hitReactionTime-dt);
  const nextAnimation=grappleMove?'throws.powerbomb-attacker':playerHP<=0?'fall':traversal?'idle':hitReactionTime>0?hitReaction:punchRemaining>0?activeAttack:ropeAnimationTime>ropeReboundDuration?'ropeLean':ropeAnimationTime>0?'ropeRebound':isWalking?'run':'idle';
  if(loadedWrestler._ttwState!==nextAnimation){
   playTTWAnimation(loadedWrestler,nextAnimation,.2);
   loadedWrestler._ttwState=nextAnimation;
  }
  loadedWrestler.update(dt);
  keepWrestlerAtHitbox(loadedWrestler);
  if(grappleMove&&remoteWrestler){remoteWrestler.update(dt);keepWrestlerAtHitbox(remoteWrestler);}
 }
 target.lerp(new THREE.Vector3(player.position.x,player.position.y+1.25,player.position.z),Math.min(1,dt*6));
 const cinematicActive=swingTime>=0?updateSwing(dt):magicianTime>=0?updateMagician(dt):storyMode>=0?updateStory(dt):convoyTime>=0?updateConvoy(dt):godTime>=0?updateGod(dt):betterTime>=0?updateBetter(dt):showcaseMode>=0?updateShowcase(dt):tinyTime>=0?updateTiny(dt):processionTime>=0?updateProcession(dt):slideEntranceTime>=0?updateSlideEntrance(dt):epicEntranceTime>=0?updateEpicEntrance(dt):updateEntrance(dt);
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
