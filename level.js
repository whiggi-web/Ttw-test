import * as THREE from 'three';

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

// Temporary player capsule. This is independent of the future wrestling arena asset.
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

let yaw=Math.PI/4,pitch=.6,distance=31;
const target=new THREE.Vector3(0,0,0);
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
  pitch=THREE.MathUtils.clamp(pitch+(e.clientY-prev.y)*.006,.15,1.35);
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
 if(!document.getElementById('home').hidden){camera.position.set(22,20,22);camera.lookAt(target);renderer.render(scene,camera);return;}
 if(movement.active){
  const inputX=movement.x,inputZ=movement.y;
  const forward=new THREE.Vector3(-Math.sin(yaw),0,-Math.cos(yaw));
  const right=new THREE.Vector3(Math.cos(yaw),0,-Math.sin(yaw));
  const move=right.multiplyScalar(inputX).add(forward.multiplyScalar(-inputZ));
  if(move.lengthSq()>.0001){
   move.clampLength(0,1);
   player.position.addScaledVector(move,5*dt);
   player.position.x=THREE.MathUtils.clamp(player.position.x,-7.65,7.65);
   player.position.z=THREE.MathUtils.clamp(player.position.z,-7.65,7.65);
   player.rotation.y=Math.atan2(-move.x,-move.z);
  }
 }

 camera.position.set(
 target.x+Math.sin(yaw)*Math.cos(pitch)*distance,
 target.y+1+Math.sin(pitch)*distance,
 target.z+Math.cos(yaw)*Math.cos(pitch)*distance
 );
 camera.lookAt(target);
 renderer.render(scene,camera);
});
