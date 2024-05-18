

from kiwipiepy import Kiwi
from fastapi import FastAPI, File, UploadFile , Form
from pydantic import BaseModel
import asyncio
import make_image,make_novel,respond

app = FastAPI()


@app.post("/make-novel/")
async def make_novel_dummy(data : make_novel.NovelData):
    a =  make_novel.make_novel(data)
    return a


@app.post("/make-interaction/")
async def make_interaction_dummy(data : make_novel.MadeNovelData):
    print(data)
    a = await make_novel.make_interaction(data)
    return a


@app.post("/predict-emotion/")
async def predict_emotion_dummy(audiofile: UploadFile = File(...)):
    a = await respond.predict_emotion_endpoint(audiofile)
    return a


@app.post("/asr-similarity/")
async def asr_similarity_dummy(audio_file: UploadFile = UploadFile(...), groundtruth: str = Form(...)):
    a = await respond.asr_similarity(audio_file , groundtruth)
    return a


@app.post("/make-image/")
async def make_image_dummy(data:make_image.Imageprompt):
    a = await make_image.make_novel(data)
    return a

@app.post("/make-cover/")
async def make_cover_dummy(data:make_image.Coverprompt):
    a = await make_image.make_cover(data)
    return a

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
