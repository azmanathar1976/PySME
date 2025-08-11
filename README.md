# PySme

> Python-first, Svelte-inspired full-stack framework — compiled to WASM, powered by Tailwind.

## Vision
PySme aims to bring the productivity of Python to modern, reactive, single-page applications — without compromising on performance. By compiling to WebAssembly and embracing TailwindCSS, PySme lets you write clean, declarative Python components that run seamlessly in the browser.

**Core principles:**
- **Python-first**: Write both frontend and backend in Python, no JavaScript required.
- **Separation of concerns**: Svelte-like `.pysme` file format for clean code + markup separation.
- **Performance**: WASM output, tree-shaking, and bundle splitting for production.
- **Styling freedom**: TailwindCSS as the default styling engine.
- **Full-stack**: Built-in API routing, database ORM, and state management.

## Goals
- Provide a familiar Python syntax for frontend components, layouts, and stores.
- Compile `.pysme` files to optimized WASM using a Rust-based compiler.
- Offer a powerful reactive state system similar to Svelte's stores.
- Integrate TailwindCSS automatically into the build pipeline.
- Include a simple, async-first API routing system for backends.
- Provide a pluggable ORM with migrations, relations, and type safety.
- Deliver a DX-focused dev server with hot module replacement (HMR).
- Ensure accessibility and i18n support out of the box.
- Make deploying PySme apps to modern hosting platforms seamless.

## Non-goals
- Supporting legacy browsers without WASM support.
- Re-implementing JavaScript frameworks in Python line-by-line.
- Being a drop-in replacement for Django/Flask — PySme is opinionated.
- Abstracting away Tailwind — it’s required and central to the styling system.
- Compiling arbitrary Python standard library modules to WASM (only a curated subset will work client-side).

## License
MIT — see [LICENSE](LICENSE) for details.
