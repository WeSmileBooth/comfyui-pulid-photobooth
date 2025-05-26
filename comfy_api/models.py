import pathlib

MODELS = [
    # FLUX Core Models - Fixed paths and URLs
    {
        "url": "https://huggingface.co/Kijai/flux-fp8/resolve/main/flux1-dev-fp8.safetensors",
        "directory": "/root/models/flux",
        "filename": "flux1-dev-fp8.safetensors"
    },
    {
        "url": "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn_scaled.safetensors",
        "directory": "/root/models/clip",
        "filename": "t5xxl_fp8_e4m3fn_scaled_flux.safetensors"
    },
    {
        "url": "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors", 
        "directory": "/root/models/clip",
        "filename": "clip_l_flux.safetensors"
    },
    {
        "url": "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/ae.safetensors",
        "directory": "/root/models/flux",
        "filename": "ae.safetensors"
    },
    
    # PuLID Models
    {
        "url": "https://huggingface.co/guozinan/PuLID/resolve/main/pulid_flux_v0.9.1.safetensors",
        "directory": "/root/models/pulid",
        "filename": "pulid_flux_v0.9.1.safetensors"
    },
    
    # ControlNet Models - Fixed URL
    {
        "url": "https://huggingface.co/Shakker-Labs/FLUX.1-dev-ControlNet-Union-Pro/resolve/main/FLUX.1-dev-ControlNet-Union-Pro.safetensors",
        "directory": "/root/models/controlnet",
        "filename": "FLUX.1-dev-ControlNet-Union-Pro-2.0-fp8.safetensors"
    },
    
    # Face Detection Models
    {
        "url": "https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov8m.pt",
        "directory": "/root/models/ultralytics/bbox",
        "filename": "face_yolov8m.pt"
    },
    
    # DWPose Models - Fixed URL
    {
        "url": "https://huggingface.co/yzd-v/DWPose/resolve/main/dw-ll_ucoco_384.torchscript.pt",
        "directory": "/root/models/dwpose",
        "filename": "dw-ll_ucoco_384_bs5.torchscript.pt"
    },
    
    # Upscaling Models - Corrected URL
    {
        "url": "https://huggingface.co/uwg/upscaler/resolve/main/ESRGAN/2x-NomosUni_span_multijpg_ldl.pth",
        "directory": "/root/models/upscale_models", 
        "filename": "2xNomosUni_span_multijpg_ldl.safetensors"
    },
    
    # InsightFace Models
    {
        "url": "https://huggingface.co/datasets/Gourieff/ReActor/resolve/main/models/inswapper_128.onnx",
        "directory": "/root/models/insightface",
        "filename": "inswapper_128.onnx"
    },
]

def download_checkpoints():
    import httpx
    from tqdm import tqdm

    for model in MODELS:
        url = model["url"]
        filename = model.get("filename", url.split("/")[-1])
        directory = model["directory"]
        
        local_filepath = pathlib.Path(directory, filename)
        local_filepath.parent.mkdir(parents=True, exist_ok=True)

        if local_filepath.exists():
            print(f"Model {filename} already exists, skipping...")
            continue

        print(f"Downloading {url} to {local_filepath}...")
        try:
            with httpx.stream("GET", url, follow_redirects=True, timeout=300) as stream:
                total = int(stream.headers.get("Content-Length", 0))
                with open(local_filepath, "wb") as f, tqdm(
                    total=total, unit_scale=True, unit_divisor=1024, unit="B"
                ) as progress:
                    num_bytes_downloaded = stream.num_bytes_downloaded
                    for data in stream.iter_bytes():
                        f.write(data)
                        progress.update(stream.num_bytes_downloaded - num_bytes_downloaded)
                        num_bytes_downloaded = stream.num_bytes_downloaded
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
            continue

def download_additional_models():
    """Download additional models that need special handling"""
    import subprocess
    import os
    
    # Download InsightFace AntelopeV2 models  
    antelope_dir = "/root/models/insightface/models/antelopev2"
    os.makedirs(antelope_dir, exist_ok=True)
    
    print("InsightFace models will be auto-downloaded on first use")