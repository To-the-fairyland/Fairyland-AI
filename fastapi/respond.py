from fastapi import FastAPI, File, UploadFile
from typing import List
import numpy as np
import librosa
import torch , torchaudio
import speech_recog , similar_check
from pydantic import BaseModel
import shutil
import os

app = FastAPI()


class audiofile(BaseModel):
    file : UploadFile

@app.post("/predict-emotion/")
async def predict_emotion_endpoint(audiofile: UploadFile = File(...)):
    print(audiofile)
    filename = 'imsi.wav'

    file = audiofile.file
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(file, buffer)

    # Get the current directory
    current_directory = os.getcwd()
    # List all files in the current directory
    files = os.listdir(current_directory)
    print(files)

    try:
        emotion = speech_recog.predict(filename)
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
    uvicorn.run(app, host="0.0.0.0", port=8001)
