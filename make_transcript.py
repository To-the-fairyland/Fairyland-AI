from kiwipiepy import Kiwi
from openai import OpenAI


def trans_blank(previous):
    kiwi = Kiwi()

    a = kiwi.split_into_sents(previous)
    splited_fairytale = ''
    for i, aa in enumerate(a):
        splited_fairytale += f'[{i + 1}]' + aa[0]
    return splited_fairytale


def extract_trans(api_key,splited_fairytale,sen_len):

    trans_role = """너는 문학평론가야. 문학평론가란 소설 속 인물과 사건을 면밀히 분석하여 인물의 대사들을 구분하고 어떤 인물이 한 대사인지 아는 역할을 말해"""

    def trans_prompt(novel):
        user_prompt = f"""    
    <원문> : {novel}

    <원문>은 하나의 문학 작품이 문장 별로 분리된 형태야. 

    - 주인공의 대사만 골라줘. 주인공은 작품에서 단 한 명인데, 소설 속 사건과 대사의 중심에 있는 역할을 의미해. 너는 다른 인물의 대사가 아닌 주인공의 대사만 골라야 해.
    - 출력할 때는 숫자만 반환해줘 예를 들면 , [1],[2] 이런식으로
    - 주인공의 대사는 하나도 빠짐없이 모두 골라줘
    - ~어요 라고 끝나는 나레이션은 선택하지마. (예 : 주인공은 행복했어요)
    - 주인공의 감정을 나타내는 중요한 대사도 골라줘

    <대사> : """
        return user_prompt

    apikey = api_key

    client = OpenAI(
        api_key=apikey
    )

    fairy_tales = []

    trans_set = set()

    gpt = "gpt-4-turbo"  ##"gpt-4-0125-preview"

    splited = sen_len // 3
    pos = splited_fairytale.find(f'[{str(splited)}]')

    for k in range(3):
        splited_ = splited_fairytale[k * pos:(k + 1) * pos]
        completion = client.chat.completions.create(
            model=gpt,
            messages=[
                {"role": "system", "content": trans_role},
                {"role": "user", "content": trans_prompt(splited_)}
            ]
        )

        list_answer = completion.choices[0].message.content
        for k in list_answer.split(','):
            trans_set.add(k)

        print(list_answer)

    return trans_set


