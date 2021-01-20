#!/bin/bash

MODEL_ROOT_URL="https://public.ukp.informatik.tu-darmstadt.de/reimers/sentence-transformers/v0.2/"

MODEL_FILE="distiluse-base-multilingual-cased-v2.zip"

MODEL_FILE_URL="${MODEL_ROOT_URL}${MODEL_FILE}"

echo ${MODEL_FILE_URL}

cd language-models

wget ${MODEL_FILE_URL}
unzip ${MODEL_FILE} -d ${MODEL_FILE%.zip}