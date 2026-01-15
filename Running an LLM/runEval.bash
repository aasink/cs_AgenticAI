#!/bin/bash

MODELS="
meta-llama/Llama-3.2-1B-Instruct
allenai/OLMo-2-0425-1B-RLVR1
Qwen/Qwen2.5-1.5B-Instruct
"

for model in $MODELS; do 
    for quant in 0 4 8; do 
        for gpu in cpu gpu; do 
            if [[ "$gpu" == "gpu" && "$quant" != 0 ]]; then 
                continue
            fi

            echo "Running MMLU_EVAL.PY w/ model=$model, quant=$quant gpu=$gpu"

            python mmlu_eval.py --model "$model" --quant "$quant" $( [[ "$gpu" == "gpu" ]] && echo "--gpu")
        done
    done
done