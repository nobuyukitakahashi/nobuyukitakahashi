"use strict";

/**
 * Float-Preserving JSON Parser & Serializer for Moho Pro 14.5.1 (Project.mohoproj).
 *
 * Moho's C++ JSON loader strictly distinguishes integer vs double tokens (e.g. `0` vs `0.0`, `24` vs `24.0`).
 * Standard JS JSON.parse/stringify strips `.0` from whole-number floats, causing Moho Error (108).
 *
 * This module parses JSON into ordinary JS values while recording exact & array-wildcard paths
 * whose numeric tokens contained a decimal point or exponent, and re-emits `.0` on serialization.
 */

const KNOWN_MOHO_FLOAT_PATHS = new Set([
  "project_data.fps",
  "project_data.focus_distance",
  "project_data.focus_range",
  "project_data.focus_blur",
  "project_data.stereo_separation"
]);

/**
 * Parse JSON text while tracking all exact paths and array-wildcard paths that were floats.
 */
function parseMohoJson(text) {
  const src = String(text).replace(/^\uFEFF/, "");
  let pos = 0;
  const len = src.length;
  const exactFloatPaths = new Set(KNOWN_MOHO_FLOAT_PATHS);
  const wildcardFloatPaths = new Set(KNOWN_MOHO_FLOAT_PATHS);

  function skipWs() {
    while (pos < len) {
      const ch = src.charCodeAt(pos);
      if (ch === 32 || ch === 9 || ch === 10 || ch === 13) pos++;
      else break;
    }
  }

  function parseString() {
    const start = pos;
    pos++; // opening quote
    while (pos < len) {
      const ch = src.charCodeAt(pos);
      if (ch === 92) { // backslash
        pos += 2;
      } else if (ch === 34) { // closing quote
        pos++;
        return JSON.parse(src.slice(start, pos));
      } else {
        pos++;
      }
    }
    throw new Error(`Unterminated JSON string at offset ${start}`);
  }

  function parseNumber(exactPath, wildPath) {
    const start = pos;
    if (src.charCodeAt(pos) === 45) pos++; // '-'
    while (pos < len && src.charCodeAt(pos) >= 48 && src.charCodeAt(pos) <= 57) pos++;
    let isFloatToken = false;
    if (pos < len && src.charCodeAt(pos) === 46) { // '.'
      isFloatToken = true;
      pos++;
      while (pos < len && src.charCodeAt(pos) >= 48 && src.charCodeAt(pos) <= 57) pos++;
    }
    if (pos < len && (src.charCodeAt(pos) === 101 || src.charCodeAt(pos) === 69)) { // 'e'/'E'
      isFloatToken = true;
      pos++;
      if (pos < len && (src.charCodeAt(pos) === 43 || src.charCodeAt(pos) === 45)) pos++;
      while (pos < len && src.charCodeAt(pos) >= 48 && src.charCodeAt(pos) <= 57) pos++;
    }
    const token = src.slice(start, pos);
    const num = Number(token);
    if (Number.isNaN(num)) {
      throw new Error(`Invalid JSON number "${token}" at offset ${start}`);
    }
    if (isFloatToken) {
      exactFloatPaths.add(exactPath);
      wildcardFloatPaths.add(wildPath);
    }
    return num;
  }

  function parseArray(exactPath, wildPath) {
    pos++; // '['
    skipWs();
    const arr = [];
    if (src.charCodeAt(pos) === 93) { // ']'
      pos++;
      return arr;
    }
    let idx = 0;
    while (pos < len) {
      skipWs();
      const childExact = exactPath ? `${exactPath}.${idx}` : String(idx);
      const childWild = wildPath ? `${wildPath}.*` : "*";
      arr.push(parseValue(childExact, childWild));
      idx++;
      skipWs();
      const ch = src.charCodeAt(pos);
      if (ch === 93) { // ']'
        pos++;
        return arr;
      } else if (ch === 44) { // ','
        pos++;
      } else {
        throw new Error(`Expected ',' or ']' in JSON array at offset ${pos}`);
      }
    }
    throw new Error("Unterminated JSON array");
  }

  function parseObject(exactPath, wildPath) {
    pos++; // '{'
    skipWs();
    const obj = {};
    if (src.charCodeAt(pos) === 125) { // '}'
      pos++;
      return obj;
    }
    while (pos < len) {
      skipWs();
      if (src.charCodeAt(pos) !== 34) {
        throw new Error(`Expected string key in JSON object at offset ${pos}`);
      }
      const key = parseString();
      skipWs();
      if (src.charCodeAt(pos) !== 58) { // ':'
        throw new Error(`Expected ':' after key "${key}" at offset ${pos}`);
      }
      pos++;
      skipWs();
      const childExact = exactPath ? `${exactPath}.${key}` : key;
      const childWild = wildPath ? `${wildPath}.${key}` : key;
      obj[key] = parseValue(childExact, childWild);
      skipWs();
      const ch = src.charCodeAt(pos);
      if (ch === 125) { // '}'
        pos++;
        return obj;
      } else if (ch === 44) { // ','
        pos++;
      } else {
        throw new Error(`Expected ',' or '}' in JSON object at offset ${pos}`);
      }
    }
    throw new Error("Unterminated JSON object");
  }

  function parseValue(exactPath, wildPath) {
    skipWs();
    const ch = src.charCodeAt(pos);
    if (ch === 123) return parseObject(exactPath, wildPath); // '{'
    if (ch === 91) return parseArray(exactPath, wildPath);   // '['
    if (ch === 34) return parseString();                     // '"'
    if (ch === 45 || (ch >= 48 && ch <= 57)) return parseNumber(exactPath, wildPath);
    if (src.startsWith("true", pos)) { pos += 4; return true; }
    if (src.startsWith("false", pos)) { pos += 5; return false; }
    if (src.startsWith("null", pos)) { pos += 4; return null; }
    throw new Error(`Unexpected JSON token "${src.slice(pos, pos + 16)}" at offset ${pos}`);
  }

  const data = parseValue("", "");
  return {
    data,
    floatMeta: { exactFloatPaths, wildcardFloatPaths }
  };
}

