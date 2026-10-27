import * as THREE from 'three';
import { loadArena } from './assets/wrestling-arena/arena-loader.js';
import { loadWrestler } from './assets/ttw-master-wrestler/loader.js';

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
let loadedWrestler=null;
let remoteWrestler=null;
try{
 loadedWrestler=await loadWrestler('./assets/ttw-master-wrestler/wrestler.json');
 console.info('TTW: Claude master wrestler loaded');
 remoteWrestler=await loadWrestler('./assets/ttw-master-wrestler/wrestler.json');
}catch(error){console.error('TTW wrestler asset failed:',error);}

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
function registerRopeBounce(inward){
 ropeSpeedMultiplier*=1.10;
 ropeFacingTime=.38;
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
 loadedWrestler.play('idle');
}
// Two-player online test: state is relayed through the companion WebSocket server.
const remote=new THREE.Group();remote.name='TTW_REMOTE_PLAYER';remote.visible=false;remote.position.set(1.5,1.2,0);
if(remoteWrestler){remote.add(remoteWrestler.object);remoteWrestler.play('idle');remoteWrestler._ttwState='idle';}
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
   if(m.hit==='self')showDamage(player.position,'-11','#ff6969');
   if(m.hit==='other')showDamage(remote.position,'-11','#ffdf55');
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
  if(remoteWrestler._ttwState!==state){remoteWrestler.play(state,{fade:.12});remoteWrestler._ttwState=state;}
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
 ropeFacingTime=Math.max(0,ropeFacingTime-dt);
 updateRopes(dt);
 if(!document.getElementById('home').hidden){camera.position.set(22,20,22);camera.lookAt(target);renderer.render(scene,camera);return;}
 let isWalking=false;
 const keyboardX=Number(heldKeys.has('KeyD'))-Number(heldKeys.has('KeyA'));
 const keyboardZ=Number(heldKeys.has('KeyS'))-Number(heldKeys.has('KeyW'));
 const inputX=keyboardX||keyboardZ?keyboardX:movement.active?movement.x:0;
 const inputZ=keyboardX||keyboardZ?keyboardZ:movement.active?movement.y:0;
 const sprint=heldKeys.has('ShiftLeft')||heldKeys.has('ShiftRight');
 if(playerHP>0&&Math.abs(inputX)+Math.abs(inputZ)>.001){
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

 if(playerHP>0&&ropeRecoilTime>0){
  ropeRecoilTime=Math.max(0,ropeRecoilTime-dt);
  const amount=dt*(ropeRecoilTime/.28);
  const nx=player.position.x+ropeRecoil.x*amount,nz=player.position.z+ropeRecoil.z*amount;
  if(!blockedByArena(nx,nz,player.position.y)){player.position.x=nx;player.position.z=nz;}
 }
 if(playerPunchImpact>=0){playerPunchImpact-=dt;if(playerPunchImpact<0&&remoteConnected&&playerHP>0)sendNetwork({type:'punch'});}
 combatTick(dt);
 if(loadedWrestler){
  if(punchRemaining>0)punchRemaining=Math.max(0,punchRemaining-dt);
  const nextAnimation=playerHP<=0?'fall':punchRemaining>0?'punch':isWalking?'run':'idle';
  if(loadedWrestler._ttwState!==nextAnimation){
   loadedWrestler.play(nextAnimation,{fade:.2});
   loadedWrestler._ttwState=nextAnimation;
  }
  loadedWrestler.update(dt);
 }
 target.lerp(new THREE.Vector3(player.position.x,player.position.y+1.25,player.position.z),Math.min(1,dt*6));
 camera.position.set(
 target.x+Math.sin(yaw)*Math.cos(pitch)*distance,
 target.y+Math.sin(pitch)*distance,
 target.z+Math.cos(yaw)*Math.cos(pitch)*distance
 );
 // Aim below the wrestler so the character is framed in the centre of the gameplay view.
 camera.lookAt(target.x,target.y-2.7,target.z);
 renderer.render(scene,camera);
});
