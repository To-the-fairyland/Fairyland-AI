from openai import OpenAI


def history_prompt(api_key,source):

    apikey = api_key

    client = OpenAI(
        api_key=apikey
    )

    role = """너는 prompt engeneer야. 너는 소설이 주어졌을 때 사건,인물,배경에 대해서 깊이 있게 분석하며 이를 사람들이 쉽게 이해하게끔 text-to-image model 한테 넣어주는 prompt로 변환해주는 역할을 해. 너는 이 장면을 prompt로 변환하려고 해."""

    prompt = f"""<원문> : {source}


    <원문>에 나오는 역사,시대적 배경을 1~2 단어로 말해줘

    영어 단어로 답해줘 (example : apple)

    answer : """

    completion = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[
            {"role": "system", "content": role},
            {"role": "user", "content": prompt}
        ]
    )

    historical_prompt = completion.choices[0].message.content
    return historical_prompt


def age_prompt(api_key,source):

    apikey = api_key

    client = OpenAI(
        api_key=apikey
    )

    role = """너는 prompt engeneer야. 너는 소설이 주어졌을 때 사건,인물,배경에 대해서 깊이 있게 분석하며 이를 사람들이 쉽게 이해하게끔 text-to-image model 한테 넣어주는 prompt로 변환해주는 역할을 해. 너는 이 장면을 prompt로 변환하려고 해."""

    prompt = f"""<원문> : {source}


    <원문>에 나오는 주인공(들)의 성별과 연령을 구체적인 영어 단어로 답해줘
    주인공이 한 명이면 한 명만 출력해도 돼.

    (NOT EXAMPLE : young girl , young boy)
    (NOT EXAMPLE : girl , boy)

    (CORRECT example : adolscent korean girl , early thirty man)
    (CORRECT example : forty mid woman )
    (CORRECT example : prepubescent boy)

    answer : """

    completion = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": role},
            {"role": "user", "content": prompt}
        ]
    )

    character_ages = completion.choices[0].message.content
    return character_ages


def scene_prompt(api_key,pharagraph,character_ages):

    apikey = api_key

    client = OpenAI(
        api_key=apikey
    )

    role = """너는 prompt engeneer야. 너는 소설이 주어졌을 때 사건,인물,배경에 대해서 깊이 있게 분석하며 이를 사람들이 쉽게 이해하게끔 text-to-image model 한테 넣어주는 prompt로 변환해주는 역할을 해. 너는 이 장면을 prompt로 변환하려고 해."""

    prompt = f"""<원문> : {pharagraph}
    
    <원문>을 dalle에 넣을 prompt로 변환해줘. 다음과 같은 고려 사항을 지켜줘.

    -prompt를 보아도 어떤 장면인지 한 눈에 알아볼 수 있도록 할 것.
    -prompt를 보면 <원문>이 어떤 내용인지 한 눈에 알아볼 수 있도록 할 것
    -해당 부분의 시대,공간적인 배경을 알아볼 수 있도록 할 것.
    -<원문>에 나오는 핵심적인 사건,소재,인물,인물 연령이 드러나게 할 것
    -<원문>에 나오는 인물의 성별을 명확하게 구별할 수 있게 할 것
    -text to image 모델에 넣을 수 있게 문장 길이는 한 문장으로 될 것
    -등장하는 주인공들의 연령도 고려할 것 : {character_ages}
    -영어로 답변할 것 """

    completion = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": role},
            {"role": "user", "content": prompt}
        ]
    )

    scene_prompt = completion.choices[0].message.content
    return scene_prompt

def character_prompt(api_key,source):
    apikey = api_key

    client = OpenAI(
        api_key=apikey
    )

    role = """너는 prompt engeneer야. 너는 캐릭터의 특징을 잘 묘사하는 prompt를 작성하려고 해."""

    prompt = f"""{source}

    <원문>을 dalle에 넣을 prompt로 변환해줘. 다음과 같은 고려 사항을 지켜줘.

    -원문에 주로 등장하는 주인공이 누가 있는지 말해줘
    -주인공의 명칭만 말할 것

    예시1 : 1.김첨지

    예시2 : 1.어린 왕자  2.여우

    """
    while True:
        completion = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system", "content": role},
                {"role": "user", "content": prompt}
            ]
        )

        characters = completion.choices[0].message.content

        character_list = characters.split()
        for i, a in enumerate(character_list):
            character_list[i] = a[a.find('.') + 1:]

        if '' in character_list:
            continue
        else:
            break

    char_des_dict = {}
    for a in character_list:
        char_des_dict[a] = ''
    print(f'character list : {character_list}')


    ### detail한 스타일 정하기
    role = """너는 prompt engeneer야. 너는 캐릭터의 특징을 잘 묘사하는 prompt를 작성하려고 해."""

    for char in character_list:
        prompt = f"""{source}

<원문>을 dalle에 넣을 prompt로 변환해줘. 다음과 같은 고려 사항을 지켜줘.

-<원문>에서 {char}의 옷차림을 최대한 자세히 묘사하려고 해
-dalle3에 어떤 장면과 결합하더라도 동일한 모습을 유지할 수 있게 할 것
-{char}의 머리스타일 , 옷 , 옷 색깔 , 신발 , 체형 , 성별 , 연령대 ,성숙도,키 등 외관에대한 자세한 묘사 
-디즈니 스타일처럼 expressive한 얼굴인 것을 강조할 것 
-<원문>의 역사적 ,시대적 배경에 맞는 외형으로 나타낼 것 
-text to image model에 넣을 수 있게 한 문장으로 작성할 것
-영어로 작성할 것

        """

        completion = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": role},
                {"role": "user", "content": prompt}
            ]
        )

        character_description = completion.choices[0].message.content
        print(character_description)
        char_des_dict[char] = character_description

    return char_des_dict


def make_character_description(api_key,scene_prompt,char_des_dict):
    key_list = list(char_des_dict.keys())
    appears = [False] * len(key_list)

    apikey = api_key

    client = OpenAI(
        api_key=apikey
    )

    for i, key in enumerate(key_list):

        role = """너는 문학평론가야. 너는 소설의 한 장면을 보고 특정 인물이 등장하는지 여부를 판단하려고해 """

        prompt = f"""<source> : {scene_prompt}

        in <source> dose character {list(char_des_dict.keys())[i]} appear in this description?
        if the character appear , return only {0} 
        if not , return only {-1}
        """

        completion = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system", "content": role},
                {"role": "user", "content": prompt}
            ]
        )

        character_appear = completion.choices[0].message.content
        print(character_appear)
        if character_appear == '0':
            appears[i] = True

    character_description = ''

    for i in range(len(appears)):
        if appears[i]:
            character_description += char_des_dict[list(char_des_dict.keys())[i]]

    return character_description


def make_image(api_key,image_prompt , history_prompt , character_description , style_prompt):
    apikey = api_key

    client = OpenAI(
        api_key=apikey
    )

    final_image_prompt = image_prompt + f',{history_prompt},no text,' + character_description + style_prompt

    response = client.images.generate(
        model="dall-e-3",
        prompt=final_image_prompt,
        size="1792x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url

    return image_url
