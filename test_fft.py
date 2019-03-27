from threading import Thread,Event
import wave
import numpy
import pretty_midi
import matplotlib.pyplot as plt
import math
from scipy import signal
import sys

#thr = Thread(target = self.file_path_search,args=(file_path,_composer,_op,_title,_year,))
#thr.start()

_e = 1e-24
def GetNearestPitch(_dict,_num):
    _keys = numpy.array(list(_dict.keys()))
    idx = numpy.abs(_keys - _num)
    idx = idx.argmin()
    return idx

def GetKeyFreq(key_count = 88):
    center_a = 48 #440Hzの音
    key_freq = {i:0 for i in range(key_count)}
    diff = [i - center_a for i in range(key_count)]
    
    for i in range(len(key_freq)):
        key_freq[i] = 440 * math.pow(2,diff[i] * (1/12.0))
    output_dict = {v:k for k,v in key_freq.items()}
    
    print("INFO:","Getting_",key_count,"_keys_frequency","____done")
    return output_dict
    
def GetMeasureRate(_frame_rate,_beats,_export_bpm): #一小節に相当するサンプル数
    return (_frame_rate * 60 * 4 * _beats[0]) / (_export_bpm * _beats[1])

def GetMeasureCount(_int_data,_measure_rate): #小節の数を取得
    whole_size = _int_data.size
    whole_split_rate = math.ceil(whole_size / _measure_rate) #切り上げ（後に丸める）
    return whole_split_rate
    
def SplitIntData(_int_data,_rate): #配列を分ける
    if not _rate == 1:
        _int_data = numpy.array_split(_int_data,_rate) #個数に区切る（末尾余り）
        L = len(_int_data[0]) #Xの長さの最大値
        for i in range(1,len(_int_data)):
            if L > len(_int_data[i]):
                _int_data[i] = numpy.append(_int_data[i],[0] * (L-len(_int_data[i]))) #配列の長さを最大値で丸める
            else:
                pass
        del L
        _int_data = numpy.array(_int_data,ndmin=2)
    else:
        pass
    if not _int_data.size == _rate:
        _int_data = numpy.reshape(_int_data,(_rate,-1))
    else:
        pass
    return _int_data

def SplitMeasureData(_measure_data,_measure_split_rate): #微小時間あたりに分割する
    print("INFO:","Spliting_by_every_note")
    _measure_data = list(map(lambda x: x,_measure_data))
    for i in range(len(_measure_data)):
        splited_measure = SplitIntData(_measure_data[i],_measure_split_rate)
        _measure_data[i] = list(map(lambda x: x.tolist(),splited_measure))
        _measure_data[i] = numpy.array(_measure_data[i])
        
        _p = int(i / (len(_measure_data) - 1 + _e) * 100)
        print("\r{0:d}".format(_p),end = "%")
    _measure_data = numpy.array(_measure_data)
    print("","____done")
    return _measure_data

def GetPeakValues(_data,_freq): #ピーク値を求める
    _data = _data.tolist()
    peak_freq = signal.argrelmax(numpy.array_split(_data,2)[0],order=100)[0]
    peak_amp = [_data[x] for x in peak_freq]
    peak_freq = [_freq[x] for x in peak_freq]
    return peak_freq,peak_amp

