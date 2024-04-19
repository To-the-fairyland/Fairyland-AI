
from openai import OpenAI

def infant_prompt(previous, novel, th, all_th, length):
    if previous == '':
        user_prompt = f"""
<원문> : {novel}

<원문>의 부분을 아동이 읽기 쉬운 형태로 변환하려고 하는데 다음과 같은 사항을 고려해줘

-문장이 끝날 때는 ~~요 라고 해줘.
-<원문>에서의 핵심적인 사건을 중심으로 묘사를 해줘
-두 문장 또는 세 문장으로
-시대적이고 공간적인 배경 , 그리고 인물과 핵심적인 사건을 넣어줘
-핵심적인 사건을 묘사할 때 , 주인공의 대사나 인물의 대사는 꼭 넣어줘.
-주인공의 대사는 ''로 표시된 생각이 아닌 , ""로 표시된 대사로 변환해줘
-대사에서 호칭은 원문 그대로 써줘
-혼자말은 반말로 , 그 외에 다른 대사의 반말/존댓말도 그대로 변환해줘 
-지금은 글의 첫 번째 단락이라 이후에 글이 이어질 것을 고려해서 이야기가 완전히 끝나지 않은 채로 작성해줘
-'오늘 이야기는 끝입니다' 라는거 없이 불완전하게 이야기가 마무리 되게 해줘
- 본문에 없는 부가적인 설명은 넣지 마
- {str(length)}자 이내로 만들 것


<변환> : """



    else:
        user_prompt = f"""
<이전 이야기> : {previous}    

<원문> : {novel}

<원문>의 부분을 아동이 읽기 쉬운 형태로 변환하려고 하는데 다음과 같은 사항을 고려해줘

-<이전 이야기>에서 이어지는 것을 고려해서 적절한 내용으로 바꿔줘
-문장이 끝날 때는 ~~요 라고 해줘.
-<원문>에서의 핵심적인 사건을 중심으로 묘사를 해줘
-두 문장 또는 세 문장으로 만들어줘
-<변환>은 <원문>의 분량을 넘지 않게 해줘
-시대적이고 공간적인 배경 , 그리고 인물과 핵심적인 사건을 넣어줘
-핵심적인 사건을 묘사할 때 , 주인공의 대사나 인물의 대사는 꼭 넣어줘
-주인공의 대사는 ''로 표시된 생각이 아닌 , ""로 표시된 대사로 변환해줘
-대사에서 호칭은 원문 그대로 써줘
-혼자말은 반말로 , 그 외에 다른 대사의 반말/존댓말도 그대로 변환해줘 
-이전 단락과 이어지는 부분에서 내용이 중첩되지 않게 해줘
- {str(length)}자 이내로 만들 것
{'-이번 단락은 소설의 마무리인 점을 고려해서 전체적인 내용을 고려하며 원문 내용을 보존하도록 결말을 지어줘.' if th == all_th else '-이번 단락은 전체 ' + str(all_th) + '개의 단락 중에 ' + str(th) + '번째 임을 고려해서 이야기를 이어질 것을 염두하고 이야기가 끝나지 않은 채 작성해줘 그런데 사족은 달지마. 오늘 이야기는 여기까지에요.. 같은 말 하지마'}


<변환> : """

    return user_prompt

def make_novel(api_key,split_pharagraph,length_limit):

    apikey = api_key

    client = OpenAI(
        api_key=apikey
    )

    fairytale_role = """너는 아동문학 작가야. 너가 하는 일은 기존에 있는 어려운 소설을 아동이 이해하기 쉬운 형태로 변환하는 일이야. 친절하고 구체적으로 , 그리고 대사도 이해하기 쉽고 순화해서 말해야해. 또한 원문의 내용은 최대한 보존해야해. 사건을 있는 그대로 전하고 스타일만 변환하는 거야."""

    # fairy_tales = []
    fairy_tales = []
    previous = ''
    for i, phara in enumerate(split_pharagraph):
        while True:
            if length_limit > 80:
                completion = client.chat.completions.create(
                    model="gpt-4-0125-preview",
                    messages=[
                        {"role": "system", "content": fairytale_role},
                        {"role": "user",
                         "content": infant_prompt(previous, phara, i + 1, len(split_pharagraph), length_limit)}
                    ]
                )
            else:
                completion = client.chat.completions.create(
                    model="gpt-4-0125-preview",
                    messages=[
                        {"role": "system", "content": fairytale_role},
                        {"role": "user",
                         "content": infant_prompt(previous, phara, i + 1, len(split_pharagraph), length_limit)}
                    ]
                )

            print(completion.choices[0].message)

            tale = completion.choices[0].message.content
            if len(tale) > 200:
                print(f'{len(tale)} retry')
                continue
            else:
                break

        fairy_tales.append(tale)
        previous += completion.choices[0].message.content + ' '

    return fairy_tales , previous
