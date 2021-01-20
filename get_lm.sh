#!/bin/sh

MODEL_ROOT_URL=https://public.ukp.informatik.tu-darmstadt.de/reimers/sentence-transformers/v0.2/

MODEL_FILE=distiluse-base-multilingual-cased-v2.zip

cd language-models

wget "$MODEl_ROOT_URL$MODEL_FILE"
unzip $MODEL_FILE