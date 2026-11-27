"use strict";

/**
 * Unified Moho Pro 14.5.1 Tool Definitions & Dispatcher
 * Shared by both MCP Server (server.js) and CLI Bridge (cli.js).
 */

const { detectMohoEnvironment } = require("./env");
const {
  inspectMohoFile,
  createMohoFile,
  patchMohoFile,
  unpackMohoFile,
  packMohoFile
} = require("./moho-file");
const { renderMoho, renderPreviewFrame } = require("./cli-render");
const { launchMohoGui, nudgeMohoWindow, triggerReloadScriptsWindows } = require("./win32-nudge");
const {
  pingLiveBridge,
  executeMohoLua,
  getLiveDocumentSummary,
  liveManageLayers,
  liveDrawVector,
  liveRigBones,
  liveAnimate
} = require("./live-bridge");

const TOOLS_DEFINITION = [
  {
    name: "get_moho_status",
    description:
      "Detect Moho Pro 14.x installation, Custom Content Folder (EditableFilesDir), running processes, Lua bridge deployment, and live heartbeat status.",
    inputSchema: {
      type: "object",
      properties: {
        ping_live: {
          type: "boolean",
          description: "If true and Moho is running, actively ping the Live Lua Bridge."
        }
      }
    }
  },
  {
    name: "inspect_moho_file",
    description:
      "Headlessly inspect any .moho project archive (ZIP + Project.mohoproj JSON) without opening Moho GUI: dimensions, FPS, frame range, styles, layercomps, and full recursive layer/mesh/skeleton tree.",
    inputSchema: {
      type: "object",
      properties: {
        moho_path: { type: "string", description: "Absolute path to .moho project file." }
      },
      required: ["moho_path"]
    }
  },
  {
    name: "create_moho_file",
    description:
      "Headlessly create a brand-new, Moho 14.5.1 compliant .moho project file with custom resolution, FPS, frame range, background color, and initial layers.",
    inputSchema: {
      type: "object",
      properties: {
        output_path: { type: "string", description: "Destination .moho file path." },
        width: { type: "number", description: "Canvas width in pixels (default 1920)." },
        height: { type: "number", description: "Canvas height in pixels (default 1080)." },
        fps: { type: "number", description: "Frames per second (default 24)." },
        start_frame: { type: "number", description: "Start frame (default 1)." },
        end_frame: { type: "number", description: "End frame (default 240)." },
        back_color: {
          type: "object",
          description: "Background RGBA color {r,g,b,a} (0-255).",
          properties: {
            r: { type: "number" },
            g: { type: "number" },
            b: { type: "number" },
            a: { type: "number" }
          }
        },
        layers: {
          type: "array",
          description: "Initial layer names or objects [{name}] (default ['Layer 1']).",
          items: { type: "string" }
        },
        comment: { type: "string" },
        template_path: { type: "string", description: "Optional custom template .moho file." },
        keep_template_layers: { type: "boolean", description: "If true, preserve all layers from template." }
      },
      required: ["output_path"]
    }
  },
  {
    name: "patch_moho_file",
    description:
      "Headlessly modify an existing .moho project file (resolution, FPS, frame range, background color, layer rename/visibility/origin, arbitrary dot-paths, or deep JSON merge).",
    inputSchema: {
      type: "object",
      properties: {
        moho_path: { type: "string", description: "Source .moho file path." },
        save_as: { type: "string", description: "Optional destination path (overwrites source if omitted)." },
        width: { type: "number" },
        height: { type: "number" },
        fps: { type: "number" },
        start_frame: { type: "number" },
        end_frame: { type: "number" },
        antialiasing: { type: "boolean" },
        back_color: { type: "object" },
        comment: { type: "string" },
        layer_updates: {
          type: "array",
          description: "Array of {name, rename?, visible?, origin?, render_only?, edit_only?}."
        },
        set_paths: {
          type: "object",
          description: "Map of dot-paths to values (e.g. {'project_data.fps': 30, 'layers.0.name': 'BG'})."
        },
        raw_patch: { type: "object", description: "Deep-merge JSON patch applied onto Project.mohoproj." }
      },
      required: ["moho_path"]
    }
  },
  {
    name: "unpack_moho_file",
    description: "Unpack a .moho archive into a directory with pretty-printed Project.mohoproj JSON (for Git version control or deep JSON editing).",
    inputSchema: {
      type: "object",
      properties: {
        moho_path: { type: "string" },
        output_dir: { type: "string" },
        pretty: { type: "boolean", description: "Pretty-print JSON (default true)." }
      },
      required: ["moho_path", "output_dir"]
    }
  },
  {
    name: "pack_moho_file",
    description: "Pack an unpacked directory containing Project.mohoproj and assets back into a valid .moho archive.",
    inputSchema: {
      type: "object",
      properties: {
        input_dir: { type: "string" },
        output_path: { type: "string" }
      },
      required: ["input_dir", "output_path"]
    }
  },
  {
    name: "render_moho",
    description:
      "Headlessly render a .moho project via Moho.exe -r to PNG/JPEG/TGA/BMP/QT/MP4/GIF/SVG with full control over frame range, layercomp, antialiasing, multithreading, and output folder.",
    inputSchema: {
      type: "object",
      properties: {
        moho_path: { type: "string" },
        format: { type: "string", description: "Output format: PNG, JPEG, TGA, BMP, QT, MP4, GIF, SVG (default PNG)." },
        outfolder: { type: "string", description: "Output directory." },
        output_path: { type: "string", description: "Explicit output file path (-o)." },
        start_frame: { type: "number" },
        end_frame: { type: "number" },
        layercomp: { type: "string" },
        aa: { type: "boolean" },
        extrasmooth: { type: "boolean" },
        halfsize: { type: "boolean" },
        halffps: { type: "boolean" },
        fewparticles: { type: "boolean" },
        multithread: { type: "boolean" },
        shapefx: { type: "boolean" },
        layerfx: { type: "boolean" },
        ntscsafe: { type: "boolean" },
        premultiply: { type: "boolean" },
        addformatsuffix: { type: "boolean" },
        timeout_ms: { type: "number" }
      },
      required: ["moho_path"]
    }
  },
  {
    name: "render_preview_frame",
    description: "Render a single frame of a .moho file directly to a specified PNG path for fast visual QA inspection.",
    inputSchema: {
      type: "object",
      properties: {
        moho_path: { type: "string" },
        frame: { type: "number", description: "Frame number to render (default 1)." },
        output_png: { type: "string", description: "Target PNG file path." },
        halfsize: { type: "boolean" }
      },
      required: ["moho_path"]
    }
  },
  {
    name: "open_in_moho",
    description: "Launch Moho Pro 14.5.1 GUI (optionally opening a .moho file), nudge window, or trigger script reload (Ctrl+Shift+Alt+L).",
    inputSchema: {
      type: "object",
      properties: {
        moho_path: { type: "string", description: "Optional .moho file to open in GUI." },
        reload_scripts: { type: "boolean", description: "Send Ctrl+Shift+Alt+L to reload Moho Lua scripts." },
        nudge_only: { type: "boolean", description: "Only send non-intrusive repaint nudge to running Moho." }
      }
    }
  },
  {
    name: "execute_moho_lua",
    description:
      "Execute arbitrary Lua 5.4 code directly inside the running Moho Pro 14.5.1 instance via the Live Lua Bridge. Receives `(moho, args)` and returns any JSON-serializable Lua value.",
    inputSchema: {
      type: "object",
      properties: {
        code: { type: "string", description: "Lua 5.4 source code (has `moho` and `args` in scope)." },
        args: { type: "object", description: "Optional JSON object passed as `args` table." },
        update_ui: { type: "boolean", description: "Call moho:UpdateUI() after execution (default true)." },
        timeout_ms: { type: "number", description: "Timeout in milliseconds (default 30000)." }
      },
      required: ["code"]
    }
  },
  {
    name: "get_live_document_summary",
    description: "Inspect the currently active document inside the running Moho Pro 14.5.1 GUI via Live Lua Bridge.",
    inputSchema: {
      type: "object",
      properties: {
        timeout_ms: { type: "number" }
      }
    }
  },
  {
    name: "live_manage_layers",
    description: "Create, select, rename, delete, duplicate, reparent into group, or modify properties of layers in the running Moho Pro GUI.",
    inputSchema: {
      type: "object",
      properties: {
        operation: {
          type: "string",
          enum: ["create", "select", "rename", "delete", "duplicate", "move_into_group", "set_properties"]
        },
        layer_type: {
          type: "string",
          enum: ["vector", "bone", "group", "switch", "image", "audio", "note", "particle", "patch", "text"]
        },
        name: { type: "string" },
        target_layer: { type: "string" },
        new_name: { type: "string" },
        parent_group: { type: "string" },
        frame: { type: "number" },
        visible: { type: "boolean" },
        opacity: { type: "number" },
        translation: { type: "object" },
        scale: { type: "object" },
        rotation_z_deg: { type: "number" },
        origin: { type: "object" }
      },
      required: ["operation"]
    }
  },
  {
    name: "live_draw_vector",
    description: "Procedurally draw vector shapes (rectangle, ellipse, polygon, star, custom points path) with fill/stroke colors and line width in the running Moho Pro GUI.",
    inputSchema: {
      type: "object",
      properties: {
        layer_name: { type: "string", description: "Existing or new Vector layer name." },
        shape_type: { type: "string", enum: ["rectangle", "ellipse", "polygon", "star", "points"] },
        shape_name: { type: "string" },
        cx: { type: "number" },
        cy: { type: "number" },
        width: { type: "number" },
        height: { type: "number" },
        radius: { type: "number" },
        rx: { type: "number" },
        ry: { type: "number" },
        sides: { type: "number" },
        spikes: { type: "number" },
        inner_radius: { type: "number" },
        segments: { type: "number" },
        rotation_deg: { type: "number" },
        points: { type: "array" },
        close: { type: "boolean" },
        fill: { type: "boolean" },
        stroke: { type: "boolean" },
        fill_color: { type: "object", description: "{r,g,b,a} in 0-255 or 0-1" },
        stroke_color: { type: "object", description: "{r,g,b,a} in 0-255 or 0-1" },
        line_width: { type: "number", description: "Line width in pixels." },
        frame: { type: "number" }
      },
      required: ["shape_type"]
    }
  },
  {
    name: "live_rig_bones",
    description: "Create/update a Bone skeleton hierarchy (positions, angles, lengths, parents, strengths, angle constraints) and bind child layers to bones in the running Moho Pro GUI.",
    inputSchema: {
      type: "object",
      properties: {
        bone_layer: { type: "string", description: "Existing or new Bone layer name." },
        bones: {
          type: "array",
          description: "Array of {name, x, y, angle_deg, length, parent?, strength?, min_angle_deg?, max_angle_deg?}."
        },
        bind_layers: {
          type: "array",
          description: "Array of {layer_name, bone} to move into Bone layer and bind to bone."
        }
      }
    }
  },
  {
    name: "live_animate",
    description: "Control timeline, set keyframes (layer transforms, opacity, visibility, bone angle/pos/scale, camera track/zoom/roll, switch values with interpolation), save/open/new document, or export current frame PNG in the running Moho Pro GUI.",
    inputSchema: {
      type: "object",
      properties: {
        operation: {
          type: "string",
          enum: ["keyframe", "set_frame", "save", "open_document", "new_document", "export_frame_png"]
        },
        frame: { type: "number" },
        file_path: { type: "string" },
        output_png: { type: "string" },
        keyframes: { type: "array", description: "Array of keyframe descriptors." },
        set_end_frame: { type: "number" },
        set_frame: { type: "number" }
      },
      required: ["operation"]
    }
  }
];

