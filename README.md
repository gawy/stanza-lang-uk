# Ukrainian NER data set conversion to be used by Stanza (Stanford NLP Library) 

Purpose of this project is to convert NER data set provided by [lang-uk group](https://github.com/lang-uk/ner-uk) 
from [Brat Standoff Format](https://brat.nlplab.org/standoff.html) to [BEIOS](https://en.wikipedia.org/wiki/Inside–outside–beginning_(tagging)) format required by [Stanford Stanza Library](https://stanfordnlp.github.io/stanza)

You can also use this tool convert any other NER data set from BSF to BEIOS format. 
But mind that it will only convert simple entity tgs (T), no overlapping, relations, events are supported for now.  

## Usage

1. Clone lang-uk data set to the folder of your choice (later referred as $SRC_DATASET)
```shell script
git clone https://github.com/lang-uk/ner-uk
```
2. Run conversion script
```shell script
python bsf_to_beios.py --src_dataset $SRC_DATASET/data
```
Data will be saved to `../ner-base/` dir. Or you can change this path with `--dst` argument

## Stanza training
After obtaining `*.bio` files you can run Stanza NER training.

Make sure to follow instructions at [https://stanfordnlp.github.io/stanza/training.html](https://stanfordnlp.github.io/stanza/training.html). There are all sorts of naming gotchas that you want to avoid.

After necessary configuration you will be able to run NER model training
```shell script
scripts/run_ner.sh Ukrainian-languk
```

## Using trained model
```jupyterpython
import stanza
nlp = stanza.Pipeline('uk', processors='tokenize,pos,lemma', 
                      ner_model_path='your_path/saved_models/ner/uk_languk_nertagger.pt', 
                      ner_forward_charlm_path="", ner_backward_charlm_path="")
```

```
## Recent training results
Training ended with 34000 steps.
Best dev F1 = 84.24, at iteration = 22000

Running tagger in predict mode
Loading data with batch size 32...
41 batches created.
Start evaluation...
Prec.	Rec.	F1
84.58	83.89	84.24
NER tagger score:
uk_languk 84.24

Running tagger in predict mode
Loading data with batch size 32...
37 batches created.
Start evaluation...
Prec.	Rec.	F1
86.86	85.25	86.05
NER tagger score:
uk_languk 86.05
```


## Kudos 

"Корпус NER-анотацій українських текстів" by lang-uk is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
Based on a work at https://github.com/lang-uk/ner-uk.