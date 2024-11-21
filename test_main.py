# モールス信号生成：実装サンプル

from morse_gen import MorseGen

if __name__ == "__main__":
    # クラスを生成。
    mg = MorseGen()

    # # (debug)波形の内容をダンプ。
    # f = open('D:/WORK/tone.txt', 'w')
    # for lv in mg.tone_l:
    #     f.write(str(lv) + '\n')
    # f.close()

    # 音声ストリームを開く。
    mg.stream_open()

    # 電文をモールス符号に変換。
    denbun = 'でんぶん　テスト わゐウヱｦ abc　ｉｒｏｈａ'
    m = mg.parse(denbun)
    print(denbun + ' -> ' + m)
    # モールス信号を発生させる。
    mg.gen_beep(m)

    # ※電文から直接モールス信号を発生させるコトも可能。
    # mg.exec('direct test.')

    # 音声ストリームを閉じる。
    mg.stream_close()
