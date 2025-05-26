NODES = [
    # PuLID for FLUX
    "https://github.com/balazik/ComfyUI-PuLID-Flux",
    
    # Enhanced Gemini integration
    "https://github.com/ShmuelRonen/ComfyUI-Gemini_Flash_2.0_Exp",
    
    # ControlNet Auxiliary
    "https://github.com/Fannovel16/comfyui_controlnet_aux",
    
    # Impact Pack for face detection
    "https://github.com/ltdrdata/ComfyUI-Impact-Pack",
    
    # Additional utilities
    "https://github.com/pythongosssss/ComfyUI-Custom-Scripts",
    "https://github.com/rgthree/rgthree-comfy",
    
    # Manager
    "https://github.com/ltdrdata/ComfyUI-Manager",
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
            subprocess.run(command, shell=True, check=True)
            print(f"Repository {url} cloned successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repository: {e}")
            continue

        # Install requirements if they exist
        requirements_path = f"/root/custom_nodes/{name}/requirements.txt"
        if os.path.isfile(requirements_path):
            print(f"Installing requirements for {name}...")
            pip_command = f"pip install -r {requirements_path}"
            try:
                subprocess.run(pip_command, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error installing requirements for {name}: {e}")

        # Run install.py if it exists
        install_script = f"/root/custom_nodes/{name}/install.py"
        if os.path.isfile(install_script):
            print(f"Running install script for {name}...")
            try:
                process = subprocess.Popen(
                    ["python", install_script], 
                    cwd=f"/root/custom_nodes/{name}"
                )
                process.wait()
                if process.returncode != 0:
                    print(f"Install script for {name} exited with code {process.returncode}")
            except Exception as e:
                print(f"Error running install script for {name}: {e}")