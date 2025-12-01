# Repository Guidelines

## Project Structure & Module Organization
- Vite + Vanilla JS entrypoint lives in `src/main.js`, wiring UI helpers from `src/ui.js` and the Three.js viewer core in `src/viewer.js`; shared styles and CSS variables stay in `src/style.css`.
- Static assets and GLB/GLTF models belong in `public/`; keep repository-friendly samples in `public/models/` (default `sample.glb`) and reference new defaults via `MODEL_PATH` in `src/viewer.js`.
- `docs/DEV_GUIDE.md` holds a deeper technical reference; `index.html` defines the single-page shell used by Vite's dev server and production build.

## Build, Test, and Development Commands
- `npm install` - install dependencies (Node 18+ recommended; project is ESM via `"type": "module"`).
- `npm run dev` - start Vite dev server at `http://localhost:5173` with hot reload for rapid Three.js iteration.
- `npm run build` - create a production bundle in `dist/`; use to catch missing imports and asset paths.
- `npm run preview` - serve the built `dist/` bundle locally to verify production behavior.

## Coding Style & Naming Conventions
- Use ES modules, `const`/`let`, arrow functions for callbacks, and keep functions small and composable (mirroring `initViewer`, `bindResetButton`, etc.).
- Indent with 2 spaces, keep semicolons, and prefer descriptive camelCase identifiers; reserve ALL_CAPS for configuration constants like `MODEL_PATH`.
- UI copy may be bilingual; keep existing Chinese text intact and add concise inline comments only when behavior is non-obvious.
- Place new styles in `src/style.css` alongside existing CSS variables instead of inline styles.

## Testing Guidelines
- No automated test suite yet; use `npm run build` as a baseline check.
- Manual smoke pass before submitting: load the default model, load a local GLB/GLTF via the sidebar button, test `Reset View`, resize the window, and confirm errors surface through the toast instead of the console.

## Commit & Pull Request Guidelines
- Write concise, imperative commit subjects ("Add local file loader"), with optional bodies explaining rationale or edge cases.
- PRs should include: summary of changes, before/after screenshots or short screen captures of the viewer, model filenames used for verification, reproduction steps, and any related issue IDs.
- Keep diffs focused; avoid committing large binary models. If needed for docs, prefer small samples in `public/models/` and note approximate sizes.

## Security & Configuration Tips
- Do not embed remote model URLs without review; prefer local assets to avoid CORS surprises and to keep offline support.
- Ensure added models are redistributable; strip sensitive metadata before committing.
- When adjusting Three.js loaders or new env maps, document new dependencies or CDN usage in `docs/DEV_GUIDE.md` and update `MODEL_PATH` defaults accordingly.