def match_trans(numed_fairytale,previous,trans_set):

    trans_tuple = []
    for trans in trans_set:
        trans = trans.strip()
        start_pos = numed_fairytale.find(trans)
        start_num = int(trans[1:-1])
        end_num = start_num + 1
        trans_next = f'[{str(end_num)}]'
        end_pos = numed_fairytale.find(trans_next)

        string = numed_fairytale[numed_fairytale.find(trans) + len(trans):numed_fairytale.find(trans_next)]
        print(f'{trans} {string}')
        if '"' in string:
            if string.count('"') == 1:
                trans_string = string[:string.find('"')]
            else:
                start_pos = 0
                for j in range(string.count('"') // 2):
                    start_pos = string.find('"', start_pos + 1)
                    end_pos = string.find('"', start_pos + 1)
                    trans_string = string[start_pos + 1:end_pos]
                    start_pos = end_pos
        #        print(True)
        else:
            if numed_fairytale[start_pos - 1:start_pos] == '"':
                trans_string = string
            #            print(True)
            else:
                print(False)

        final_target = trans_string.strip()

        if final_target == '':
            continue
        if final_target[-2:] == '요.':
            continue

        trans_tuple.append((int(trans[1:-1]), trans_string.strip()))

    trans_tuple = sorted(trans_tuple, key=lambda x: x[0])
    for trans in trans_tuple:
        order, string = trans
        trans_previous = previous.replace(string, '_')
    return trans_tuple , trans_previous


def emo_trans(api_key,trans_previous , trans_tuple):
    trans_role = """너는 동화 전문가야. 너는 다음 주어질 동화를 읽고 지정된 대사에 담겨있는 인물의 감정을 알아내려고 해."""

    def trans_emo_prompt(novel, emo, transs):
        user_prompt = f"""
    <원문> : {novel}

    <모든 대사> : {transs}

    <원문>은 동화야. 다음의 지시 사항을 따라줘.

    - 감정이 '{emo}' 인 대사를 모두 찾으려고 해. 이에 해당하는 대사를 모두 골라줘
    - 해당하는 대사의 번호로만 대답할 것
    - 존재하지 않으면 0 이라고 답할 것

    예시1 : {transs[-1][0]}
    예시2 : {transs[-2][0]},{transs[1][0]}
    예시3 : 0


    <대사> : """

        return user_prompt

    def main_point_prompt(novel, emo, transs):
        user_prompt = f"""    
    <원문> : {novel}

    <모든 대사> : {transs}

    <원문>은 동화야. 다음의 지시 사항을 따라줘.

    - 이 소설에서 메인 포인트가 되는 가장 중요한 대사를 고르려고 해 
    - 메인 포인트란 , 소설을 읽고 가장 기억에 남는 장면,대사를 의미해
    - 해당하는 대사의 번호로만 대답할 것

    예시1 : {transs[-1][0]}
    예시2 : {transs[-2][0]},{transs[1][0]}


    <대사> : """

        return user_prompt

    apikey = api_key

    client = OpenAI(
        api_key=apikey
    )

    label_list = ['calm',  'happy','sad', 'anger','fear','surprise', 'main']

    trans_sets = []

    gpt = "gpt-4-turbo"  ##"gpt-4-0125-preview"

    for l, label in enumerate(label_list):

        if label == 'main':
            prompt = main_point_prompt(trans_previous, label, trans_tuple)
        else:
            prompt = trans_emo_prompt(trans_previous, label, trans_tuple)

        completion = client.chat.completions.create(
            model=gpt,
            messages=[
                {"role": "system", "content": trans_role},
                {"role": "user", "content": prompt}
            ]
        )

        transcript_nums = completion.choices[0].message.content
        print(transcript_nums)
        trans_sets.append(transcript_nums)

    transes = []
    for tran in trans_sets:
        transes.append(tran.split(','))

    for i, tran in enumerate(transes):
        if i == 0:
            continue
        for t in tran:
            if t == '0':
                break
            t = t.strip()
            find = '[' + t + ']'
            for u in trans_tuple:
                if not u[0] == int(t):
                    continue
                print(f'{find} {u[1]}')
                break
    return transes



def make_guide(api_key,trans_sets,trans_tuple,previous):

    apikey = api_key
    client = OpenAI(
        api_key=apikey
    )

    trans_role = """너는 동화 전문가야. 너는 어린이한테 원래 들어갈 대사의 내용을 맞출 수 있도록 도와주려고 해"""

    def generate_guide_trans(novel, transs):
        user_prompt = f"""    
    <원문> : {novel}

    <대사> : {transs}

    <원문>은 대사가 포함된 소설의 일부분이야. 어린이는 <원문>에 <대사>가 들어가 있는지 몰라. 
    맥락적인 요소를 고려하여 어린이가 <대사>를 맞히기 위해 안내를 하려고 해.
    다음과 같은 지시사항을 지켜줘

    - 안내 문구는 1~2문장으로 할 것
    - 문장은 '말해보세요' 라고 끝날 것
    - 설명 없이 안내 문구만 출력할 것
    - 맥락적 상황을 설명하며 어떤 말이 적절할지 유도하는 상황 설명을 할 것 
    - 대사의 주체가 원문 그대로 반영되도록 할 것

    """
        return user_prompt

    guide_transes = []

    for i, tran in enumerate(trans_sets):
        gens = []
        if i == 0:
            guide_transes.append(gens)
            continue
        for t in tran:
            if t == '0':
                break
            t = t.strip()

            for u in trans_tuple:
                if not u[0] == int(t):
                    print(f'{u[0]} , {t} different')
                    continue
                break

            pos = previous.find(u[1])
            if pos < 200:
                context = previous[:pos + 200]
            elif pos + 200 > len(previous):
                context = previous[pos - 200:]
            else:
                context = previous[pos - 200:pos + 200]
            gen_trans_prompt = generate_guide_trans(context, u[1])

            completion = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": trans_role},
                    {"role": "user", "content": gen_trans_prompt}
                ]
            )

            generated_trans = completion.choices[0].message.content
            gens.append(generated_trans)
            print(generated_trans)
        guide_transes.append(gens)

    return guide_transes



def make_interaction(api_key,trans_sets , trans_tuple , previous):

    apikey = api_key
    client = OpenAI(
        api_key=apikey
    )

    trans_role = """너는 동화 전문가야. 너는 다음 주어질 동화와 해당하는 대사를 읽고 그 대사 주변의 말에 대한 롤플레잉을 생성하려고 해."""

    def generate_role_trans(novel, transs):
        user_prompt = f"""    
    <원문> : {novel}

    <대사> : {transs}

    <원문>은 대사가 포함된 소설의 일부분이야. 다음의 지시 사항을 따라줘.

    - [나]와 [너]의 4마디의 대사로만 대답할 것
    - 주변의 맥락을 파악하여 적절한 대사를 만들 것
    - <대사>가 실제로 인물이 말하는 대사가 아니라면 0으로 답할것
    - <대사>는 예시에 반드시 포함될 것
    - <대사>는 [나]가 말할 것
    - 반말/존댓말은 <원문> 그대로 유지할 것
    - 단 , 대사가 혼잣말이고 대화하는 대상이 없다면 그 말 1마디만 출력할 것

    예시1 , <대사>가 '안녕'일 때 : [나]:안녕 \n[너]:안녕 \n[나]:잘지내? \n[너]:잘지내 \n

    <롤플레잉> : """

        return user_prompt


    gen_transes = []

    for i, tran in enumerate(trans_sets):
        gens = []
        if i == 0:
            gen_transes.append(gens)
            continue
        for t in tran:
            if t == '0':
                break
            t = t.strip()
            find = '[' + t + ']'
            for u in trans_tuple:
                if not u[0] == int(t):
                    continue
                break

            pos = previous.find(u[1])
            window = 200
            if pos < window:
                context = previous[:pos + window]
            elif pos + window > len(previous):
                context = previous[pos - window:]
            else:
                context = previous[pos - window:pos + window]

            gen_trans_prompt = generate_role_trans(context, u[1])

            completion = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": trans_role},
                    {"role": "user", "content": gen_trans_prompt}
                ]
            )

            generated_trans = completion.choices[0].message.content
            gens.append(generated_trans)
            print(generated_trans)
            print('')
        gen_transes.append(gens)

    return gen_transes





