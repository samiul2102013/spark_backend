# AGENTS.md — ChargeSafe

This file helps OpenCode agents avoid mistakes in this repo. It is a living document; update it whenever the project introduces new conventions, tooling, or architectural decisions that an agent would not guess from defaults.

## Current state

This repository is empty — no source code, no dependencies, no configuration, no git history.

## What to do when starting work

1. Initialize the project (pick framework, set up toolchain, create root manifest).
2. Establish a `package.json` / `Cargo.toml` / equivalent and lockfile.
3. Configure lint, format, typecheck, and test runners before writing application code.
4. After the toolchain is in place, update this file with:
   - exact developer commands
   - how to run focused verification (single test, single package)
   - monorepo structure if applicable
   - any framework or toolchain quirks
   - test prerequisites and conventions

## Conventions

- Keep this file short. Prefer executable sources of truth (configs, scripts) over prose.
- If docs conflict with config, trust the config and update this file.
- Preserve verified useful guidance; delete fluff and stale claims.
