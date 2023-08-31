#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 11:03:14 2022

@author: luke.abram
"""

# import matplotlib.pyplot as plt
from matplotlib import image
import librosa
from scipy.io import wavfile
from scipy import signal
# from scipy import signal
import numpy as np
from PIL import Image
import os
import shutil
from natsort import natsorted
import unittest

import random


from pydub import AudioSegment


import py_midicsv as pm
from sound_to_midi.monophonic import wave_to_midi


def makeSpec(fn, folder, a=""):
    # Load audio file as 1D array
    sig2, fs = librosa.load(fn, sr=44100)
    
    # Create spectrogram from 1D array
    spec = librosa.stft(sig2)
    if len(spec[0]) < 255:
        spec = np.hstack((spec, np.zeros((len(spec),255-len(spec[0])))))
    hexspec = np.empty((len(spec), len(spec[0]) * 2, 3), dtype='uint8')
    for i in range(len(spec)):
        for j in range(len(spec[0])):
            #Negative indicators
            s = 0
            s2 = 0
                        
    
            #Scaling normal and "complex" components
            n = spec[i, j].real * 382
            c = spec[i, j].imag * 382

            
            
            #Set negative indicators
            if n < 0:
                s = 1
            
            if c < 0:
                s2 = 1
                
                
            #Take the absolute value and cast components to ints
            n = int(abs(n))
            c = int(abs(c))
            
            #n shifting
            
            hexspec[i, 2 * j, 0] = n & 0xFF
            n = n >> 8
            hexspec[i, 2 * j, 1] = n & 0xFF
            n = n >> 8
            hexspec[i, 2 * j, 2] = s
      
            
            
            #c shifting
            
            hexspec[i, 2 * j + 1, 0] = c & 0xFF
            c = c >> 8
            hexspec[i, 2 * j + 1, 1] = c & 0xFF
            c = c >> 8
            hexspec[i, 2 * j + 1, 2] = s2
            

         
            # print(hexspec[i,j,0])
    print(hexspec[:,:,0].max())
    print(hexspec[:,:,1].max())
    print(np.shape(hexspec))
    files = os.listdir('./' + folder)
    
    #Slice spectrogram into squares of row length * row length
    for i in range(int(len(hexspec[0]) / 256)):
        
       
        arr = hexspec[:256, i * 256: (i + 1)* 256, :]
        img = Image.fromarray(arr)
        while str(i) + a + '.png' in files:
            i += 1
        img.save('./' + folder + '/' + str(i) + a + '.png')
        print('made ' + folder + '/'+ str(i) + a +'.png')
        # if count > 0:
        #     break
    
def testSpec(fn, folder, a=""):
    # Load audio file as 1D array
    sig2, fs = librosa.load(fn, sr=44100)
    
    # Create spectrogram from 1D array
    spec = librosa.stft(sig2)
    
    hexspec = np.empty((len(spec), len(spec[0]) * 2, 3), dtype='uint8')
    for i in range(len(spec)):
        for j in range(len(spec[0])):
            #Negative indicators
            s = 0
            s2 = 0
                        
    
            #Scaling normal and "complex" components
            n = spec[i, j].real * 382
            c = spec[i, j].imag * 382

            
            
            #Set negative indicators
            if n < 0:
                s = 255
            
            if c < 0:
                s2 = 255
                
                
            #Take the absolute value and cast components to ints
            n = int(abs(n))
            c = int(abs(c))
            
            #n shifting
            
            hexspec[i, 2 * j, 0] = n & 0xFF
            n = n >> 8
            hexspec[i, 2 * j, 1] = n & 0xFF
            n = n >> 8
            hexspec[i, 2 * j, 2] = s
      
            
            
            #c shifting
            
            hexspec[i, 2 * j + 1, 0] = c & 0xFF
            c = c >> 8
            hexspec[i, 2 * j + 1, 1] = c & 0xFF
            c = c >> 8
            hexspec[i, 2 * j + 1, 2] = s2
            

         
            # print(hexspec[i,j,0])
    print(hexspec[:,:,0].max())
    print(hexspec[:,:,1].max())
    print(np.shape(hexspec))
    
    
    #Slice spectrogram into squares of row length * row length
    for i in range(int(len(hexspec[0]) / len(hexspec)) +1):
        
       
        arr = hexspec[:len(hexspec), i * len(hexspec): (i + 1)* len(hexspec), :]
        img = Image.fromarray(arr)
        img.save('./' + folder + '/' + str(i) + a + '.png')
        print('made ' + folder + '/'+ str(i) + a +'.png')
        # if count > 0:
        #     break
    


def storePhase(spec, fn):
    phase = np.empty((len(spec), len(spec[0])))
    for i in range(len(spec)):
        for j in range(len(spec[0])):
            if spec[i, j].real < 0:
                phase[i, j] = 10
            if spec[i, j].imag < 0:
                phase[i, j] += 1
    np.savetxt(fn, phase)


        
def imageToAudio(outputfn, folder, volume=1):
    #Open image as array
    spec2 = np.array(Image.open('./' + folder  + '.png'))
    # spec2[:, :, 2] = normalize(spec2[:, :, 2])
    spec2 = np.vstack((spec2, np.zeros((768,256,3),dtype=int)))
    
    #Create an empty array the same size as the image
    spec = np.empty((len(spec2), int((len(spec2[0]) - 1) / 2)), dtype='complex64')
    
    factor = 382 / volume
    phase = []
    for i in range(256):
        arr = spec2[:, i, 2]
        s = np.sum(arr)
        if s > 255:
            spec2[:, i, 2] = 1
        else:
            spec2[:, i, 2] = 0
        
    for i in range(len(spec)):
        for j in range(len(spec[0])):
            n = 0
            c1 = str(format(spec2[i, j * 2, 0], '02x'))
            c2 = str(format(spec2[i, j * 2, 1], '02x'))
            num = c2 + c1
            n = int(num, 16) / factor
            if spec2[i, j * 2, 2] >= 1:
                n = n * -1
            
            c = 0
            c1 = str(format(spec2[i, j * 2 + 1, 0], '02x'))
            c2 = str(format(spec2[i, j * 2 + 1, 1], '02x'))
            num = c2 + c1
            c = int(num, 16) / factor
            if spec2[i, j * 2 + 1, 2] >= 1:
                c = c * -1
            spec[i, j] = complex(n, c)
            

           
    #Print the max value of spec // helpful for verifying accuracy
    print(spec.max())
    
    #Covnert the spectrogram back into a 1D audio signal
    audio_signal = librosa.istft(spec)
    
    #Write the array to a wave file
    wavfile.write(outputfn, 44100, audio_signal)
    print('Wrote ' + outputfn)
    
def cqtSpec(fn, folder, a="", single=False):
    # Load audio file as 1D array
    sig2, fs = librosa.load(fn, sr=44100)
    
    # Create spectrogram from 1D array
    spec = librosa.cqt(sig2, sr=44100, hop_length=256, bins_per_octave=24, n_bins=200)
    # print('Spec max:',hex(int(spec.real.max())))
    # print('Spec max:',hex(int(spec.imag.max())))
    
    #Print the max value of spec // helpful for verifying accuracy

    hexspec = np.empty((len(spec), len(spec[0]) * 2, 3), dtype='uint8')
    for i in range(len(spec)):
        for j in range(len(spec[0])):
            #Negative indicators
            s = 0
            s2 = 0
                        
    
            #Scaling normal and "complex" components
            n = spec[i, j].real * 1000
            c = spec[i, j].imag * 1000

            
            
            #Set negative indicators
            if n < 0:
                s = 255
            
            if c < 0:
                s2 = 255
                
                
            #Take the absolute value and cast components to ints
            n = int(abs(n))
            c = int(abs(c))
            
            #n shifting
            
            hexspec[i, 2 * j, 0] = n & 0xFF
            n = n >> 8
            hexspec[i, 2 * j, 1] = n & 0xFF
            n = n >> 8
            hexspec[i, 2 * j, 2] = s
      
            
            
            #c shifting
            
            hexspec[i, 2 * j + 1, 0] = c & 0xFF
            c = c >> 8
            hexspec[i, 2 * j + 1, 1] = c & 0xFF
            c = c >> 8
            hexspec[i, 2 * j + 1, 2] = s2
            
            
    # img = Image.fromarray(hexspec)
    # img.save('./' + folder + '/0' + a + '.png')
    
    #Slice spectrogram into squares of row length * row length
    for i in range(int(len(hexspec[0]) / len(hexspec)) +1):
        arr = hexspec[:len(hexspec), i * len(hexspec): (i + 1)* len(hexspec), :]
        img = Image.fromarray(arr)
        files = os.listdir('./' + folder + '/')
        while str(i) + a + '.png' in files:
            i += 1
        img.save('./' + folder + '/' + str(i) + a + '.png')
        print('made ' + folder + '/'+ str(i) + a +'.png')
        if single:
            break

def cqtAudio(outputfn, folder, name, volume=1):
    #Open image as array
    spec2 = np.array(Image.open('./' + folder + '/' + name + '.png'))
    # spec2 = np.vstack((spec2, np.zeros((768,256,3),dtype=int)))
    
    #Create an empty array the same size as the image
    spec = np.empty((len(spec2), int((len(spec2[0]) - 1) / 2)), dtype='complex64')
    
    factor = 1000 / volume
    
    for i in range(len(spec)):
        for j in range(len(spec[0])):
            n = 0
            c1 = str(format(spec2[i, j * 2, 0], '02x'))
            c2 = str(format(spec2[i, j * 2, 1], '02x'))
            num = c2 + c1
            n = int(num, 16) / factor
            if spec2[i, j * 2, 2] > 127:
                n = n * -1
            
            c = 0
            c1 = str(format(spec2[i, j * 2 + 1, 0], '02x'))
            c2 = str(format(spec2[i, j * 2 + 1, 1], '02x'))
            num = c2 + c1
            c = int(num, 16) / factor
            if spec2[i, j * 2 + 1, 2] > 127:
                c = c * -1
            spec[i, j] = complex(n, c)
            

           
    #Print the max value of spec // helpful for verifying accuracy
    print(spec.max())
    
    #Covnert the spectrogram back into a 1D audio signal
    audio_signal = librosa.icqt(spec, sr=44100, hop_length=256, bins_per_octave=24)
    #Write the array to a wave file
    wavfile.write(outputfn, 44100, audio_signal)
    print('Wrote ' + outputfn)


def testsm(audiofn, folder):
    cqtSpec(audiofn, folder)
    cqtAudio('./'+ folder + '/testc.wav', folder, 0,.9 )
    for f in os.listdir('./'+folder):
        if '.png' in f:
            os.remove('./'+folder+'/'+f)
    

def joinAudio(fns, outfn):
    out = np.array([])
    for i in fns:
        a = librosa.load(i, sr=44100)
        out = np.hstack((out, a[0]))
    wavfile.write(outfn, 44100, out)
def normalize(arr):
    arrmax = np.amax(arr)
    arrmin = np.amin(arr)
    newarr = np.zeros((len(arr), len(arr[0])))
    for i in range(len(arr)):
        for j in range(len(arr[0])):
            newarr[i, j] = (arr[i][j] - arrmin) / (arrmax-arrmin)
    return newarr
def separateNotes(audio_fn):
    file_in = audio_fn
    file_out = 'temp.mid'
    y, sr = librosa.load(file_in, sr=44100)
    midi = wave_to_midi(y, srate=44100)
    with open (file_out, 'wb') as f:
        midi.writeFile(f)
    csv = pm.midi_to_csv(file_out)
    i = 0
    tempo = 60 / (int(csv[2].split(',')[3])  * 10 ** -6)
    ticks = int(csv[0].split(',')[5])
    notes = []
    audio = AudioSegment.from_wav(file_in)
    while i < len(csv):
        if "Note_on_c" not in csv[i]:
            csv.pop(i)
            i -= 1
        else:
            notes.append(int(csv[i].split(',')[1]) / ticks / int(tempo+2) * 60000)
        i += 1
    for i in range(len(notes) - 1):
        print(notes[i], notes[i+1])
        tempaudio = audio[notes[i]:notes[i+1]]
        tempaudio.export('./parsed/' + str(i)+ '.wav', format='wav')
    tempaudio = audio[notes[len(notes) - 1]:]
    tempaudio.export('./parsed/' + str(len(notes) - 1)+ '.wav', format='wav')

def multiSpec(source, target):
    for f in os.listdir('./'+target):
        if '.png' in f:
            os.remove('./'+target+'/'+f)
    files = os.listdir('./' + source)
    files.sort()
    for f in files:
        print(f)
        makeSpec('./' + source + '/' + f, target)
        
def arrange_data(f1, f2, dn):
    if os.path.isdir(dn):
        shutil.rmtree(dn)
    os.mkdir(dn)
    os.mkdir(dn + '/trainA')
    os.mkdir(dn + '/trainB')
    os.mkdir(dn + '/testA')
    os.mkdir(dn + '/testB')
    #Set A
    # print('./'+f1)
    files = natsorted(os.listdir('./'+f1))
    # print(files)
    #Train
    use = True

    for f in files:
        if use:
            os.system('mv ./' + f1 + '/' + f +' ./' + dn + '/trainA')
        else:
            use = True
        if random.uniform(0,1) > .9:
            use = False
    files = natsorted(os.listdir('./'+f1))
    #Test
    for f in files:
        os.system('mv ./' + f1 + '/' + f +' ./' + dn + '/testA')
    
    #Set B
    files = natsorted(os.listdir('./'+f2))
    
    #Train
    use = True
    for f in files:
        if use:
            os.system('mv ./' + f2 + '/' + f +' ./' + dn + '/trainB')
        else:
            use = True
        if random.uniform(0,1) > .9:
            use = False
        
    files = natsorted(os.listdir('./'+f2))
    #Test
    for f in files:
        os.system('mv ./' + f2 + '/' + f +' ./' + dn + '/testB')
        
# joinAudio(['0.wav', '1.wav', '2.wav'], '012.wav')
            

            

# imageToAudio('e_1_36k.wav', 'prediction', 12, 1)
# imageToAudio('8b.wav', 'electric/7', 1)
# imageToAudio('2b.wav', 'parsed/4b', 1)
# imageToAudio('3b.wav', 'parsed/5b', 1)
# joinAudio(['1b.wav','2b.wav','3b.wav'], '123e.wav')
# makeSpec('3030a.wav', 'acoustic')
# makeSpec('3030e.wav', 'electric')
# makeSpec('1.wav', 'parsed')
# makeSpec('2.wav', 'parsed')
# cqtSpec('acoustic_audio/acoustic01.wav', 'electricv2', 'cqt')
# testsm('acoustic_audio/acoustic07.wav', 'cqt_test')
# separateNotes('012a.wav')

# imageToAudio('clean5.wav', 'prediction', 5, 1)
multiSpec('./5x12/acoustic', './5x12/aImages')
multiSpec('./5x12/electric', './5x12/eImages')
# multiSpec('parsed', 'parsed')
# arrange_data('./acoustic', './electric', '3030')
# cqtAudio('5cqt.wav', 'prediction', '')
# cqtAudio('10comp.wav', 'prediction', '10compiled')
# cqtAudio('originalb.wav', 'cqt+/testB/', '3')
# cqtAudio('targeta.wav', 'cqt+/testA/', '3')

# testSpec('ae/testA/1.wav', 'electricv2')