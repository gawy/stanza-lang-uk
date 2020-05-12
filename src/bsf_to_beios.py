import os
from collections import namedtuple
import re


BsfMeta = namedtuple('BsfMeta', 'id, type, start_idx, end_idx, token')

def convert_bsf_2_beios(data: str, bsf_markup: str) -> str:
    """
    Convert data file with NER markup in Brat Standoff Format to BEIOS format.

    :param data: tokenized data to be converted. Each token separated with a space
    :param bsf_markup: Brat Standoff Format markup
    :return: data in BEIOS format https://en.wikipedia.org/wiki/Inside–outside–beginning_(tagging)
    """


    return ''


def parse_bsf(bsf_data: str) -> list:
    """
    Convert textual bsf representation to a list of named entities.

    :param bsf_data: data in the format 'T9	PERS 778 783    токен'
    :return: list of named tuples for each line of the data representing a single named entity token
    """
    if len(bsf_data.strip()) == 0:
        return []

    ln_ptrn = re.compile(r'(T\d+)\s(\w+)\s(\d+)\s(\d+)\s(.+?)(?=T\d+\s\w+\s\d+\s\d+|$)', flags=re.DOTALL)
    result = []
    for m in ln_ptrn.finditer(bsf_data.strip()):
        bsf = BsfMeta(m.group(1), m.group(2), int(m.group(3)), int(m.group(4)), m.group(5).strip())
        result.append(bsf)
    return result
