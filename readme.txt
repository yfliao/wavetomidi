"""
�g�p��̒���
�E���͂���file�̖��O�́Cspace���܂߂Ȃ����p�p������p���Ă��������D
�E�u./input�vfolder�ɁC���k���Ă��Ȃ�wavefile�i.wav�j�����Ă���Q�Ƃ��Ă��������D
�Efile size�̑傫��wavefile��ϊ�����ہCmemory�e�ʂ��s������ꍇ������܂��D�\�ߍׂ��������ď�������Ɖ������܂��D
�EMIDIfile��velocity�̑傫����4��track�ɕ����ďo�͂���܂��D
�ESauce code�́u./pianofftindex/wave_to_midi_stft.py�v�ɋL�ڂ���Ă��܂��D
"""
"""
�p��̐���
bpm:�@output����MIDIfile��bpm�����肷��D
beats:�@output����MIDIfile�̔��q�D
Export_measure_count:�@�����ߖ���output���邩�D(���o�[�W�����ł͋@�\�Ă��܂���D)
Output_file_name:�@output����MIDIfile�̖��O�D
Output_key_count:�@output����MIDIfile�̌��Ր��Ddefault��A0����J�E���g����88�D
Measure_split_rate:�@�ꏬ�߂����������邩�D�������́C�ꏬ�߂ɗp���鉹���̍ŏ��̒Z���D
Output_directly:�@output����ꏊ�Ddefault�́u./output�v�D
figure_ylim_value:�@�\������O���t��Y���͈̔́D���͒l-1�́C�ő�l�C�ŏ��l�����ꂼ��T���v�����O���g��/2�C0�Ƃ���D
figure_xlim_value:�@�\������O���t��x���͈̔́D���͒l-1�́C�ő�l�C�ŏ��l�����ꂼ�ꖖ�����ԁC0�Ƃ���D
Custom_STFT_resolution:�@STFT���s���ۂ�npersegment�����肷�邽�߂ɁCfrequency��������time�̕���\�����肷�邱�ƂŁC�����Е��̕���\�����肷��D
time(Custom_STFT_resolution):�@time��second(float)�œ��͂���D0�ȉ��œ��͂����ꍇ��0.01�ƂȂ�D
frequency(Custom_STFT_resolution):�@frequency��pitch(int)�œ��͂���D����\�͓��͂��ꂽ�l�ƁC���͂��ꂽ�l+1��pitch�������g���̍��Ō��肷��Ddefault��0(Bb0:29.135 - A0:27.500 = 2.135)�D
Velocity_rate:�@Velocity�����o���CMIDI_notes������ۂ̍Œ�l�DSMF�̋K�i��0~127��int�œ��͂���Ddefault��1�D
Velocity_range:�@Velocity�����o���CMIDI_notes������ۂ̕ω��̋��e�͈́D0~1��float�œ��͂���Ddefault��0.5�D
"""
"""
copyright(��)
����software�̍ĔЕz�y�юg�p�́C���̉ӏ������̏�����S�Ė������ꍇ�ɋ�����܂��D
�ΏۂƂȂ�software��Sauce code�`����binary�`�����͖₢�܂���D�܂��C���ς̗L�����₢�܂���D
�ESauce code�`���ōĔЕz����ꍇ�́C����license�̕��͑S�̂��c���K�v������܂��D
�Ebinary�`���ōĔЕz����ꍇ�́C����license�̕��͑S�̂����炩�̌`�Ŋ܂ޕK�v������܂��D
�E����software�̉��ϔł𕁋y�����邽�߂ɁC����software�̒��쌠�҂̖��O(��������contributor�̖��O)���y����Ɂz�g�p���Ă͂Ȃ�܂���D�g�p�������ꍇ�́C���O�ɏ��ʂɂ�鋖�𓾂�K�v������܂��D
�E����software�́C���쌠�҂�contributor�ɂ���āC����̂܂ܒ񋟂������̂Ƃ��܂��D�܂��C����software�͖��ۏ؂ł�����̂Ƃ��܂��D
�E���쌠�҂�contributor�́A�����Ȃ�ꍇ�ł���A�ǂ�ȑ��Q�����ɑ΂��Ă��A�ӔC�𕉂�Ȃ����̂Ƃ��܂��B
"""
"""
��������Ă���\��������Python-library�Ƃ���license�D
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