def Fft(_data,_frame_rate,_figure=False,_int_data=None,run_average=False):#フーリエ級数変換
    if type(_data) == list:
        _data = numpy.array(_data)
    N = _data.size
    fourier = numpy.fft.fft(_data,n=None,axis=-1,norm=None)
    freq = numpy.fft.fftfreq(N , d = 1/_frame_rate)
    
    amp = numpy.abs(fourier) / (N / 2)
    amp = amp[1:int(N/2)] #サンプリング定理により、Nの1/2で有効
    
    if run_average == True:
        run_rate = 10
        run_rate = numpy.ones(run_rate)/run_rate
        amp = numpy.convolve(amp,run_rate,mode="same") #平滑化
    else:
        pass
    
    peak_freq,peak_amp = GetPeakValues(amp,freq)
    output = [[i,j]  for i,j in zip(peak_freq,peak_amp)] #[周波数,振幅]
    
    if _figure == True:
        fig = plt.figure(figsize=(6,6))
        ax_0 = fig.add_subplot(3,2,1)
        ax_0.plot(_int_data,label="Wave_data")
        ax_0.legend()
        
        ax_1 = fig.add_subplot(3,2,2)
        ax_1.plot(freq,fourier.real,label="Real_part")
        ax_1.legend()
        ax_2 = fig.add_subplot(3,2,4)
        ax_2.plot(freq,fourier.imag,label="Imaginaly_part")
        ax_2.legend()
        ax_3 = fig.add_subplot(3,2,6)
        ax_3.plot(freq,freq,label="frequency")
        ax_3.legend()
        ax_3.set_xlabel("frequency")
        
        ax_4 = fig.add_subplot(3,2,5)
        ax_4.plot(freq[1:int(N/2)],amp,label="Frequency_domain")
        ax_4.scatter(peak_freq,peak_amp,s=10,label="Peak",color="r")
        ax_4.set_xlabel("Frequency[Hz]")
        ax_4.set_ylabel("Amplitude")
        ax_4.legend()
        print("INFO:Peaks",output)
        plt.show()
    else:
        pass
    return output

def FrequencyToNoteNumber(_freq,_key_freq): #周波数をピッチに変換
    for i in range(len(_freq)):
        _freq[i][0] = GetNearestPitch(_key_freq,_freq[i][0])+24
    return _freq

def FftForAll(_splited_data,_frame_rate,_key_freq): #フーリエ級数変換を全てに適応させ、pitchとvelocityの情報を得る
    _p = 0
    _splited_data = list(map(lambda x: x,_splited_data))
    print("INFO:","fourier_transforming")
    for i in range(len(_splited_data)):
        _splited_data[i] = _splited_data[i].tolist()
        for j in range(len(_splited_data[i])):
            fft_data = Fft(numpy.array(_splited_data[i])[j],_frame_rate) #[周波数,振幅]のデータに書き換え
            fft_data = FrequencyToNoteNumber(fft_data,_key_freq) #[pitch,振幅]のデータに書き換え
            _splited_data[i][j] = numpy.array(fft_data,dtype=object)
            del fft_data
        
        _p = int(i / (len(_splited_data) - 1 + _e) * 100)
        print("\r{0:d}".format(_p),end = "%")
    print("","____done")
    _splited_data = numpy.array(_splited_data,dtype=object)
    return _splited_data

def DataToMidi(_data,_rate,_bpm,_name="output/output.mid"): #MIDIの生成
    print("INFO:","Making_MIDI_file",_name)
    fft_midi = pretty_midi.PrettyMIDI(initial_tempo=_bpm)
    piano = pretty_midi.Instrument(program = 1) #インストゥルメントトラックを追加
    
    note_time = 0
    note_count = 0
    measure_count = 0
    _data = list(map(lambda x: x.tolist(),_data))
    for _measure in range(len(_data)): #小節毎
        if not _data == []:
            for _notes in _data[_measure]: #単位時間毎
                for _note in _notes: #note毎
                    if not _note == []:
                        _velocity = int(_note[1] * 100)
                        _pitch = int(_note[0])
                        adding_note = pretty_midi.Note(velocity = _velocity,
                                    pitch = _pitch,
                                    start =  note_time,
                                    end = note_time + _rate) #ノーツを作成
                        piano.notes.append(adding_note) #インストゥルメントトラックにノーツを追加
                        note_count +=1
                    else:
                        pass
                note_time = note_time + _rate #時間を進める
        else:
            pass
        measure_count += 1
        _p = int(_measure / (len(_data) - 1 + _e) * 100)
        print("\r{0:d}".format(_p),end = "%")
    print("","____done")
    print("_____Note_count:",note_count)
    print("_____Measure_count:",measure_count)
    
    del _data
    
    print("_____Midi_instruments_appending",end=" ")
    fft_midi.instruments.append(piano)
    print("____done")
    
    del piano
    
    print("_____Exporting_MIDI_file",end=" ")
    fft_midi.write(_name)
    print("____done")
    
    del fft_midi
    
    return True
