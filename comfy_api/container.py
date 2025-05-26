from modal import Image
import pathlib

from .models import download_checkpoints, download_additional_models
from .nodes import download_nodes, create_aq_gemini_node

# Use specific ComfyUI commit that works well with FLUX
commit_sha = "2a02546e2085487d34920e5b5c9b367918531f32"
gpu = "h100" 

# Define the image with FLUX-specific configuration
image = (
    Image.from_registry("nvidia/cuda:12.1.1-devel-ubuntu22.04", add_python="3.11")
    .apt_install(
        "git", "git-lfs", "libgl1-mesa-glx", "libglib2.0-0", 
        "unzip", "clang", "wget", "curl", "libgoogle-perftools4",
        "libsm6", "libxext6", "libxrender-dev", "libgl1-mesa-dev"
    )
    .run_commands(
        "cd /root && git init .",
        "cd /root && git remote add --fetch origin https://github.com/comfyanonymous/ComfyUI",
        f"cd /root && git checkout {commit_sha}",
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
        "matplotlib",
        "scikit-image",
    )
    # Download custom nodes
    .run_function(download_nodes, gpu=gpu)
    # Create custom AQ_Gemini node
    .run_function(create_aq_gemini_node)
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