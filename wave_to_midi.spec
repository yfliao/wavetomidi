# -*- mode: python -*-

block_cipher = None
import sys
sys.setrecursionlimit(10000)

a = Analysis(['wave_to_midi_stft.py'],
             pathex=['C:\\Users\\NASIMA\\Desktop\\pianofftindex'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          Tree('output',prefix='output'),
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='WaveToMidi',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False,
          icon='frame.ico')
