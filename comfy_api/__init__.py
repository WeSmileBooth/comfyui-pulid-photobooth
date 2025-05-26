import pathlib
import json
import subprocess
import time
import modal
import random
import os
import datetime

from .container import image, gpu
from pydantic import BaseModel

app = modal.App("comfy-api-flux")

class InferModel(BaseModel):
    session_id: str
    prompt: str

class JobResult(BaseModel):
    base64_image: str
    signed_url: str

with image.imports():
    from firebase_admin import credentials, initialize_app, storage, firestore

@app.cls(
    gpu=gpu,
    image=image,
    container_idle_timeout=60 * 10,
    timeout=60 * 5,  # Increased timeout for FLUX
    secrets=[
        modal.Secret.from_name("googlecloud-secret"),
        modal.Secret.from_name("gemini-secret")  # Add Gemini API key
    ],
)
class ComfyUI:
    def __init__(self):
        # Firebase setup
        service_account_info = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])
        cred = credentials.Certificate(service_account_info)
        firebase = initialize_app(
            cred,
            options={"storageBucket": "wesmile-photobooth-2.firebasestorage.app"},
        )
        self.bucket = storage.bucket(app=firebase)
        self.db = firestore.client(app=firebase)

        # Load workflow
        self.workflow_json = json.loads(
            pathlib.Path("/root/workflow_api.json").read_text()
        )

    def _run_comfyui_server(self, port=8188):
        cmd = f"python main.py --listen 0.0.0.0 --port {port}"
        subprocess.Popen(cmd, shell=True)

    @modal.enter()
    def prepare(self):
        self._run_comfyui_server(port=8189)

    @modal.method()
    def infer(self, input: InferModel):
        import urllib
        import base64
        import websocket
        import requests
        import copy

        # Wait for ComfyUI to start
        while True:
            try:
                requests.get("http://0.0.0.0:8189/prompt")
                break
            except (requests.ConnectionError, requests.Timeout):
                continue
            except Exception:
                pass

        # Download input image
        bytes_data = self.bucket.blob(f"{input.session_id}/before").download_as_bytes()
        pathlib.Path(f"/root/input/{input.session_id}").write_bytes(bytes_data)

        # Setup timestamps
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        start_time = {
            'timestamp': now_utc.timestamp(),
            'iso': now_utc.isoformat()
        }

        # Prepare workflow
        workflow = copy.deepcopy(self.workflow_json)
        
        # Update key workflow nodes based on your Latest_WeSmile_Workflow.json
        # You'll need to identify which nodes need to be updated with input data
        workflow["111"]["inputs"]["noise_seed"] = random.randint(1, 2**64)
        workflow["232"]["inputs"]["image"] = input.session_id
        
        # Set Gemini API key if using AQ_Gemini nodes
        if "425" in workflow and "gemini_api_key" in workflow["425"]["inputs"]:
            workflow["425"]["inputs"]["gemini_api_key"] = os.environ.get("GEMINI_API_KEY", "")
        
        # The prompt will be processed by your Gemini node in the workflow
        # Update the text concatenation node that feeds into Gemini
        if "378" in workflow:
            workflow["378"]["inputs"]["text"] = f"people. {input.prompt}"

        # Submit workflow
        data = json.dumps({"prompt": workflow, "client_id": input.session_id}).encode("utf-8")
        response = urllib.request.Request(f"http://0.0.0.0:8189/prompt", data=data)
        result = json.loads(urllib.request.urlopen(response).read())
        prompt_id = result["prompt_id"]

        # Update Firestore
        doc_ref = self.db.collection("records").document(input.session_id)
        doc = doc_ref.get()
        doc_data = doc.to_dict() if doc.exists else {}
        generation_count = doc_data.get('generation_count', 0)

        doc_ref.update({
            "prompt_id": prompt_id,
            "prompt": input.prompt,
            "status": "started",
            "progress": 0,
            "generation_count": generation_count + 1,
            "generation_start_times": firestore.ArrayUnion([start_time])
        })

        # Monitor progress via WebSocket
        ws = websocket.WebSocket()
        while True:
            try:
                ws.connect(f"ws://0.0.0.0:8189/ws?clientId={input.session_id}")
                break
            except ConnectionRefusedError:
                time.sleep(1)

        images_output = None
        current_node = ""
        
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)

                if message["type"] == "executing":
                    data = message["data"]
                    if data.get("prompt_id") == prompt_id:
                        if data["node"] is None:
                            doc_ref.update({"status": "executed"})
                            break
                        else:
                            current_node = data["node"]

                elif message["type"] == "progress":
                    data = message["data"]
                    if (data.get("prompt_id") == prompt_id and 
                        data["node"] == "236"):  # SamplerCustomAdvanced node
                        doc_ref.update({
                            "progress": data["value"], 
                            "status": "pending"
                        })
            else:
                # Check for output from VAEDecode node (175 in your workflow)
                if current_node == "175":
                    images_output = out[8:]

        # Save result
        self.bucket.blob(f"{input.session_id}/after").upload_from_string(
            images_output, content_type="image/png"
        )

        # Update completion time
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        end_time = {
            'timestamp': now_utc.timestamp(),
            'iso': now_utc.isoformat()
        }
        
        doc_ref.update({
            "status": "completed",
            "generation_end_times": firestore.ArrayUnion([end_time])
        })

        result = base64.b64encode(images_output).decode()
        return f"data:image/png;base64,{result}"

# Rest of the API remains the same...
@app.function(
    gpu=False,
    image=image,
    allow_concurrent_inputs=100,
    timeout=60 * 15,
    container_idle_timeout=60 * 15,
    secrets=[
        modal.Secret.from_name("googlecloud-secret"),
        modal.Secret.from_name("gemini-secret")
    ],
)
@modal.asgi_app()
def api():
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware

    fastapi = FastAPI()
    fastapi.add_middleware(
        CORSMiddleware,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
        allow_origins=["*"],
    )

    service_account_info = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])
    cred = credentials.Certificate(service_account_info)
    firebase = initialize_app(
        cred,
        options={"storageBucket": "wesmile-photobooth-2.firebasestorage.app"},
    )
    bucket = storage.bucket(app=firebase)

    ComfyUI = modal.Cls.lookup("comfy-api-flux", "ComfyUI")
    comfyui = ComfyUI()

    @fastapi.get("/blob/{blob_name:path}")
    def get_presigned_url(blob_name: str):
        import datetime
        return bucket.blob(blob_name).generate_signed_url(
            expiration=datetime.timedelta(minutes=30), method="GET"
        )

    @fastapi.post("/job")
    def on_job_post(input: InferModel):
        job = comfyui.infer.spawn(input)
        return job.object_id

    @fastapi.get("/job/{job_id}/{session_id}")
    def on_get_job(job_id: str, session_id: str):
        function_call = modal.functions.FunctionCall.from_id(job_id)
        try:
            base64_result = function_call.get(timeout=60)
            signed_url = bucket.blob(f"{session_id}/after").generate_signed_url(
                expiration=datetime.timedelta(minutes=30), method="GET"
            )
            return JobResult(base64_image=base64_result, signed_url=signed_url)
        except TimeoutError:
            raise HTTPException(status_code=425, detail="Job is still processing")
        except Exception as e:
            print(f"Error processing job {job_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing job: {str(e)}")

    return fastapi