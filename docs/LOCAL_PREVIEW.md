# Stable local preview

The stable play server runs at **http://127.0.0.1:5178**. The source-watching development server runs at **http://127.0.0.1:5179**. Keep play on the former and development/QA on the latter. Different browser origins have separate localStorage profiles; retaining the original play URL preserves existing saves.

The preview is an isolated build copy, not a virtual machine or security sandbox. Its server binds only to loopback, serves completed static assets, runs outside the repo and has no dependency on the repository’s node_modules at runtime. It never clears browser storage or sends game progress to a backend.

## Commands

| Command | Effect |
| --- | --- |
| `npm run play:install` | Build a snapshot, install the user LaunchAgent and start the stable server. Use once; rerun to replace the server implementation. |
| `npm run play:update` | Build directly into a fresh release folder and atomically switch the current manifest. The server stays running. |
| `npm run play:status` | Verify service identity and report the loaded release, build time and source revision. |
| `npm run play:stop` | Unload the user service for the current login session. Snapshots and saves remain. |
| `npm run play:start` | Start an installed service using its existing snapshot. |
| `npm run dev` / `npm start` | Run live Vite development on 5179 with a strict port. |

Refresh the play browser only when ready to use an updated snapshot. Updates do not inject a reload client, stop the simulation in an already loaded page or restart the HTTP process. Old hashed assets remain available so an older loaded version can still finish its requests. If a build fails, the previously published manifest stays active.

The launchd service starts at login, survives terminal/Codex sessions and recovers after process exit. It runs only while the Mac/user session is available; this is not cloud hosting. `play:stop` does not remove the LaunchAgent, so it starts again at the next login unless removed.

## Local files

- User service: `~/Library/LaunchAgents/com.andrewcote.the-space-game.preview.plist`.
- Service and releases: `~/Library/Application Support/The Space Game/preview/`.
- Current release: `current.json`; the build metadata notes uncommitted workspace changes when present.
- Logs: `stdout.log` and `stderr.log` in the preview directory.
- Entry points: `scripts/stable-preview.mjs` and `scripts/stable-preview-server.mjs`.

The service uses the installed Node executable through its normal PATH location. Its copied server imports only Node built-ins. Node must remain installed. Snapshots and older assets are retained intentionally; updates do not automatically delete them.

The install/start commands refuse to occupy an unrelated listener on 5178. The original task replaced the known game Vite listener once with this managed service. Future development should leave the stable service running and use `play:update` only when the owner wants the play version refreshed. Source changes alone do not update the play copy.
