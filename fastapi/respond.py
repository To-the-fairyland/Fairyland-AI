from fastapi import FastAPI, File, UploadFile, Form
from typing import List
import numpy as np
import librosa
import torch , torchaudio
import speech_recog , similar_check
from pydantic import BaseModel
import shutil
import os
import main


class audiofile(BaseModel):
    file : UploadFile

#@main.app.post("/predict-emotion/")
async def predict_emotion_endpoint(audiofile: UploadFile = File(...)):
    print(audiofile)
    filename = 'imsi.wav'

    file = audiofile.file
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(file, buffer)

    try:
        emotion = speech_recog.predict(filename)
    except FileNotFoundError:
        return {"emotion": 'file not exist'}

    return {"emotion": emotion}

class similarity_audiofile(BaseModel):
    file : UploadFile
    groundtruth : str

#@main.app.post("/asr-similarity/")
async def asr_similarity(audio_file: UploadFile = UploadFile(...), groundtruth: str = Form(...)):

    filename = 'imsi.wav'

    print(audio_file)
    print(groundtruth)

    file,GT = audio_file.file , groundtruth
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(file, buffer)

    transcript = similar_check.asr(filename)
    similarity = similar_check.similar_check(transcript,GT)

    return {"transcript": transcript , "similarity" : similarity}



