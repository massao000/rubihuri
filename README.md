# rubihuri

日本語テキストに対して漢字の読み方や発音を自動的に付与するPythonライブラリです。

## インストール

**MeCab**と**mecab-ipadic-NEologd**（推奨辞書）のインストールが必要になります。

### Ubuntu の場合

MeCabのインストール
```
$ sudo apt install mecab libmecab-dev mecab-ipadic-utf8 git make curl xz-utils file
```

mecab-ipadic-NEologdのインストール
```
# 辞書元になるデータを GitHub からクローン
$ git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git

# クローン先のリポジトリに移動
$ cd mecab-ipadic-neologd

# 辞書のインストール
$ ./bin/install-mecab-ipadic-neologd -n -y
```

辞書のインストールされているパスの確認
```
$ echo `mecab-config --dicdir`"/mecab-ipadic-neologd"
```

[mecab-ipadic-NEologd 公式キュメント](https://github.com/neologd/mecab-ipadic-neologd/blob/master/README.ja.md#%E4%BE%8B-%E5%8B%95%E4%BD%9C%E3%81%AB%E5%BF%85%E8%A6%81%E3%81%AA%E3%83%A9%E3%82%A4%E3%83%96%E3%83%A9%E3%83%AA%E3%81%AE%E3%82%A4%E3%83%B3%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AB)

### Windowsの場合

mecab-python3 を使っているので**WindowsにMeCab本体**のインストールは不要です。

wslを使って mecab-ipadic-NEologd のインストール

> wslとはWindows上で簡単にLinuxを動かすためのものです。

[Microsoftのwslインストールドキュメント](https://learn.microsoft.com/ja-jp/windows/wsl/install#install-wsl-command)

PowerShellまたはコマンドプロンプトを管理者モードで開き以下のコマンドを実行。
```
wsl --install
```
インストール後、メッセージに従ってPCの再起動が必要になります。


再起動すると、ユーザ名の設定する必要があります。
設定すると以下の様にUbuntuにログインできます。
```
ユーザ名@DESKTOP-PJH30LR:
```

必要なパッケージのインストールをします。
```
$ sudo apt update
$ sudo apt upgrade
$ sudo apt install install make automake autoconf autotools-dev m4 mecab libmecab-dev mecab-ipadic-utf8 git make curl xz-utils file unzip
```

mecab-ipadic-NEologdのインストール
```
# 辞書元になるデータを GitHub からクローン
$ git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git

# クローン先のリポジトリに移動
$ cd mecab-ipadic-neologd

# 辞書のインストール
$ ./bin/install-mecab-ipadic-neologd -n -y
```

辞書のインストールされているパスの確認
```
$ echo `mecab-config --dicdir`"/mecab-ipadic-neologd"
```

windowの任意のドライブに辞書をコピーするディレクトリを新しく作ります。
エクスプローラでもコマンドでもどちらでも構いません。

例でコマンドでwindowのCドライブに dicmecab-ipadic-neologd ディレクトリを新しく作ります。

> **/mnt/c** はWindowsのCドライブを表します
```
$ mkdir /mnt/c/dicmecab-ipadic-neologd
```

先ほど作ったwindowのCドライブの dicmecab-ipadic-neologd に辞書をコピーします。
> /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd/ は辞書のインストール先の場所を確認して出てきたパスになります。
```
$ cp /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd/* /mnt/c/dicmecab-ipadic-neologd
```

以下のコマンドで Ubuntu を抜けることができます。
```
exit
```


### rubihuriのインストール

```bash
pip install rubihuri
```

## 使い方

### 基本的な使用方法
```py
from rubihuri import Rubihuri

# mecab-unidic-NEologd辞書を使用してRubihuriのインスタンスを作成
rubihuri = Rubihuri(dic_path="path/to/mecab-ipadic-neologd")  # パスは環境によって異なる場合があります

# テスト用のテキスト
text = "今日の天気は晴れのち雨でした。"

# ひらがなで読みを付与
result = rubihuri.yomi_hiragana(text)
print(result)
# {今日の天気<きょうのてんき>}は{晴れ<はれ>}のち{雨<あめ>}でした

# カタカナで読みを付与
result = rubihuri.yomi_katakana(text)
print(result)
# {今日の天気<キョウノテンキ>}は{晴れ<ハレ>}のち{雨<アメ>}でした

# ひらがなで発音を付与
result = rubihuri.hatuon_hiragana(text)
print(result)
# {今日の天気<きょーのてんき>}は{晴れ<はれ>}のち{雨<あめ>}でした

# カタカナで発音を付与
result = rubihuri.hatuon_katakana(text)
print(result)
# {今日の天気<キョーノテンキ>}は{晴れ<ハレ>}のち{雨<アメ>}でした
```

### カスタム設定

```py
from rubihuri import Rubihuri

rubihuri1 = Rubihuri(
    dic_path="path/to/mecab-ipadic-neologd",  # 辞書パス
    left_brace="",      # 漢字を囲む左括弧
    right_brace="",     # 漢字を囲む右括弧
    left_delimiter="(",  # 読み/発音を囲む左記号
    right_delimiter=")"  # 読み/発音を囲む右記号
)

text = "今日の天気は晴れのち雨でした。"
result = rubihuri1.yomi_hiragana(text)
print(result)
# 今日の天気(きょうのてんき)は晴れ(はれ)のち雨(あめ)でした。
```

char_typeを指定することで文字種の設定 ("half"=半角のみ or "both"=半角・全角)することができます。
デフォルトは both です。
```py
from rubihuri import Rubihuri

tagger = Rubihuri(
    dic_path="path/to/mecab-ipadic-neologd",  # 辞書パス
    char_type="half"
)

text = "ＰＣ２台とPC1台"
result = rubihuri1.yomi_hiragana(text)
print(result)
# ＰＣ２{台<だい>}と{P<ぴー>}{C1<しーわん>}{台<だい>}
```

## ライセンス

このプロジェクトのライセンスはMIT Licenseです。