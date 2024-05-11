import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from kiwipiepy import Kiwi
from fastapi import FastAPI, File, UploadFile
import preprocess_novel , config,craft_img_prompt
from pydantic import BaseModel

make_novel_api = FastAPI()


class Imageprompt(BaseModel):
    source: str
    split : int
    scene : int   ### splited 소설 중에서 해당하는 scene
    image_try : int  ### 한번 생성에 몇 번 생성할 것인지

    history_prompt : str  ##이미지 일관성을 위한 사전 역사적 배경 , 없으면 ''
    age_prompt : str      ##이미지 일관성 위한 나이 정보 , 없으면 ''
    char_des_dict : dict  ##이미지 일관성 위한 캐릭터 정보 , 없으면 ''

@make_novel_api.post("/make-image/")
async def make_novel(data : Imageprompt):

    source , split , target_scene,image_try = data.source , data.split , data.scene , data.image_try
    api_key = config.API_KEY

    splited, num_sens = preprocess_novel.split_novel(source, split)

    assert len(splited) >= target_scene

    style_prompt = '- Soft, warm color palette with golden sunlight effect\n- Detailed digital painting with a smooth texture\n- Stylized natural environments with enhanced lighting and shadows\n- Anime-inspired character design with expressive eyes and faces\n- Cinematic composition with a focus on depth and perspective\n- Glistening highlights and subtle glow effects for a magical ambiance'

    history_prompt , age_prompt , char_des_dict = data.history_prompt , data.age_prompt , data.char_des_dict
    if history_prompt == '':
        history_prompt = craft_img_prompt.history_prompt(api_key, source)
    if age_prompt == '':
        age_prompt = craft_img_prompt.age_prompt(api_key, source)
    if char_des_dict == {}:
        char_des_dict = craft_img_prompt.character_prompt(api_key, source)


    for i, scene in enumerate(splited):
        if i != target_scene:
            continue
        final_images = []

        scene_prompt = craft_img_prompt.scene_prompt(api_key, splited[i], age_prompt)
        character_description = craft_img_prompt.make_character_description(api_key, scene_prompt, char_des_dict)
        for j in range(image_try):
            for k in range(5):
                print(f'scene : {scene_prompt}')
                print(f'charac description : {character_description}')
                try:
                    final_image = craft_img_prompt.make_image(api_key, scene_prompt, history_prompt,
                                                              character_description, style_prompt)
                    break
                except Exception as e:
                    ### violation
                    scene_prompt = craft_img_prompt.scene_prompt(api_key, splited[i], age_prompt)
                    continue
            if k == 5:
                print('full violation')
                return
            final_images.append(final_image)


    return {
        'scene_link' : final_images,   ##   ['imglink1','imglink2' ...]
        'history_prompt' : history_prompt,
        'age_prompt' : age_prompt,
        'char_des_dict' : char_des_dict,
            }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(make_novel_api, host="0.0.0.0", port=8002)



