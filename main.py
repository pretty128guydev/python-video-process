from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from video_analysis import model_interface
from video_process_first import model_interface_first
from video_process_second import model_interface_second

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

#app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("frontend/index.html") as f:
        return HTMLResponse(f.read())

@app.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    upload_path = f"temp_{file.filename}"
    with open(upload_path, "wb") as f:
        f.write(await file.read())

    best_result, segment_path = model_interface(upload_path)
    os.remove(upload_path)

    # Определим порог вероятности
    probability_threshold = 70.0  # Порог в процентах

    # Формируем ответ на основе порога
    analysis_result = f"Маргинальная активность обнаружена с вероятностью {best_result['likely_probability']:.2f}%"

    response = {
        "Результаты анализа": {
            "Вероятность маргинальной активности": analysis_result
        }
    }

    if segment_path:
        response["Ссылка на сегмент видео"] = f"/download/{os.path.basename(segment_path)}"

    return JSONResponse(content=response)

@app.post("/analyze_first")
async def analyze_video_first(file: UploadFile = File(...)):
    upload_path = f"temp_{file.filename}"
    with open(upload_path, "wb") as f:
        f.write(await file.read())

    best_result, segment_path = model_interface_first(upload_path)
    os.remove(upload_path)

    # Определим порог вероятности
    probability_threshold = 70.0  # Порог в процентах
    if best_result["likely_label"] != "other":
        # Формируем ответ на основе порога
        analysis_result = f"Маргинальная активность обнаружена с вероятностью {best_result['likely_probability']:.2f}%"
    else:
        analysis_result = "Маргинальная активность не обнаружена"

    response = {
        "Результаты анализа": {
            "Вероятность маргинальной активности": analysis_result
        }
    }

    if segment_path:
        response["Ссылка на сегмент видео"] = f"/download/{os.path.basename(segment_path)}"

    return JSONResponse(content=response)

@app.post("/analyze_second")
async def analyze_video_first(file: UploadFile = File(...)):
    upload_path = f"temp_{file.filename}"
    with open(upload_path, "wb") as f:
        f.write(await file.read())

    best_result, segment_path = model_interface_second(upload_path)
    os.remove(upload_path)

    # Определим порог вероятности
    probability_threshold = 70.0  # Порог в процентах

    if best_result["likely_label"] != "other":
        # Формируем ответ на основе порога
        analysis_result = f"Маргинальная активность обнаружена с вероятностью {best_result['likely_probability']:.2f}%"
    else:
        analysis_result = "Маргинальная активность не обнаружена"

    response = {
        "Результаты анализа": {
            "Вероятность маргинальной активности": analysis_result
        }
    }

    if segment_path:
        response["Ссылка на сегмент видео"] = f"/download/{os.path.basename(segment_path)}"

    return JSONResponse(content=response)

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join("saved_segments", filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=filename, media_type='application/octet-stream')
    return JSONResponse(content={"error": "Файл не найден"}, status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
