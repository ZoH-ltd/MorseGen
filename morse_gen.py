#
# モールス信号生成
# 英文/和文に対応。
#

from morse_dict_def import MorseDictDef
import numpy as np
import scipy.signal
import pyaudio
import jaconv

class MorseGen():

    # サンプリング周波数
    SAMPLING_RATE = 44100
    # トーン長さ(sec)
    TONE_TIME = 0.033
    # 基本周波数(Hz)
    TONE_FREQ = 880
    CL = 72

    # オーディオストリーム
    morse_stream = None

    # トーン：短音
    tone_l = None
    # トーン：長音
    tone_h = None
    # 無音
    tone_n = None

    # 文字とモールス符号の変換テーブル
    MORSE_DICT = MorseDictDef.get_dict()


    # コンストラクタ
    def __init__(self):

        # サンプル点ごとの時間を生成。
        t_sh = np.arange(0, self.SAMPLING_RATE * self.TONE_TIME  ) / self.SAMPLING_RATE
        t_lg = np.arange(0, self.SAMPLING_RATE * self.TONE_TIME*3) / self.SAMPLING_RATE

        # トーン波形を生成。
        self.tone_l = self.get_tone_wave(self.TONE_FREQ, t_sh)
        self.tone_h = self.get_tone_wave(self.TONE_FREQ, t_lg)

        self.tone_n = np.zeros(self.tone_l.size * 2)

        # トーンの前後をまろやかにする(プチノイズ対策)。
        self.cut_wave_mod(self.tone_l)
        self.cut_wave_mod(self.tone_h)

    # トーン波形を生成する。
    #   freq       : トーン周波数
    #   time_array : サンプル点ごとの時間配列
    def get_tone_wave(self, freq, time_array):
        return np.sin(2 * np.pi * freq * time_array)
        # return scipy.signal.square(2 * np.pi * freq * time_array)
        # return scipy.signal.sawtooth(2 * np.pi * freq * time_array)

    # トーンの前後をまろやかにする(プチノイズ対策)。
    def cut_wave_mod(self, wave_array):
        for t in range(self.CL):
            d = (t/self.CL)
            wave_array[t] *= d
            wave_array[wave_array.size - 1 - t] *= d


    # オーディオストリームを開く。
    def stream_open(self):
        p = pyaudio.PyAudio()
        self.morse_stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.SAMPLING_RATE,
            frames_per_buffer=1024,
            output=True
        )

    # オーディオストリームを閉じる。
    def stream_close(self):
        if self.morse_stream != None:
            self.morse_stream.stop_stream()
            self.morse_stream.close()
            self.morse_stream = None


    # 電文を解釈し、モールス信号を発生する。
    def exec(self, denbun):
        morses = self.parse(denbun)
        self.gen_beep(morses)

    # 電文からモールス符号を取得する。
    def parse(self, denbun):
        morses = ''

        # かな文字を半角カナに変換(&全角英数字→ascii)。
        denbun = jaconv.z2h(jaconv.hira2hkata(denbun), kana=True, ascii=True, digit=True)
        # 英字を大文字に変換。
        denbun = denbun.upper()

        for word in list(denbun):
            if word in self.MORSE_DICT.keys():
                morses += self.MORSE_DICT[word]
            else:
                morses += ' '

        return morses

    # モールス信号を発生する。
    def gen_beep(self, morse):
        if self.morse_stream == None:
            self.stream_open()

        for tone in list(morse):
            if tone == '.':
                self.morse_stream.write(self.tone_l.astype(np.float32).tobytes())
            elif tone == '-':
                self.morse_stream.write(self.tone_h.astype(np.float32).tobytes())
            else:
                self.morse_stream.write(self.tone_n.astype(np.float32).tobytes())

            self.morse_stream.write(self.tone_n.astype(np.float32).tobytes())


if __name__ == "__main__":
    #-- TEST CODE ----------------
    mg = MorseGen()

    mg.stream_open()

    denbun = 'でんぶん　テスト わゐウヱｦ abc　ｉｒｏｈａ'
    # denbun = 'denbun TEST'
    m = mg.parse(denbun)
    print(denbun + ' -> ' + m)
    mg.gen_beep(m)

    mg.stream_close()
