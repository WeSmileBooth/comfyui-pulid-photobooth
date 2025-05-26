from modal import Image
import pathlib

from .models import download_checkpoints, download_additional_models
from .nodes import download_nodes

# Use latest ComfyUI commit with FLUX support
commit_sha = "latest"  # Use latest for FLUX support
gpu = "h100"  # H100 recommended for FLUX

# Define the image with FLUX-specific configuration
image = (
    Image.from_registry("nvidia/cuda:12.1.1-devel-ubuntu22.04", add_python="3.11")
    .apt_install(
        "git", "git-lfs", "libgl1-mesa-glx", "libglib2.0-0", 
        "unzip", "clang", "wget", "curl", "libgoogle-perftools4"
    )
    .run_commands(
        "cd /root && git init .",
        "cd /root && git remote add --fetch origin https://github.com/comfyanonymous/ComfyUI",
        "cd /root && git checkout main",  # Use latest for FLUX support
        "cd /root && git pull origin main",
    )
    # Install PyTorch with CUDA 12.1
    .run_commands(
        "cd /root && pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121",
        "cd /root && pip install -r requirements.txt",
        gpu=gpu,
    )
    # Install additional dependencies for FLUX and PuLID
    .pip_install(
        "httpx",
        "requests", 
        "tqdm",
        "gdown",
        "websocket-client",
        "firebase_admin",
        "transformers>=4.28.0",
        "diffusers>=0.25.0",
        "opencv-python",
        "insightface",
        "onnxruntime-gpu",
        "facexlib",
        "gfpgan",
        "google-generativeai",
        "google-genai",
        "pillow",
        "ultralytics",
    )
    # Download custom nodes
    .run_function(download_nodes, gpu=gpu)
    # Download models
    .run_function(download_checkpoints)
    .run_function(download_additional_models)
    # Upgrade FastAPI
    .run_commands("pip install --upgrade fastapi")
    # Add the workflow file
    .add_local_file(
        local_path=str(pathlib.Path(__file__).parent / "workflow_api.json"),
        remote_path="/root/workflow_api.json"
    )
)