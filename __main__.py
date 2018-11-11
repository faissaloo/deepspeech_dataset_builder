#!/usr/bin/env python3
import argparse
import random
import os
import csv
import time
from livespeech import *

def mkdir_safe(dir):
    try:
        os.mkdir(dir)
    except FileExistsError:
        pass

def designate_transcription(transcript, audio, p):
    mkdir_safe('custom_data')
    mkdir_safe('custom_data/train')
    mkdir_safe('custom_data/dev')
    mkdir_safe('custom_data/test')

    fieldnames = ['wav_filename', 'wav_filesize', 'transcript']
    # Percentages as per https://discourse.mozilla.org/t/tutorial-how-i-trained-a-specific-french-model-to-control-my-robot/22830
    dataset = random.choice(['train', 'train', 'train', 'train', 'train', 'train', 'train', 'dev', 'dev', 'test'])

    audio_filename = dataset+'/'+str(random.getrandbits(32))+'.wav'
    save_deepspeech_audio(audio, p, 'custom_data/'+audio_filename)

    needs_header = False
    try:
        with open('custom_data/'+dataset+'.csv', 'r', newline='') as datafile:
            reader = csv.reader(datafile)
            if next(reader) != fieldnames:
                needs_header = True
    except FileNotFoundError:
        print('Dataset file not found, creating a new one')
        needs_header = True

    with open('custom_data/'+dataset+'.csv', 'a', newline='') as datafile:
        writer = csv.writer(datafile)
        if needs_header:
            writer.writerow(fieldnames)

        writer.writerow((audio_filename, os.path.getsize('custom_data/'+audio_filename), transcript))
    return dataset

def on_record_start():
    print("Recording started")

def on_record_end(audio, p):
    global transcript_file
    global current_phrase

    print('Playing back audio')
    play_stream = p.open(format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        output=True,
        frames_per_buffer=CHUNK)
    play_stream.write(b''.join(audio))
    play_stream.close()

    if input("Save? [Y/N] ").lower() == 'y':
        if transcript_file:
            dataset = designate_transcription(current_phrase, audio, p)
        else:
            transcript = input("Please transcribe your audio: ")
            dataset = designate_transcription(transcript, audio, p)

        print("Saved to dataset: " + dataset)
    else:
        print("Not saved")

def on_ready():
    global transcript_file
    global current_phrase

    if transcript_file:
        current_phrase = get_random_phrase(transcript_file)
        print('Please say "'+current_phrase+'"')
        os.system('espeak -vmb-en1+f1 -s 90 "Please say '+current_phrase+'"')
        print('Ready')
    else:
        print("Ready")

def get_random_phrase(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        return random.choice(lines).strip()

parser = argparse.ArgumentParser(description='Create datasets for Mozilla Deepspeech')

parser.add_argument('-f','--file', nargs = 1, help = 'A file to read transcripts from')

arguments = parser.parse_args()

if arguments.file:
    transcript_file = arguments.file[0]
else:
    transcript_file = None


listen_for_speech(
    transcribe_audio = False,
    on_record_start = on_record_start,
    on_record_end = on_record_end,
    on_ready = on_ready,
    #on_transcription=main_on_transcription
)
