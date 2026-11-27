-- **************************************************
-- Antigravity Moho Pro 14.5.1 Live Control Bridge
-- Tool Script: Automatically polled on Moho UI refreshes
-- even when another tool is selected (via IsRelevant/IsEnabled).
-- Zero external dependencies, zero console popups, atomic file IPC.
-- **************************************************

ScriptName = "AGY_MohoBridge"

AGY_MohoBridge = AGY_MohoBridge or {}
AGY_MohoBridge.VERSION = "1.0.0"
AGY_MohoBridge.enabled = true
AGY_MohoBridge._busy = false
AGY_MohoBridge._lastHeartbeat = -999
AGY_MohoBridge._lastPoll = -999
AGY_MohoBridge._commandsExecuted = 0
AGY_MohoBridge._lastCommandId = ""
AGY_MohoBridge._lastError = ""
AGY_MohoBridge._lastHookScan = -999
AGY_MohoBridge._wrappedToolsCount = 0

-- Wrap DrawMe on ALL loaded Moho tool tables (including LM_TransformLayer which lacks IsEnabled!)
-- Re-scans periodically so tools loaded alphabetically after agy_moho_bridge.lua are always hooked.
function AGY_MohoBridge:InstallUniversalHooks(force)
	local now = os.clock()
	if (not force) and (now - self._lastHookScan < 5.0) and self._wrappedToolsCount > 0 then
		return
	end
	self._lastHookScan = now
	for k, v in pairs(_G) do
		if type(k) == "string" and type(v) == "table" and v ~= AGY_MohoBridge then
			local isToolLike = (type(v.DrawMe) == "function")
				or (type(v.UILabel) == "function" and (type(v.IsEnabled) == "function" or type(v.UpdateWidgets) == "function"))
			if isToolLike and not v._agyDrawMeWrapped then
				v._agyDrawMeWrapped = true
				self._wrappedToolsCount = self._wrappedToolsCount + 1
				local origDrawMe = v.DrawMe
				if type(origDrawMe) == "function" then
					v.DrawMe = function(toolSelf, moho, view)
						AGY_MohoBridge:ProcessQueue(moho, false)
						return origDrawMe(toolSelf, moho, view)
					end
				else
					v.DrawMe = function(toolSelf, moho, view)
						AGY_MohoBridge:ProcessQueue(moho, false)
					end
				end
			end
		end
	end
end

function AGY_MohoBridge:Name()
	return "Antigravity Moho Bridge"
end

function AGY_MohoBridge:Version()
	return AGY_MohoBridge.VERSION
end

function AGY_MohoBridge:Description()
	return "Antigravity Live Lua 5.4 Control Bridge (IPC Poller for MCP & CLI)"
end

function AGY_MohoBridge:Creator()
	return "Antigravity"
end

function AGY_MohoBridge:UILabel()
	return "AGY Bridge"
end

function AGY_MohoBridge:GetBridgeDir()
	local envDir = os.getenv("MOHO_BRIDGE_DIR")
	if envDir and envDir ~= "" then
		return envDir
	end
	local tmp = os.getenv("TEMP") or os.getenv("TMP") or os.getenv("TMPDIR") or "/tmp"
	local sep = (package.config:sub(1, 1) == "\\") and "\\" or "/"
	if tmp:sub(-1) == sep then
		return tmp .. "agy-moho-bridge"
	end
	return tmp .. sep .. "agy-moho-bridge"
end

function AGY_MohoBridge:JoinPath(dir, name)
	local sep = (package.config:sub(1, 1) == "\\") and "\\" or "/"
	if dir:sub(-1) == sep then
		return dir .. name
	end
	return dir .. sep .. name
end

function AGY_MohoBridge:WriteFileAtomic(targetPath, content)
	local tmpPath = targetPath .. ".tmp_" .. tostring(math.floor(os.clock() * 100000))
	local f = io.open(tmpPath, "wb")
	if not f then
		-- Fallback direct write if tmp cannot be created
		local df = io.open(targetPath, "wb")
		if not df then return false end
		df:write(content)
		df:close()
		return true
	end
	f:write(content)
	f:close()
	os.remove(targetPath)
	local ok = os.rename(tmpPath, targetPath)
	if not ok then
		-- Fallback copy if rename failed on busy handle
		local df = io.open(targetPath, "wb")
		if df then
			df:write(content)
			df:close()
			os.remove(tmpPath)
			return true
		end
		return false
	end
	return true
end

