// Lightweight polygonal stage pyrotechnics for the opening three seconds.
const pyroGroup=new THREE.Group();scene.add(pyroGroup);
const pyroBursts=[];
for(const x of [-8,-5,-2,2,5,8]){
 const group=new THREE.Group();group.position.set(x,1.25,-27.1);pyroGroup.add(group);
 const shards=[];
 for(let j=0;j<13;j++){
  const material=new THREE.MeshBasicMaterial({color:j%3===0?0xffffff:j%2?0xff9b20:0xffdb43,transparent:true,opacity:0,depthWrite:false,side:THREE.DoubleSide});
  const mesh=new THREE.Mesh(new THREE.ConeGeometry(.15,.9,3),material);
  group.add(mesh);
  const angle=(j/13)*Math.PI*2;
  shards.push({mesh,velocity:entranceV(Math.cos(angle)*(1+j%3),3+(j%4),Math.sin(angle)*(1+j%3)),phase:(j%4)*.12});
 }
 pyroBursts.push(shards);
}
function resetStagePyro(){for(const shards of pyroBursts)for(const s of shards){s.mesh.visible=false;s.mesh.material.opacity=0;}}
function updateStagePyro(t,dt){
 for(let i=0;i<pyroBursts.length;i++)for(const s of pyroBursts[i]){
  const age=t-(i%2)*.35-s.phase;
  const active=age>=0&&age<2.2;
  s.mesh.visible=active;
  if(active){
   s.mesh.position.copy(s.velocity).multiplyScalar(age);
   s.mesh.position.y-=2.5*age*age;
   s.mesh.rotation.z=age*4;
   s.mesh.scale.setScalar(1+age*.6);
   s.mesh.material.opacity=Math.min(1,age*6)*Math.max(0,1-age/2.2);
  }
 }
}
const entranceKeyframes=[
 {t:0,x:0,y:1.2,z:-37.5,anim:'movement.idle',face:0},
 {t:2.5,x:0,y:1.2,z:-31,anim:'movement.walk',face:Math.PI},
 {t:5.5,x:-7,y:1.2,z:-29.5,anim:'movement.walk',face:Math.PI/2},
 {t:7.5,x:-7,y:1.2,z:-29.5,anim:'movement.idle',face:-Math.PI/2},
 {t:10,x:-7,y:1.2,z:-29.5,anim:'movement.idle',face:-Math.PI/2},
 {t:13,x:7,y:1.2,z:-29.5,anim:'movement.walk',face:-Math.PI/2},
 {t:15,x:7,y:1.2,z:-29.5,anim:'movement.idle',face:Math.PI/2},
 {t:18,x:7,y:1.2,z:-29.5,anim:'movement.idle',face:Math.PI/2},
 {t:20,x:0,y:1.2,z:-29,anim:'movement.walk',face:Math.PI},
 {t:23,x:0,y:.8,z:-18,anim:'movement.run',face:Math.PI},
 {t:26,x:0,y:.06,z:-9,anim:'movement.run',face:Math.PI},
 {t:28,x:0,y:.06,z:-6,anim:'movement.run',face:Math.PI},
 {t:30,x:0,y:.06,z:-6,anim:'movement.idle',face:Math.PI}
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
 entranceTime=0;entranceBot.visible=false;
 resetStagePyro();
 entranceBot.position.set(0,1.2,-37.5);entranceBot.rotation.y=Math.PI;
 if(entranceActor){entranceActor._entranceState=null;entranceActor.play('movement.idle',{fade:.15,restart:true});}
 entranceButton.textContent='🎬 RESTART ENTRANCE';
});
function updateEntrance(dt){
 if(entranceTime<0)return false;
 entranceTime=Math.min(entranceDuration,entranceTime+dt);
 const t=entranceTime,pose=entrancePose(t);
 updateStagePyro(t,dt);
 entranceBot.visible=t>=3;
 entranceBot.position.copy(pose.pos);
 // Look outward during each crowd acknowledgement, face the direction of travel otherwise.
 if(t>=8.5&&t<13)entranceBot.rotation.y=Math.PI/2;
 else if(t>=16&&t<21)entranceBot.rotation.y=-Math.PI/2;
 else{
  const ahead=entrancePose(Math.min(entranceDuration,t+.05)).pos;
  if(ahead.distanceToSquared(pose.pos)>.00001)
   entranceBot.rotation.y=Math.atan2(-(ahead.x-pose.pos.x),-(ahead.z-pose.pos.z))+Math.PI;
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
 if(t<3){ // stage pyro before entrance
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
  // Frame the face from directly in front of the player's actual facing direction.
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
 const cinematicActive=updateEntrance(dt);
 if(!cinematicActive){
 camera.position.set(
 target.x+Math.sin(yaw)*Math.cos(pitch)*distance,
 target.y+Math.sin(pitch)*distance,
 target.z+Math.cos(yaw)*Math.cos(pitch)*distance
 );
 // Aim below the wrestler so the character is framed in the centre of the gameplay view.
 camera.lookAt(target.x,target.y-2.7,target.z);
 }
 renderer.render(scene,camera);
});
const entranceKeyframes=[
 {t:0,x:0,y:1.2,z:-37.5,anim:'movement.idle',face:0},
 {t:2.5,x:0,y:1.2,z:-31,anim:'movement.walk',face:Math.PI},
 {t:5.5,x:-7,y:1.2,z:-29.5,anim:'movement.walk',face:Math.PI/2},
 {t:7.5,x:-7,y:1.2,z:-29.5,anim:'movement.idle',face:-Math.PI/2},
 {t:10,x:-7,y:1.2,z:-29.5,anim:'movement.idle',face:-Math.PI/2},
 {t:13,x:7,y:1.2,z:-29.5,anim:'movement.walk',face:-Math.PI/2},
 {t:15,x:7,y:1.2,z:-29.5,anim:'movement.idle',face:Math.PI/2},
 {t:18,x:7,y:1.2,z:-29.5,anim:'movement.idle',face:Math.PI/2},
 {t:20,x:0,y:1.2,z:-29,anim:'movement.walk',face:Math.PI},
 {t:23,x:0,y:.8,z:-18,anim:'movement.run',face:Math.PI},
 {t:26,x:0,y:.06,z:-9,anim:'movement.run',face:Math.PI},
 {t:28,x:0,y:.06,z:-6,anim:'movement.run',face:Math.PI},
 {t:30,x:0,y:.06,z:-6,anim:'movement.idle',face:Math.PI}
];
const entranceDuration=30;
const entranceV=(x,y,z)=>new THREE.Vector3(x,y,z);
function entrancePose(t){
 const i=Math.max(0,entranceKeyframes.findIndex((k,j)=>j>0&&t<=k.t)-1);
 const a=entranceKeyframes[i],b=entranceKeyframes[Math.min(i+1,entranceKeyframes.length-1)];
 const p=a===b?0:THREE.MathUtils.clamp((t-a.t)/(b.t-a.t),0,1);
 const pos=entranceV(THREE.MathUtils.lerp(a.x,b.x,p),THREE.MathUtils.lerp(a.y,b.y,p),THREE.MathUtils.lerp(a.z,b.z,p));
 // Destination keyframe specifies movement type for each segment.
 const moving=pos.distanceToSquared(entranceV(b.x,b.y,b.z))>.00001;
 const anim=moving?(b.anim==='movement.run'?'movement.run':'movement.walk'):'movement.idle';
 return {pos,anim,face:b.face};
}
entranceButton.addEventListener('click',()=>{
 entranceTime=0;entranceBot.visible=true;
 entranceBot.position.set(0,1.2,-37.5);entranceBot.rotation.y=Math.PI;
 if(entranceActor){entranceActor._entranceState=null;entranceActor.play('movement.walk',{fade:.15,restart:true});}
 entranceButton.textContent='🎬 RESTART ENTRANCE';
});
function updateEntrance(dt){
 if(entranceTime<0)return false;
 entranceTime=Math.min(entranceDuration,entranceTime+dt);
 const t=entranceTime,pose=entrancePose(t);
 entranceBot.position.copy(pose.pos);
 // Look outward during each crowd acknowledgement, face the direction of travel otherwise.
 if(t>=5.5&&t<10)entranceBot.rotation.y=-Math.PI/2;
 else if(t>=13&&t<18)entranceBot.rotation.y=Math.PI/2;
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
 if(t<2.5){ // curtain reveal
  eye=entranceV(-5,3.2,-28);focus=pose.pos.clone().add(entranceV(0,1.1,0));
 }else if(t<5.5){ // track left across stage
  eye=pose.pos.clone().add(entranceV(-2.5,2.2,5.5));focus=pose.pos.clone().add(entranceV(0,1.2,0));
 }else if(t<7.5){ // wrestler acknowledges left crowd
  eye=entranceV(-11,3.3,-25);focus=pose.pos.clone().add(entranceV(0,1.2,0));
 }else if(t<10){ // panoramic right-side audience, independent of wrestler
  const p=(t-7.5)/2.5;
  eye=entranceV(8+p*10,5.5,-16+p*3);
  focus=entranceV(22+p*9,5,-17+p*7);
 }else if(t<13){ // cross stage to the right
  eye=pose.pos.clone().add(entranceV(2.8,2.4,5.2));focus=pose.pos.clone().add(entranceV(0,1.2,0));
 }else if(t<15){ // look out over right-side crowd
  eye=entranceV(11,3.1,-25);focus=pose.pos.clone().add(entranceV(0,1.2,0));
 }else if(t<18){ // close-up of the human player already in the ring
  eye=player.position.clone().add(entranceV(1.4,1.9,2.7));
  focus=player.position.clone().add(entranceV(0,1.3,0));
 }else if(t<20){ // dramatic low-angle stage departure
  eye=entranceV(-3,1.5,-23);focus=pose.pos.clone().add(entranceV(0,1.1,0));
 }else if(t<22){ // head-on tracking run
  eye=pose.pos.clone().add(entranceV(0,1.6,5.5));focus=pose.pos.clone().add(entranceV(0,1.1,0));
 }else if(t<24){ // sweeping side shot
  eye=pose.pos.clone().add(entranceV(-6,3.4,1));focus=pose.pos.clone().add(entranceV(0,1.1,0));
 }else if(t<26){ // high angle looking down the ramp
  eye=pose.pos.clone().add(entranceV(4.5,8,4));focus=pose.pos.clone().add(entranceV(0,1,0));
 }else{ // ringside finish
  eye=entranceV(-6,3.6,2);focus=pose.pos.clone().add(entranceV(0,1.1,0));
 }
 camera.position.lerp(eye,Math.min(1,dt*12));
 camera.lookAt(focus);
 if(t>=entranceDuration){entranceTime=-1;entranceButton.textContent='🎬 BOT ENTRANCE';}
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
 const cinematicActive=updateEntrance(dt);
 if(!cinematicActive){
 camera.position.set(
 target.x+Math.sin(yaw)*Math.cos(pitch)*distance,
 target.y+Math.sin(pitch)*distance,
 target.z+Math.cos(yaw)*Math.cos(pitch)*distance
 );
 // Aim below the wrestler so the character is framed in the centre of the gameplay view.
 camera.lookAt(target.x,target.y-2.7,target.z);
 }
 renderer.render(scene,camera);
});
