/*
  Dark Arena Controller Pack: Forged
  -------------------------------------------
  Self-contained on-screen controller. Look, layout and behaviour all live in this
  one file. Styles are sealed inside Shadow DOM, so game CSS cannot change it.
  Every controller in the pack has the same layout, control IDs and API, so they
  can be swapped by changing which file is loaded. Load only ONE pack file per page.

  LOAD:
    Add a script tag with src="controller-forged.js" to your page.

  MOUNT:
    const pad = GameController.mount(document.getElementById('controllerSlot'), { mode: 'auto' });
    // mode: 'auto' (follows screen orientation), 'portrait' or 'landscape'
    // The container must have a real width and height. In landscape the controller
    // is transparent and meant to overlay the game: give the container
    // position:absolute; inset:0; inside a position:relative parent of the canvas.
    // Taps on empty areas pass through to the game underneath.

  READ INPUT (either way works):
    1) Events on window
       window.addEventListener('controller:button',   e => { e.detail.id, e.detail.pressed });
       window.addEventListener('controller:joystick', e => { e.detail.id, e.detail.x, e.detail.y, e.detail.active });
       window.addEventListener('controller:mode',     e => { e.detail.mode });
    2) Poll state each frame
       pad.state.buttons.ability1           -> true/false
       pad.state.joysticks.controlMOVEMENT  -> { x, y, active }   x/y in -1..1, y -1 = up

  OTHER:
    pad.setMode('portrait' | 'landscape' | 'auto')
    pad.on('button', fn) / pad.on('joystick', fn) / pad.on('mode', fn)
    pad.destroy()
    GameController.theme  -> 'forged'

  CONTROL IDS (identical in both modes and in every pack controller):
    Buttons:   lobby, talk, inventory, quests, abilities, ultimate, ability1, ability2, ability3, ability4
    Joysticks: controlMOVEMENT, targetJoystick, classJoystick
*/
(function (global) {
  'use strict';

  const THEME = 'forged';

  const CONTROLS = [
    { id: 'lobby',           type: 'button',   label: 'Lobby',     area: 'lob', role: 'menu' },
    { id: 'talk',            type: 'button',   label: 'Talk',      area: 'tlk', role: 'menu' },
    { id: 'inventory',       type: 'button',   label: 'Inventory', area: 'inv', role: 'nav' },
    { id: 'quests',          type: 'button',   label: 'Quests',    area: 'qst', role: 'nav' },
    { id: 'abilities',       type: 'button',   label: 'Abilities', area: 'abl', role: 'action' },
    { id: 'ultimate',        type: 'button',   label: 'Ultimate',  area: 'ult', role: 'ultimate' },
    { id: 'ability1',        type: 'button',   label: '1',         area: 'a1',  role: 'ability' },
    { id: 'ability2',        type: 'button',   label: '2',         area: 'a2',  role: 'ability' },
    { id: 'ability3',        type: 'button',   label: '3',         area: 'a3',  role: 'ability' },
    { id: 'ability4',        type: 'button',   label: '4',         area: 'a4',  role: 'ability' },
    { id: 'controlMOVEMENT', type: 'joystick', label: 'MOVE',      area: 'mv',  role: 'move' },
    { id: 'targetJoystick',  type: 'joystick', label: 'TARGET',    area: 'tj',  role: 'aim' },
    { id: 'classJoystick',   type: 'joystick', label: 'CLASS',     area: 'cj',  role: 'aim' }
  ];

  // Layout and structure, shared by every controller in the pack
  const LAYOUT_CSS = `
    :host { all: initial; display: block; width: 100%; height: 100%; pointer-events: none; }
    * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
    .wrap { pointer-events: none; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
      touch-action: none; user-select: none; -webkit-user-select: none; }
    .pad { display: grid; gap: 2%; padding: 2%; border-radius: 14px;
      max-width: 100%; max-height: 100%; container-type: size; }

    .pad.portrait { pointer-events: auto; aspect-ratio: 1 / 1; height: 100%;
      grid-template-columns: repeat(4, 1fr); grid-template-rows: 2fr 2fr 2fr 1fr 1fr;
      grid-template-areas:
        ".   .   a3  a4"
        "mv  mv  a1  a2"
        "mv  mv  tj  cj"
        "inv qst abl ult"
        "lob lob tlk tlk"; }

    .pad.landscape { aspect-ratio: 2 / 1; width: 100%; pointer-events: none;
      grid-template-columns: repeat(12, 1fr); grid-template-rows: repeat(6, 1fr);
      grid-template-areas:
        "lob lob .   .   .   .   .   .   .   .   tlk tlk"
        ".   .   .   .   .   .   .   .   .   .   .   .  "
        "mv  mv  mv  mv  .   .   .   .   a1  a2  a3  a4 "
        "mv  mv  mv  mv  .   .   .   .   tj  tj  cj  cj "
        "mv  mv  mv  mv  .   .   .   .   tj  tj  cj  cj "
        "inv inv qst qst .   .   .   .   abl abl ult ult"; }
    .pad.landscape { background: transparent !important; border-color: transparent !important;
      box-shadow: none !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important; }
    .pad.landscape > * { pointer-events: auto; opacity: var(--ls-opacity, 0.7); transition: opacity .1s; }
    .pad.landscape > .pressed, .pad.landscape > .stick.active { opacity: 1; }

    .btn { min-width: 0; min-height: 0; display: flex; align-items: center; justify-content: center;
      padding: 0; cursor: pointer; font-size: clamp(9px, 3.6cqmin, 18px); line-height: 1;
      transition: transform .06s, background .08s, box-shadow .08s; }
    .btn.pressed { transform: scale(0.96); }

    .stick { min-width: 0; min-height: 0; position: relative; display: flex; align-items: center;
      justify-content: center; container-type: size; }
    .base { position: relative; width: min(100cqw, 100cqh); height: min(100cqw, 100cqh); flex: none; border-radius: 50%; }
    .knob { position: absolute; left: 29%; top: 29%; width: 42%; height: 42%; border-radius: 50%; pointer-events: none; z-index: 2; }
    .label { position: absolute; bottom: 2px; font-size: clamp(9px, 8cqmin, 13px); pointer-events: none; z-index: 3; }
  `;

  // Visual theme
  const THEME_CSS = `
    .pad.portrait { background: linear-gradient(170deg, #2b241e, #15110e); border: 2px solid #5a4630;
      box-shadow: inset 0 0 30px rgba(0,0,0,.7), 0 6px 18px rgba(0,0,0,.5); }
    .btn { border: 1px solid #8a6a3a; border-radius: 6px; color: #ead8b2;
      background: linear-gradient(180deg, #4a4038 0%, #2c2520 100%);
      box-shadow: inset 0 1px 0 rgba(255,220,160,.18), inset 0 -2px 0 rgba(0,0,0,.4), 0 2px 5px rgba(0,0,0,.6);
      font-family: Georgia, 'Times New Roman', serif; font-weight: 700; text-transform: uppercase;
      letter-spacing: .08em; text-shadow: 0 1px 1px #000; }
    .btn.nav, .btn.action { font-size: clamp(8px, 3cqmin, 15px); }
    .btn.menu { background: linear-gradient(180deg, #e6cd9f 0%, #b8955e 100%); border-color: #6e5230;
      color: #2b1d0e; text-shadow: 0 1px 0 rgba(255,240,210,.5); }
    .btn.ability { color: #f0c46a; border-color: #b8893a; font-size: clamp(11px, 5cqmin, 24px); }
    .btn.ultimate { background: linear-gradient(180deg, #7a2a18 0%, #3e140b 100%); border-color: #d4a046; color: #ffd98a; }
    .btn.pressed { background: linear-gradient(180deg, #e8b85a 0%, #9a7330 100%); border-color: #ffd98a;
      color: #1a1208; text-shadow: none; box-shadow: 0 0 12px rgba(232,184,90,.65), inset 0 2px 4px rgba(0,0,0,.3); }
    .base { background: radial-gradient(circle, #3a322b 0%, #1e1916 72%); border: 3px solid #8a6a3a;
      box-shadow: inset 0 0 14px #000, 0 0 0 2px #2a2018, 0 4px 10px rgba(0,0,0,.6); }
    .ring { position: absolute; inset: 14%; border-radius: 50%; border: 1px solid rgba(184,137,58,.35); }
    .knob { background: radial-gradient(circle at 35% 30%, #f6e2b4 0%, #b08848 50%, #5e4524 100%);
      border: 1px solid #3a2a14; box-shadow: 0 3px 8px rgba(0,0,0,.7), inset 0 -3px 6px rgba(0,0,0,.35); }
    .stick.active .base { border-color: #e8b85a; box-shadow: inset 0 0 14px #000, 0 0 16px rgba(232,184,90,.5); }
    .label { color: #b89a68; font-family: Georgia, 'Times New Roman', serif; font-weight: 700; letter-spacing: .12em; }
 `;

  function mount(container, opts) {
    opts = opts || {};
    if (!container) throw new Error('GameController.mount: container element required');

    // Let taps on empty areas pass through to the game underneath
    container.style.pointerEvents = 'none';

    const host = document.createElement('div');
    host.style.cssText = 'width:100%;height:100%;pointer-events:none;';
    container.appendChild(host);
    const root = host.attachShadow({ mode: 'open' });

    const style = document.createElement('style');
    style.textContent = LAYOUT_CSS + THEME_CSS;
    root.appendChild(style);

    const wrap = document.createElement('div');
    wrap.className = 'wrap';
    const pad = document.createElement('div');
    pad.className = 'pad portrait';
    wrap.appendChild(pad);
    root.appendChild(wrap);

    const state = { mode: 'portrait', buttons: {}, joysticks: {} };
    const listeners = { button: [], joystick: [], mode: [] };
    const cleanups = [];

    const emit = (kind, detail) => {
      listeners[kind].forEach(fn => fn(detail));
      global.dispatchEvent(new CustomEvent('controller:' + kind, { detail }));
    };

    CONTROLS.forEach(c => {
      if (c.type === 'button') {
        const el = document.createElement('button');
        el.className = 'btn ' + c.role;
        el.style.gridArea = c.area;
        el.innerHTML = '<span class="txt"></span>';
        el.firstChild.textContent = c.label;
        el.dataset.id = c.id;
        state.buttons[c.id] = false;
        const set = pressed => {
          if (state.buttons[c.id] === pressed) return;
          state.buttons[c.id] = pressed;
          el.classList.toggle('pressed', pressed);
          emit('button', { id: c.id, pressed });
        };
        el.addEventListener('pointerdown', e => { e.preventDefault(); el.setPointerCapture(e.pointerId); set(true); });
        el.addEventListener('pointerup', () => set(false));
        el.addEventListener('pointercancel', () => set(false));
        el.addEventListener('contextmenu', e => e.preventDefault());
        pad.appendChild(el);
      } else {
        const el = document.createElement('div');
        el.className = 'stick ' + c.role;
        el.style.gridArea = c.area;
        el.dataset.id = c.id;
        el.innerHTML = '<div class="base"><div class="ring"></div><div class="knob"></div></div><span class="label">' + c.label + '</span>';
        const base = el.querySelector('.base');
        const knob = el.querySelector('.knob');
        const js = state.joysticks[c.id] = { x: 0, y: 0, active: false };
        let pid = null;

        const update = (cx, cy) => {
          const r = base.getBoundingClientRect();
          const radius = r.width / 2, max = radius * 0.6;
          let dx = cx - (r.left + radius), dy = cy - (r.top + radius);
          const d = Math.hypot(dx, dy);
          if (d > max) { dx = dx / d * max; dy = dy / d * max; }
          knob.style.transform = 'translate(' + dx + 'px,' + dy + 'px)';
          js.x = +(dx / max).toFixed(3);
          js.y = +(dy / max).toFixed(3);
          emit('joystick', { id: c.id, x: js.x, y: js.y, active: js.active });
        };
        const release = () => {
          pid = null; js.active = false; js.x = 0; js.y = 0;
          knob.style.transform = '';
          el.classList.remove('active');
          emit('joystick', { id: c.id, x: 0, y: 0, active: false });
        };

        base.addEventListener('pointerdown', e => {
          e.preventDefault();
          pid = e.pointerId; base.setPointerCapture(pid);
          js.active = true; el.classList.add('active');
          update(e.clientX, e.clientY);
        });
        base.addEventListener('pointermove', e => { if (e.pointerId === pid) update(e.clientX, e.clientY); });
        base.addEventListener('pointerup', e => { if (e.pointerId === pid) release(); });
        base.addEventListener('pointercancel', e => { if (e.pointerId === pid) release(); });
        pad.appendChild(el);
      }
    });

    let auto = false;
    const applyMode = mode => {
      if (state.mode === mode && pad.classList.contains(mode)) return;
      state.mode = mode;
      pad.className = 'pad ' + mode;
      emit('mode', { mode });
    };
    const autoMode = () => { if (auto) applyMode(innerWidth > innerHeight ? 'landscape' : 'portrait'); };
    global.addEventListener('resize', autoMode);
    cleanups.push(() => global.removeEventListener('resize', autoMode));

    const api = {
      state,
      theme: THEME,
      setMode(mode) {
        auto = mode === 'auto';
        auto ? autoMode() : applyMode(mode);
      },
      on(kind, fn) { if (listeners[kind]) listeners[kind].push(fn); return api; },
      destroy() { cleanups.forEach(f => f()); host.remove(); }
    };

    api.setMode(opts.mode || 'auto');
    return api;
  }

  global.GameController = { mount, theme: THEME, CONTROLS: CONTROLS.map(c => ({ id: c.id, type: c.type })) };
})(window);
