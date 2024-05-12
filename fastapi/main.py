

from kiwipiepy import Kiwi
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import asyncio
import make_scene,make_novel,respond

app = FastAPI()


@app.post("/make-novel/")
async def make_novel_dummy(data : make_novel.NovelData):
    a = make_novel.make_novel(data)
    return a


@app.post("/make-interaction/")
async def make_interaction_dummy(data:make_novel.MadeNovelData):
    a = make_novel.make_interaction(data)
    return a


@app.post("/make-image/")
async def make_scene_dummy(data:make_scene.Imageprompt):
    a = make_scene.make_novel(data)
    return a

@app.post("/predict-emotion/")
async def predict_emotion_dummy(data:respond.audiofile):
    a = respond.predict_emotion_endpoint(data)
    return a


@app.post("/asr-similarity/")
async def asr_similarity_dummy(data:respond.similarity_audiofile):
    a = respond.asr_similarity(data)
    return a


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
