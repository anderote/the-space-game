# Project decisions

## 2026-10-11 — Separate stable play from live development

The owner requested a game environment that stays running while development continues. Preserve port 5178 and its existing browser save origin for play; move Vite development to 5179. Use a per-user macOS launchd service serving copied static releases outside the worktree, with loopback-only binding and no repository dependency at runtime. Publish only after a successful build through an atomic manifest swap, retaining old hashed assets for already loaded pages. The owner refreshes the play page when ready; development must not automatically restart or update it.

This is local process/build isolation, not a VM sandbox or public deployment. No backend account or game-save migration is introduced.
