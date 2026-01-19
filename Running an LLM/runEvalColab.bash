#!/bin/bash

MODELS="
meta-llama/Llama-3.2-1B-Instruct
allenai/OLMo-2-0425-1B-RLVR1
Qwen/Qwen2.5-1.5B-Instruct
mistralai/Mistral-7B-Instruct-v0.3
allenai/Olmo-3-7B-Instruct
Qwen/Qwen2.5-7B-Instruct
"

for model in $MODELS; do 
    for quant in 0 4 8; do 
        for gpu in cpu gpu; do 

            if [[ "$gpu" == "cpu" ]]; then
                continue
            fi

            echo "Running MMLU_EVAL.PY w/ model=$model, quant=$quant gpu=$gpu"

            time python mmlu_eval.py --model "$model" --quant "$quant" $( [[ "$gpu" == "gpu" ]] && echo "--gpu")
        done
    done
done