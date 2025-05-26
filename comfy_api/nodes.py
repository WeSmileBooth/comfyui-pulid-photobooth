NODES = [
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

def create_aq_gemini_node():
    """Create the AQ_Gemini node since it's not in a standard repository"""
    import os
    
    node_dir = "/root/custom_nodes/AQ_Gemini"
    os.makedirs(node_dir, exist_ok=True)
    
    # Create a simple AQ_Gemini node
    node_code = '''
import json
import requests
import os

class AQ_Gemini:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "gemini_api_key": ("STRING", {"default": ""}),
                "model_selection": (["gemini-2.0-flash-lite", "gemini-1.5-flash", "gemini-1.5-pro"], {"default": "gemini-2.0-flash-lite"}),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "system_message": ("STRING", {"multiline": True, "default": ""}),
                "temperature": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
                "top_k": ("INT", {"default": 64, "min": 1, "max": 100}),
                "top_p": ("FLOAT", {"default": 0.95, "min": 0.0, "max": 1.0, "step": 0.05}),
                "enable_json": ("BOOLEAN", {"default": True}),
                "json_schema": ("STRING", {"multiline": True, "default": "{}"}),
                "result_template": ("STRING", {"default": "{json[new_scene_description]} in style {json[new_style]}, {json[new_image_type]}"}),
            },
            "optional": {
                "image": ("IMAGE",),
                "custom_model": ("STRING", {"default": ""}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("result", "json_output", "raw_response")
    FUNCTION = "generate"
    CATEGORY = "AQ_Gemini"
    
    def generate(self, gemini_api_key, model_selection, prompt, system_message, temperature, top_k, top_p, enable_json, json_schema, result_template, image=None, custom_model=""):
        try:
            # Simple mock response for testing
            mock_json = {
                "user_idea": prompt,
                "new_scene_description": f"A transformed scene based on: {prompt}",
                "new_image_type": "digital art",
                "new_style": "realistic"
            }
            
            json_output = json.dumps(mock_json)
            
            # Apply result template
            try:
                result = result_template.format(json=mock_json)
            except:
                result = mock_json["new_scene_description"]
            
            return (result, json_output, json_output)
            
        except Exception as e:
            error_msg = f"Error in AQ_Gemini: {str(e)}"
            return (error_msg, "{}", error_msg)

NODE_CLASS_MAPPINGS = {
    "AQ_Gemini": AQ_Gemini,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AQ_Gemini": "AQ Gemini",
}
'''
    
    with open(f"{node_dir}/__init__.py", "w") as f:
        f.write(node_code)
    
    print("Created AQ_Gemini node")