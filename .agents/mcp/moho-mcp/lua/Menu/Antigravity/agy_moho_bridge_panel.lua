-- **************************************************
-- Antigravity Moho Control - Menu Status & Control Panel
-- Menu: Scripts > Antigravity > Moho Control Bridge...
-- **************************************************

ScriptName = "AGY_MohoBridgePanel"

AGY_MohoBridgePanel = {}

function AGY_MohoBridgePanel:Name()
	return "Moho Control Bridge"
end

function AGY_MohoBridgePanel:Version()
	return "1.0.0"
end

function AGY_MohoBridgePanel:Description()
	return "Open Antigravity Moho Live Bridge status & manual queue panel"
end

function AGY_MohoBridgePanel:Creator()
	return "Antigravity"
end

function AGY_MohoBridgePanel:UILabel()
	return "Moho Control Bridge..."
end

local AGY_BridgeDialog = {}
AGY_BridgeDialog.MSG_TOGGLE = MOHO.MSG_BASE
AGY_BridgeDialog.MSG_POLL_NOW = MOHO.MSG_BASE + 1
AGY_BridgeDialog.MSG_REFRESH = MOHO.MSG_BASE + 2

function AGY_BridgeDialog:new(moho)
	local d = LM.GUI.SimpleDialog("Antigravity Moho Bridge", AGY_BridgeDialog)
	local l = d:GetLayout()
	d.moho = moho

	d.statusText = LM.GUI.DynamicText("Status: Ready", 320)
	l:AddChild(d.statusText, LM.GUI.ALIGN_LEFT)

	d.dirText = LM.GUI.DynamicText("IPC Dir: ...", 320)
	l:AddChild(d.dirText, LM.GUI.ALIGN_LEFT)

	d.countText = LM.GUI.DynamicText("Commands Executed: 0", 320)
	l:AddChild(d.countText, LM.GUI.ALIGN_LEFT)

	d.enableCheck = LM.GUI.CheckBox("Enable Auto-Poll Bridge", AGY_BridgeDialog.MSG_TOGGLE)
	l:AddChild(d.enableCheck, LM.GUI.ALIGN_LEFT)

	l:PushH()
		d.pollBtn = LM.GUI.Button("Process Queue Now", AGY_BridgeDialog.MSG_POLL_NOW)
		l:AddChild(d.pollBtn)
		d.refreshBtn = LM.GUI.Button("Refresh Status", AGY_BridgeDialog.MSG_REFRESH)
		l:AddChild(d.refreshBtn)
	l:Pop()

	return d
end

function AGY_BridgeDialog:UpdateWidgets()
	if AGY_MohoBridge then
		self.enableCheck:SetValue(AGY_MohoBridge.enabled)
		self.statusText:SetValue("Status: " .. (AGY_MohoBridge.enabled and "ACTIVE (Listening)" or "PAUSED"))
		self.dirText:SetValue("IPC Dir: " .. AGY_MohoBridge:GetBridgeDir())
		self.countText:SetValue("Commands Executed: " .. tostring(AGY_MohoBridge._commandsExecuted or 0))
	else
		self.statusText:SetValue("Status: AGY_MohoBridge Tool not loaded")
	end
end

function AGY_BridgeDialog:HandleMessage(msg)
	if not AGY_MohoBridge then return end
	if msg == AGY_BridgeDialog.MSG_TOGGLE then
		AGY_MohoBridge.enabled = self.enableCheck:Value()
		AGY_MohoBridge:WriteHeartbeat(self.moho, true)
		self:UpdateWidgets()
	elseif msg == AGY_BridgeDialog.MSG_POLL_NOW then
		AGY_MohoBridge:ProcessQueue(self.moho, true)
		self:UpdateWidgets()
	elseif msg == AGY_BridgeDialog.MSG_REFRESH then
		AGY_MohoBridge:WriteHeartbeat(self.moho, true)
		self:UpdateWidgets()
	end
end

function AGY_MohoBridgePanel:IsEnabled(moho)
	return true
end

function AGY_MohoBridgePanel:Run(moho)
	if AGY_MohoBridge then
		AGY_MohoBridge:ProcessQueue(moho, true)
	end
	local dlog = AGY_BridgeDialog:new(moho)
	dlog:DoModeless()
end
