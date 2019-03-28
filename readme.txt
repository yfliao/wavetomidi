・入力するファイルの名前は，スペースを含めない半角英数字を用いてください．

・「./input」フォルダに，圧縮していないwaveファイル（.wav）を入れてから参照してください．

・ファイルサイズの大きなwaveファイルを変換する際，メモリ容量が不足する場合があります．予め細かく分けて処理すると解決します．

・MIDIファイルはボリュームの大きさで4つのトラックに分けて出力されます．

・用語の説明

bpm:　outputするmidiファイルのbpmを決定する．

beats:　outputするmidiファイルの拍子．

Export_measure_count:　何小節毎にoutputするか．(現バージョンでは機能ていません．)

Output_file_name:　outputするmidiファイルの名前．

Output_key_count:　outputするmidiファイルの鍵盤数．defaultはA0からカウントして88個．

Measure_split_rate:　一小節を何等分するか．もしくは，一小節に用いる音符の最小の短さ．

Output_directly:　outputする場所．defaultは「./output」．

figure_ylim_value:　表示するグラフのY軸の範囲．入力値-1は，最大値，最小値をそれぞれサンプリング周波数/2，0とする．

figure_xlim_value:　表示するグラフのx軸の範囲．入力値-1は，最大値，最小値をそれぞれ末尾時間，0とする．

Custom_STFT_resolution:　STFTを行う際のnpersegmentを決定するために，frequencyもしくはtimeの分解能を決定することで，もう片方の分解能も決定する．

time(Custom_STFT_resolution):　timeはsecond(float)で入力する．0以下で入力した場合は0.01となる．

frequency(Custom_STFT_resolution):　frequencyはpitch(int)で入力する．分解能は入力された値と，入力された値+1のpitchが持つ周波数の差で決定する．defaultは0(Bb0:29.135 - A0:27.500 = 2.135)．

Velocity_rate:　抽出する最低限の強さ，floatで入力する．SMFのVelocity（0~127）で決定するが，0だと出力が適切ではない．0よりも大きな値を用いることが望ましい．defaultは1．

Velocity_range:　velocityが変化したかどうかを判断する定数．defaultの0.5であれば，元の値から50%以内(即ち1.5倍の値まで)の変化を許容する．