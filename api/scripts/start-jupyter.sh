#! /usr/bin/env bash

# starts jupyter notebook

jupyter notebook \
    --allow-root \
    --ip=0.0.0.0 \
    --no-browser \
    --notebook-dir="/notebooks" \
    --NotebookApp.password='sha1:da67d1326b24:37df26a945a0459f12da8d04cb85855387f3332e' &