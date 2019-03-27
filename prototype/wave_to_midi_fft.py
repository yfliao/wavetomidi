def main():
    from threading import Thread,Event
    import sys
    import dill
    import wx
    import time
    from time import sleep
    import matplotlib
    import wx.lib.agw.flatnotebook as fnotebook
    from wx.lib.mixins.listctrl import CheckListCtrlMixin,ListCtrlAutoWidthMixin
    import os
    from pathlib import Path
    matplotlib.interactive(True)
    matplotlib.use("WXAgg")
    from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as Figagg
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    import numpy
    from scipy import signal
    import math
    import wave
    import pretty_midi
    
    if getattr(sys,'frozen',False):
        os.chdir(os.path.dirname(sys.executable))#カレントディレクトリの処理
    
    _e = 1e-24
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
    
    def FrequencyToNoteNumber(_freq,_key_freq): #周波数をピッチに変換
        for i in range(len(_freq)):
            _freq[i][0] = GetNearestPitch(_key_freq,_freq[i][0])
        return _freq
    
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
        
    def Fft(_data,_frame_rate,_key_freq,_figure=False,_int_data=None,run_average=False):#フーリエ級数変換
        if type(_data) == list:
            _data = numpy.array(_data)
        N = _data.size
        hanwindow = numpy.hanning(N)
        _data = hanwindow * _data
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
        
        output = [[i,j]  for i,j in zip(freq,amp)] #[周波数,振幅]
        output = FrequencyToNoteNumber(output,_key_freq) #[pitch,振幅]のデータに書き換え
        output,vel_range = GetAmpOfKey(output,_key_freq) #pitch毎に振幅を集約
        
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
            ax_4.set_xlabel("Frequency[Hz]")
            ax_4.set_ylabel("Amplitude")
            ax_4.legend()
            print("INFO:Peaks",output)
            plt.show()
        else:
            pass
        return output,vel_range
    
    def FftForAll(_splited_data,_frame_rate,_key_freq): #フーリエ級数変換を全てに適応させ、pitchとvelocityの情報を得る
        _p = 0
        _splited_data = list(map(lambda x: x,_splited_data))
        print("INFO:","fourier_transforming")
        _vel_range = [100,0]
        for i in range(len(_splited_data)):
            _splited_data[i] = _splited_data[i].tolist()
            for j in range(len(_splited_data[i])):
                fft_data,vel_range = Fft(numpy.array(_splited_data[i])[j],_frame_rate,_key_freq) #[pitch,振幅]のデータに書き換え
                _splited_data[i][j] = numpy.array(fft_data,dtype=object)
                del fft_data
                if vel_range[0] < _vel_range[0]:
                    _vel_range[0] = vel_range[0]
                if vel_range[1] > _vel_range[1]:
                    _vel_range[1] = vel_range[1]
            
            _p = int(i / (len(_splited_data) - 1 + _e) * 100)
            print("\r{0:d}".format(_p),end = "%")
        print("","____done")
        _splited_data = numpy.array(_splited_data,dtype=object)
        print("_____Amplitude_range:",_vel_range)
        return _splited_data,_vel_range
    
    def DataToMidi(_data,_rate,_bpm,vel_range,_name="output/output.mid"): #MIDIの生成
        print("INFO:","Making_MIDI_file",_name)
        fft_midi = pretty_midi.PrettyMIDI(initial_tempo=_bpm)
        piano_vol_1 = pretty_midi.Instrument(program = 1) #インストゥルメントトラックを追加(音量が一番大きい)
        piano_vol_2 = pretty_midi.Instrument(program = 1) #3/4くらい
        piano_vol_3 = pretty_midi.Instrument(program = 1) #2/4くらい
        piano_vol_4 = pretty_midi.Instrument(program = 1) #1/4くらい
        
        _vel = (vel_range[1] - vel_range[0])/4
        note_time = 0
        note_count = 0
        measure_count = 0
        note_count_1 = 0
        note_count_2 = 0
        note_count_3 = 0
        note_count_4 = 0
        _data = list(map(lambda x: x.tolist(),_data))
        if not _data == []:
            for _measure in range(len(_data)): #小節毎
                for _notes in _data[_measure]: #単位時間毎
                    if not _notes == []:
                        for _note in _notes: #note毎
                            if _note[1] > 0:
                                _velocity = int(_note[1] * 100)
                                _pitch = int(_note[0]) + 21 #midiの標準pitchではA0が21
                                adding_note = pretty_midi.Note(velocity = _velocity,
                                            pitch = _pitch,
                                            start =  note_time,
                                            end = note_time + _rate) #ノーツを作成
                                if _velocity > (vel_range[0] + _vel * 3) * 100: #インストゥルメントトラックにノーツを追加(4/4)
                                    note_count_1 += 1
                                    piano_vol_1.notes.append(adding_note)
                                elif _velocity > (vel_range[0] + _vel * 2) * 100: #インストゥルメントトラックにノーツを追加(3/4)
                                    note_count_2 += 1
                                    piano_vol_2.notes.append(adding_note)
                                elif _velocity > (vel_range[0] + _vel) * 100: #インストゥルメントトラックにノーツを追加(2/4)
                                    note_count_3 += 1
                                    piano_vol_3.notes.append(adding_note)
                                else: #インストゥルメントトラックにノーツを追加(1/4)
                                    note_count_4 += 1
                                    piano_vol_4.notes.append(adding_note)
                                note_count +=1
                            else:
                                pass
                    else:
                        pass
                    note_time = note_time + _rate #時間を進める
                measure_count += 1
                _p = int(_measure / (len(_data) - 1 + _e) * 100)
                print("\r{0:d}".format(_p),end = "%")
        else:
            pass
        print("","____done")
        print("_____Note_count:",note_count)
        print("_____Measure_count:",measure_count)
        print("_____Velocity_interval:",_vel)
        print("_____Notes_count_by_track:",note_count_1,",",note_count_2,",",note_count_3,",",note_count_4)
        
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
    def DivisionMidiExport(_data,_rate,_bpm,_measure_count,vel_range,split_rate = 200,_name = "output",_output_directly = "output"):
        _split_count = math.ceil(_measure_count / split_rate) #小節数で複数のファイルを出力（DAW側の負担軽減）
        print("INFO:","Exporting_",_split_count,"_MIDI_file")
        
        split_rate = _measure_count - (_split_count - 1) * split_rate #末尾小節数
        if split_rate == 0:
            _data = numpy.array_split(_data,_split_count) #個数に区切る（末尾余り）
            _data = numpy.array(_data)
            for i in range(_data.size):
                _name = _output_directly + "/" + _name + "_" + str(i) + ".mid"
                DataToMidi(_data[i],_rate,_bpm,vel_range,_name = _name)
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
                DataToMidi(_data[i],_rate,_bpm,vel_range,_name = "output/" + _name + "_" + str(i) + ".mid")
                _data[i] = []
        else:
            DataToMidi(_data,_rate,_bpm,vel_range,_name = "output/" + _name + ".mid")
            _data = []
    def WaveToIntData(wave_file):
        print("INFO:","Converting_wave_to_buffer",end=" ")
        buff = wave_file.readframes(wave_file.getnframes()) #バッファーに変換
        print("____done")
        frame_rate = wave_file.getframerate() #フレームレート
        wave_file.close()
        del wave_file
        print("INFO:","Converting_buffer_to_int_data",end=" ")
        int_data = numpy.frombuffer(buff,dtype="int16") #waveの中身を16bitintに変換
        int_data = int_data / (math.pow(2,16) / 2) #0から1に変更
        print("____done")
        del buff
        return int_data,frame_rate
    def WaveToMIDI(int_data,frame_rate,_bpm,beats,export_measure_count,output_name,key_count=88,_measure_split_rate=64,output_directly="output"):
        key_freq = GetKeyFreq(key_count=key_count) #88鍵盤の周波数を取得
        
        export_bpm = _bpm
        beats = [2,4] #[0]/[1]拍子
        
        measure_rate = GetMeasureRate(frame_rate,beats,export_bpm) #一小節にあたるサンプル数
        whole_split_rate = GetMeasureCount(int_data,measure_rate) #何小節に等分するか
        measure_split_rate = _measure_split_rate #一小節あたり何等分するか
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
        
        int_data,vel_range = FftForAll(int_data,frame_rate,key_freq)
        print("_____Data_shape:",int_data.shape)
        DivisionMidiExport(int_data,
            output_rate,
            export_bpm,
            whole_split_rate,
            vel_range,
            split_rate = export_measure_count,
            _name = output_name,
            _output_directly = output_directly)
        print("INFO:","Exporting_MIDI_file_is_succeeded")
    """
    
    
    
    """
    class import_dialog(wx.Dialog):#インポートのプロパティ入力画面
        file_name = "input"
        _bpm = 100
        beats = [4,4]
        export_measure_count = 100
        output_name = "output"
        key_count = 88
        _measure_split_rate = 64
        output_directly = "output"
        
        def __init__(self):
            wx.Dialog.__init__(self,None,-1,"import_menu",size=(400,600),
                               style=wx.SYSTEM_MENU|
                               wx.CAPTION | wx.CLIP_CHILDREN)
            print("INFO:enter_your_self")
            self.SetBackgroundColour("#dabae7")
            panel_taxt = wx.Panel(self, wx.ID_ANY)
            panel_button = wx.Panel(self, wx.ID_ANY)
            panel_taxt.SetBackgroundColour("#dabae7")
            panel_button.SetBackgroundColour("#dabae7")
            
            button_ok = wx.Button(panel_button,wx.ID_OK,"OK")
            button_cancel = wx.Button(panel_button,wx.ID_CANCEL,"CANCEL")
            
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
            
            text_beats_v = wx.TextCtrl(panel_taxt,wx.ID_ANY,"beats ([number_of_beats : phonetic_value]):")
            text_beats_v.Disable()
            text_beats_v.SetBackgroundColour("#dabae7")
            self.text_beats = wx.TextCtrl(panel_taxt,wx.ID_ANY,str(self.beats)) #beats
            
            text_export_measure_count_v = wx.TextCtrl(panel_taxt,wx.ID_ANY,"Export_measure_count :")
            text_export_measure_count_v.Disable()
            text_export_measure_count_v.SetBackgroundColour("#dabae7")
            self.text_export_measure_count = wx.TextCtrl(panel_taxt,wx.ID_ANY,str(self.export_measure_count)) #export_measure_count
            
            text_output_name_v = wx.TextCtrl(panel_taxt,wx.ID_ANY,"Output_file_name :")
            text_output_name_v.Disable()
            text_output_name_v.SetBackgroundColour("#dabae7")
            self.text_output_name = wx.TextCtrl(panel_taxt,wx.ID_ANY,str(self.output_name)) #output_name
            
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
            
            layout_1 = wx.BoxSizer(wx.VERTICAL)
            layout_1.Add(panel_taxt,8,wx.EXPAND|wx.ALL,0)
            layout_1.Add(panel_button,1,wx.EXPAND|wx.ALL,0)
            self.SetSizer(layout_1)
            layout_2 = wx.BoxSizer(wx.HORIZONTAL)
            layout_2.Add(button_ok,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,20)
            layout_2.Add(button_cancel,1,wx.EXPAND|wx.RIGHT|wx.LEFT|wx.BOTTOM,20)
            panel_button.SetSizer(layout_2)
            
            _box = 5
            layout_3 = wx.BoxSizer(wx.VERTICAL)
            layout_3.Add(text_file_name_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_3.Add(self.text_file_name,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)#入力不可
            
            layout_3.Add(text_bpm_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_3.Add(self.text_bpm,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            
            layout_3.Add(text_beats_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_3.Add(self.text_beats,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            
            layout_3.Add(text_export_measure_count_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_3.Add(self.text_export_measure_count,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            
            layout_3.Add(text_output_name_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_3.Add(self.text_output_name,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            
            layout_3.Add(text_key_count_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_3.Add(self.text_key_count,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            
            layout_3.Add(text_measure_split_rate_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_3.Add(self.text_measure_split_rate,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            
            layout_3.Add(text_output_directly_v,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,_box)#入力不可
            layout_3.Add(self.text_output_directly,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,_box)
            
            panel_taxt.SetSizer(layout_3)
    """
    
    
    
    """
    class DataPreview():#データ参照画面
        def __init__(self,parent,int_data,frame_rate,file_name,output_propaties):
            print("INFO:","Setting_DataPreview",end=" ")
            self.panel_data = wx.Panel(parent,wx.ID_ANY)
            self.panel_data.SetBackgroundColour("#dabae7")
            self._startBT = wx.Button(self.panel_data,0,"Export_MIDI_file")
            print("____done")
            
            self.int_data = int_data
            self.frame_rate = frame_rate
            self.output_propaties = output_propaties
            del int_data
            
            print("INFO:","Setting_Figure",end=" ")
            self.fig_panel = wx.Panel(self.panel_data,wx.ID_ANY)
            self.figure = Figure(None)
            self.figure.set_facecolor((218/256,186/256,231/256))
            self.figure.set_size_inches(0.5,0.5)
            self.canvas = Figagg(self.fig_panel,0,self.figure)
            self.canvas.SetBackgroundColour("WHITE")
            self.canvas.SetSize((100,100))
            self.subplot = self.figure.add_subplot(1,1,1,polar=False)
            self.subplot.plot(self.int_data)
            self.subplot.set_ylim([-1,1])
            _layout_f = wx.BoxSizer(wx.VERTICAL)
            _layout_f.Add(self.canvas,1,wx.EXPAND|wx.ALL,0)
            self.fig_panel.SetSizer(_layout_f)
            print("____done")
            
            _layout = wx.BoxSizer(wx.VERTICAL)
            _layout.Add(self.fig_panel,5,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,5) #グラフ部分
            _layout.Add(self._startBT,1,wx.EXPAND|wx.ALL,5) #ボタン部分
            
            self._startBT.Bind(wx.EVT_BUTTON,self.LaunchWaveToMIDI)
            
            self.panel_data.SetSizer(_layout)
            parent.InsertPage(1,self.panel_data,str(file_name))
            
        def LaunchWaveToMIDI(self,event):
            thr = Thread(target = WaveToMIDI,args=(
                self.int_data,
                self.frame_rate,
                self.output_propaties._bpm,
                self.output_propaties.beats,
                self.output_propaties.export_measure_count,
                self.output_propaties.output_name,
                self.output_propaties.key_count,
                self.output_propaties._measure_split_rate,
                self.output_propaties.output_directly,))
            thr.start()
            pass
    class dad(wx.FileDropTarget):#ドラッグアンドドロップ
        def __init__(self,window,_parent):
            wx.FileDropTarget.__init__(self)
            self.window = window
            self._parent = _parent
            self.output_propaties = output_propaties()
        
        def OnDropFiles(self,x,y,files):
            self.FileManager(files)
            if self.tof == True:
                self.SetDataPreview(self._parent,self.int_data,self.frame_rate,self.file_name,self.output_propaties)
            return 0
        def SetDataPreview(self,_parent,_file,frame_rate,file_name,output_propaties):
            DataPreview(_parent,_file,frame_rate,file_name,output_propaties)
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
                    self.output_propaties.beats = list(dialog.text_beats.GetValue())
                    self.output_propaties.export_measure_count = int(dialog.text_export_measure_count.GetValue())
                    self.output_propaties.output_name = str(dialog.text_output_name.GetValue())
                    self.output_propaties.key_count = int(dialog.text_key_count.GetValue())
                    self.output_propaties._measure_split_rate = int(dialog.text_measure_split_rate.GetValue())
                    self.output_propaties.output_directly = str(dialog.text_output_directly.GetValue())
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
                    self.int_data,self.frame_rate = WaveToIntData(self.wave_file)
                    self.wave_file.close()
                    del self.wave_file
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
            self.int_data = None
            self.frame_rate = None
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
            tex2.Disable()
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
                    self.SetDataPreview(self.notebook,self.int_data,self.frame_rate,self.file_name,self.output_propaties)
            else:
                pass
        def SetDataPreview(self,_parent,_file,frame_rate,file_name,output_propaties):
            DataPreview(_parent,_file,frame_rate,file_name,output_propaties)
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
                    self.output_propaties.beats = list(dialog.text_beats.GetValue())
                    self.output_propaties.export_measure_count = int(dialog.text_export_measure_count.GetValue())
                    self.output_propaties.output_name = str(dialog.text_output_name.GetValue())
                    self.output_propaties.key_count = int(dialog.text_key_count.GetValue())
                    self.output_propaties._measure_split_rate = int(dialog.text_measure_split_rate.GetValue())
                    self.output_propaties.output_directly = str(dialog.text_output_directly.GetValue())
                    
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
                    self.int_data,self.frame_rate = WaveToIntData(self.wave_file)
                    self.wave_file.close()
                    del self.wave_file
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
                        self.SetDataPreview(self.notebook,self.int_data,self.frame_rate,self.file_name,self.output_propaties)
                else:
                    pass
            if ev_id == 99:
                self.Destroy()
        def ResetRayout(self):
            layout_p = wx.BoxSizer(wx.VERTICAL)
            layout_p.Add(self.notebook,3,wx.EXPAND|wx.ALL,0)
            layout_p.Add(self.textlog,1,wx.EXPAND|wx.ALL,10)
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