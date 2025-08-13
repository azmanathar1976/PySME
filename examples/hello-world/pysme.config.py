from pysme.build.config import BuildConfig, TailwindConfig  # type: ignore

build_config = BuildConfig(
    entry_point="pages/index.component.pysme",
    output_dir="dist",
    static_dir="static",
    wasm_target="web",
    optimization_level="debug",
    bundle_splitting=False,
    tree_shaking=False,
)

tailwind_config = TailwindConfig(
    content=["**/*.pysme"], theme={"extend": {}}, plugins=[]
)
