# Notes, Questions, & Graphs

## Runtimes for LLama 3.2B w/ 2 Subjects:

### Llama 3.2-1B Runtimes w/ 2 Subjects  (Local)
-----------------------------------

GPU - no Quantization      : 7.12s user 2.45s system 52% cpu 18.307 total
GPU - 4 bit Quantization   : -
GPU - 8 bit Quantization   : -

CPU - no Quantization      : 57.07s user 14.34s system 194% cpu 36.782 total
CPU - 4 bit Quantization   : 12.50s user 5.03s system 15% cpu 1:56.74 total


### Llama 3.2-1B Runtimes w/ 2 Subjects  (Colab)
-----------------------------------

GPU - no Quantization      : real	1m18.293s   user	0m34.911s   sys	0m9.470s
GPU - 4 bit Quantization   : real	0m45.814s   user	0m34.058s   sys	0m3.440s
GPU - 8 bit Quantization   : real	0m56.388s   user	0m45.400s   sys	0m3.188s

CPU - no Quantization      : real	11m1.537s   user	10m32.780s  sys	0m5.216s
CPU - 4 bit Quantization   : real	1m25.376s   user	0m39.463s   sys	0m5.321s

## Results of LLM Runtimes and Accuracy:

### Graphs of Results (Local)

![Description of Graph](graphs/graph1.png)

### Answers to Questions:

Can you see any patterns to the mistakes each model makes or do they appear random?  Do the all the models make mistakes on the same questions? 

### Graphs of Results (Colab)

![Description of Graph](graphs/graph1.png)

### Answers to Questions:

Can you see any patterns to the mistakes each model makes or do they appear random?  Do the all the models make mistakes on the same questions? 