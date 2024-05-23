import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from kiwipiepy import Kiwi
from fastapi import FastAPI, File, UploadFile
import transfer_novel,preprocess_novel , config,make_transcript
from pydantic import BaseModel

class NovelData(BaseModel):
    source: str
    split : int
    length_limit : int

#@main.app.post("/make-novel/")
def make_novel(data):

    source , split , length_limit = data.source , data.split , data.length_limit
    api_key = config.API_KEY
    splited , num_sens = preprocess_novel.split_novel(source , split)
    fairytail_pharas , previous = transfer_novel.make_novel(api_key,splited , length_limit)

    splited_novel_dict = {}
    for i,phara in enumerate(fairytail_pharas):
        splited_novel_dict[i+1] = phara

    kiwi = Kiwi()
    a = kiwi.split_into_sents(previous)
    novel_num_dict = {}
    for i, aa in enumerate(a):
        novel_num_dict[i+1] = aa[0]

    return {
        'novel_num_dict' :novel_num_dict,   ##  { '문장 번호' : '문장 내용' }
        'splited_novel_dict' : splited_novel_dict   ##  { '단락 번호' : '단락 내용' }
            }


class MadeNovelData(BaseModel):
    novel_num_dict: dict
    splited_novel_dict : dict

#@main.app.post("/make-interaction/")
async def make_interaction(data : MadeNovelData):

    sen_dict , para_dict = data.novel_num_dict , data.splited_novel_dict
    api_key = config.API_KEY
    fairytail_pharas = []

    # Open the file in read mode
    for key in para_dict.keys():
        fairytail_pharas.append(para_dict[key].strip())

    print(fairytail_pharas)
    print(len(fairytail_pharas))


    previous = ''
    for sp in fairytail_pharas:
        previous += sp + ' '

    numed_novel = ''
    for key in sen_dict.keys():
        numed_novel +=f'[{key}]'+sen_dict[key]
    num_sens = len(sen_dict.keys())

    print(numed_novel)
    print(num_sens)

    try:
        script_set = make_transcript.extract_trans(api_key, numed_novel, num_sens)
        trans_tuple, trans_previous = make_transcript.match_trans(numed_novel, previous, script_set)

        emo_script = make_transcript.emo_trans(api_key, trans_previous, trans_tuple)

        guide_script = make_transcript.make_guide(api_key, emo_script, trans_tuple, previous)

        interaction_script = make_transcript.make_interaction(api_key, emo_script, trans_tuple, previous)
    except ValueError:
        return {
            'emotion': 'error',
            'guide': 'error',
            'interaction': 'error'
        }

    script_dict = {
        'emotion': emo_script,
        'guide': guide_script,
        'interaction': interaction_script
    }

    return {
        'emotion' : emo_script,
        'guide' : guide_script,
        'interaction' : interaction_script
            }






