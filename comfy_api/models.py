import pathlib

MODELS = [
    # FLUX Core Models
    {
        "url": "https://huggingface.co/Kijai/flux-fp8/resolve/main/flux1-dev-fp8.safetensors",
        "directory": "/root/models/unet",
    },
    {
        "url": "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn_scaled.safetensors",
        "directory": "/root/models/clip",
    },
    {
        "url": "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors", 
        "directory": "/root/models/clip",
    },
    {
        "url": "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/ae.safetensors",
        "directory": "/root/models/vae",
    },
    
    # PuLID Models
    {
        "url": "https://huggingface.co/guozinan/PuLID/resolve/main/pulid_flux_v0.9.1.safetensors",
        "directory": "/root/models/pulid",
    },
    
    # ControlNet Models
    {
        "url": "https://huggingface.co/Shakker-Labs/FLUX.1-dev-ControlNet-Union-Pro/resolve/main/FLUX.1-dev-ControlNet-Union-Pro.safetensors",
        "directory": "/root/models/controlnet",
    },
    
    # Face Detection Models
    {
        "url": "https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov8m.pt",
        "directory": "/root/models/ultralytics/bbox",
    },
    
    # DWPose Models
    {
        "url": "https://huggingface.co/yzd-v/DWPose/resolve/main/dw-ll_ucoco_384.torchscript.pt",
        "directory": "/root/models/dwpose",
    },
    
    # Upscaling Models
    {
        "url": "https://huggingface.co/uwg/upscaler/resolve/main/ESRGAN/2xNomosUni_span_multijpg_ldl.pth",
        "directory": "/root/models/upscale_models",
    },
    
    # InsightFace Models (for PuLID)
    {
        "url": "https://huggingface.co/datasets/Gourieff/ReActor/resolve/main/models/inswapper_128.onnx",
        "directory": "/root/models/insightface",
    },
]

def download_checkpoints():
    import httpx
    from tqdm import tqdm

    for model in MODELS:
        url = model["url"]
        local_filename = url.split("/")[-1]
        
        # Handle special naming
        if "t5xxl_fp8_e4m3fn_scaled.safetensors" in local_filename:
            local_filename = "t5xxl_fp8_e4m3fn_scaled_flux.safetensors"
        elif "clip_l.safetensors" in local_filename:
            local_filename = "clip_l_flux.safetensors"
        elif "FLUX.1-dev-ControlNet-Union-Pro.safetensors" in local_filename:
            local_filename = "FLUX.1-dev-ControlNet-Union-Pro-2.0-fp8.safetensors"
        elif "2xNomosUni_span_multijpg_ldl.pth" in local_filename:
            local_filename = "2xNomosUni_span_multijpg_ldl.safetensors"

        local_filepath = pathlib.Path(model["directory"], local_filename)
        local_filepath.parent.mkdir(parents=True, exist_ok=True)

        if local_filepath.exists():
            print(f"Model {local_filename} already exists, skipping...")
            continue

        print(f"Downloading {url} ...")
        with httpx.stream("GET", url, follow_redirects=True) as stream:
            total = int(stream.headers.get("Content-Length", 0))
            with open(local_filepath, "wb") as f, tqdm(
                total=total, unit_scale=True, unit_divisor=1024, unit="B"
            ) as progress:
                num_bytes_downloaded = stream.num_bytes_downloaded
                for data in stream.iter_bytes():
                    f.write(data)
                    progress.update(stream.num_bytes_downloaded - num_bytes_downloaded)
                    num_bytes_downloaded = stream.num_bytes_downloaded

def download_additional_models():
    """Download additional models that need special handling"""
    import subprocess
    import os
    
    # Download InsightFace AntelopeV2 models
    antelope_dir = "/root/models/insightface/models/antelopev2"
    os.makedirs(antelope_dir, exist_ok=True)
    
    # These will be auto-downloaded by the PuLID node on first use
    print("InsightFace models will be auto-downloaded on first use")