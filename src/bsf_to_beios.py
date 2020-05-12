import os
import glob
from collections import namedtuple
import re
import logging
from tqdm import tqdm


BsfInfo = namedtuple('BsfInfo', 'id, tag, start_idx, end_idx, token')

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def convert_bsf_2_beios(data: str, bsf_markup: str) -> str:
    """
    Convert data file with NER markup in Brat Standoff Format to BEIOS format.

    :param data: tokenized data to be converted. Each token separated with a space
    :param bsf_markup: Brat Standoff Format markup
    :return: data in BEIOS format https://en.wikipedia.org/wiki/Inside–outside–beginning_(tagging)
    """

    def join_simple_chunk(chunk: str) -> list:
        if len(chunk.strip()) == 0:
            return []
        tokens = re.split(r'\s', chunk.strip())
        return [token + ' O' if len(token.strip()) > 0 else token for token in tokens]

    res = []
    markup = parse_bsf(bsf_markup)

    prev_idx = 0
    m_ln: BsfInfo
    for m_ln in markup:
        res += join_simple_chunk(data[prev_idx:m_ln.start_idx])

        t_words = m_ln.token.split(' ')
        if len(t_words) == 1:
            res.append(m_ln.token + ' S-' + m_ln.tag)
        else:
            res.append(t_words[0] + ' B-' + m_ln.tag)
            for t_word in t_words[1: -1]:
                res.append(t_word + ' I-' + m_ln.tag)
            res.append(t_words[-1] + ' E-' + m_ln.tag)
        prev_idx = m_ln.end_idx

    if prev_idx < len(data) - 1:
        res += join_simple_chunk(data[prev_idx:])

    return '\n'.join(res)


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
        bsf = BsfInfo(m.group(1), m.group(2), int(m.group(3)), int(m.group(4)), m.group(5).strip())
        result.append(bsf)
    return result


def convert_bsf_to_beios_in_folder(src_dir_path: str, dst_dir_path: str) -> None:
    ann_path = os.path.join(src_dir_path, '*.tok.ann')
    ann_files = glob.glob(ann_path)
    ann_files.sort()

    tok_path = os.path.join(src_dir_path, '*.tok.txt')
    tok_files = glob.glob(tok_path)
    tok_files.sort()

    if len(ann_files) == 0 or len(tok_files) == 0:
        log.warning(f'Token and annotation files are not found at specified path {ann_path}')
    if len(ann_files) != len(tok_files):
        log.warning(f'Mismatch between Annotation and Token files. Ann files: {len(ann_files)}, token files: {len(tok_files)}')

    log.info(f'Found {len(tok_files)} files')
    for (tok_fname, ann_fname) in tqdm(zip(tok_files, ann_files), total=len(tok_files), unit='file'):
        if tok_fname[:-3] != ann_fname[:-3]:
            tqdm.write(f'Token and Annotation file names do not match ann={ann_fname}, tok={tok_fname}')
            continue
        f_name = '-'.join(tok_fname.split('/')[-1].split('.')[:-2])
        bio_path = os.path.join(dst_dir_path, f_name + '.bio')
        with open(tok_fname) as tok_file, open(ann_fname) as ann_file, open(bio_path, 'w') as bio_file:
            token_data = tok_file.read()
            ann_data = ann_file.read()
            beios_data = convert_bsf_2_beios(token_data, ann_data)
            # log.info(tok_fname)
            # log.info(beios_data)

            bio_file.write(beios_data)

    log.info('All done')

if __name__ == '__main__':
    logging.basicConfig()
    convert_bsf_to_beios_in_folder('/Users/andrew/Projects/law/ner-uk/data/', '/Users/andrew/Projects/law/stanza-training/ner-base/')