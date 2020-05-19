import argparse
import logging
import os
import glob
from collections import namedtuple
import re
from tqdm import tqdm
from random import choices

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
    # following 2 constants need to comply with stanza naming for corpus and language
    corpus_name = 'Ukrainian-languk'

    ann_path = os.path.join(src_dir_path, '*.tok.ann')
    ann_files = glob.glob(ann_path)
    ann_files.sort()

    tok_path = os.path.join(src_dir_path, '*.tok.txt')
    tok_files = glob.glob(tok_path)
    tok_files.sort()

    corpus_folder = os.path.join(dst_dir_path, corpus_name)
    if not os.path.exists(corpus_folder):
        os.makedirs(corpus_folder)

    if len(ann_files) == 0 or len(tok_files) == 0:
        log.warning(f'Token and annotation files are not found at specified path {ann_path}')
        return
    if len(ann_files) != len(tok_files):
        log.warning(
            f'Mismatch between Annotation and Token files. Ann files: {len(ann_files)}, token files: {len(tok_files)}')

    train_json = []
    dev_json = []
    test_json = []

    data_sets = [train_json, dev_json, test_json]
    split_weights = (8, 1, 1)

    log.info(f'Found {len(tok_files)} files')
    for (tok_fname, ann_fname) in tqdm(zip(tok_files, ann_files), total=len(tok_files), unit='file'):
        if tok_fname[:-3] != ann_fname[:-3]:
            tqdm.write(f'Token and Annotation file names do not match ann={ann_fname}, tok={tok_fname}')
            continue

        with open(tok_fname) as tok_file, open(ann_fname) as ann_file:
            token_data = tok_file.read()
            ann_data = ann_file.read()
            beios_data = convert_bsf_2_beios(token_data, ann_data)

            target_dataset = choices(data_sets, split_weights)[0]
            target_dataset.append(beios_data)
    log.info(f'Data is split as following: train={len(train_json)}, dev={len(dev_json)}, test={len(test_json)}')

    # writing data to {train/dev/test}.bio files
    names = ['train', 'dev', 'test']
    for idx, name in enumerate(names):
        fname = os.path.join(corpus_folder, name + '.bio')
        with open(fname, 'w') as f:
            f.write('\n'.join(data_sets[idx]))
        log.info('Writing to ' + fname)

    log.info('All done')


if __name__ == '__main__':
    logging.basicConfig()

    parser = argparse.ArgumentParser(description='Convert lang-uk NER data set from BSF format to BEIOS format compatible with Stanza NER model training requirements.\n'
                                                 'Original data set should be downloaded from https://github.com/lang-uk/ner-uk')
    parser.add_argument('--src_dataset', type=str, default='../ner-uk/data', help='Dir with lang-uk dataset "data" folder (https://github.com/lang-uk/ner-uk)')
    parser.add_argument('--dst', type=str, default='../ner-base/', help='Where to store the converted dataset')
    parser.print_help()
    args = parser.parse_args()

    convert_bsf_to_beios_in_folder(args.src_dataset, args.dst)
