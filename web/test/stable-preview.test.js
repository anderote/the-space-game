import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, writeFile, rename, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { resolve } from "node:path";
import { createPreviewServer } from "../../scripts/stable-preview-server.mjs";
test("stable preview stays isolated, swaps releases without restarting and retains old hashed assets", async () => {
  const state = await mkdtemp(resolve(tmpdir(), "space-preview-"));
  for (const id of ["old", "new"]) {
    await mkdir(resolve(state, "releases", id), { recursive: true });
    await writeFile(
      resolve(state, "releases", id, "index.html"),
      `<h1>${id}</h1>`,
    );
  }
  await mkdir(resolve(state, "assets"));
  await writeFile(resolve(state, "assets", "old-hash.js"), "old bundle");
  await writeFile(resolve(state, "assets", "new-hash.js"), "new bundle");
  await writeFile(
    resolve(state, "current.json"),
    JSON.stringify({ release: "old" }),
  );
  const server = createPreviewServer(state);
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  const base = `http://127.0.0.1:${server.address().port}`;
  try {
    assert.equal(await (await fetch(base)).text(), "<h1>old</h1>");
    await writeFile(resolve(state, "unrelated-source.js"), "edited source");
    assert.equal(await (await fetch(base)).text(), "<h1>old</h1>");
    await writeFile(
      resolve(state, "current.tmp"),
      JSON.stringify({ release: "new" }),
    );
    await rename(resolve(state, "current.tmp"), resolve(state, "current.json"));
    assert.equal(await (await fetch(base)).text(), "<h1>new</h1>");
    const old = await fetch(base + "/assets/old-hash.js");
    assert.equal(await old.text(), "old bundle");
    assert.match(old.headers.get("cache-control"), /immutable/);
    assert.equal(
      await (await fetch(base + "/assets/new-hash.js")).text(),
      "new bundle",
    );
    const status = await (await fetch(base + "/__preview_status")).json();
    assert.equal(status.release, "new");
    assert.equal(status.service, "the-space-game-stable-preview");
    const head = await fetch(base, { method: "HEAD" });
    assert.equal(head.status, 200);
    assert.equal(await head.text(), "");
    assert.equal((await fetch(base, { method: "POST" })).status, 405);
    assert.equal((await fetch(base + "/unrelated-source.js")).status, 404);
    assert.equal((await fetch(base + "/%2e%2e%2fcurrent.json")).status, 403);
    assert.equal((await fetch(base + "/%invalid")).status, 400);
  } finally {
    await new Promise((r) => server.close(r));
    await rm(state, { recursive: true, force: true });
  }
});
