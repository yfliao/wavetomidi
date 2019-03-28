def main():
    from threading import Thread,Event
    import sys
    import dill
    import wx
    import time
    from time import sleep
    import matplotlib
    import wx.lib.agw.flatnotebook as fnotebook
    import os
    from pathlib import Path
    matplotlib.interactive(True)
    matplotlib.use("WXAgg")
    from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as Figagg
    import wx.lib.scrolledpanel as scrolledpanel
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    import numpy
    from scipy import signal
    from scipy import fftpack
    import math
    import wave
    import pretty_midi
    
    if getattr(sys,'frozen',False):
        os.chdir(os.path.dirname(sys.executable))#カレントディレクトリの処理
    
    _e = 1e-24
    def PerCountPrint(past,now,end):
        if past == -1:
            print("|0%___________________________100%|")
            print("{}".format("|||||"),end="")
        elif (past/end*100)//10 < (now/end*100)//10 and now < end:
            print("{}".format("|||||"),end="")
        elif now >= end:
            print("{}".format("|||||"))
    def min_max_norm(x,axis=None):
        min = x.min(axis=axis,keepdims=True)
        max = x.max(axis=axis,keepdims=True)
        result = (x-min)/(max-min)
        return result
        
    def GetNearestPitch(_dict,_num):
        _keys = numpy.array(list(_dict.keys()))
        if _num <= max(_keys) and _num >= min(_keys):
            idx = numpy.abs(_keys - _num)
            idx = idx.argmin()
        else:
            idx = -1
        return idx
    
    def GetKeyFreq(key_count = 88):
        center_a = 48 #440Hzの音
        
        key_freq = {i:0 for i in range(key_count)}
        diff = [i - center_a for i in range(key_count)]
        
        for i in range(len(key_freq)):
            key_freq[i] = 440 * math.pow(2,diff[i] * (1/12.0))
        output_dict = {v:k for k,v in key_freq.items()}
        
        return output_dict
        
    def GetMeasureRate(_frame_rate,_beats,_export_bpm): #一小節に相当するサンプル数
        return (int(_frame_rate) * 60 * 4 * int(_beats[0])) / (int(_export_bpm) * int(_beats[1]))
    
    def GetMeasureCount(whole_size,_measure_rate): #小節の数を取得
        whole_split_rate = math.ceil(whole_size / _measure_rate) #切り上げ（後に丸める）
        return whole_split_rate
    
    def FrequencyToPitchNumber(_data,_key_freq): #周波数をピッチに変換
        print("INFO:","Frequency_to_pitch",end=" ")
        for i in range(numpy.size(_data,0)):
            _data[i][0] = GetNearestPitch(_key_freq,_data[i][0])
        print("____done")
        return _data
    
    def GetAmpOfKey(_data,_key_freq): #pitch毎の振幅を取得
        L = [[i,0] for i in range(len(_key_freq))]
        vel_range = [100,0]
        for d in _data:
            if d[0] != -1:
                L[d[0]][1] += d[1]
                if L[d[0]][1] < vel_range[0] and L[d[0]][1] > 0:
                    vel_range[0] = L[d[0]][1]
                if L[d[0]][1] > vel_range[1] and L[d[0]][1] < 100:
                    vel_range[1] = L[d[0]][1]
            else:
                pass
        return L,vel_range
    
    def DataToMidi(_data,_bpm,_name="output/output.mid"): #MIDIの生成
        print("INFO:","Making_MIDI_file",_name)
        fft_midi = pretty_midi.PrettyMIDI(initial_tempo=_bpm)
        piano_vol_1 = pretty_midi.Instrument(program = 1) #インストゥルメントトラックを追加(音量が一番大きい)
        piano_vol_2 = pretty_midi.Instrument(program = 1) #3/4くらい
        piano_vol_3 = pretty_midi.Instrument(program = 1) #2/4くらい
        piano_vol_4 = pretty_midi.Instrument(program = 1) #1/4くらい
        
        note_count = 0
        note_count_1 = 0
        note_count_2 = 0
        note_count_3 = 0
        note_count_4 = 0
        
        if not numpy.size(_data,0) == 0: #(frequency,start,end,velocity)
            for i in range(numpy.size(_data,0)):
                if not numpy.size(_data[i],0) == 0:
                    if _data[i][0] > 0:
                        _velocity = int(_data[i][3]) #0~127
                        _pitch = int(_data[i][0]) + 21 #midiの標準pitchではA0が21
                        _start = _data[i][1]
                        _end = _data[i][2]
                        adding_note = pretty_midi.Note(velocity = _velocity,
                                    pitch = _pitch,
                                    start =  _start,
                                    end = _end) #ノーツを作成
                        if _velocity > (127 * 3 / 4): #インストゥルメントトラックにノーツを追加(4/4)
                            note_count_1 += 1
                            piano_vol_1.notes.append(adding_note)
                        elif _velocity > (127 * 2 / 4): #インストゥルメントトラックにノーツを追加(3/4)
                            note_count_2 += 1
                            piano_vol_2.notes.append(adding_note)
                        elif _velocity > (127 * 1 / 4): #インストゥルメントトラックにノーツを追加(2/4)
                            note_count_3 += 1
                            piano_vol_3.notes.append(adding_note)
                        else: #インストゥルメントトラックにノーツを追加(1/4)
                            note_count_4 += 1
                            piano_vol_4.notes.append(adding_note)
                        note_count += 1
                    else:
                        pass
                else:
                    pass
                PerCountPrint(i-1,i,numpy.size(_data,0))
        else:
            pass
        print("","____done")
        print("_____Note_count:",note_count)
        print("_____Notes_count_by_track: 1:",note_count_1,", 2:",note_count_2,", 3:",note_count_3,", 4:",note_count_4)
        
        del _data
        
        print("_____Midi_instruments_appending",end=" ")
        fft_midi.instruments.append(piano_vol_1)
        del piano_vol_1
        fft_midi.instruments.append(piano_vol_2)
        del piano_vol_2
        fft_midi.instruments.append(piano_vol_3)
        del piano_vol_3
        fft_midi.instruments.append(piano_vol_4)
        del piano_vol_4
        print("____done")
        
        print("_____Exporting_MIDI_file",end=" ")
        fft_midi.write(_name)
        print("____done")
        
        del fft_midi
        
        return True
    def WaveToIntData(wave_file,output_propaties): #wavを16bitintに変換し、stftを行う
        print("INFO:","Converting_wave_to_buffer",end=" ")
        buff = wave_file.readframes(wave_file.getnframes()) #バッファーに変換
        print("____done")
        
        frame_rate = wave_file.getframerate() #フレームレート
        wave_file.close()
        del wave_file
        
        print("INFO:","Converting_buffer_to_int_data",end=" ")
        int_data = numpy.frombuffer(buff,dtype="int16") #waveの中身を16bitintに変換
        del buff
        int_data = int_data / (math.pow(2,16) / 2) #0から1に変更
        fs = int(GetMeasureRate(frame_rate,output_propaties.beats,output_propaties._bpm)/output_propaties._measure_split_rate)
        print("____done")
        
        print("INFO:","Int_data_activate_with_STFT",end=" ")
        
        if output_propaties.resolution_settings == "frequency":
            key_freq = list(GetKeyFreq(key_count = output_propaties.key_count).keys())
            frequency_resolution = key_freq[int(output_propaties.resolution) + 1] - key_freq[int(output_propaties.resolution)]
            del key_freq
            n = int(frame_rate / frequency_resolution) #周波数分解能からnを逆算
            frequency_resolution = frame_rate / n
            Time_res = n / frame_rate
        elif output_propaties.resolution_settings == "time":
            n = output_propaties.resolution * frame_rate #時間からnを逆算
            frequency_resolution = frame_rate / n
            Time_res = n / frame_rate
        
        freq, t, Zxx = signal.stft(int_data,fs=fs,nperseg=n)
        int_shape = int_data.shape
        print("____done")
        del int_data
        Zxx = min_max_norm(numpy.abs(Zxx))*127 #強さを0から127にする
        t = fs * t #データ点数に戻す
        t = t / frame_rate
        freq = min_max_norm(freq) * frame_rate #周波数を0から22050にする
        print("_____wave_data_shape:",int_shape)
        print("_____Frequency_data_shape:",freq.shape)
        print("_____Time_data_shape:",t.shape)
        print("_____Velocity_data_shape:",Zxx.shape)
        print("_____N_per_segment:",n)
        print("_____Framerate:",frame_rate,"Hz")
        print("_____Frequency_resolution:",frequency_resolution,"Hz")
        print("_____Time_resolution:",Time_res,"sec")
        
        return [freq, t, Zxx,frame_rate,Time_res]
    def FftdataToMidiLikeArray(_datas,velocity_range=0.5,velocity_rate=35): #MIDIファイルに記載するのに適したarrayに変換する
        print("INFO:","Make_midi_like_data")
        output = numpy.array([[0,0,0,0]],dtype=object) #(frequency,start,end,velocity)
        freqlist = [[] for i in range(_datas[0].size)]
        
        for i in range(numpy.size(_datas[1],0)): #time毎の
            for j in range(numpy.size(_datas[0],0)): #全てのfreq
                if _datas[2][j][i] > velocity_rate: #検出
                    if len(freqlist[j]) == 0: #初検出である
                        freqlist[j] = [ _datas[0][j], _datas[1][i], _datas[1][i] + _datas[4], _datas[2][j][i]]
                    else: #連続検出である
                        if numpy.abs(1 - freqlist[j][3] / _datas[2][j][i]) < velocity_range: #velocityの変化が少ない
                            freqlist[j][2] = _datas[1][i] + _datas[4] #endを更新
                        else: #velocityの変化が大きい
                            output = numpy.append(output,numpy.array([freqlist[j]]),axis=0)
                            freqlist[j] = [ _datas[0][j], _datas[1][i], _datas[1][i] + _datas[4], _datas[2][j][i]] #一旦区切り、代入で初期化
                else: #非検出
                    if len(freqlist[j]) == 0: #連続非検出である
                        pass
                    else: #検出が途絶えた
                        output = numpy.append(output,numpy.array([freqlist[j]]),axis=0)
                        freqlist[j] = [] #初期化
            PerCountPrint(i-1,i,numpy.size(_datas[1],0))
        print("____done")
        print("_____Midi_like_data_shape:",output.shape)
        return output
        
    def WaveToMIDI(_datas,output_propaties):
        print("INFO:","Getting_",output_propaties.key_count,"_keys_frequency",end=" ")
        key_freq = GetKeyFreq(key_count = output_propaties.key_count) #88鍵盤の周波数を取得
        print("____done")
        _datas = FftdataToMidiLikeArray(_datas,velocity_range=output_propaties.velocity_range,velocity_rate=output_propaties.velocity_rate) #MIDIファイルに記載するのに適したarrayに変換する
        _datas = FrequencyToPitchNumber(_datas,key_freq) #frequencyをpitchに変換
        DataToMidi(_datas,output_propaties._bpm,_name=output_propaties.output_directly+"/"+output_propaties.output_name+".mid")
        print("INFO:","Exporting_MIDI_flie_is_succeeded")
    """
    
    
    
    """
    class advanced_setting_dialog(wx.Dialog):
        export_measure_count = 100
        key_count = 88
        _measure_split_rate = 64
        output_directly = "output"
        ymax = -1
        ymin = -1
        xmax = -1
        xmin = -1
        resolution_settings = "frequency"
        resolution = 0
        velocity_rate = 1
        velocity_range = 0.5
        def __init__(self):
            wx.Dialog.__init__(self,None,-1,"advanced_setting",size=(400,600),
                               style=wx.SYSTEM_MENU|
                               wx.CAPTION | wx.CLIP_CHILDREN)
            panel_taxt = scrolledpanel.ScrolledPanel(self, wx.ID_ANY)
            panel_taxt.SetupScrolling(scroll_x = False,scroll_y = True)
            panel_button = wx.Panel(self, wx.ID_ANY)
            
            panel_taxt.SetBackgroundColour("#dabae7")
            panel_button.SetBackgroundColour("#dabae7")
            
            button_ok = wx.Button(panel_button,wx.ID_OK,"OK")
            button_cancel = wx.Button(panel_button,wx.ID_CANCEL,"CANCEL")
            
            text_export_measure_count_v = wx.TextCtrl(panel_taxt,wx.ID_ANY,"Export_measure_count :")
            text_export_measure_count_v.Disable()
            text_export_measure_count_v.SetBackgroundColour("#dabae7")
            self.text_export_measure_count = wx.TextCtrl(panel_taxt,wx.ID_ANY,str(self.export_measure_count)) #export_measure_count
            
            text_key_count_v = wx.TextCtrl(panel_taxt,wx.ID_ANY,"Output_key_count :")
            text_key_count_v.Disable()
            text_key_count_v.SetBackgroundColour("#dabae7")
            self.text_key_count = wx.TextCtrl(panel_taxt,wx.ID_ANY,str(self.key_count)) #key_count
            
            text_measure_split_rate_v = wx.TextCtrl(panel_taxt,wx.ID_ANY,"Measure_split_rate :")
            text_measure_split_rate_v.Disable()
            text_measure_split_rate_v.SetBackgroundColour("#dabae7")
            self.text_measure_split_rate = wx.TextCtrl(panel_taxt,wx.ID_ANY,str(self._measure_split_rate)) #_measure_split_rate
            
            text_output_directly_v = wx.TextCtrl(panel_taxt,wx.ID_ANY,"Output_directly :")
            text_output_directly_v.Disable()
            text_output_directly_v.SetBackgroundColour("#dabae7")
            self.text_output_directly = wx.TextCtrl(panel_taxt,wx.ID_ANY,str(self.output_directly)) #output_directly
            
            text_ylim_v = wx.TextCtrl(panel_taxt,wx.ID_ANY,"figure_ylim_value(max,min)[Hz]:")
            text_ylim_v.Disable()
            text_ylim_v.SetBackgroundColour("#dabae7")
            self.ylim_max = wx.TextCtrl(panel_taxt,wx.ID_ANY,str(self.ymax))
            self.ylim_max.SetHint("ylim_max")
            self.ylim_min = wx.TextCtrl(panel_taxt,wx.ID_ANY,str(self.ymin))
            self.ylim_min.SetHint("yim_min")
            text_xlim_v = wx.TextCtrl(panel_taxt,wx.ID_ANY,"figure_xlim_value(max,min)[sec]:")
            text_xlim_v.Disable()
            text_xlim_v.SetBackgroundColour("#dabae7")
            self.xlim_max = wx.TextCtrl(panel_taxt,wx.ID_ANY,str(self.xmax))
            self.xlim_max.SetHint("xim_max")
            self.xlim_min = wx.TextCtrl(panel_taxt,wx.ID_ANY,str(self.xmin))
            self.xlim_min.SetHint("xim_min")
            
            self.text_resolution_v = wx.RadioBox(panel_taxt,wx.ID_ANY,"Custom_resolution",choices=("frequency","time"))
            self.text_resolution_v.SetBackgroundColour("#dabae7")
            self.text_resolution = wx.TextCtrl(panel_taxt,wx.ID_ANY,str(self.resolution)) #values
            self.text_resolution.SetHint("frequency:pitch,time:sec")
            
            text_velocity_v = wx.TextCtrl(panel_taxt,wx.ID_ANY,"Velocity_rate") #values
            text_velocity_v.SetBackgroundColour("#dabae7")
            text_velocity_v.Disable()
            self.text_velocity = wx.TextCtrl(panel_taxt,wx.ID_ANY,str(self.velocity_rate)) #values
            self.text_velocity.SetHint("0 ~ 127")
            
            text_velocity_range_v = wx.TextCtrl(panel_taxt,wx.ID_ANY,"Velocity_range") #values
            text_velocity_range_v.SetBackgroundColour("#dabae7")
            text_velocity_range_v.Disable()
            self.text_velocity_range = wx.TextCtrl(panel_taxt,wx.ID_ANY,str(self.velocity_range)) #values
            self.text_velocity_range.SetHint("0 ~ 1")
            
            layout_1 = wx.BoxSizer(wx.VERTICAL)
            layout_1.Add(panel_taxt,8,wx.EXPAND|wx.ALL,0)
            layout_1.Add(panel_button,1,wx.EXPAND|wx.ALL,0)
            self.SetSizer(layout_1)
            layout_2 = wx.BoxSizer(wx.HORIZONTAL)
            layout_2.Add(button_ok,1,wx.EXPAND|wx.ALL,20)
            layout_2.Add(button_cancel,1,wx.EXPAND|wx.ALL,20)
            panel_button.SetSizer(layout_2)
            _box = 5
            layout_3 = wx.BoxSizer(wx.VERTICAL)
            layout_3.Add(text_export_measure_count_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_3.Add(self.text_export_measure_count,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box) #export_measure_count
            layout_3.Add(text_key_count_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_3.Add(self.text_key_count,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box) #key_count
            layout_3.Add(text_measure_split_rate_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_3.Add(self.text_measure_split_rate,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            layout_3.Add(text_output_directly_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_3.Add(self.text_output_directly,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            layout_3.Add(text_ylim_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_3.Add(self.ylim_max,1,wx.EXPAND|wx.LEFT|wx.RIGHT,_box)
            layout_3.Add(self.ylim_min,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            layout_3.Add(text_xlim_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_3.Add(self.xlim_max,1,wx.EXPAND|wx.LEFT|wx.RIGHT,_box)
            layout_3.Add(self.xlim_min,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            layout_3.Add(self.text_resolution_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_3.Add(self.text_resolution,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            layout_3.Add(text_velocity_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_3.Add(self.text_velocity,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            layout_3.Add(text_velocity_range_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_3.Add(self.text_velocity_range,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            panel_taxt.SetSizer(layout_3)
            
            
    class import_dialog(wx.Dialog):#インポートのプロパティ入力画面
        file_name = "input"
        _bpm = 100
        beats_1 = 4
        beats_2 = 4
        output_name = "output"
        export_measure_count = 100
        key_count = 88
        _measure_split_rate = 64
        output_directly = "output"
        ymax = -1
        ymin = -1
        xmax = -1
        xmin = -1
        resolution_settings = "frequency"
        resolution = 0
        velocity_rate = 1
        velocity_range = 0.5
        def __init__(self):
            wx.Dialog.__init__(self,None,-1,"import_menu",size=(400,600),
                               style=wx.SYSTEM_MENU|
                               wx.CAPTION | wx.CLIP_CHILDREN)
            print("INFO:enter_your_self")
            self.SetBackgroundColour("#dabae7")
            panel_taxt = wx.Panel(self, wx.ID_ANY)
            panel_button = wx.Panel(self, wx.ID_ANY)
            advanced_setting_showing = scrolledpanel.ScrolledPanel(self, wx.ID_ANY)
            panel_taxt.SetBackgroundColour("#dabae7")
            panel_button.SetBackgroundColour("#dabae7")
            advanced_setting_showing.SetBackgroundColour("#dabae7")
            advanced_setting_showing.SetupScrolling(scroll_x = False,scroll_y = True)
            
            button_ok = wx.Button(panel_button,wx.ID_OK,"OK")
            button_cancel = wx.Button(panel_button,wx.ID_CANCEL,"CANCEL")
            button_setting = wx.Button(panel_taxt,0,"Advanced_setting")
            
            text_file_name_v = wx.TextCtrl(panel_taxt,wx.ID_ANY,"File_name :")
            text_file_name_v.Disable()
            text_file_name_v.SetBackgroundColour("#dabae7")
            self.text_file_name = wx.TextCtrl(panel_taxt,wx.ID_ANY,str(self.file_name)) #ファイル名
            self.text_file_name.Disable()
            self.text_file_name.SetBackgroundColour("#dabae7")
            
            text_bpm_v = wx.TextCtrl(panel_taxt,wx.ID_ANY,"bpm(midi_output) :")
            text_bpm_v.Disable()
            text_bpm_v.SetBackgroundColour("#dabae7")
            self.text_bpm = wx.TextCtrl(panel_taxt,wx.ID_ANY,str(self._bpm)) #bpm
            
            text_beats_v = wx.TextCtrl(panel_taxt,wx.ID_ANY,"beats (number_of_beats , phonetic_value):")
            text_beats_v.Disable()
            text_beats_v.SetBackgroundColour("#dabae7")
            self.text_beats_1 = wx.TextCtrl(panel_taxt,wx.ID_ANY,str(self.beats_1)) #beats1
            self.text_beats_1.SetHint("number_of_beats/")
            self.text_beats_2 = wx.TextCtrl(panel_taxt,wx.ID_ANY,str(self.beats_2)) #beats2
            self.text_beats_2.SetHint("/phonetic_value")
            
            text_output_name_v = wx.TextCtrl(panel_taxt,wx.ID_ANY,"Output_file_name :")
            text_output_name_v.Disable()
            text_output_name_v.SetBackgroundColour("#dabae7")
            self.text_output_name = wx.TextCtrl(panel_taxt,wx.ID_ANY,str(self.output_name)) #output_name
            
            self.figure_output_checkbox = wx.CheckBox(panel_taxt,label="save_figure")
            """
            addvanced
            
            """
            text_export_measure_count_v = wx.TextCtrl(advanced_setting_showing,wx.ID_ANY,"Export_measure_count :")
            text_export_measure_count_v.Disable()
            text_export_measure_count_v.SetBackgroundColour("#dabae7")
            self.text_export_measure_count = wx.TextCtrl(advanced_setting_showing,wx.ID_ANY,str(self.export_measure_count)) #export_measure_count
            self.text_export_measure_count.Disable()
            
            text_key_count_v = wx.TextCtrl(advanced_setting_showing,wx.ID_ANY,"Output_key_count :")
            text_key_count_v.Disable()
            text_key_count_v.SetBackgroundColour("#dabae7")
            self.text_key_count = wx.TextCtrl(advanced_setting_showing,wx.ID_ANY,str(self.key_count)) #key_count
            self.text_key_count.Disable()
            
            text_measure_split_rate_v = wx.TextCtrl(advanced_setting_showing,wx.ID_ANY,"Measure_split_rate :")
            text_measure_split_rate_v.Disable()
            text_measure_split_rate_v.SetBackgroundColour("#dabae7")
            self.text_measure_split_rate = wx.TextCtrl(advanced_setting_showing,wx.ID_ANY,str(self._measure_split_rate)) #_measure_split_rate
            self.text_measure_split_rate.Disable()
            
            text_output_directly_v = wx.TextCtrl(advanced_setting_showing,wx.ID_ANY,"Output_directly :")
            text_output_directly_v.Disable()
            text_output_directly_v.SetBackgroundColour("#dabae7")
            self.text_output_directly = wx.TextCtrl(advanced_setting_showing,wx.ID_ANY,str(self.output_directly)) #output_directly
            self.text_output_directly.Disable()
            
            text_ylim_v = wx.TextCtrl(advanced_setting_showing,wx.ID_ANY,"figure_ylim_value(max,min)[Hz]:")
            text_ylim_v.Disable()
            text_ylim_v.SetBackgroundColour("#dabae7")
            self.ylim_max = wx.TextCtrl(advanced_setting_showing,wx.ID_ANY,str(self.ymax))
            self.ylim_min = wx.TextCtrl(advanced_setting_showing,wx.ID_ANY,str(self.ymin))
            self.ylim_max.Disable()
            self.ylim_min.Disable()
            text_xlim_v = wx.TextCtrl(advanced_setting_showing,wx.ID_ANY,"figure_xlim_value(max,min)[sec]:")
            text_xlim_v.Disable()
            text_xlim_v.SetBackgroundColour("#dabae7")
            self.xlim_max = wx.TextCtrl(advanced_setting_showing,wx.ID_ANY,str(self.xmax))
            self.xlim_min = wx.TextCtrl(advanced_setting_showing,wx.ID_ANY,str(self.xmin))
            self.xlim_max.Disable()
            self.xlim_min.Disable()
            
            text_reso_v = wx.TextCtrl(advanced_setting_showing,wx.ID_ANY,"Custom_STFT_resolution :")
            text_reso_v.Disable()
            self.text_resolution_v = wx.TextCtrl(advanced_setting_showing,wx.ID_ANY,self.resolution_settings) #"freqency"or"time"
            self.text_resolution_v.Disable()
            self.text_resolution_v.SetBackgroundColour("#dabae7")
            self.text_resolution = wx.TextCtrl(advanced_setting_showing,wx.ID_ANY,str(self.resolution)) #values
            self.text_resolution.Disable()
            
            text_velocity_v = wx.TextCtrl(advanced_setting_showing,wx.ID_ANY,"Velocity_rate") #values
            text_velocity_v.SetBackgroundColour("#dabae7")
            text_velocity_v.Disable()
            self.text_velocity = wx.TextCtrl(advanced_setting_showing,wx.ID_ANY,str(self.velocity_rate)) #values
            self.text_velocity.Disable()
            
            text_velocity_range_v = wx.TextCtrl(advanced_setting_showing,wx.ID_ANY,"Velocity_range") #values
            text_velocity_range_v.SetBackgroundColour("#dabae7")
            text_velocity_range_v.Disable()
            self.text_velocity_range = wx.TextCtrl(advanced_setting_showing,wx.ID_ANY,str(self.velocity_range)) #values
            self.text_velocity_range.Disable()
            
            layout_1 = wx.BoxSizer(wx.VERTICAL)
            layout_1.Add(panel_taxt,6,wx.EXPAND|wx.ALL,0)
            layout_1.Add(advanced_setting_showing,3,wx.EXPAND|wx.ALL,0)
            layout_1.Add(panel_button,1,wx.EXPAND|wx.ALL,0)
            self.SetSizer(layout_1)
            layout_2 = wx.BoxSizer(wx.HORIZONTAL)
            layout_2.Add(button_ok,1,wx.EXPAND|wx.ALL,20)
            layout_2.Add(button_cancel,1,wx.EXPAND|wx.ALL,20)
            panel_button.SetSizer(layout_2)
            
            button_setting.Bind(wx.EVT_BUTTON,self.AdvancedSetting)
            
            _box = 2
            layout_3 = wx.BoxSizer(wx.VERTICAL)
            layout_3.Add(text_file_name_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_3.Add(self.text_file_name,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)#入力不可
            layout_3.Add(text_bpm_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_3.Add(self.text_bpm,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            layout_3.Add(text_beats_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_3.Add(self.text_beats_1,1,wx.EXPAND|wx.LEFT|wx.RIGHT,_box)
            layout_3.Add(self.text_beats_2,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            layout_3.Add(text_output_name_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_3.Add(self.text_output_name,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            layout_3.Add(self.figure_output_checkbox,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            layout_3.Add(button_setting,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)
            panel_taxt.SetSizer(layout_3)
            
            layout_4 = wx.BoxSizer(wx.VERTICAL)
            layout_4.Add(text_export_measure_count_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_4.Add(self.text_export_measure_count,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box) #export_measure_count
            layout_4.Add(text_key_count_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_4.Add(self.text_key_count,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box) #key_count
            layout_4.Add(text_measure_split_rate_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_4.Add(self.text_measure_split_rate,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            layout_4.Add(text_output_directly_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_4.Add(self.text_output_directly,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            layout_4.Add(text_ylim_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_4.Add(self.ylim_max,1,wx.EXPAND|wx.LEFT|wx.RIGHT,_box)
            layout_4.Add(self.ylim_min,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            layout_4.Add(text_xlim_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_4.Add(self.xlim_max,1,wx.EXPAND|wx.LEFT|wx.RIGHT,_box)
            layout_4.Add(self.xlim_min,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            layout_4.Add(text_reso_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_4.Add(self.text_resolution_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_4.Add(self.text_resolution,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            layout_4.Add(text_velocity_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_4.Add(self.text_velocity,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            layout_4.Add(text_velocity_range_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_4.Add(self.text_velocity_range,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            advanced_setting_showing.SetSizer(layout_4)
        def AdvancedSetting(self,event):
            advanced_setting_dialog.export_measure_count = self.text_export_measure_count.GetValue()
            advanced_setting_dialog.key_count = self.text_key_count.GetValue()
            advanced_setting_dialog._measure_split_rate = self.text_measure_split_rate.GetValue()
            advanced_setting_dialog.output_directly = self.text_output_directly.GetValue()
            advanced_setting_dialog.ylim_max = self.ylim_max.GetValue()
            advanced_setting_dialog.ylim_min = self.ylim_min.GetValue()
            advanced_setting_dialog.resolution = self.text_resolution.GetValue()
            advanced_setting_dialog.velocity_rate = self.text_velocity.GetValue()
            advanced_setting_dialog.velocity_range = self.text_velocity_range.GetValue()
            dialog = advanced_setting_dialog()
            result = dialog.ShowModal()
            if result == wx.ID_OK:
                self.tof = True
                self.text_export_measure_count.SetValue(dialog.text_export_measure_count.GetValue())
                self.text_key_count.SetValue(dialog.text_key_count.GetValue())
                self.text_measure_split_rate.SetValue(dialog.text_measure_split_rate.GetValue())
                self.text_output_directly.SetValue(dialog.text_output_directly.GetValue())
                self.ylim_max.SetValue(dialog.ylim_max.GetValue())
                self.ylim_min.SetValue(dialog.ylim_min.GetValue())
                self.xlim_max.SetValue(dialog.xlim_max.GetValue())
                self.xlim_min.SetValue(dialog.xlim_min.GetValue())
                self.text_velocity.SetValue(dialog.text_velocity.GetStringSelection())
                self.text_resolution_v.SetValue(dialog.text_resolution_v.GetStringSelection())
                self.text_velocity.SetValue(dialog.text_velocity.GetValue())
                self.text_velocity_range.SetValue(dialog.text_velocity_range.GetValue())
                if dialog.text_resolution_v.GetStringSelection() == "frequency" and int(dialog.text_resolution.GetValue()) >= 88:
                    self.text_resolution.SetValue(str(87))
                else:
                    self.text_resolution.SetValue(dialog.text_resolution.GetValue())
            else:
                self.tof = False
                print("INFO:","Advanced_setting_is_Canceled")
            dialog.Destroy()
    """
    
    
    
    """
    class DataPreview():#データ参照画面
        def __init__(self,parent,wave_file,file_name,output_propaties,figname="figure"):
            print("INFO:","Setting_DataPreview",end=" ")
            self.panel_data = wx.Panel(parent,wx.ID_ANY)
            self.panel_data.SetBackgroundColour("#dabae7")
            self._startBT = wx.Button(self.panel_data,0,"Export_MIDI_file")
            print("____done")
            
            print("INFO:","Setting_figure_and_datapreview_panel",end=" ")
            self.fig_panel = wx.Panel(self.panel_data,wx.ID_ANY)
            self.figure = Figure(None)
            self.figure.set_facecolor((218/256,186/256,231/256))
            self.figure.set_size_inches(0.2,0.2)
            self.canvas = Figagg(self.fig_panel,0,self.figure)
            self.canvas.SetBackgroundColour("WHITE")
            self.canvas.SetSize((1,1))
            self.subplot = self.figure.add_subplot(1,1,1,polar=False)
            
            self._layout_f = wx.BoxSizer(wx.VERTICAL)
            self._layout_f.Add(self.canvas,1,wx.EXPAND|wx.ALL,0)
            self._layout = wx.BoxSizer(wx.VERTICAL)
            self._layout.Add(self.fig_panel,9,wx.EXPAND|wx.ALL,0) #グラフ部分
            self._layout.Add(self._startBT,1,wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT,10) #ボタン部分
            
            self._startBT.Bind(wx.EVT_BUTTON,self.LaunchWaveToMIDI)
            print("____done")
            
            thread_1 = Thread(target = self.LaunchSelf,args=(parent,wave_file,file_name,output_propaties,figname))
            thread_1.start()
            
            return None
            
        def LaunchSelf(self,parent,wave_file,file_name,output_propaties,figname):
            self._datas = WaveToIntData(wave_file,output_propaties)
            self.output_propaties = output_propaties
            wave_file.close()
            del wave_file
            
            self.subplot.pcolormesh(self._datas[1],self._datas[0],self._datas[2],cmap="jet")
            self.subplot.set_ylabel("frequency[Hz]")
            self.subplot.set_xlabel("time[sec]")
            
            if output_propaties.ylim[1] == -1 or output_propaties.ylim[0] == -1:
                if output_propaties.ylim[0] != -1:
                    self.subplot.set_ylim([output_propaties.ylim[0],self._datas[0].max()/2])
                if output_propaties.ylim[1] != -1:
                    self.subplot.set_ylim([0,output_propaties.ylim[1]])
                else:
                    self.subplot.set_ylim([0,self._datas[0].max()/2])
            else:
                self.subplot.set_ylim(output_propaties.ylim)
            
            if output_propaties.xlim[1] == -1 or output_propaties.xlim[0] == -1:
                if output_propaties.xlim[0] != -1:
                    self.subplot.set_xlim([output_propaties.xlim[0],self._datas[1].max()])
                if output_propaties.xlim[1] != -1:
                    self.subplot.set_xlim([0,output_propaties.xlim[1]])
                else:
                    self.subplot.set_xlim([0,self._datas[1].max()])
            else:
                self.subplot.set_xlim(output_propaties.xlim)
            
            mapp = self.subplot.pcolormesh(self._datas[1],self._datas[0],self._datas[2],cmap="jet")
            self.figure.colorbar(mapp)
            
            self.fig_panel.SetSizer(self._layout_f)
            self.panel_data.SetSizer(self._layout)
            print("INFO:","Inserting_page",end=" ")
            parent.InsertPage(1,self.panel_data,str(file_name))
            print("____done")
            if output_propaties.savefig == True:
                self.figure.savefig(output_propaties.output_name+".png")
            else:
                pass
        
        def LaunchWaveToMIDI(self,event):
            thr = Thread(target = WaveToMIDI,args=(self._datas,self.output_propaties))
            thr.start()
    class dad(wx.FileDropTarget):#ドラッグアンドドロップ
        def __init__(self,window,_parent):
            wx.FileDropTarget.__init__(self)
            self.window = window
            self._parent = _parent
            self.output_propaties = output_propaties()
        
        def OnDropFiles(self,x,y,files):
            self.FileManager(files)
            if self.tof == True:
                self.SetDataPreview(self._parent,self.wave_file,self.file_name,self.output_propaties)
            return 0
        def SetDataPreview(self,_parent,wave_file,file_name,output_propaties):
            DataPreview(_parent,wave_file,file_name,output_propaties)
            del self.wave_file
        def FileManager(self,file_paths):
            for i in file_paths:
                self.tof = False
                file_path = i
                file_name_def = os.path.basename(str(file_path)).rstrip("']").replace(" ","_") #ファイル名のスペースを置換
                import_dialog.file_name = file_name_def
                dialog = import_dialog()
                result = dialog.ShowModal()
                if result == wx.ID_OK:
                    self.tof = True
                    self.output_propaties._bpm = int(dialog.text_bpm.GetValue())
                    self.output_propaties.beats = [int(dialog.text_beats_1.GetValue()),int(dialog.text_beats_2.GetValue())]
                    self.output_propaties.export_measure_count = int(dialog.text_export_measure_count.GetValue())
                    self.output_propaties.output_name = str(dialog.text_output_name.GetValue())
                    self.output_propaties.key_count = int(dialog.text_key_count.GetValue())
                    self.output_propaties._measure_split_rate = int(dialog.text_measure_split_rate.GetValue())
                    self.output_propaties.output_directly = str(dialog.text_output_directly.GetValue())
                    self.output_propaties.savefig = dialog.figure_output_checkbox.GetValue()
                    self.output_propaties.ylim = [int(dialog.ylim_min.GetValue()),int(dialog.ylim_max.GetValue())]
                    self.output_propaties.xlim = [int(dialog.xlim_min.GetValue()),int(dialog.xlim_max.GetValue())]
                    self.output_propaties.resolution_settings = dialog.text_resolution_v.GetValue()
                    self.output_propaties.resolution = float(dialog.text_resolution.GetValue())
                    self.output_propaties.velocity_rate = int(dialog.text_velocity.GetValue())
                    self.output_propaties.velocity_range = float(dialog.text_velocity_range.GetValue())
                else:
                    self.tof = False
                    print("INFO:Canceled")
                dialog.Destroy()
                self.file_path_search(file_path)
            del file_paths
            return True
        def file_path_search(self,file_path):
            if self.tof == True:
                _root,_ext = os.path.splitext(str(file_path))
                if "wav" in _ext: #ファイルの種類選別
                    self.file_name = "input/" + os.path.basename(str(file_path)).rstrip("']")
                    self.wave_file = wave.open(self.file_name,"r")
                else:
                    dialog = wx.MessageDialog(None,"This file is not abailable","Error",style = wx.OK)
                    print("")
                    print("ERROR:This_file_is_not_abailable")
                    dialog.ShowModal()
                    dialog.Destroy()
                print("INFO:File_importing",end="")
                print("","____done")
                print("_____File_name:",self.file_name)
            else:
                pass
            return True
    """
    
    #メインGUIを以下に記入
    
    
    """
    class output_propaties:
        pass
    class m_frame(wx.Frame):#メインフレーム
        def __init__(self,title):
            wx.Frame.__init__(self , None , title = title , size = (500,600))
            icon = wx.Icon("./frame.ico",wx.BITMAP_TYPE_ICO)
            self.SetIcon(icon)
            self.output_propaties = output_propaties()
            self.wave_file = None
            self.file_name = ""
            self.parent_panel = wx.Panel(self, wx.ID_ANY)
            self.parent_panel.SetBackgroundColour("#d0b0dd")
            self.notebook = fnotebook.FlatNotebook(self.parent_panel, wx.ID_ANY,agwStyle = fnotebook.FNB_X_ON_TAB | fnotebook.FNB_NO_X_BUTTON | fnotebook.FNB_NO_NAV_BUTTONS)
            
            self.textlog = wx.TextCtrl(self.parent_panel,-1,value = "Hello WaveToMidi.\n",style=wx.TE_MULTILINE)
            
            sys.stdout = sys.stderr = self #ログの表示箇所を破壊的に変更
            
            panel1 = wx.Panel(self.notebook, wx.ID_ANY)#説明書を開く
            panel1.SetBackgroundColour("#dabae7")
            tex2 = wx.TextCtrl(panel1,0,style=wx.TE_MULTILINE)
            tex2.SetBackgroundColour("#dabae7")
            font = wx.Font(10,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL)
            tex2.SetFont(font)
            with open("readme.txt","r") as read_me_text:
                tex2.AppendText(str(read_me_text.read()))
            layout = wx.BoxSizer(wx.HORIZONTAL)
            layout.Add(tex2,1,wx.EXPAND|wx.ALL,20)
            panel1.SetSizer(layout)
            self.notebook.SetBackgroundColour("#dabae7")
            self.notebook.InsertPage(0, panel1, "readme")
            
            menu_menu = wx.Menu()#メニュー一番左
            menu_menu.Append(11,"file")
            menu_menu.AppendSeparator()
            menu_menu.Append(99,"exit")
            
            menu_bar = wx.MenuBar()
            menu_bar.Append(menu_menu,"menu")
            self.SetMenuBar(menu_bar)
            self.Bind(wx.EVT_MENU,self.Menu_click)
            
            self.ResetRayout()
            
            self.SetDropTarget(dad(self,self.notebook))
            self.notebook.SetDropTarget(dad(self,self.notebook))
            self.Show(True)
            file_paths = sys.argv
            if len(file_paths) > 1:#ファイル読み込み開始
                file_paths = file_paths[1:]
                self.FileManager(file_paths)
                if self.tof == True:
                    self.SetDataPreview(self.notebook,self.wave_file,self.file_name,self.output_propaties)
            else:
                pass
        def SetDataPreview(self,_parent,wave_file,file_name,output_propaties):
            DataPreview(_parent,wave_file,file_name,output_propaties)
            del self.wave_file
        def FileManager(self,file_paths):
            _bpm = 100
            beats = [4,4]
            export_measure_count = 100
            output_name = ""
            key_count = 88
            _measure_split_rate = 64
            output_directly = ""
            for i in file_paths:
                self.tof = False
                file_path = i
                file_name_def = os.path.basename(str(file_path)).rstrip("']").replace(" ","_") #ファイル名のスペースを置換
                import_dialog.file_name = file_name_def
                dialog = import_dialog()
                result = dialog.ShowModal()
                if result == wx.ID_OK:
                    self.tof = True
                    self.output_propaties._bpm = int(dialog.text_bpm.GetValue())
                    self.output_propaties.beats = [int(dialog.text_beats_1.GetValue()),int(dialog.text_beats_2.GetValue())]
                    self.output_propaties.export_measure_count = int(dialog.text_export_measure_count.GetValue())
                    self.output_propaties.output_name = str(dialog.text_output_name.GetValue())
                    self.output_propaties.key_count = int(dialog.text_key_count.GetValue())
                    self.output_propaties._measure_split_rate = int(dialog.text_measure_split_rate.GetValue())
                    self.output_propaties.output_directly = str(dialog.text_output_directly.GetValue())
                    self.output_propaties.savefig = dialog.figure_output_checkbox.GetValue()
                    self.output_propaties.ylim = [int(dialog.ylim_min.GetValue()),int(dialog.ylim_max.GetValue())]
                    self.output_propaties.xlim = [int(dialog.xlim_min.GetValue()),int(dialog.xlim_max.GetValue())]
                    self.output_propaties.resolution_settings = str(dialog.text_resolution_v.GetValue())
                    self.output_propaties.resolution = float(dialog.text_resolution.GetValue())
                    self.output_propaties.velocity_rate = int(dialog.text_velocity.GetValue())
                    self.output_propaties.velocity_range = float(dialog.text_velocity_range.GetValue())
                else:
                    self.tof = False
                    print("INFO:Canceled")
                dialog.Destroy()
                self.file_path_search(file_path)
            del file_paths
            return True
        def file_path_search(self,file_path):
            if self.tof == True:
                _root,_ext = os.path.splitext(str(file_path))
                if "wav" in _ext: #ファイルの種類選別
                    self.file_name = "input/" + os.path.basename(str(file_path)).rstrip("']")
                    self.wave_file = wave.open(self.file_name,"r")
                else:
                    dialog = wx.MessageDialog(None,"This file is not abailable","Error",style = wx.OK)
                    print("")
                    print("ERROR:This_file_is_not_abailable")
                    dialog.ShowModal()
                    dialog.Destroy()
                print("INFO:File_importing",end="")
                print("","____done")
                print("_____File_name:",self.file_name)
            else:
                pass
            return True
        def write(self,msg):#ログのイベント（書き換え不可）
            self.textlog.AppendText(msg)
        def flush(self):#ログのイベント（書き換え不可）
            pass
        def Menu_click(self,event): #メニューイベント
            ev_id = event.GetId()
            #1つめ(基本動作)
            if ev_id == 11: #ファイル選択ダイアログ
                dlg = wx.FileDialog(self,message = "Choose a file",defaultFile = "",style = wx.FD_OPEN|wx.FD_MULTIPLE)
                if dlg.ShowModal() == wx.ID_OK:
                    file_paths = dlg.GetPaths()
                if not file_paths == []:#ファイル読み込み開始
                    self.FileManager(file_paths)
                    if self.tof == True:
                        self.SetDataPreview(self.notebook,self.wave_file,self.file_name,self.output_propaties)
                else:
                    pass
            if ev_id == 99:
                self.Destroy()
        def ResetRayout(self):
            layout_p = wx.BoxSizer(wx.VERTICAL)
            layout_p.Add(self.notebook,15,wx.EXPAND|wx.ALL,0)
            layout_p.Add(self.textlog,5,wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT,10)
            self.parent_panel.SetSizer(layout_p)
            
            layout_m = wx.BoxSizer(wx.VERTICAL)
            layout_m.Add(self.parent_panel,1,wx.EXPAND|wx.ALL,0)
            
            self.SetSizer(layout_m)
    class MyApp(wx.App):
        def OnInit(self):
            mainframe = m_frame("WaveToMidi")
            #mainframe.Show(True)
            self.SetTopWindow(mainframe)
            return True
    app = MyApp()
    app.MainLoop()
    
if __name__ == "__main__":
    main()