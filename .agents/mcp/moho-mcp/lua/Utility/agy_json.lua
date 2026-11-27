-- **************************************************
-- Antigravity Moho Control - Pure Lua 5.4 JSON Module
-- Auto-loaded globally by Moho from Scripts/Utility/
-- **************************************************

AGY_JSON = AGY_JSON or {}

local escape_map = {
	["\\"] = "\\\\",
	["\""] = "\\\"",
	["\b"] = "\\b",
	["\f"] = "\\f",
	["\n"] = "\\n",
	["\r"] = "\\r",
	["\t"] = "\\t"
}

local function escape_char(c)
	return escape_map[c] or string.format("\\u%04x", string.byte(c))
end

local function encode_string(s)
	return "\"" .. s:gsub("[%z\1-\31\\\"]", escape_char) .. "\""
end

local function is_array(tbl)
	local count = 0
	local max_idx = 0
	for k, _ in pairs(tbl) do
		if type(k) ~= "number" or k < 1 or math.floor(k) ~= k then
			return false, 0
		end
		if k > max_idx then max_idx = k end
		count = count + 1
	end
	if count == 0 then return false, 0 end
	return max_idx == count, count
end

local function encode_value(val, seen, depth)
	if depth > 40 then
		return "\"<max_depth>\""
	end
	local t = type(val)
	if val == nil then
		return "null"
	elseif t == "boolean" then
		return val and "true" or "false"
	elseif t == "number" then
		if val ~= val or val == math.huge or val == -math.huge then
			return "null"
		end
		return tostring(val)
	elseif t == "string" then
		return encode_string(val)
	elseif t == "table" then
		if seen[val] then
			return "\"<circular>\""
		end
		seen[val] = true
		local arr, count = is_array(val)
		local out
		if arr then
			local parts = {}
			for i = 1, count do
				parts[i] = encode_value(val[i], seen, depth + 1)
			end
			out = "[" .. table.concat(parts, ",") .. "]"
		else
			local parts = {}
			for k, v in pairs(val) do
				if type(k) == "string" or type(k) == "number" then
					if type(v) ~= "function" and type(v) ~= "thread" then
						table.insert(parts, encode_string(tostring(k)) .. ":" .. encode_value(v, seen, depth + 1))
					end
				end
			end
			out = "{" .. table.concat(parts, ",") .. "}"
		end
		seen[val] = nil
		return out
	else
		return encode_string(tostring(val))
	end
end

function AGY_JSON.encode(val)
	return encode_value(val, {}, 0)
end

-- **************************************************
-- JSON Decoder (RFC 8259 compliant, UTF-8 safe)
-- **************************************************

local function utf8_from_codepoint(cp)
	if cp <= 0x7F then
		return string.char(cp)
	elseif cp <= 0x7FF then
		return string.char(
			0xC0 + math.floor(cp / 0x40),
			0x80 + (cp % 0x40)
		)
	elseif cp <= 0xFFFF then
		return string.char(
			0xE0 + math.floor(cp / 0x1000),
			0x80 + (math.floor(cp / 0x40) % 0x40),
			0x80 + (cp % 0x40)
		)
	elseif cp <= 0x10FFFF then
		return string.char(
			0xF0 + math.floor(cp / 0x40000),
			0x80 + (math.floor(cp / 0x1000) % 0x40),
			0x80 + (math.floor(cp / 0x40) % 0x40),
			0x80 + (cp % 0x40)
		)
	end
	return "?"
end

local decode_value

local function skip_ws(str, pos)
	local _, e = str:find("^[ \t\r\n]*", pos)
	return (e or (pos - 1)) + 1
end

