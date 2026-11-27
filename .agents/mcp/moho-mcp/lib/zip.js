"use strict";

/**
 * Minimal, zero-dependency ZIP reader/writer built on Node.js `zlib`.
 * Supports STORE (0) and DEFLATE (8) compression, UTF-8 filenames (GP flag bit 11),
 * and standard .moho archive structure.
 */

const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

// Precompute standard IEEE 802.3 CRC-32 table
const CRC_TABLE = new Uint32Array(256);
for (let i = 0; i < 256; i++) {
  let c = i;
  for (let k = 0; k < 8; k++) {
    c = (c & 1) ? (0xedb88320 ^ (c >>> 1)) : (c >>> 1);
  }
  CRC_TABLE[i] = c >>> 0;
}

function crc32(buf) {
  let c = 0xffffffff;
  for (let i = 0; i < buf.length; i++) {
    c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  }
  return (c ^ 0xffffffff) >>> 0;
}

function toDosTimeDate(date = new Date()) {
  const year = Math.max(1980, date.getFullYear());
  const dosTime =
    ((date.getHours() & 0x1f) << 11) |
    ((date.getMinutes() & 0x3f) << 5) |
    ((date.getSeconds() >> 1) & 0x1f);
  const dosDate =
    (((year - 1980) & 0x7f) << 9) |
    (((date.getMonth() + 1) & 0x0f) << 5) |
    (date.getDate() & 0x1f);
  return { dosTime, dosDate };
}

/**
 * Read a ZIP archive buffer and return Map<entryName, Buffer>.
 */
function readZipBuffer(buf) {
  if (!Buffer.isBuffer(buf) || buf.length < 22) {
    throw new Error("Invalid ZIP archive: buffer too small");
  }

  // Locate End of Central Directory (EOCD) signature 0x06054b50
  const maxBack = Math.min(buf.length, 65557);
  let eocdOffset = -1;
  for (let i = buf.length - 22; i >= buf.length - maxBack; i--) {
    if (
      buf[i] === 0x50 &&
      buf[i + 1] === 0x4b &&
      buf[i + 2] === 0x05 &&
      buf[i + 3] === 0x06
    ) {
      eocdOffset = i;
      break;
    }
  }
  if (eocdOffset === -1) {
    throw new Error("Invalid ZIP archive: EOCD signature not found");
  }

  const totalEntries = buf.readUInt16LE(eocdOffset + 10);
  const cdOffset = buf.readUInt32LE(eocdOffset + 16);

  const entries = new Map();
  let ptr = cdOffset;

  for (let i = 0; i < totalEntries; i++) {
    if (ptr + 46 > buf.length || buf.readUInt32LE(ptr) !== 0x02014b50) {
      throw new Error(`Invalid ZIP Central Directory header at offset ${ptr}`);
    }
    const method = buf.readUInt16LE(ptr + 10);
    const compSize = buf.readUInt32LE(ptr + 20);
    const nameLen = buf.readUInt16LE(ptr + 28);
    const extraLen = buf.readUInt16LE(ptr + 30);
    const commentLen = buf.readUInt16LE(ptr + 32);
    const localHeaderOffset = buf.readUInt32LE(ptr + 42);

    const name = buf.slice(ptr + 46, ptr + 46 + nameLen).toString("utf8");
    ptr += 46 + nameLen + extraLen + commentLen;

    // Skip directory entries
    if (name.endsWith("/")) continue;

    if (localHeaderOffset + 30 > buf.length || buf.readUInt32LE(localHeaderOffset) !== 0x04034b50) {
      throw new Error(`Invalid ZIP local file header for "${name}"`);
    }
    const lNameLen = buf.readUInt16LE(localHeaderOffset + 26);
    const lExtraLen = buf.readUInt16LE(localHeaderOffset + 28);
    const dataStart = localHeaderOffset + 30 + lNameLen + lExtraLen;
    const compData = buf.slice(dataStart, dataStart + compSize);

    let rawData;
    if (method === 0) {
      rawData = Buffer.from(compData);
    } else if (method === 8) {
      rawData = zlib.inflateRawSync(compData);
    } else {
      throw new Error(`Unsupported ZIP compression method ${method} for "${name}"`);
    }
    entries.set(name, rawData);
  }

  return entries;
}

/**
 * Read a ZIP archive from disk.
 */
function readZipFile(zipPath) {
  const resolved = path.resolve(zipPath);
  if (!fs.existsSync(resolved)) {
    throw new Error(`Archive not found: ${resolved}`);
  }
  return readZipBuffer(fs.readFileSync(resolved));
}

/**
 * Create a ZIP archive Buffer from a Map<entryName, Buffer|string> or array of {name, data, compress}.
 */