function AGY_MohoBridge:WriteHeartbeat(moho, force)
	local now = os.clock()
	if (not force) and (now - self._lastHeartbeat < 1.5) then
		return
	end
	self._lastHeartbeat = now

	if not AGY_JSON then return end
	local dir = self:GetBridgeDir()
	local hbPath = self:JoinPath(dir, "heartbeat.json")

	local docInfo = nil
	if moho and moho.document then
		local doc = moho.document
		docInfo = {
			name = doc:Name(),
			path = doc:Path(),
			width = doc:Width(),
			height = doc:Height(),
			fps = doc:Fps(),
			startFrame = doc:StartFrame(),
			endFrame = doc:EndFrame(),
			currentFrame = moho.frame,
			layerCount = doc:CountLayers()
		}
	end

	local payload = {
		bridgeVersion = self.VERSION,
		luaVersion = _VERSION,
		timestamp = os.time(),
		clock = now,
		enabled = self.enabled,
		wrappedToolsCount = self._wrappedToolsCount,
		commandsExecuted = self._commandsExecuted,
		lastCommandId = self._lastCommandId,
		lastError = self._lastError,
		document = docInfo
	}

	self:WriteFileAtomic(hbPath, AGY_JSON.encode(payload))
end

function AGY_MohoBridge:ProcessQueue(moho, force)
	if not self.enabled or self._busy then
		return false
	end
	if not AGY_JSON then
		return false
	end

	local now = os.clock()
	if (not force) and (now - self._lastPoll < 0.05) then
		return false
	end
	self._lastPoll = now

	self:WriteHeartbeat(moho, force)

	local dir = self:GetBridgeDir()
	local reqPath = self:JoinPath(dir, "req_active.json")
	local f = io.open(reqPath, "rb")
	if not f then
		return false
	end

	local raw = f:read("*a")
	f:close()
	os.remove(reqPath)

	if not raw or raw == "" then
		return false
	end

	self._busy = true
	local reqId = "unknown"
	local response = { ok = false, id = reqId, error = "Uninitialized" }

	pcall(function()
		local parseOk, req = pcall(AGY_JSON.decode, raw)
		if not parseOk or type(req) ~= "table" then
			response = {
				ok = false,
				id = reqId,
				error = "Invalid request JSON: " .. tostring(req)
			}
			self._lastError = response.error
		else
			reqId = tostring(req.id or "unknown")
			self._lastCommandId = reqId

			local execOk, execResult = xpcall(function()
				local action = req.action or "eval"
				if action == "ping" then
					return {
						pong = true,
						bridgeVersion = self.VERSION,
						luaVersion = _VERSION,
						timestamp = os.time(),
						hasDocument = (moho ~= nil and moho.document ~= nil)
					}
				elseif action == "eval" then
					local code = tostring(req.code or "")
					local args = req.args or {}
					local fn, loadErr = load(code, "agy_eval_" .. reqId, "t", _ENV)
					if not fn then
						error("Lua syntax error: " .. tostring(loadErr), 0)
					end
					local res = fn(moho, args)
					if req.update_ui ~= false and moho then
						pcall(function() moho:UpdateUI() end)
					end
					return res
				else
					error("Unknown bridge action: " .. tostring(action), 0)
				end
			end, function(err)
				return debug.traceback(tostring(err), 2)
			end)

			if execOk then
				self._commandsExecuted = self._commandsExecuted + 1
				self._lastError = ""
				response = {
					ok = true,
					id = reqId,
					result = execResult
				}
			else
				self._lastError = tostring(execResult)
				response = {
					ok = false,
					id = reqId,
					error = tostring(execResult)
				}
			end
		end

		local resPath = self:JoinPath(dir, "res_" .. reqId .. ".json")
		local encOk, encoded = pcall(AGY_JSON.encode, response)
		if not encOk then
			local fbOk, fbEncoded = pcall(AGY_JSON.encode, {
				ok = false,
				id = reqId,
				error = "JSON encode error: " .. tostring(encoded)
			})
			encoded = fbOk and fbEncoded or '{"ok":false,"error":"JSON encode failed"}'
		end
		pcall(function() self:WriteFileAtomic(resPath, encoded) end)
		pcall(function() self:WriteHeartbeat(moho, true) end)
	end)

	self._busy = false
	return true
end

-- Moho calls IsRelevant & IsEnabled on ALL tools during UI refresh!
function AGY_MohoBridge:IsRelevant(moho)
	self:InstallUniversalHooks()
	self:ProcessQueue(moho, false)
	return true
end

function AGY_MohoBridge:IsEnabled(moho)
	self:InstallUniversalHooks()
	self:ProcessQueue(moho, false)
	return true
end

function AGY_MohoBridge:UpdateWidgets(moho)
	self:ProcessQueue(moho, false)
end

function AGY_MohoBridge:DrawMe(moho, view)
	self:ProcessQueue(moho, false)
end

function AGY_MohoBridge:OnMouseDown(moho, mouseEvent)
	self:ProcessQueue(moho, true)
end
