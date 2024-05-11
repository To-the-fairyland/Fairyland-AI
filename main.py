
import argparse
import make_transcript
import preprocess_novel
import transfer_novel
import craft_img_prompt
from kiwipiepy import Kiwi
import json
import requests
import os
import config

def download_image(url, filename):
    try:
        # Send a GET request to the image URL
        response = requests.get(url)
        # Check if the request was successful
        if response.status_code == 200:
            # Open a file in binary write mode
            with open(filename, 'wb') as f:
                # Write the content of the response to the file
                f.write(response.content)
            print("Image downloaded successfully as", filename)
        else:
            print("Failed to download image:", response.status_code)
    except Exception as e:
        print("An error occurred:", e)
def main(args):
    split = args.split
    source_novel = args.source_novel_txt
    make_novel = args.make_novel
    make_interaction = args.make_interaction
    make_image = args.make_image
    length_limit = args.length_limit
    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    api_key = config.API_KEY

    ### source 불러오기
    source = ''
    with open(source_novel, "r",encoding = 'utf-8') as file:
        # Read all lines into a list
        lines = file.readlines()
    for line in lines:
        source += line

    novel_file_name = output_dir + '/'+f'output_novel_{str(length_limit)}.txt'
    if make_novel:
        splited , num_sens = preprocess_novel.split_novel(source , split)
        fairytail_pharas , previous = transfer_novel.make_novel(api_key,splited , length_limit)

        with open(novel_file_name , "w") as file:
            for item in fairytail_pharas:
                file.write(item + "\n")



    if make_interaction:

        fairytail_pharas = []

        # Open the file in read mode
        with open(novel_file_name, "r") as file:
            # Read each line and append it to the loaded_list
            for line in file:
                fairytail_pharas.append(line.strip())

        print(fairytail_pharas)
        print(len(fairytail_pharas))

        def split_sens(pharas):
            kiwi = Kiwi()
            a = kiwi.split_into_sents(pharas)
            splited = ''
            for i, aa in enumerate(a):
                splited += f'[{i + 1}]' + aa[0]

            num_sens = int(splited[splited.rfind('[') + 1:splited.rfind(']')])
            return splited , num_sens
        previous = ''
        for sp in fairytail_pharas:
            previous += sp + ' '

        numed_novel , num_sens = split_sens(previous)
        script_set = make_transcript.extract_trans(api_key,numed_novel,num_sens)
        trans_tuple , trans_previous = make_transcript.match_trans(numed_novel , previous , script_set)

        emo_script = make_transcript.emo_trans(api_key,trans_previous,trans_tuple)

        guide_script = make_transcript.make_guide(api_key,emo_script,trans_tuple,previous)

        interaction_script = make_transcript.make_interaction(api_key,emo_script,trans_tuple,previous)

        script_dict = {
            'emotion' : emo_script,
            'guide' : guide_script,
            'interaction' : interaction_script
        }

        transcript_file_name = output_dir +'/'+f'transcript_{str(length_limit)}.json'

        with open(transcript_file_name, "w") as json_file:
            json.dump(script_dict, json_file)

    if make_image:
        image_try = args.image_try

        image_dir = output_dir + '/' + 'images'
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        splited, num_sens = preprocess_novel.split_novel(source, split)

        style_prompt = '- Soft, warm color palette with golden sunlight effect\n- Detailed digital painting with a smooth texture\n- Stylized natural environments with enhanced lighting and shadows\n- Anime-inspired character design with expressive eyes and faces\n- Cinematic composition with a focus on depth and perspective\n- Glistening highlights and subtle glow effects for a magical ambiance'
        history_prompt = craft_img_prompt.history_prompt(api_key,source)
        age_prompt = craft_img_prompt.age_prompt(api_key,source)
        char_des_dict = craft_img_prompt.character_prompt(api_key,source)

        scene_dict = {}
        for i , scene in enumerate(splited):
            final_images = []

            scene_prompt = craft_img_prompt.scene_prompt(api_key,splited[i], age_prompt)
            character_description = craft_img_prompt.make_character_description(api_key,scene_prompt, char_des_dict)
            for j in range(image_try):
                for k in range(5):
                    print(f'scene : {scene_prompt}')
                    print(f'charac description : {character_description}')
                    try:
                        final_image = craft_img_prompt.make_image(api_key,scene_prompt,history_prompt,character_description,style_prompt)
                        break
                    except Exception as e:
                        ### violation
                        scene_prompt = craft_img_prompt.scene_prompt(api_key,splited[i], age_prompt)
                        continue
                if k == 5:
                    print('full violation')
                    return
                final_images.append(final_image)

                filename = f'{image_dir}/{i}_{j}.png'
                download_image(final_image,filename)
            scene_dict[i] = final_images

            with open(image_dir + '/' + 'image_scene.json', "w") as json_file:
                json.dump(scene_dict, json_file)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Example program")
    parser.add_argument("--output_dir", type=str, default=False)
    parser.add_argument("--make_novel",type=bool, default=False)
    parser.add_argument("--make_interaction",type=bool , default=False)
    parser.add_argument("--make_image", type=bool , default=False)
    parser.add_argument("--split", type=int,default=36)
    parser.add_argument("--length_limit", type=int, default=100)
    parser.add_argument("--source_novel_txt" , type=str )
    parser.add_argument("--transfered_novel_txt", type=str)
    parser.add_argument("--image_try", type=int , default = 1)
    args = parser.parse_args()
    main(args)