function createZipBuffer(entriesInput) {
  const list = [];
  if (entriesInput instanceof Map) {
    for (const [name, data] of entriesInput.entries()) {
      list.push({ name, data });
    }
  } else if (Array.isArray(entriesInput)) {
    for (const item of entriesInput) {
      list.push(item);
    }
  } else if (entriesInput && typeof entriesInput === "object") {
    for (const name of Object.keys(entriesInput)) {
      list.push({ name, data: entriesInput[name] });
    }
  }

  const localParts = [];
  const cdParts = [];
  let offset = 0;
  const { dosTime, dosDate } = toDosTimeDate();

  for (const item of list) {
    const cleanName = String(item.name).replace(/\\/g, "/").replace(/^\/+/, "");
    const nameBuf = Buffer.from(cleanName, "utf8");
    const rawBuf = Buffer.isBuffer(item.data)
      ? item.data
      : Buffer.from(String(item.data), "utf8");

    const shouldCompress = item.compress !== false && rawBuf.length > 0;
    const compBuf = shouldCompress ? zlib.deflateRawSync(rawBuf, { level: 6 }) : rawBuf;
    const useDeflate = shouldCompress && compBuf.length < rawBuf.length;
    const finalBuf = useDeflate ? compBuf : rawBuf;
    const method = useDeflate ? 8 : 0;
    const crc = crc32(rawBuf);
    const gpFlag = 0x0800; // UTF-8 filename encoding

    // Local File Header (30 bytes + filename)
    const lfh = Buffer.alloc(30);
    lfh.writeUInt32LE(0x04034b50, 0);
    lfh.writeUInt16LE(20, 4); // version needed 2.0
    lfh.writeUInt16LE(gpFlag, 6);
    lfh.writeUInt16LE(method, 8);
    lfh.writeUInt16LE(dosTime, 10);
    lfh.writeUInt16LE(dosDate, 12);
    lfh.writeUInt32LE(crc, 14);
    lfh.writeUInt32LE(finalBuf.length, 18);
    lfh.writeUInt32LE(rawBuf.length, 22);
    lfh.writeUInt16LE(nameBuf.length, 26);
    lfh.writeUInt16LE(0, 28);

    localParts.push(lfh, nameBuf, finalBuf);

    // Central Directory Header (46 bytes + filename)
    const cdh = Buffer.alloc(46);
    cdh.writeUInt32LE(0x02014b50, 0);
    cdh.writeUInt16LE(20, 4); // version made by
    cdh.writeUInt16LE(20, 6); // version needed
    cdh.writeUInt16LE(gpFlag, 8);
    cdh.writeUInt16LE(method, 10);
    cdh.writeUInt16LE(dosTime, 12);
    cdh.writeUInt16LE(dosDate, 14);
    cdh.writeUInt32LE(crc, 16);
    cdh.writeUInt32LE(finalBuf.length, 20);
    cdh.writeUInt32LE(rawBuf.length, 24);
    cdh.writeUInt16LE(nameBuf.length, 28);
    cdh.writeUInt16LE(0, 30);
    cdh.writeUInt16LE(0, 32);
    cdh.writeUInt16LE(0, 34);
    cdh.writeUInt16LE(0, 36);
    cdh.writeUInt32LE(0, 38);
    cdh.writeUInt32LE(offset, 42);

    cdParts.push(cdh, nameBuf);
    offset += lfh.length + nameBuf.length + finalBuf.length;
  }

  const cdBuf = Buffer.concat(cdParts);
  const eocd = Buffer.alloc(22);
  eocd.writeUInt32LE(0x06054b50, 0);
  eocd.writeUInt16LE(0, 4);
  eocd.writeUInt16LE(0, 6);
  eocd.writeUInt16LE(list.length, 8);
  eocd.writeUInt16LE(list.length, 10);
  eocd.writeUInt32LE(cdBuf.length, 12);
  eocd.writeUInt32LE(offset, 16);
  eocd.writeUInt16LE(0, 20);

  return Buffer.concat([...localParts, cdBuf, eocd]);
}

/**
 * Write a ZIP archive atomically to disk.
 */
function writeZipFile(zipPath, entriesInput) {
  const resolved = path.resolve(zipPath);
  fs.mkdirSync(path.dirname(resolved), { recursive: true });
  const zipBuf = createZipBuffer(entriesInput);
  const tmpPath = `${resolved}.tmp_${process.pid}_${Date.now()}`;
  fs.writeFileSync(tmpPath, zipBuf);
  fs.renameSync(tmpPath, resolved);
  return resolved;
}

module.exports = {
  crc32,
  readZipBuffer,
  readZipFile,
  createZipBuffer,
  writeZipFile
};