function handleToolCall(toolName, args = {}) {
  switch (toolName) {
    case "get_moho_status": {
      const env = detectMohoEnvironment();
      let livePing = null;
      if (args.ping_live && env.isRunning && env.bridgeInstalled) {
        livePing = pingLiveBridge({ timeout_ms: 4000 });
      }
      return {
        ok: env.installed,
        ...env,
        livePing,
        capabilities: {
          headlessMohoJsonEngine: true,
          headlessCliRender: env.installed,
          liveLua54Bridge: env.bridgeInstalled,
          mcpStdioServer: true,
          directCli: true
        }
      };
    }
    case "inspect_moho_file":
      return inspectMohoFile(args);
    case "create_moho_file":
      return createMohoFile(args);
    case "patch_moho_file":
      return patchMohoFile(args);
    case "unpack_moho_file":
      return unpackMohoFile(args);
    case "pack_moho_file":
      return packMohoFile(args);
    case "render_moho":
      return renderMoho(args);
    case "render_preview_frame":
      return renderPreviewFrame(args);
    case "open_in_moho": {
      if (args.nudge_only) return nudgeMohoWindow();
      if (args.reload_scripts) return triggerReloadScriptsWindows();
      return launchMohoGui(args.moho_path || null);
    }
    case "execute_moho_lua":
      return executeMohoLua(args);
    case "get_live_document_summary":
      return getLiveDocumentSummary(args);
    case "live_manage_layers":
      return liveManageLayers(args);
    case "live_draw_vector":
      return liveDrawVector(args);
    case "live_rig_bones":
      return liveRigBones(args);
    case "live_animate":
      return liveAnimate(args);
    default:
      return { ok: false, error: `Unknown Moho tool: ${toolName}` };
  }
}

module.exports = {
  TOOLS_DEFINITION,
  handleToolCall
};
