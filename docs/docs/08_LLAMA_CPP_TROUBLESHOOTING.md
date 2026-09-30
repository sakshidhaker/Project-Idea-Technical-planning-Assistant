# 08 — llama.cpp / llama-cpp-python Troubleshooting

The project uses **`llama-cpp-python`** because the Python backend directly creates a local `llama_cpp.Llama` object.

Official sources:

- llama-cpp-python: https://github.com/abetlen/llama-cpp-python
- llama.cpp install guide: https://github.com/ggml-org/llama.cpp/blob/master/docs/install.md
- Qwen model: https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF

## First choice for this teaching project: CPU wheel

The project is deliberately CPU-first and does not require students to configure CUDA, Metal, or GPU detection.

```bash
pip install llama-cpp-python \
  --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

This avoids many compiler problems caused by building `llama-cpp-python` from source.

## Ubuntu / WSL

If the CPU wheel does not match your Python/platform, install build tools:

```bash
sudo apt update
sudo apt install -y build-essential cmake python3-dev
```

Then:

```bash
CMAKE_ARGS="-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS" \
pip install llama-cpp-python
```

If using WSL, make sure commands are being run inside the same Linux virtual environment used to start the project.

## Windows

First try the CPU wheel command above from PowerShell.

If pip falls back to a source build and reports missing compiler/CMake tools, install a supported C/C++ build environment. The official `llama-cpp-python` documentation lists Visual Studio or MinGW as Windows compiler options.

A common source-build fallback is:

```powershell
$env:CMAKE_GENERATOR = "MinGW Makefiles"
$env:CMAKE_ARGS = "-DGGML_OPENBLAS=on"
pip install llama-cpp-python
```

Use the project's CPU path first; do not add GPU configuration just to make the basic teaching edition run.

## macOS

For Intel Mac, the CPU wheel is the simplest path.

For Apple Silicon, the official `llama-cpp-python` project documents a Metal wheel:

```bash
pip install llama-cpp-python \
  --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/metal
```

Make sure Python itself is the correct architecture for the Mac. The official documentation specifically warns that an x86 Python on Apple Silicon can lead to architecture/performance problems.

## Common errors

### `ModuleNotFoundError: No module named 'llama_cpp'`

The Python package is missing from the active environment:

```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

### `CMAKE_C_COMPILER` / `nmake` / compiler error

The package is trying to build from source. Use a compatible pre-built wheel first. If no wheel matches your Python/platform, install the compiler tools described above.

### `mach-o ... incompatible architecture` on Apple Silicon

Use an arm64 Python environment and the Metal installation path documented by `llama-cpp-python`.

### Model download fails

Check internet access. The Qwen file is downloaded automatically by `huggingface_hub`. You do not need to use a separate Hugging Face CLI command.

### Model file is corrupt

Delete the bad file from `models/` and restart. The application checks the GGUF header and downloads again when the file is missing/invalid.

### Model loads but generation is very slow

This teaching build intentionally runs the single model with CPU inference. That is a design choice to keep hardware configuration out of the student project.

## Current Qwen file

The official Qwen repository currently lists:

```text
qwen2.5-0.5b-instruct-q4_k_m.gguf
```

at about 491 MB. Qwen's model page also documents direct llama.cpp usage with `Q4_K_M`.
