#!/bin/bash

PARALLEL=false

while getopts "p" opt; do
  case $opt in
    p)
      PARALLEL=true
      ;;
  esac
done

if $PARALLEL; then
    echo "Parallel Execution"
    /usr/bin/time bash -c "python llama_mmlu_eval1.py & python llama_mmlu_eval2.py & wait"
else
    echo "Sequential Execution"
    /usr/bin/time bash -c "python llama_mmlu_eval1.py ; python llama_mmlu_eval2.py"
fi
