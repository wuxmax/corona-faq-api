#!/bin/bash

MODEL_ROOT_URL="https://public.ukp.informatik.tu-darmstadt.de/reimers/sentence-transformers/v0.2/"

MODEL_FILES=(
"distiluse-base-multilingual-cased-v2.zip" \
"paraphrase-xlm-r-multilingual-v1.zip" \
"quora-distilbert-multilingual.zip" \
"stsb-xlm-r-multilingual.zip" \
)

cd embedding-models || exit

for MODEL_FILE in "${MODEL_FILES[@]}"; do

  MODEL_FILE_URL="${MODEL_ROOT_URL}${MODEL_FILE}"

  echo "${MODEL_FILE_URL}"

  wget "${MODEL_FILE_URL}"
  unzip "${MODEL_FILE}" -d "${MODEL_FILE%.zip}"

done