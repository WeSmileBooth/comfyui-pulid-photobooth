NODES = [
    # AQ Nodes
    "https://github.com/2frames/ComfyUI-AQnodes",
    
    # Core custom nodes for your workflow
    "https://github.com/balazik/ComfyUI-PuLID-Flux",
    "https://github.com/Fannovel16/comfyui_controlnet_aux", 
    "https://github.com/ltdrdata/ComfyUI-Impact-Pack",
    "https://github.com/pythongosssss/ComfyUI-Custom-Scripts",
    "https://github.com/rgthree/rgthree-comfy",
    "https://github.com/ltdrdata/ComfyUI-Manager",
    
    # For your specific workflow nodes
    "https://github.com/WASasquatch/was-node-suite-comfyui",
]

def download_nodes():
    import subprocess
    import os

    for url in NODES:
        name = url.split("/")[-1]
        target_path = f"/root/custom_nodes/{name}"
        
        if os.path.exists(target_path):
            print(f"Node {name} already exists, skipping...")
            continue
            
        print(f"Cloning {name}...")
        command = f"cd /root/custom_nodes && git clone {url}"

        try:
            subprocess.run(command, shell=True, check=True, timeout=300)
            print(f"Repository {url} cloned successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repository: {e}")
            continue
        except subprocess.TimeoutExpired:
            print(f"Timeout cloning {name}")
            continue

        # Install requirements if they exist
        requirements_path = f"/root/custom_nodes/{name}/requirements.txt"
        if os.path.isfile(requirements_path):
            print(f"Installing requirements for {name}...")
            pip_command = f"pip install -r {requirements_path}"
            try:
                subprocess.run(pip_command, shell=True, check=True, timeout=600)
            except subprocess.CalledProcessError as e:
                print(f"Error installing requirements for {name}: {e}")
            except subprocess.TimeoutExpired:
                print(f"Timeout installing requirements for {name}")

        # Run install.py if it exists
        install_script = f"/root/custom_nodes/{name}/install.py"
        if os.path.isfile(install_script):
            print(f"Running install script for {name}...")
            try:
                process = subprocess.Popen(
                    ["python", install_script], 
                    cwd=f"/root/custom_nodes/{name}"
                )
                process.wait(timeout=600)
                if process.returncode != 0:
                    print(f"Install script for {name} exited with code {process.returncode}")
            except subprocess.TimeoutExpired:
                print(f"Timeout running install script for {name}")
            except Exception as e:
                print(f"Error running install script for {name}: {e}")