local function decode_string(str, pos)
	pos = pos + 1 -- skip opening quote
	local chunks = {}
	local len = #str
	while pos <= len do
		local c = str:sub(pos, pos)
		if c == "\"" then
			return table.concat(chunks), pos + 1
		elseif c == "\\" then
			local nxt = str:sub(pos + 1, pos + 1)
			if nxt == "\"" or nxt == "\\" or nxt == "/" then
				table.insert(chunks, nxt)
				pos = pos + 2
			elseif nxt == "b" then table.insert(chunks, "\b"); pos = pos + 2
			elseif nxt == "f" then table.insert(chunks, "\f"); pos = pos + 2
			elseif nxt == "n" then table.insert(chunks, "\n"); pos = pos + 2
			elseif nxt == "r" then table.insert(chunks, "\r"); pos = pos + 2
			elseif nxt == "t" then table.insert(chunks, "\t"); pos = pos + 2
			elseif nxt == "u" then
				local hex = str:sub(pos + 2, pos + 5)
				local cp = tonumber(hex, 16)
				if not cp then error("Invalid unicode escape at pos " .. pos) end
				pos = pos + 6
				if cp >= 0xD800 and cp <= 0xDBFF and str:sub(pos, pos + 1) == "\\u" then
					local lowHex = str:sub(pos + 2, pos + 5)
					local low = tonumber(lowHex, 16)
					if low and low >= 0xDC00 and low <= 0xDFFF then
						cp = 0x10000 + ((cp - 0xD800) * 0x400) + (low - 0xDC00)
						pos = pos + 6
					end
				end
				table.insert(chunks, utf8_from_codepoint(cp))
			else
				error("Invalid escape sequence \\" .. nxt .. " at pos " .. pos)
			end
		else
			local nextSpecial = str:find("[\"\\]", pos)
			if not nextSpecial then
				error("Unterminated string")
			end
			table.insert(chunks, str:sub(pos, nextSpecial - 1))
			pos = nextSpecial
		end
	end
	error("Unterminated string")
end

local function decode_number(str, pos)
	local s, e = str:find("^-?%d+%.?%d*[eE]?[+-]?%d*", pos)
	if not s then error("Invalid number at pos " .. pos) end
	local num = tonumber(str:sub(s, e))
	if not num then error("Failed to parse number at pos " .. pos) end
	return num, e + 1
end

local function decode_array(str, pos)
	pos = skip_ws(str, pos + 1)
	local arr = {}
	if str:sub(pos, pos) == "]" then
		return arr, pos + 1
	end
	local idx = 1
	while true do
		local val
		val, pos = decode_value(str, pos)
		arr[idx] = val
		idx = idx + 1
		pos = skip_ws(str, pos)
		local c = str:sub(pos, pos)
		if c == "]" then
			return arr, pos + 1
		elseif c == "," then
			pos = skip_ws(str, pos + 1)
		else
			error("Expected ',' or ']' in array at pos " .. pos)
		end
	end
end

local function decode_object(str, pos)
	pos = skip_ws(str, pos + 1)
	local obj = {}
	if str:sub(pos, pos) == "}" then
		return obj, pos + 1
	end
	while true do
		if str:sub(pos, pos) ~= "\"" then
			error("Expected string key in object at pos " .. pos)
		end
		local key
		key, pos = decode_string(str, pos)
		pos = skip_ws(str, pos)
		if str:sub(pos, pos) ~= ":" then
			error("Expected ':' after key at pos " .. pos)
		end
		pos = skip_ws(str, pos + 1)
		local val
		val, pos = decode_value(str, pos)
		obj[key] = val
		pos = skip_ws(str, pos)
		local c = str:sub(pos, pos)
		if c == "}" then
			return obj, pos + 1
		elseif c == "," then
			pos = skip_ws(str, pos + 1)
		else
			error("Expected ',' or '}' in object at pos " .. pos)
		end
	end
end

decode_value = function(str, pos)
	pos = skip_ws(str, pos)
	local c = str:sub(pos, pos)
	if c == "\"" then
		return decode_string(str, pos)
	elseif c == "{" then
		return decode_object(str, pos)
	elseif c == "[" then
		return decode_array(str, pos)
	elseif c == "-" or (c >= "0" and c <= "9") then
		return decode_number(str, pos)
	elseif str:sub(pos, pos + 3) == "true" then
		return true, pos + 4
	elseif str:sub(pos, pos + 4) == "false" then
		return false, pos + 5
	elseif str:sub(pos, pos + 3) == "null" then
		return nil, pos + 4
	else
		error("Unexpected character '" .. c .. "' at pos " .. pos)
	end
end

function AGY_JSON.decode(str)
	if type(str) ~= "string" then
		error("AGY_JSON.decode expects string")
	end
	-- Strip UTF-8 BOM if present
	if str:sub(1, 3) == "\239\187\191" then
		str = str:sub(4)
	end
	local val, pos = decode_value(str, 1)
	return val
end
