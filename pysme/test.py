# pysme.config.py (or sample_module.py for testing)

from pysme.build.config import BuildConfig
from pysme.build.tailwind import TailwindConfig

# Core build configuration
build_config = BuildConfig(
    entry_point="pages/index.component.pysme",
    output_dir="dist",
    static_dir="static",
    wasm_target="web",
    optimization_level="release",
    bundle_splitting=True,
    tree_shaking=True,
)

# Tailwind configuration
tailwind_config = TailwindConfig(
    content=["**/*.pysme", "**/*.py"],
    theme={"extend": {"colors": {"primary": "#3b82f6", "secondary": "#64748b"}}},
    plugins=["@tailwindcss/forms", "@tailwindcss/typography"],
)

# Optional debug flag (can also be set via env: PYSME_DEBUG=1)
debug = True
