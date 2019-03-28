"""
使用上の注意
・入力するfileの名前は，spaceを含めない半角英数字を用いてください．
・「./input」folderに，圧縮していないwavefile（.wav）を入れてから参照してください．
・file sizeの大きなwavefileを変換する際，memory容量が不足する場合があります．予め細かく分けて処理すると解決します．
・MIDIfileはvelocityの大きさで4つのtrackに分けて出力されます．
・Sauce codeは「./pianofftindex/wave_to_midi_stft.py」に記載されています．
"""
"""
用語の説明
bpm:　outputするMIDIfileのbpmを決定する．
beats:　outputするMIDIfileの拍子．
Export_measure_count:　何小節毎にoutputするか．(現バージョンでは機能ていません．)
Output_file_name:　outputするMIDIfileの名前．
Output_key_count:　outputするMIDIfileの鍵盤数．defaultはA0からカウントして88個．
Measure_split_rate:　一小節を何等分するか．もしくは，一小節に用いる音符の最小の短さ．
Output_directly:　outputする場所．defaultは「./output」．
figure_ylim_value:　表示するグラフのY軸の範囲．入力値-1は，最大値，最小値をそれぞれサンプリング周波数/2，0とする．
figure_xlim_value:　表示するグラフのx軸の範囲．入力値-1は，最大値，最小値をそれぞれ末尾時間，0とする．
Custom_STFT_resolution:　STFTを行う際のnpersegmentを決定するために，frequencyもしくはtimeの分解能を決定することで，もう片方の分解能も決定する．
time(Custom_STFT_resolution):　timeはsecond(float)で入力する．0以下で入力した場合は0.01となる．
frequency(Custom_STFT_resolution):　frequencyはpitch(int)で入力する．分解能は入力された値と，入力された値+1のpitchが持つ周波数の差で決定する．defaultは0(Bb0:29.135 - A0:27.500 = 2.135)．
Velocity_rate:　Velocityを検出し，MIDI_notes化する際の最低値．SMFの規格内0~127のintで入力する．defaultは1．
Velocity_range:　Velocityを検出し，MIDI_notes化する際の変化の許容範囲．0~1のfloatで入力する．defaultは0.5．
"""
"""
copyright(仮)
このsoftwareの再頒布及び使用は，次の箇条書きの条件を全て満たす場合に許可されます．
対象となるsoftwareがSauce code形式かbinary形式かは問いません．また，改変の有無も問いません．
・Sauce code形式で再頒布する場合は，このlicenseの文章全体を残す必要があります．
・binary形式で再頒布する場合は，このlicenseの文章全体を何らかの形で含む必要があります．
・このsoftwareの改変版を普及させるために，このsoftwareの著作権者の名前(もしくはcontributorの名前)を【勝手に】使用してはなりません．使用したい場合は，事前に書面による許可を得る必要があります．
・このsoftwareは，著作権者やcontributorによって，現状のまま提供されるものとします．また，このsoftwareは無保証であるものとします．
・著作権者やcontributorは、いかなる場合であれ、どんな損害賠償に対しても、責任を負わないものとします。
"""
"""
同封されている可能性があるPython-libraryとそのlicense．
altgraph        0.16.1  MIT     https://altgraph.readthedocs.io
attrs   19.1.0  MIT     https://www.attrs.org/
certifi 2018.11.29      MPL-2.0 https://certifi.io/
cycler  0.10.0  BSD     http://github.com/matplotlib/cycler
future  0.17.1  MIT     https://python-future.org
jsonform        0.0.2   MIT     https://github.com/RussellLuo/jsonform
jsonschema      3.0.1   MIT License     https://github.com/Julian/jsonschema
jsonsir 0.0.2   MIT     https://github.com/RussellLuo/jsonsir
kiwisolver      1.0.1   (Licence not found)     https://github.com/nucleic/kiwi
macholib        1.11    MIT     http://bitbucket.org/ronaldoussoren/macholib
matplotlib      3.0.2   BSD     http://matplotlib.org
mido    1.2.9   MIT     https://mido.readthedocs.io/
numpy   1.15.4  BSD     http://www.numpy.org
pefile  2018.8.8        (Licence not found)     https://github.com/erocarrera/pefile
pretty-midi     0.2.8   MIT     https://github.com/craffel/pretty_midi
pyinstaller     3.4     GPL license with a special exception which allows to use PyInstaller to build and distribute non-free programs (including commercial ones)      http://www.pyinstaller.org
pyparsing       2.3.0   MIT License     https://github.com/pyparsing/pyparsing/
pypubsub        4.0.0   BSD License     https://github.com/schollii/pypubsub
pyreadline      2.1     BSD     http://ipython.org/pyreadline.html
pyrsistent      0.14.11 MIT     http://github.com/tobgu/pyrsistent/
python-dateutil 2.7.5   Dual License    https://dateutil.readthedocs.io
python-easyconfig       0.1.7   MIT     https://github.com/RussellLuo/easyconfig
python-resources        0.3     BSD     https://github.com/doist/resources
pytz    2018.7  MIT     http://pythonhosted.org/pytz
pywin32 224     PSF     https://github.com/mhammond/pywin32
pywin32-ctypes  0.2.0   BSD     https://github.com/enthought/pywin32-ctypes
pyyaml  5.1     MIT     https://github.com/yaml/pyyaml
resource        0.2.1   MIT     https://github.com/RussellLuo/resource
scipy   1.2.1   BSD     https://www.scipy.org
setuptools      40.6.3  MIT License     https://github.com/pypa/setuptools
six     1.12.0  MIT     https://github.com/benjaminp/six
tornado 6.0.1   http://www.apache.org/licenses/LICENSE-2.0      http://www.tornadoweb.org/
wave    0.0.2   GNU Library or Lesser General Public License (LGPL)     http://packages.python.org/Wave/
wheel   0.32.3  MIT     https://github.com/pypa/wheel
wincertstore    0.2     PSFL    https://bitbucket.org/tiran/wincertstore
wxpython        4.0.3   wxWindows Library License (https://opensource.org/licenses/wxwindows.php)       http://wxPython.org/
"""