/**
 * Serialize JS value back to Moho-compatible JSON, preserving `.0` for float fields.
 */
function stringifyMohoJson(value, floatMeta = null, indent = 0) {
  const exactSet = floatMeta && floatMeta.exactFloatPaths ? floatMeta.exactFloatPaths : KNOWN_MOHO_FLOAT_PATHS;
  const wildSet = floatMeta && floatMeta.wildcardFloatPaths ? floatMeta.wildcardFloatPaths : KNOWN_MOHO_FLOAT_PATHS;
  const padUnit = typeof indent === "number" && indent > 0 ? " ".repeat(indent) : (typeof indent === "string" ? indent : "");

  function isFloatPath(exactPath, wildPath) {
    return exactSet.has(exactPath) || wildSet.has(wildPath);
  }

  function formatNumber(num, exactPath, wildPath) {
    if (!Number.isFinite(num)) return "null";
    const s = String(num);
    if (s.includes(".") || s.includes("e") || s.includes("E")) {
      return s;
    }
    if (isFloatPath(exactPath, wildPath)) {
      return `${s}.0`;
    }
    return s;
  }

  function emit(val, exactPath, wildPath, depth) {
    if (val === null || val === undefined) return "null";
    const t = typeof val;
    if (t === "boolean") return val ? "true" : "false";
    if (t === "number") return formatNumber(val, exactPath, wildPath);
    if (t === "string") return JSON.stringify(val);

    if (Array.isArray(val)) {
      if (val.length === 0) return "[]";
      const items = [];
      for (let i = 0; i < val.length; i++) {
        const ce = exactPath ? `${exactPath}.${i}` : String(i);
        const cw = wildPath ? `${wildPath}.*` : "*";
        items.push(emit(val[i], ce, cw, depth + 1));
      }
      if (!padUnit) return `[${items.join(",")}]`;
      const nl = "\n" + padUnit.repeat(depth + 1);
      const closeNl = "\n" + padUnit.repeat(depth);
      return `[${nl}${items.join(`,${nl}`)}${closeNl}]`;
    }

    if (t === "object") {
      const keys = Object.keys(val).filter((k) => val[k] !== undefined && typeof val[k] !== "function");
      if (keys.length === 0) return "{}";
      const pairs = [];
      const sep = padUnit ? ": " : ":";
      for (const k of keys) {
        const ce = exactPath ? `${exactPath}.${k}` : k;
        const cw = wildPath ? `${wildPath}.${k}` : k;
        pairs.push(`${JSON.stringify(k)}${sep}${emit(val[k], ce, cw, depth + 1)}`);
      }
      if (!padUnit) return `{${pairs.join(",")}}`;
      const nl = "\n" + padUnit.repeat(depth + 1);
      const closeNl = "\n" + padUnit.repeat(depth);
      return `{${nl}${pairs.join(`,${nl}`)}${closeNl}}`;
    }

    return "null";
  }

  return emit(value, "", "", 0);
}

module.exports = {
  parseMohoJson,
  stringifyMohoJson
};
