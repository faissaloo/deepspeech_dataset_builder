#!/bin/bash
mkdir lm
sort -u -f transcripts.txt -o transcripts.txt
grep -o -E '\w+' transcripts.txt | sort -u -f > lm/words.txt
grep -o -E '.' transcripts.txt | sort -u -f > lm/alphabet.txt
lmplz -o 2 < transcripts.txt > lm/transcripts.arpa
build_binary trie lm/transcripts.arpa lm/transcripts.binary -q 8 -a 255
../DeepSpeech/generate_trie lm/alphabet.txt lm/transcripts.binary lm/words.txt lm/vocab.trie
