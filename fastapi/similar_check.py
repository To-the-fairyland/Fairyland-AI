import os,sys

from openai import OpenAI
import numpy as np
from numpy.linalg import norm

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

import config

def cosine_similarity(vector_a, vector_b):
    dot_product = np.dot(vector_a, vector_b)
    norm_a = norm(vector_a)
    norm_b = norm(vector_b)
    similarity = dot_product / (norm_a * norm_b)
    return similarity

def asr(filename):
    audio_file = open(filename, "rb")
    apikey = config.API_KEY
    client = OpenAI(
        api_key=apikey
    )
    transcript = client.audio.transcriptions.create(
      model="whisper-1",
      file=audio_file
    )
    return transcript.text

def similar_check(transcript , GT):

    apikey = config.API_KEY
    client = OpenAI(
        api_key=apikey
    )
    def get_embedding(text):
        text = text.replace("\n", " ")
        return client.embeddings.create(input=[text], model='text-embedding-3-large').data[0].embedding

    gt_embedding = get_embedding(GT)
    trans_embedding = get_embedding(transcript)

    return cosine_similarity(gt_embedding , trans_embedding)







