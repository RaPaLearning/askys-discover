#!/bin/bash
set -e

git clone https://github.com/RaPaLearning/gita-begin
python normalize_text.py gita-begin/gita
mv normalized_docs.pkl.gz ../askys-discover/
