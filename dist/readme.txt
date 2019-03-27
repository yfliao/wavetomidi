・入力するファイルの名前は、スペースを含めない半角英数字を用いてください。
・「./input」フォルダに、圧縮していないwaveファイル（.wav）を入れてから参照してください。
・ファイルサイズの大きなwaveファイルを変換する際、メモリ容量が不足する場合があります。予め細かく分けて処理すると解決します。
・MIDIファイルはボリュームの大きさで4つのトラックに分けて出力されます。
・用語の説明
bpm:　outputするmidiファイルのbpmを決定する。
beats:　outputするmidiファイルの拍子。n分のm拍子を[n,m]と表記する。
Export_measure_count:　何小節毎にoutputするか。
Output_file_name:　outputするmidiファイルの名前。
Output_key_count:　outputするmidiファイルの鍵盤数。defaultはA0からカウントして88個。
Measure_split_rate:　一小節を何等分するか。もしくは、一小節に用いる音符の最小の短さ。
Output_directly:　outputする場所。defaultは「./output」。