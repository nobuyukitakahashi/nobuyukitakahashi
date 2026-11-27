"use strict";

/**
 * Live Moho Pro 14.5.1 Lua 5.4 IPC Bridge Client
 * Communicates atomically via %TEMP%/agy-moho-bridge/ with automatic Win32 non-intrusive
 * viewport nudging, plus high-level structured Lua builders for layers, vectors, bones,
 * animation keyframes, and document management.
 */

const fs = require("fs");
const path = require("path");
const { BRIDGE_DIR, IS_WIN, detectMohoEnvironment, readBridgeHeartbeat } = require("./env");
const { nudgeMohoWindow, startNudgeLoop } = require("./win32-nudge");

function sleepSync(ms) {
  const sab = new SharedArrayBuffer(4);
  const ia = new Int32Array(sab);
  Atomics.wait(ia, 0, 0, ms);
}

function ensureBridgeDir(dir = BRIDGE_DIR) {
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

function writeAtomic(targetPath, text) {
  const tmpPath = `${targetPath}.tmp_${process.pid}_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`;
  fs.writeFileSync(tmpPath, text, "utf8");
  fs.renameSync(tmpPath, targetPath);
}

/**
 * Send a raw IPC request to the running Moho Lua Bridge and wait for response.
 */
function sendLiveRequest(payload, options = {}) {
  const dir = ensureBridgeDir(options.bridgeDir || BRIDGE_DIR);
  const timeoutMs = Number(options.timeout_ms || 15000);
  const nudgeIntervalMs = Number(options.nudge_interval_ms || 350);

  const reqId = `cmd_${process.pid}_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
  const reqPath = path.join(dir, "req_active.json");
  const resPath = path.join(dir, `res_${reqId}.json`);

  // Wait briefly if another request is still active
  const lockStart = Date.now();
  while (fs.existsSync(reqPath) && Date.now() - lockStart < 3000) {
    sleepSync(40);
  }
  if (fs.existsSync(reqPath)) {
    // Stale request from an earlier timed-out call; overwrite safely
    try { fs.unlinkSync(reqPath); } catch (_) { }
  }

  const envelope = {
    id: reqId,
    ...payload
  };

  writeAtomic(reqPath, JSON.stringify(envelope));

  const start = Date.now();
  let lastNudge = 0;
  let nudgesSent = 0;
  const nudger = IS_WIN ? startNudgeLoop(resPath, timeoutMs) : null;
  if (nudger) nudgesSent = 1;

  try {
    while (Date.now() - start < timeoutMs) {
      if (fs.existsSync(resPath)) {
        try {
          const raw = fs.readFileSync(resPath, "utf8").replace(/^\uFEFF/, "").trim();
          if (raw.length > 0) {
            const parsed = JSON.parse(raw);
            try { fs.unlinkSync(resPath); } catch (_) { }
            return {
              ...parsed,
              elapsedMs: Date.now() - start,
              nudgesSent
            };
          }
        } catch (_) {
          // File might still be flushing; wait one tick
        }
      }

      if (!nudger) {
        const now = Date.now();
        if (now - lastNudge >= nudgeIntervalMs) {
          nudgeMohoWindow();
          lastNudge = now;
          nudgesSent++;
        }
      }
      sleepSync(40);
    }
  } finally {
    if (nudger && !nudger.killed) {
      try { nudger.kill(); } catch (_) { }
    }
  }

  // Cleanup stale pending request on timeout
  if (fs.existsSync(reqPath)) {
    try {
      const cur = JSON.parse(fs.readFileSync(reqPath, "utf8"));
      if (cur && cur.id === reqId) fs.unlinkSync(reqPath);
    } catch (_) { }
  }

  const env = detectMohoEnvironment();
  const hb = readBridgeHeartbeat(dir);
  return {
    ok: false,
    id: reqId,
    timeout: true,
    elapsedMs: Date.now() - start,
    nudgesSent,
    error: !env.isRunning
      ? "Moho Pro is not running. Start Moho Pro (e.g. via open_in_moho) and retry."
      : !env.bridgeInstalled
        ? "Lua bridge scripts are not installed in Moho Pro/Scripts. Run `node .agents/mcp/moho-mcp/install-bridge.js`."
        : "Timed out waiting for Moho Live Lua Bridge response. Ensure Moho Pro has an active visible window and scripts are loaded (Ctrl+Shift+Alt+L or restart Moho).",
    diagnostics: {
      isRunning: env.isRunning,
      bridgeInstalled: env.bridgeInstalled,
      heartbeat: hb
    }
  };
}

/**
 * Ping the Live Lua Bridge.
 */
function pingLiveBridge(options = {}) {
  return sendLiveRequest({ action: "ping" }, { timeout_ms: options.timeout_ms || 4000 });
}

/**
 * Execute arbitrary Lua 5.4 code inside running Moho Pro 14.5.1.
 * The Lua chunk receives `(moho, args)` as varargs (`local moho, args = ...`).
 */
function executeMohoLua(args = {}) {
  const code = args.code || args.lua || args.script;
  if (!code || typeof code !== "string") {
    return { ok: false, error: "code (Lua script string) is required" };
  }
  const wrappedCode = args.raw_chunk
    ? code
    : `local moho, args = ...\n${code}`;

  return sendLiveRequest(
    {
      action: "eval",
      code: wrappedCode,
      args: args.args || {},
      update_ui: args.update_ui !== false
    },
    { timeout_ms: args.timeout_ms || 30000 }
  );
}

/**
 * High-Level Tool: Get Live Document Summary from running Moho GUI.
 */
function getLiveDocumentSummary(args = {}) {
  const lua = `
local doc = moho.document
if not doc then
  return { hasDocument = false }
end

local layerTypeNames = {
  [MOHO.LT_VECTOR] = "Vector",
  [MOHO.LT_IMAGE] = "Image",
  [MOHO.LT_GROUP] = "Group",
  [MOHO.LT_BONE] = "Bone",
  [MOHO.LT_SWITCH] = "Switch",
  [MOHO.LT_PARTICLE] = "Particle",
  [MOHO.LT_NOTE] = "Note",
  [MOHO.LT_3D] = "3D",
  [MOHO.LT_AUDIO] = "Audio",
  [MOHO.LT_PATCH] = "Patch",
  [MOHO.LT_TEXT] = "Text"
}

local function inspectLayer(layer, depth, pathStr)
  local lt = layer:LayerType()
  local info = {
    path = pathStr,
    depth = depth,
    name = layer:Name(),
    type = layerTypeNames[lt] or tostring(lt),
    typeId = lt,
    uuid = layer:UUID(),
    visible = layer:IsVisible(),
    selected = (moho.layer == layer),
    parentBone = layer:LayerParentBone()
  }
  if lt == MOHO.LT_VECTOR then
    local vl = moho:LayerAsVector(layer)
    if vl and vl:Mesh() then
      local m = vl:Mesh()
      info.mesh = {
        points = m:CountPoints(),
        curves = m:CountCurves(),
        shapes = m:CountShapes(),
        groups = m:CountGroups()
      }
    end
  elseif lt == MOHO.LT_BONE then
    local bl = moho:LayerAsBone(layer)
    if bl and bl:Skeleton() then
      local sk = bl:Skeleton()
      local bones = {}
      for i = 0, sk:CountBones() - 1 do
        local b = sk:Bone(i)
        table.insert(bones, {
          index = i,
          name = b:Name(),
          parent = b.fParent,
          length = b.fLength,
          strength = b.fStrength,
          angleDeg = math.deg(b.fAngle),
          pos = { x = b.fPos.x, y = b.fPos.y }
        })
      end
      info.skeleton = { boneCount = sk:CountBones(), bones = bones }
    end
  end
  if layer:IsGroupType() then
    local gl = moho:LayerAsGroup(layer)
    if gl then
      local children = {}
      for i = 0, gl:CountLayers() - 1 do
        local child = gl:Layer(i)
        table.insert(children, inspectLayer(child, depth + 1, pathStr .. "." .. tostring(i)))
      end
      info.children = children
    end
  end
  return info
end

local layers = {}
for i = 0, doc:CountLayers() - 1 do
  table.insert(layers, inspectLayer(doc:Layer(i), 0, tostring(i)))
end

return {
  hasDocument = true,
  name = doc:Name(),
  path = doc:Path(),
  width = doc:Width(),
  height = doc:Height(),
  fps = doc:Fps(),
  startFrame = doc:StartFrame(),
  endFrame = doc:EndFrame(),
  currentFrame = moho.frame,
  selectedLayer = moho.layer and moho.layer:Name() or nil,
  topLevelLayerCount = doc:CountLayers(),
  layers = layers
}
`;
  return executeMohoLua({ code: lua, update_ui: false, timeout_ms: args.timeout_ms || 15000 });
}

/**
 * High-Level Tool: Manage Layers in live Moho GUI.
 */
function liveManageLayers(args = {}) {
  const lua = `
local doc = moho.document
if not doc then error("No active document in Moho") end

local op = tostring(args.operation or "create")

local typeMap = {
  vector = MOHO.LT_VECTOR,
  bone = MOHO.LT_BONE,
  group = MOHO.LT_GROUP,
  switch = MOHO.LT_SWITCH,
  image = MOHO.LT_IMAGE,
  audio = MOHO.LT_AUDIO,
  note = MOHO.LT_NOTE,
  particle = MOHO.LT_PARTICLE,
  patch = MOHO.LT_PATCH,
  text = MOHO.LT_TEXT
}

local function findLayerByName(name)
  local function walk(parent)
    local count = parent and parent:CountLayers() or doc:CountLayers()
    for i = 0, count - 1 do
      local l = parent and parent:Layer(i) or doc:Layer(i)
      if l:Name() == name then return l end
      if l:IsGroupType() then
        local gl = moho:LayerAsGroup(l)
        local found = walk(gl)
        if found then return found end
      end
    end
    return nil
  end
  return walk(nil)
end

local target = nil
if args.target_layer then
  target = findLayerByName(tostring(args.target_layer))
  if not target and op ~= "create" then
    error("Target layer not found: " .. tostring(args.target_layer))
  end
else
  target = moho.layer
end

if op == "create" then
  local ltypeKey = string.lower(tostring(args.layer_type or "vector"))
  local ltype = typeMap[ltypeKey]
  if not ltype then error("Unsupported layer_type: " .. ltypeKey) end
  doc:SetDirty()
  local newLayer = moho:CreateNewLayer(ltype, false)
  if args.name then newLayer:SetName(tostring(args.name)) end
  if args.parent_group then
    local grp = findLayerByName(tostring(args.parent_group))
    if not grp or not grp:IsGroupType() then
      error("Parent group not found or not a group/bone/switch layer: " .. tostring(args.parent_group))
    end
    moho:PlaceLayerInGroup(newLayer, grp, true, false)
  end
  moho:SetSelLayer(newLayer)
  return { operation = "create", name = newLayer:Name(), uuid = newLayer:UUID(), type = ltypeKey }

elseif op == "select" then
  moho:SetSelLayer(target)
  return { operation = "select", name = target:Name(), uuid = target:UUID() }

elseif op == "rename" then
  if not args.new_name then error("new_name is required") end
  doc:SetDirty()
  local oldName = target:Name()
  target:SetName(tostring(args.new_name))
  return { operation = "rename", oldName = oldName, newName = target:Name() }

elseif op == "delete" then
  doc:SetDirty()
  local oldName = target:Name()
  moho:DeleteLayer(target)
  return { operation = "delete", deleted = oldName }

elseif op == "duplicate" then
  doc:SetDirty()
  local dup = moho:DuplicateLayer(target, false)
  if args.new_name and dup then dup:SetName(tostring(args.new_name)) end
  return { operation = "duplicate", source = target:Name(), created = dup and dup:Name() or nil }

elseif op == "move_into_group" then
  local grp = findLayerByName(tostring(args.parent_group or ""))
  if not grp or not grp:IsGroupType() then
    error("Parent group not found: " .. tostring(args.parent_group))
  end
  doc:SetDirty()
  moho:PlaceLayerInGroup(target, grp, true, false)
  return { operation = "move_into_group", layer = target:Name(), group = grp:Name() }

elseif op == "set_properties" then
  doc:PrepUndo(target)
  doc:SetDirty()
  local f = tonumber(args.frame) or moho.frame or 0
  if args.visible ~= nil then
    target:SetVisible(args.visible and true or false)
  end
  if args.opacity ~= nil then
    target.fAlpha:SetValue(f, tonumber(args.opacity))
  end
  if args.translation and type(args.translation) == "table" then
    local v = LM.Vector3:new_local()
    v:Set(tonumber(args.translation.x or args.translation[1] or 0),
          tonumber(args.translation.y or args.translation[2] or 0),
          tonumber(args.translation.z or args.translation[3] or 0))
    target.fTranslation:SetValue(f, v)
  end
  if args.scale and type(args.scale) == "table" then
    local v = LM.Vector3:new_local()
    v:Set(tonumber(args.scale.x or args.scale[1] or 1),
          tonumber(args.scale.y or args.scale[2] or 1),
          tonumber(args.scale.z or args.scale[3] or 1))
    target.fScale:SetValue(f, v)
  end
  if args.rotation_z_deg ~= nil then
    target.fRotationZ:SetValue(f, math.rad(tonumber(args.rotation_z_deg)))
  end
  if args.origin and type(args.origin) == "table" then
    local o = LM.Vector2:new_local()
    o:Set(tonumber(args.origin.x or args.origin[1] or 0),
          tonumber(args.origin.y or args.origin[2] or 0))
    target:SetOrigin(o)
  end
  return { operation = "set_properties", layer = target:Name(), frame = f }

else
  error("Unknown layer operation: " .. op)
end
`;
  return executeMohoLua({ code: lua, args, timeout_ms: args.timeout_ms || 15000 });
}

/**
 * High-Level Tool: Procedural Vector Shape Drawing in live Moho GUI.
 */
function liveDrawVector(args = {}) {
  const lua = `
local doc = moho.document
if not doc then error("No active document in Moho") end

local function findLayerByName(name)
  local function walk(parent)
    local count = parent and parent:CountLayers() or doc:CountLayers()
    for i = 0, count - 1 do
      local l = parent and parent:Layer(i) or doc:Layer(i)
      if l:Name() == name then return l end
      if l:IsGroupType() then
        local found = walk(moho:LayerAsGroup(l))
        if found then return found end
      end
    end
    return nil
  end
  return walk(nil)
end

local layer = nil
if args.layer_name then
  layer = findLayerByName(tostring(args.layer_name))
  if not layer then
    layer = moho:CreateNewLayer(MOHO.LT_VECTOR, false)
    layer:SetName(tostring(args.layer_name))
  end
else
  layer = moho.layer
  if not layer or layer:LayerType() ~= MOHO.LT_VECTOR then
    layer = moho:CreateNewLayer(MOHO.LT_VECTOR, false)
    layer:SetName("Vector Shape")
  end
end

moho:SetSelLayer(layer)
local vl = moho:LayerAsVector(layer)
if not vl then error("Target layer is not a Vector layer: " .. layer:Name()) end
local mesh = vl:Mesh()
if not mesh then error("Vector layer has no mesh") end

doc:PrepUndo(layer)
doc:SetDirty()

local frame = tonumber(args.frame) or 0
local shapeType = string.lower(tostring(args.shape_type or "rectangle"))
local cx = tonumber(args.cx) or 0
local cy = tonumber(args.cy) or 0
local w = tonumber(args.width) or 0.6
local h = tonumber(args.height) or 0.4
local rx = tonumber(args.rx or args.radius) or (w / 2)
local ry = tonumber(args.ry or args.radius) or (h / 2)
local closeShape = (args.close ~= false)
local oldCount = mesh:CountPoints()

mesh:SelectNone()
local pts = {}
local defaultCurvature = MOHO.PEAKED

if shapeType == "rectangle" or shapeType == "rect" then
  local hw, hh = w / 2, h / 2
  pts = {
    { x = cx - hw, y = cy + hh },
    { x = cx + hw, y = cy + hh },
    { x = cx + hw, y = cy - hh },
    { x = cx - hw, y = cy - hh }
  }
elseif shapeType == "ellipse" or shapeType == "circle" then
  defaultCurvature = MOHO.SMOOTH
  local segs = math.max(4, tonumber(args.segments) or 8)
  for i = 0, segs - 1 do
    local a = (2 * math.pi * i) / segs
    table.insert(pts, { x = cx + rx * math.cos(a), y = cy + ry * math.sin(a) })
  end
elseif shapeType == "polygon" then
  local sides = math.max(3, tonumber(args.sides) or 6)
  local rot = math.rad(tonumber(args.rotation_deg) or 90)
  for i = 0, sides - 1 do
    local a = rot + (2 * math.pi * i) / sides
    table.insert(pts, { x = cx + rx * math.cos(a), y = cy + ry * math.sin(a) })
  end
elseif shapeType == "star" then
  local spikes = math.max(3, tonumber(args.spikes) or 5)
  local innerR = tonumber(args.inner_radius) or (rx * 0.42)
  local rot = math.rad(tonumber(args.rotation_deg) or 90)
  for i = 0, spikes * 2 - 1 do
    local a = rot + (math.pi * i) / spikes
    local r = (i % 2 == 0) and rx or innerR
    table.insert(pts, { x = cx + r * math.cos(a), y = cy + r * math.sin(a) })
  end
elseif shapeType == "points" or shapeType == "path" then
  if type(args.points) ~= "table" or #args.points < 2 then
    error("points array with at least 2 points is required for shape_type='points'")
  end
  for _, p in ipairs(args.points) do
    table.insert(pts, {
      x = tonumber(p.x or p[1] or 0),
      y = tonumber(p.y or p[2] or 0),
      curvature = p.curvature
    })
  end
  if args.smooth then defaultCurvature = MOHO.SMOOTH end
else
  error("Unsupported shape_type: " .. shapeType)
end

local v = LM.Vector2:new_local()
for i, p in ipairs(pts) do
  v:Set(p.x, p.y)
  if i == 1 then
    mesh:AddLonePoint(v, frame)
  else
    mesh:AppendPoint(v, frame)
  end
end

if closeShape and #pts >= 3 then
  v:Set(pts[1].x, pts[1].y)
  mesh:AppendPoint(v, frame)
  mesh:WeldPoints(oldCount, oldCount + #pts, frame)
end

local addedCount = #pts
for i = 0, addedCount - 1 do
  local pt = mesh:Point(oldCount + i)
  if pt then
    local curv = defaultCurvature
    if pts[i + 1] and pts[i + 1].curvature ~= nil then
      curv = tonumber(pts[i + 1].curvature)
    elseif args.curvature ~= nil then
      curv = tonumber(args.curvature)
    end
    pt:SetCurvature(curv, frame)
  end
end

mesh:SelectConnected()

local function makeColorVector(col)
  local r = tonumber(col.r) or 0
  local g = tonumber(col.g) or 0
  local b = tonumber(col.b) or 0
  local a = (col.a ~= nil) and tonumber(col.a) or nil
  local maxVal = math.max(r, g, b, a or 0)
  local scale = (maxVal > 1) and 255 or 1
  local alpha = (a ~= nil) and (a / scale) or 1.0
  local c = LM.ColorVector:new_local()
  c:Set(r / scale, g / scale, b / scale, alpha)
  return c
end

local shapeId = -1
if args.create_shape ~= false then
  local doFill = (args.fill ~= false) and closeShape
  local doStroke = (args.stroke ~= false)
  -- CreateShape(filled, behindNeighborStrokes, frame)
  shapeId = moho:CreateShape(doFill, false, frame)
  if shapeId and shapeId >= 0 then
    local shape = mesh:Shape(shapeId)
    if shape then
      if args.shape_name then shape:SetName(tostring(args.shape_name)) end
      shape.fHasFill = doFill
      shape.fHasOutline = doStroke
      if args.fill_color and type(args.fill_color) == "table" then
        shape.fMyStyle.fFillCol:SetValue(frame, makeColorVector(args.fill_color))
      end
      if args.stroke_color and type(args.stroke_color) == "table" then
        shape.fMyStyle.fLineCol:SetValue(frame, makeColorVector(args.stroke_color))
      end
      if args.line_width ~= nil then
        shape.fMyStyle.fLineWidth = tonumber(args.line_width) / doc:Height()
      end
    end
  end
end

return {
  layer = layer:Name(),
  shapeType = shapeType,
  pointsAdded = addedCount,
  totalPoints = mesh:CountPoints(),
  shapeId = shapeId,
  totalShapes = mesh:CountShapes()
}
`;
  return executeMohoLua({ code: lua, args, timeout_ms: args.timeout_ms || 15000 });
}

/**
 * High-Level Tool: Bone Rigging & Layer Binding in live Moho GUI.
 */
function liveRigBones(args = {}) {
  const lua = `
local doc = moho.document
if not doc then error("No active document in Moho") end

local function findLayerByName(name)
  local function walk(parent)
    local count = parent and parent:CountLayers() or doc:CountLayers()
    for i = 0, count - 1 do
      local l = parent and parent:Layer(i) or doc:Layer(i)
      if l:Name() == name then return l end
      if l:IsGroupType() then
        local found = walk(moho:LayerAsGroup(l))
        if found then return found end
      end
    end
    return nil
  end
  return walk(nil)
end

local boneLayer = nil
if args.bone_layer then
  boneLayer = findLayerByName(tostring(args.bone_layer))
  if not boneLayer then
    boneLayer = moho:CreateNewLayer(MOHO.LT_BONE, false)
    boneLayer:SetName(tostring(args.bone_layer))
  end
else
  boneLayer = moho.layer
  if not boneLayer or boneLayer:LayerType() ~= MOHO.LT_BONE then
    boneLayer = moho:CreateNewLayer(MOHO.LT_BONE, false)
    boneLayer:SetName("Bone Rig")
  end
end

moho:SetSelLayer(boneLayer)
local bl = moho:LayerAsBone(boneLayer)
if not bl then error("Layer is not a Bone layer: " .. boneLayer:Name()) end
local skel = bl:Skeleton()
if not skel then error("Bone layer has no skeleton") end

doc:PrepUndo(boneLayer)
doc:SetDirty()

local created = {}
local boneIndexByName = {}
for i = 0, skel:CountBones() - 1 do
  boneIndexByName[skel:Bone(i):Name()] = i
end

if type(args.bones) == "table" then
  for _, spec in ipairs(args.bones) do
    local bone = skel:AddBone(0)
    local idx = skel:BoneID(bone)
    if spec.name then
      bone:SetName(tostring(spec.name))
      boneIndexByName[tostring(spec.name)] = idx
    end

    local parentID = -1
    if spec.parent ~= nil then
      if type(spec.parent) == "number" then
        parentID = spec.parent
      elseif type(spec.parent) == "string" and boneIndexByName[spec.parent] ~= nil then
        parentID = boneIndexByName[spec.parent]
      end
    end
    bone.fParent = parentID
    bone.fAnimParent:SetValue(0, parentID)

    local pos = LM.Vector2:new_local()
    pos:Set(tonumber(spec.x) or 0, tonumber(spec.y) or 0)
    local angleRad = math.rad(tonumber(spec.angle_deg) or 90)
    local boneLen = tonumber(spec.length) or 0.3

    if parentID >= 0 and not spec.local_coords then
      skel:UpdateBoneMatrix(parentID)
      local inverseM = LM.Matrix:new_local()
      inverseM:Set(skel:Bone(parentID).fRestMatrix)
      inverseM:Invert()
      local tip = LM.Vector2:new_local()
      tip:Set(pos.x + math.cos(angleRad) * boneLen, pos.y + math.sin(angleRad) * boneLen)
      inverseM:Transform(pos)
      inverseM:Transform(tip)
      angleRad = math.atan(tip.y - pos.y, tip.x - pos.x)
    end

    bone.fAnimPos:SetValue(0, pos)
    bone.fPos:Set(pos)

    bone.fAnimAngle:SetValue(0, angleRad)
    bone.fAngle = angleRad

    bone.fLength = boneLen
    if spec.strength ~= nil then bone.fStrength = tonumber(spec.strength) end

    if spec.min_angle_deg ~= nil and spec.max_angle_deg ~= nil then
      bone.fConstraints = true
      bone.fMinConstraint = math.rad(tonumber(spec.min_angle_deg))
      bone.fMaxConstraint = math.rad(tonumber(spec.max_angle_deg))
    end

    skel:UpdateBoneMatrix(idx)

    table.insert(created, {
      index = idx,
      name = bone:Name(),
      parent = bone.fParent,
      length = bone.fLength
    })
  end
  for i = 0, skel:CountBones() - 1 do
    skel:UpdateBoneMatrix(i)
  end
  boneLayer:UpdateCurFrame()
end

local boundLayers = {}
if type(args.bind_layers) == "table" then
  for _, bind in ipairs(args.bind_layers) do
    local child = findLayerByName(tostring(bind.layer_name or ""))
    if child then
      moho:PlaceLayerInGroup(child, boneLayer, true, false)
      local boneIdx = -1
      if type(bind.bone) == "number" then
        boneIdx = bind.bone
      elseif type(bind.bone) == "string" and boneIndexByName[bind.bone] ~= nil then
        boneIdx = boneIndexByName[bind.bone]
      end
      if boneIdx >= 0 then
        child:SetLayerParentBone(boneIdx)
      end
      table.insert(boundLayers, { layer = child:Name(), parentBone = boneIdx })
    end
  end
end

return {
  boneLayer = boneLayer:Name(),
  totalBones = skel:CountBones(),
  createdBones = created,
  boundLayers = boundLayers
}
`;
  return executeMohoLua({ code: lua, args, timeout_ms: args.timeout_ms || 15000 });
}

/**
 * High-Level Tool: Keyframe Animation, Timeline, Camera & Document Save/Open in live Moho GUI.
 */
function liveAnimate(args = {}) {
  const lua = `
local doc = moho.document
local op = tostring(args.operation or "keyframe")

if op == "new_document" then
  moho:FileNew()
  doc = moho.document
  return { operation = "new_document", hasDocument = (doc ~= nil) }
elseif op == "open_document" then
  if not args.file_path then error("file_path is required") end
  moho:FileOpen(tostring(args.file_path))
  doc = moho.document
  return { operation = "open_document", path = doc and doc:Path() or nil }
end

if not doc then error("No active document in Moho") end

if op == "save" then
  if args.file_path then
    moho:FileSaveAs(tostring(args.file_path))
  else
    moho:FileSave()
  end
  return { operation = "save", path = doc:Path() }

elseif op == "set_frame" then
  local f = tonumber(args.frame) or 0
  moho:SetCurFrame(f)
  return { operation = "set_frame", currentFrame = moho.frame }

elseif op == "export_frame_png" then
  if not args.output_png then error("output_png is required") end
  if args.frame ~= nil then moho:SetCurFrame(tonumber(args.frame)) end
  moho:FileRender(tostring(args.output_png))
  return { operation = "export_frame_png", frame = moho.frame, outputPng = tostring(args.output_png) }

elseif op == "keyframe" then
  local interpMap = {
    smooth = MOHO.INTERP_SMOOTH,
    linear = MOHO.INTERP_LINEAR,
    ease_in = MOHO.INTERP_EASE_IN,
    ease_out = MOHO.INTERP_EASE_OUT,
    ease_in_out = MOHO.INTERP_EASE_INOUT,
    step = MOHO.INTERP_STEP,
    bezier = MOHO.INTERP_BEZIER,
    bounce = MOHO.INTERP_BOUNCE,
    elastic = MOHO.INTERP_ELASTIC
  }

  local function findLayerByName(name)
    local function walk(parent)
      local count = parent and parent:CountLayers() or doc:CountLayers()
      for i = 0, count - 1 do
        local l = parent and parent:Layer(i) or doc:Layer(i)
        if l:Name() == name then return l end
        if l:IsGroupType() then
          local found = walk(moho:LayerAsGroup(l))
          if found then return found end
        end
      end
      return nil
    end
    return walk(nil)
  end

  local function setInterp(channel, frame, interpName)
    if interpName and interpMap[string.lower(interpName)] then
      channel:SetKeyInterp(frame, interpMap[string.lower(interpName)], -1, -1)
    end
  end

  local applied = 0
  local keys = args.keyframes
  if type(keys) ~= "table" then
    keys = { args }
  end

  doc:SetDirty()
  for _, k in ipairs(keys) do
    local f = tonumber(k.frame) or moho.frame or 0
    local target = k.layer_name and findLayerByName(tostring(k.layer_name)) or moho.layer
    local interp = k.interpolation

    if k.camera_track and type(k.camera_track) == "table" then
      local v = LM.Vector3:new_local()
      v:Set(tonumber(k.camera_track.x or 0), tonumber(k.camera_track.y or 0), tonumber(k.camera_track.z or 1.732))
      doc.fCameraTrack:SetValue(f, v)
      setInterp(doc.fCameraTrack, f, interp)
      applied = applied + 1
    end
    if k.camera_zoom ~= nil then
      doc.fCameraZoom:SetValue(f, tonumber(k.camera_zoom))
      setInterp(doc.fCameraZoom, f, interp)
      applied = applied + 1
    end
    if k.camera_roll_deg ~= nil then
      doc.fCameraRoll:SetValue(f, math.rad(tonumber(k.camera_roll_deg)))
      setInterp(doc.fCameraRoll, f, interp)
      applied = applied + 1
    end

    if target then
      if k.translation and type(k.translation) == "table" then
        local v = LM.Vector3:new_local()
        v:Set(tonumber(k.translation.x or 0), tonumber(k.translation.y or 0), tonumber(k.translation.z or 0))
        target.fTranslation:SetValue(f, v)
        setInterp(target.fTranslation, f, interp)
        applied = applied + 1
      end
      if k.scale and type(k.scale) == "table" then
        local v = LM.Vector3:new_local()
        v:Set(tonumber(k.scale.x or 1), tonumber(k.scale.y or 1), tonumber(k.scale.z or 1))
        target.fScale:SetValue(f, v)
        setInterp(target.fScale, f, interp)
        applied = applied + 1
      end
      if k.rotation_z_deg ~= nil then
        target.fRotationZ:SetValue(f, math.rad(tonumber(k.rotation_z_deg)))
        setInterp(target.fRotationZ, f, interp)
        applied = applied + 1
      end
      if k.opacity ~= nil then
        target.fAlpha:SetValue(f, tonumber(k.opacity))
        setInterp(target.fAlpha, f, interp)
        applied = applied + 1
      end
      if k.visible ~= nil then
        target.fVisibility:SetValue(f, k.visible and true or false)
        applied = applied + 1
      end

      -- Switch layer keyframe
      if k.switch_value ~= nil and target:LayerType() == MOHO.LT_SWITCH then
        local sl = moho:LayerAsSwitch(target)
        if sl then
          sl:SetValue(f, tostring(k.switch_value))
          applied = applied + 1
        end
      end

      -- Bone channel keyframe
      if k.bone_name ~= nil or k.bone_index ~= nil then
        local bl = moho:LayerAsBone(target)
        if bl and bl:Skeleton() then
          local sk = bl:Skeleton()
          local bone = nil
          if k.bone_index ~= nil then
            bone = sk:Bone(tonumber(k.bone_index))
          else
            for i = 0, sk:CountBones() - 1 do
              if sk:Bone(i):Name() == tostring(k.bone_name) then
                bone = sk:Bone(i)
                break
              end
            end
          end
          if bone then
            if k.bone_angle_deg ~= nil then
              bone.fAnimAngle:SetValue(f, math.rad(tonumber(k.bone_angle_deg)))
              setInterp(bone.fAnimAngle, f, interp)
              applied = applied + 1
            end
            if k.bone_pos and type(k.bone_pos) == "table" then
              local bv = LM.Vector2:new_local()
              bv:Set(tonumber(k.bone_pos.x or 0), tonumber(k.bone_pos.y or 0))
              bone.fAnimPos:SetValue(f, bv)
              setInterp(bone.fAnimPos, f, interp)
              applied = applied + 1
            end
            if k.bone_scale ~= nil then
              bone.fAnimScale:SetValue(f, tonumber(k.bone_scale))
              setInterp(bone.fAnimScale, f, interp)
              applied = applied + 1
            end
            sk:UpdateBoneMatrix(sk:BoneID(bone))
            bl:UpdateCurFrame()
          end
        end
      end
    end
  end

  if args.set_end_frame ~= nil then
    doc:SetEndFrame(tonumber(args.set_end_frame))
  end
  if args.set_frame ~= nil then
    moho:SetCurFrame(tonumber(args.set_frame))
  end

  return { operation = "keyframe", keyframesApplied = applied, currentFrame = moho.frame }
else
  error("Unknown live_animate operation: " .. op)
end
`;
  return executeMohoLua({ code: lua, args, timeout_ms: args.timeout_ms || 15000 });
}

module.exports = {
  sendLiveRequest,
  pingLiveBridge,
  executeMohoLua,
  getLiveDocumentSummary,
  liveManageLayers,
  liveDrawVector,
  liveRigBones,
  liveAnimate
};
