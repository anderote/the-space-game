import { randomUUID } from "node:crypto";
import { createServer } from "node:net";
import { mkdir, cp, writeFile, rename, access } from "node:fs/promises";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { homedir } from "node:os";
import { execFileSync, spawnSync } from "node:child_process";
const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const state = resolve(
  homedir(),
  "Library/Application Support/The Space Game/preview",
);
const label = "com.andrewcote.the-space-game.preview",
  domain = `gui/${process.getuid?.()}`;
const target = `${domain}/${label}`,
  plist = resolve(homedir(), "Library/LaunchAgents", label + ".plist");
const action = process.argv[2] || "status";
const xml = (s) =>
  String(s).replace(
    /[&<>"']/g,
    (c) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&apos;",
      })[c],
  );
const loaded = () =>
  spawnSync("/bin/launchctl", ["print", target], { stdio: "ignore" }).status ===
  0;
const launch = (args) =>
  execFileSync("/bin/launchctl", args, { stdio: "inherit" });
async function health() {
  const r = await fetch("http://127.0.0.1:5178/__preview_status", {
    signal: AbortSignal.timeout(2000),
  });
  if (!r.ok) throw new Error("Preview not ready");
  const status = await r.json();
  if (status.service !== "the-space-game-stable-preview")
    throw new Error("Port 5178 belongs to another server");
  return status;
}
async function waitReady() {
  for (let i = 0; i < 30; i++) {
    try {
      return await health();
    } catch {}
    await new Promise((r) => setTimeout(r, 200));
  }
  throw new Error(`Preview did not start; inspect ${state}/stderr.log`);
}
async function publish() {
  await mkdir(resolve(state, "releases"), { recursive: true, mode: 0o700 });
  const commit = execFileSync("git", ["rev-parse", "--short", "HEAD"], {
    cwd: root,
    encoding: "utf8",
  }).trim();
  const release = `${Date.now()}-${commit}-${randomUUID()}`;
  const output = resolve(state, "releases", release);
  execFileSync(
    "npm",
    ["run", "build", "--", "--outDir", output, "--emptyOutDir"],
    { cwd: root, stdio: "inherit" },
  );
  await cp(resolve(output, "assets"), resolve(state, "assets"), {
    recursive: true,
    force: false,
    errorOnExist: false,
  });
  const workspaceDirty =
    spawnSync("git", ["diff", "--quiet", "HEAD"], { cwd: root }).status !== 0 ||
    Boolean(
      spawnSync("git", ["ls-files", "--others", "--exclude-standard"], {
        cwd: root,
        encoding: "utf8",
      }).stdout.trim(),
    );
  const manifest = {
    release,
    builtAt: new Date().toISOString(),
    commit,
    workspaceDirty,
  };
  await writeFile(
    resolve(state, `current-${release}.tmp`),
    JSON.stringify(manifest),
  );
  await rename(
    resolve(state, `current-${release}.tmp`),
    resolve(state, "current.json"),
  );
  console.log(
    `Published stable local snapshot ${release}. Existing browser pages are not reloaded.`,
  );
  return manifest;
}
async function ensurePortAvailable() {
  if (loaded()) return;
  const probe = createServer();
  await new Promise((ok, reject) => {
    probe.once("error", () =>
      reject(
        new Error(
          "Port 5178 is occupied. Stop the old local server before installing the stable preview.",
        ),
      ),
    );
    probe.listen(5178, "127.0.0.1", () => probe.close(ok));
  });
}
async function install() {
  await ensurePortAvailable();
  await publish();
  await cp(
    resolve(root, "scripts/stable-preview-server.mjs"),
    resolve(state, "server.mjs"),
  );
  await mkdir(dirname(plist), { recursive: true });
  const node = execFileSync("/usr/bin/which", ["node"], {
    encoding: "utf8",
  }).trim();
  await writeFile(
    plist,
    `<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n<plist version="1.0"><dict><key>Label</key><string>${label}</string><key>ProgramArguments</key><array><string>${xml(node)}</string><string>${xml(resolve(state, "server.mjs"))}</string><string>${xml(state)}</string><string>5178</string></array><key>RunAtLoad</key><true/><key>KeepAlive</key><true/><key>ThrottleInterval</key><integer>5</integer><key>StandardOutPath</key><string>${xml(resolve(state, "stdout.log"))}</string><key>StandardErrorPath</key><string>${xml(resolve(state, "stderr.log"))}</string></dict></plist>\n`,
  );
  execFileSync("/usr/bin/plutil", ["-lint", plist], { stdio: "inherit" });
  if (loaded()) launch(["bootout", target]);
  launch(["bootstrap", domain, plist]);
  console.log(await waitReady());
}
if (process.platform !== "darwin")
  throw new Error(
    "The persistent preview service currently supports macOS. npm run dev works on other systems.",
  );
try {
  if (action === "install") await install();
  else if (action === "update") {
    await access(resolve(state, "server.mjs"));
    await publish();
    console.log(
      loaded()
        ? "Refresh your play browser when ready."
        : "Run npm run play:start to start the installed preview.",
    );
  } else if (action === "start") {
    await access(plist);
    if (!loaded()) {
      await ensurePortAvailable();
      launch(["bootstrap", domain, plist]);
    }
    console.log(await waitReady());
  } else if (action === "stop") {
    if (loaded()) launch(["bootout", target]);
    console.log("Stable preview stopped.");
  } else if (action === "status") {
    console.log({
      managedBy: "macOS launchd",
      loaded: loaded(),
      ...(await health()),
    });
  } else throw new Error("Use install, update, start, stop or status");
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
