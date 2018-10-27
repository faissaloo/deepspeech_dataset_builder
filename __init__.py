#!/usr/bin/env python3
import random
import os
import csv
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

    audio_filename = 'custom_data/'+dataset+'/'+str(random.getrandbits(32))+'.wav'
    save_deepspeech_audio(audio, p, audio_filename)

    needs_header = False
    try:
        with open('custom_data/'+dataset+'.csv', 'r', newline='') as datafile:
            reader = csv.reader()
            if reader.line_num == 0:
                needs_header = True
    except:
        needs_header = True

    with open('custom_data/'+dataset+'.csv', 'a', newline='') as datafile:
        writer = csv.DictWriter(datafile, delimiter=',', fieldnames = fieldnames)
        if needs_header:
            writer.writeheader()

        writer.writerow({
            'wav_filename': audio_filename,
            'wav_filesize': os.path.getsize(audio_filename),
            'transcript': transcript
        })
    return dataset

def on_record_start():
    print("Recording started")

def on_record_end(audio, p):
    print('Playing back audio')
    play_stream = p.open(format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        output=True,
        frames_per_buffer=CHUNK)
    play_stream.write(b''.join(audio))
    play_stream.close()

    if input("Save? [Y/N] ").lower() == 'y':
        transcript = input("Please transcribe your audio: ")
        dataset = designate_transcription(transcript, audio, p)
        print("Saved to dataset: " + dataset)
    else:
        print("Not saved")

def on_ready():
    print("Ready for input")

listen_for_speech(
    transcribe_audio = False,
    on_record_start = on_record_start,
    on_record_end = on_record_end,
    on_ready = on_ready,
    #on_transcription=main_on_transcription
)
