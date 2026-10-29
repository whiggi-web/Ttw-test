import { DurableObject } from "cloudflare:workers";

const ATTACKS = {
 punch:[11,.7,"reactions.hit-front"], jab:[7,.48,"reactions.hit-front"],
 hook:[13,.8,"reactions.hit-left"], uppercut:[16,.95,"reactions.knocked-back"],
 kick:[15,1,"reactions.hit-kick"], clothesline:[18,1.1,"reactions.hit-clothesline"]
};
const allowedAnimations=new Set(["idle","run","punch","jab","hook","uppercut","kick","clothesline","fall","eliminations.thrown-over-top"]);
const send=(ws,msg)=>{try{ws.send(JSON.stringify(msg));}catch{}};
const forward=(angle)=>[-Math.sin(angle),-Math.cos(angle)];
const dot=(a,b)=>a[0]*b[0]+a[1]*b[1];

export class TTWRoom extends DurableObject {
 constructor(ctx,env){super(ctx,env);this.players=new Map();this.lastHits=new Map();this.locks=new Map();
  for(const ws of ctx.getWebSockets()){const info=ws.deserializeAttachment();if(info?.slot)this.players.set(ws,info);}
 }
 broadcast(msg,except=null){for(const ws of this.players.keys())if(ws!==except)send(ws,msg);}
 async fetch(request){
  if(request.headers.get("Upgrade")?.toLowerCase()!=="websocket")return new Response("WebSocket required",{status:426});
  const pair=new WebSocketPair();const client=pair[0],server=pair[1];
  this.ctx.acceptWebSocket(server);return new Response(null,{status:101,webSocket:client});
 }
 async webSocketMessage(ws,raw){
  if(typeof raw!=="string"||raw.length>4096)return;
  let data;try{data=JSON.parse(raw);}catch{return;}
  if(!data||typeof data!=="object")return;
  let p=this.players.get(ws);
  if(!p){
   if(data.type!=="join")return;
   if(this.players.size>=4){send(ws,{type:"full"});ws.close(1000,"Room full");return;}
   const used=new Set([...this.players.values()].map(v=>v.slot));const slot=[1,2,3,4].find(n=>!used.has(n));
   p={slot,hp:100,name:String(data.name||"Wrestler").slice(0,20),position:{x:slot%2?-1.4:1.4,y:1.2,z:slot<=2?-1.4:1.4},rotation:0,animation:"idle"};
   this.players.set(ws,p);ws.serializeAttachment(p);send(ws,{type:"welcome",slot,hp:100});
   const snapshot=[...this.players.values()].map(v=>({slot:v.slot,hp:v.hp,name:v.name,position:v.position,rotation:v.rotation,animation:v.animation}));
   for(const [peer,info] of this.players)send(peer,{type:"roster",players:snapshot,slot:info.slot});
   return;
  }
  if(data.type==="state"){
   const pos=data.position,rotation=Number(data.rotation);
   if(!pos||!["x","y","z"].every(k=>Number.isFinite(pos[k]))||!Number.isFinite(rotation))return;
   if(Math.abs(pos.x)>4.1||Math.abs(pos.z)>4.1||pos.y<0||pos.y>5)return;
   p.position={x:pos.x,y:pos.y,z:pos.z};p.rotation=rotation;
   p.animation=allowedAnimations.has(data.animation)?data.animation:"idle";
   ws.serializeAttachment(p);
   this.broadcast({type:"state",slot:p.slot,position:p.position,rotation,animation:p.animation},ws);
   return;
  }
  if(data.type==="drape-status"){
   if(data.active&&["x","z"].includes(data.axis)&&[1,-1].includes(data.sign)){
    p.drape={axis:data.axis,sign:data.sign};
   }else delete p.drape;
   ws.serializeAttachment(p);
   return;
  }
  if(this.players.size<2)return;
  const candidates=[...this.players].filter(([w,v])=>w!==ws&&v.hp>0).map(([w,v])=>({ws:w,p:v,dx:v.position.x-p.position.x,dz:v.position.z-p.position.z})).filter(c=>{const d=Math.hypot(c.dx,c.dz);return d>=.1&&d<=2.2&&Math.abs(c.p.position.y-p.position.y)<=.65&&dot(forward(p.rotation),[c.dx/d,c.dz/d])>=.5;}).sort((a,b)=>Math.hypot(a.dx,a.dz)-Math.hypot(b.dx,b.dz));
  const chosen=candidates[0];if(!chosen)return;
  const otherWs=chosen.ws,other=chosen.p;
  const now=Date.now()/1000;
  if(p.hp<=0||other.hp<=0||now<(this.locks.get(ws)||0)||now<(this.locks.get(otherWs)||0))return;
  const dx=other.position.x-p.position.x,dz=other.position.z-p.position.z;
  const dist=Math.hypot(dx,dz);
  if(dist<.1||dist>2.2||Math.abs(other.position.y-p.position.y)>.65)return;
  const direction=[dx/dist,dz/dist];
  if(dot(forward(p.rotation),direction)<.5)return;
  if(data.type==="irish-whip"){
   const dir=forward(p.rotation);
   const target={x:Math.max(-3.35,Math.min(3.35,other.position.x+dir[0]*2.58)),y:1.2,z:Math.max(-3.35,Math.min(3.35,other.position.z+dir[1]*2.58))};
   this.locks.set(ws,now+1.5);this.locks.set(otherWs,now+1.5);
   const msg={type:"irish-whip",attackerSlot:p.slot,defenderSlot:other.slot,duration:1.4,target,directionYaw:p.rotation+Math.PI,attackerPosition:{...p.position}};
   this.broadcast(msg);send(ws,msg);
   return;
  }
  if(data.type==="special"){
   const behind=dot(forward(other.rotation),direction)>.5;
   const move=behind?"german-suplex":"powerbomb";
   this.locks.set(ws,now+2.55);this.locks.set(otherWs,now+2.55);
   send(ws,{type:"grapple",role:"attacker",move,duration:2.3,impact:1.55,attackerSlot:p.slot,defenderSlot:other.slot});
   send(otherWs,{type:"grapple",role:"defender",move,duration:2.3,impact:1.55,attackerSlot:p.slot,defenderSlot:other.slot});
   for(const peer of this.players.keys())if(peer!==ws&&peer!==otherWs)send(peer,{type:"grapple",role:"observer",move,duration:2.3,impact:1.55,attackerSlot:p.slot,defenderSlot:other.slot});
   const due=Date.now()+1550;
   await this.ctx.storage.put("pending-grapple",{attackerSlot:p.slot,defenderSlot:other.slot,move,due});
   await this.scheduleAlarm(due);
   return;
  }
  if(data.type!=="punch"||!Object.hasOwn(ATTACKS,data.move))return;
  const [base,cooldown,defaultReaction]=ATTACKS[data.move];
  if(now-(this.lastHits.get(ws)||0)<cooldown)return;
  this.lastHits.set(ws,now);
  const momentum=Number(data.momentum);
  const damage=Math.round(base*Math.max(1,Math.min(1.3,Number.isFinite(momentum)?momentum:1)));
  let reaction=defaultReaction;
  if(["punch","jab","hook"].includes(data.move)){
   reaction=dot(forward(other.rotation),[-direction[0],-direction[1]])>=0?"reactions.hit-front":"reactions.hit-back";
  }
  this.damage(ws,otherWs,damage,reaction,data.move);
 }
 damage(attackerWs,defenderWs,damage,reaction,move){
  const a=this.players.get(attackerWs),b=this.players.get(defenderWs);if(!a||!b)return;
  // A punch to a wrestler facing into the ring with their back against a rope triggers the throw.
  const punchHit=["punch","jab","hook"].includes(move);
  const bx=b.position.x,bz=b.position.z;
  const edges=[{axis:"x",sign:1,d:3.3-bx},{axis:"x",sign:-1,d:3.3+bx},{axis:"z",sign:1,d:3.3-bz},{axis:"z",sign:-1,d:3.3+bz}].sort((u,v)=>Math.abs(u.d)-Math.abs(v.d));
  const side=edges[0];
  const inward=side.axis==="x"?[-side.sign,0]:[0,-side.sign];
  const facing=forward(b.rotation);
  const draped=b.drape;
  const behindDraped=punchHit&&draped&&Math.hypot(a.position.x-bx,a.position.z-bz)<=2.2&&
   (draped.axis==="x"?(a.position.x-bx)*draped.sign<-.15:(a.position.z-bz)*draped.sign<-.15);
  if(behindDraped){
   delete b.drape;
   this.locks.set(defenderWs,Date.now()/1000+1.5);
   this.broadcast({type:"drape-pulled-over",slot:b.slot,axis:draped.axis,sign:draped.sign});
  }
  const overTop=punchHit&&b.position.y>.75&&Math.abs(side.d)<.85&&Math.abs((side.axis==="x"?bz:bx))<2.7&&dot(facing,inward)>.6;
  b.hp=Math.max(0,b.hp-damage);attackerWs.serializeAttachment(a);defenderWs.serializeAttachment(b);
  if(overTop&&!behindDraped){
   const event={type:"over-top-rope",slot:b.slot,axis:side.axis,sign:side.sign,duration:1.4};
   this.locks.set(defenderWs,Date.now()/1000+1.5);
   this.broadcast(event);
  }
  send(attackerWs,{type:"health",self:a.hp,other:b.hp,hit:"other",damage,reaction,move,targetSlot:b.slot});
  send(defenderWs,{type:"health",self:b.hp,other:a.hp,hit:"self",damage,reaction,move,targetSlot:a.slot});
  this.broadcast({type:"hp",slot:b.slot,hp:b.hp});
  if(b.hp===0){const due=Date.now()+10000;this.ctx.storage.put("ko-"+b.slot,due).then(()=>this.scheduleAlarm(due));}
 }
 async scheduleAlarm(due){const current=await this.ctx.storage.getAlarm();if(current===null||due<current)await this.ctx.storage.setAlarm(due);}
 async alarm(){
  const pending=await this.ctx.storage.get("pending-grapple");
  if(pending&&Date.now()>=pending.due){
   await this.ctx.storage.delete("pending-grapple");
   const attacker=[...this.players].find(([,p])=>p.slot===pending.attackerSlot)?.[0];
   const defender=[...this.players].find(([,p])=>p.slot===pending.defenderSlot)?.[0];
   if(attacker&&defender)this.damage(attacker,defender,30,"reactions.knocked-back",pending.move);
  }
  let nextDue=pending&&Date.now()<pending.due?pending.due:null;
  for(const [ws,p] of this.players){
   const deadline=await this.ctx.storage.get("ko-"+p.slot);
   if(deadline&&Date.now()<deadline)nextDue=nextDue===null?deadline:Math.min(nextDue,deadline);
   if(deadline&&Date.now()>=deadline){
    p.hp=100;ws.serializeAttachment(p);await this.ctx.storage.delete("ko-"+p.slot);
    this.broadcast({type:"hp",slot:p.slot,hp:p.hp});
   }
  }
  if(nextDue!==null)await this.scheduleAlarm(nextDue);
 }
 async webSocketClose(ws){this.leave(ws);}
 async webSocketError(ws){this.leave(ws);}
 leave(ws){if(!this.players.delete(ws))return;this.lastHits.delete(ws);this.locks.delete(ws);this.broadcast({type:"left",slot:this.players.size>=0?ws.deserializeAttachment()?.slot:null});}
}
export default {
 async fetch(request,env){
  const url=new URL(request.url);
  if(url.pathname==="/health")return Response.json({ok:true,service:"ttw-multiplayer"});
  if(url.pathname!=="/ws")return new Response("TTW multiplayer: connect to /ws",{status:404});
  if(request.headers.get("Upgrade")?.toLowerCase()!=="websocket")return new Response("WebSocket required",{status:426});
  const id=env.ROOM.idFromName("ttw-main-ring");
  return env.ROOM.get(id).fetch(request);
 }
};