def DivisionMidiExport(_data,_rate,_bpm,_measure_count,split_rate = 200,_name = "output"):
    _split_count = math.ceil(_measure_count / split_rate) #小節数で複数のファイルを出力（DAW側の負担軽減）
    print("INFO:","Exporting_",_split_count,"_MIDI_file")
    
    split_rate = _measure_count - (_split_count - 1) * split_rate #末尾小節数
    if split_rate == 0:
        _data = numpy.array_split(_data,_split_count) #個数に区切る（末尾余り）
        _data = numpy.array(_data)
        for i in range(_data.size):
            DataToMidi(_data[i],_rate,_bpm,_name = "output/" + _name + "_" + str(i) + ".mid")
            _data[i] = []
    elif split_rate >= 0 and _split_count > 1:
        _data_end = _data[(_measure_count - split_rate):]
        _data_s = _data[0:(_measure_count - split_rate)]
        _data_s = numpy.array_split(_data_s,_split_count-1)
        _data_s.append(_data_end)
        _data = _data_s
        del _data_s,_data_end
        _data = numpy.array(_data)
        for i in range(_data.size):
            DataToMidi(_data[i],_rate,_bpm,_name = "output/" + _name + "_" + str(i) + ".mid")
            _data[i] = []
    else:
        DataToMidi(_data,_rate,_bpm,_name = "output/" + _name + ".mid")
        _data = []

def WaveToMIDI(wave_file):
    key_freq = GetKeyFreq() #88鍵盤の周波数を取得
    
    buff = wave_file.readframes(wave_file.getnframes()) #バッファーに変換
    print("INFO:","Converting_wave_to_buffer","____done")
    wave_file.close()
    frame_rate = wave_file.getframerate() #フレームレート
    del wave_file
    
    int_data = numpy.frombuffer(buff,dtype="int16") #waveの中身を16bitintに変換
    int_data = int_data / (math.pow(2,16) / 2) 
    print("INFO:","Converting_buffer_to_int_data","____done")
    del buff
    
    export_bpm = 100
    beats = [2,4] #[0]/[1]拍子
    
    measure_rate = GetMeasureRate(frame_rate,beats,export_bpm) #一小節にあたるサンプル数
    whole_split_rate = GetMeasureCount(int_data,measure_rate) #何小節に等分するか
    measure_split_rate = 64 #一小節あたり何等分するか
    output_rate = (measure_rate / measure_split_rate) / frame_rate #出力の時のMIDIノーツの長さ（秒）
    data_size = int_data.size
    
    print("INFO:","Spliting_by_every_measure",end=" ")
    int_data = SplitIntData(int_data,whole_split_rate) #小節ごとに分けられた配列
    print("____done")
    print("_____Data_shape:",int_data.shape)
    
    int_data = SplitMeasureData(int_data,measure_split_rate) #微小時間ごとに分けられた配列
    print("_____Data_shape:",int_data.shape)
    
    print("_____Element_count:",data_size)
    print("_____Measure_count:",whole_split_rate)
    print("_____Frame_rate:",frame_rate)
    print("_____BPM:",export_bpm)
    print("_____Note_time_rate:",output_rate)
    
    int_data = FftForAll(int_data,frame_rate,key_freq)
    print("_____Data_shape:",int_data.shape)
    DivisionMidiExport(int_data,output_rate,export_bpm,whole_split_rate,split_rate = 100,_name = "output")

if __name__ == "__main__":
    wave_file_name = "input/Fugue_in_A_Major_Shostakovich.wav"
    wave_file = wave.open(wave_file_name,"r")
    print("INFO:","Wave_file_importing","____done")
    print("_____File_name:",wave_file_name)
    WaveToMIDI(wave_file)
    