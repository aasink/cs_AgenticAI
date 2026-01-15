#!/bin/bash

MODELS=(
    "meta-llama/Llama-3.2-1B-Instruct" 
    "allenai/OLMo-2-0425-1B-RLVR1"
    "Qwen/Qwen2.5-1.5B-Instruct"
)
QUANTS=(0 4 8)
GPUS=(0 1)