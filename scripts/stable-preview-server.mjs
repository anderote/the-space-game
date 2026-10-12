import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { createReadStream } from "node:fs";
import { resolve, extname, sep } from "node:path";
import { pathToFileURL } from "node:url";
const types = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".webp": "image/webp",
  ".ico": "image/x-icon",
  ".woff2": "font/woff2",
  ".wasm": "application/wasm",
};
export function createPreviewServer(stateDir) {
  return createServer(async (req, res) => {
    try {
      if (!["GET", "HEAD"].includes(req.method)) {
        res.writeHead(405, { Allow: "GET, HEAD" }).end();
        return;
      }
      const manifest = JSON.parse(
        await readFile(resolve(stateDir, "current.json"), "utf8"),
      );
      if (!/^[\w-]+$/.test(manifest.release))
        throw new Error("Invalid release");
      const path = decodeURIComponent(
        new URL(req.url, "http://localhost").pathname,
      );
      if (path === "/__preview_status") {
        const body = JSON.stringify({
          service: "the-space-game-stable-preview",
          ...manifest,
        });
        res.writeHead(200, {
          "Content-Type": "application/json",
          "Cache-Control": "no-store",
        });
        res.end(req.method === "HEAD" ? undefined : body);
        return;
      }
      const root = resolve(stateDir, "releases", manifest.release);
      const relative = path === "/" ? "index.html" : path.slice(1);
      let file = resolve(root, relative);
      if (!file.startsWith(root + sep)) {
        res.writeHead(403).end();
        return;
      }
      let info;
      try {
        info = await stat(file);
      } catch {
        if (path.startsWith("/assets/")) {
          const assets = resolve(stateDir, "assets");
          file = resolve(assets, path.slice(8));
          if (!file.startsWith(assets + sep)) {
            res.writeHead(403).end();
            return;
          }
          try {
            info = await stat(file);
          } catch {}
        }
      }
      if (!info?.isFile()) {
        res.writeHead(404).end("Not found");
        return;
      }
      res.writeHead(200, {
        "Content-Type": types[extname(file)] || "application/octet-stream",
        "Content-Length": info.size,
        "Cache-Control": path.startsWith("/assets/")
          ? "public, max-age=31536000, immutable"
          : "no-cache",
        "X-Content-Type-Options": "nosniff",
      });
      if (req.method === "HEAD") {
        res.end();
        return;
      }
      const stream = createReadStream(file);
      stream.on("error", () => res.destroy());
      stream.pipe(res);
    } catch (error) {
      res
        .writeHead(error instanceof URIError ? 400 : 503, {
          "Cache-Control": "no-store",
        })
        .end("Preview unavailable");
    }
  });
}
if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(resolve(process.argv[1])).href
) {
  const state = process.argv[2],
    port = Number(process.argv[3] || 5178);
  if (!state || !Number.isInteger(port) || port < 1 || port > 65535)
    throw new Error("Expected state directory and valid port");
  const server = createPreviewServer(state);
  server.listen(port, "127.0.0.1", () =>
    console.log(`Stable play preview: http://127.0.0.1:${port}`),
  );
  process.on("SIGTERM", () => server.close(() => process.exit(0)));
}
