from fastapi import FastAPI, File, UploadFile
from typing import List
import numpy as np
import librosa
import torch , torchaudio
import speech_recog , similar_check

app = FastAPI()

@app.post("/predict-emotion/")
async def predict_emotion_endpoint(file_directory: str):
    try:
        emotion = speech_recog.predict(file_directory)
    except FileNotFoundError:
        return {"emotion": 'file not exist'}

    return {"emotion": emotion}

@app.post("/asr-similarity/")
async def asr_similarity(file_directory: str,GT : str):

    transcript = similar_check.asr(file_directory)
    similarity = similar_check.similar_check(transcript,GT)

    return {"transcript": transcript , "similarity" : similarity}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
