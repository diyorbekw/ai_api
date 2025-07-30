import time
import json
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

KIE_API_KEY = "ac8c434eb623b4e04754bdff7f40000c"
IMGBB_API_KEY = "3e9ba6c3b2a65d8a1e97b15c9d5ef86d"

app = FastAPI(title="AI API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def generate_image_with_prompt(image_bytes: bytes, prompt: str) -> str:
    upload_url = "https://api.imgbb.com/1/upload"
    files = {"image": image_bytes}
    upload_resp = requests.post(upload_url, params={"key": IMGBB_API_KEY}, files=files)
    if not upload_resp.ok:
        raise HTTPException(status_code=500, detail="Image upload failed")
    image_url = upload_resp.json()["data"]["url"]

    generate_url = "https://api.kie.ai/api/v1/flux/kontext/generate"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {KIE_API_KEY}"
    }
    payload = json.dumps({
        "inputImage": image_url,
        "prompt": prompt,
        "enableTranslation": True,
        "aspectRatio": "16:9",
        "outputFormat": "jpeg",
        "promptUpsampling": False,
        "model": "flux-kontext-pro"
    })
    gen_resp = requests.post(generate_url, headers=headers, data=payload)
    if not gen_resp.ok:
        raise HTTPException(status_code=500, detail="Image generation failed")
    task_id = gen_resp.json()["data"]["taskId"]

    record_url = "https://api.kie.ai/api/v1/flux/kontext/record-info"
    for _ in range(60):
        time.sleep(2)
        result_resp = requests.get(record_url, headers=headers, params={"taskId": task_id})
        result_data = result_resp.json()["data"]
        if result_data.get("response") and result_data["response"].get("resultImageUrl"):
            return result_data["response"]["resultImageUrl"]

    raise HTTPException(status_code=504, detail="Image generation timed out")


@app.post("/ghibli", summary="Ghibli-style image", tags=["styles"])
async def ghibli_style(file: UploadFile = File(...)):
    image_bytes = await file.read()
    result_url = generate_image_with_prompt(image_bytes, "Make that image on ghibli style")
    return JSONResponse(content={"result_url": result_url})


@app.post("/cartoon", summary="Cartoon avatar style image", tags=["styles"])
async def cartoon_style(file: UploadFile = File(...)):
    image_bytes = await file.read()
    result_url = generate_image_with_prompt(image_bytes, "Make that image in cartoon avatar style")
    return JSONResponse(content={"result_url": result_url})


@app.post("/watercolor", summary="Watercolor painting style image", tags=["styles"])
async def watercolor_style(file: UploadFile = File(...)):
    image_bytes = await file.read()
    result_url = generate_image_with_prompt(image_bytes, "Make that image in watercolor painting style")
    return JSONResponse(content={"result_url": result_url})


@app.post("/anime", summary="Anime style image", tags=["styles"])
async def anime_style(file: UploadFile = File(...)):
    image_bytes = await file.read()
    result_url = generate_image_with_prompt(image_bytes, "Make that image in anime style")
    return JSONResponse(content={"result_url": result_url})


@app.post("/plastilin3d", summary="3D plastilin (clay) style image", tags=["styles"])
async def plastilin_style(file: UploadFile = File(...)):
    image_bytes = await file.read()
    result_url = generate_image_with_prompt(image_bytes, "Make that image in 3D clay plastilin style")
    return JSONResponse(content={"result_url": result_url})


@app.post("/plastic", summary="Shiny plastic sculpture style image", tags=["styles"])
async def plastic_style(file: UploadFile = File(...)):
    image_bytes = await file.read()
    result_url = generate_image_with_prompt(image_bytes, "Make that image in shiny plastic sculpture style")
    return JSONResponse(content={"result_url": result_url})
