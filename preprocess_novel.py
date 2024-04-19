
from kiwipiepy import Kiwi
import re

def split_novel(source , n=36):

    kiwi = Kiwi()
    a = kiwi.split_into_sents(source)
    splited = ''
    for i, aa in enumerate(a):
        splited += f'[{i + 1}]' + aa[0]

    num_sens = int(splited[splited.rfind('[') + 1:splited.rfind(']')])

    def split_number(num, parts):
        size = num // parts
        remainder = num % parts
        result = []
        current = 0
        for i in range(parts):
            result.append(current + size)
            current += size
            if remainder > 0:
                current += 1
                remainder -= 1
        return result

    split_pos = split_number(num_sens, n)
    split_pos = split_pos[:-1]
    split_pos = [str(x) for x in split_pos]

    split_pharagraph = []
    for i in range(len(split_pos)):
        now = splited.find('[' + split_pos[i - 1] + ']') + 2 + len(split_pos[i - 1])
        if i == len(split_pos) - 1:
            pharagraph = splited[now:]
        elif i == 0:
            next_ = splited.find('[' + split_pos[i + 1] + ']') + 2 + len(split_pos[i + 1])
            pharagraph = splited[:next_]
        else:
            next_ = splited.find('[' + split_pos[i] + ']') + 2 + len(split_pos[i])
            pharagraph = splited[now:next_]
        pharagraph_ = re.sub(r'\[\d+\]', '', pharagraph)
        split_pharagraph.append(pharagraph_)


    return split_pharagraph , num_sens



