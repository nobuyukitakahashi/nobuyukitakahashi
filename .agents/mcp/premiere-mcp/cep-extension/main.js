(function () {
  var fs = require("fs");
  var path = require("path");
  var os = require("os");

  var bridgeRoot = path.join(os.tmpdir(), "antigravity-premiere-mcp-bridge");
  var reqDir = path.join(bridgeRoot, "requests");
  var resDir = path.join(bridgeRoot, "responses");
  var heartbeatPath = path.join(bridgeRoot, "heartbeat.json");

  function ensureDirs() {
    [bridgeRoot, reqDir, resDir].forEach(function (d) {
      if (!fs.existsSync(d)) {
        fs.mkdirSync(d, { recursive: true });
      }
    });
  }

  function appendLog(msg) {
    var el = document.getElementById("log");
    if (!el) return;
    var ts = new Date().toTimeString().slice(0, 8);
    var lines = (el.textContent + "\n[" + ts + "] " + msg).split("\n");
    if (lines.length > 40) lines = lines.slice(lines.length - 40);
    el.textContent = lines.join("\n");
    el.scrollTop = el.scrollHeight;
  }

  function writeHeartbeat() {
    try {
      ensureDirs();
      var tmp = heartbeatPath + ".tmp";
      var data = JSON.stringify({
        ok: true,
        extensionId: "com.antigravity.premiere.mcp.panel",
        updatedAt: Date.now(),
        isoTime: new Date().toISOString()
      });
      fs.writeFileSync(tmp, data, "utf8");
      fs.renameSync(tmp, heartbeatPath);
    } catch (_) {}
  }

  function evalPremiereScript(jsxCode, cb) {
    if (window.__adobe_cep__ && typeof window.__adobe_cep__.evalScript === "function") {
      window.__adobe_cep__.evalScript(jsxCode, cb);
    } else {
      cb(JSON.stringify({ ok: false, error: "__adobe_cep__.evalScript is unavailable." }));
    }
  }

  var processing = false;
  function pollRequests() {
    if (processing) return;
    processing = true;
    try {
      ensureDirs();
      var files = fs.readdirSync(reqDir).filter(function (f) {
        return f.endsWith(".json");
      }).sort();
      if (files.length === 0) {
        processing = false;
        return;
      }

      var fileName = files[0];
      var reqPath = path.join(reqDir, fileName);
      var raw = fs.readFileSync(reqPath, "utf8");
      var req = JSON.parse(raw);
      try { fs.unlinkSync(reqPath); } catch (_) {}

      appendLog("Exec: " + req.id);
      evalPremiereScript(req.script, function (evalResult) {
        try {
          var outPath = path.join(resDir, req.id + ".json");
          var tmpOut = outPath + ".tmp";
          var payload = JSON.stringify({
            id: req.id,
            rawResult: evalResult,
            finishedAt: Date.now()
          });
          fs.writeFileSync(tmpOut, payload, "utf8");
          fs.renameSync(tmpOut, outPath);
          appendLog("Done: " + req.id);
        } catch (err) {
          appendLog("Write error: " + err.message);
        } finally {
          processing = false;
        }
      });
    } catch (err) {
      appendLog("Poll error: " + err.message);
      processing = false;
    }
  }

  ensureDirs();
  var qEl = document.getElementById("queueDir");
  if (qEl) qEl.textContent = "Queue: " + bridgeRoot;
  writeHeartbeat();
  appendLog("Listening for MCP requests...");

  setInterval(writeHeartbeat, 1500);
  setInterval(pollRequests, 100);
})();
