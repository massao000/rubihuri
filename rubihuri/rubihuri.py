import MeCab
import re
import jaconv
from typing import List

class Rubihuri:
    """日本語テキストの読み方と発音を変換するクラス"""
    
    # TODO:空白がある場合、空白を削除する
    # TODO:{単語<読み>}ではなくルビふり（波カッコをなくすバージョン）に使えるように
    def __init__(self, dic_path: str = '', left_brace="{", right_brace="}", left_delimiter="<", right_delimiter=">"):
        """
        Args:
            dic_path: MeCab辞書のパス
            left_brace: 漢字を囲む左括弧
            right_brace: 漢字を囲む右括弧
            left_delimiter: 読み/発音を囲む左記号
            right_delimiter: 読み/発音を囲む右記号
        """
        self.braces = (left_brace, right_brace)
        self.delimiters = (left_delimiter, right_delimiter)
        self._initialize_tagger(dic_path)
    
    def _initialize_tagger(self, dic_path: str) -> None:
        """MeCab Taggerを初期化"""
        if not isinstance(dic_path, str):
            raise TypeError('dic_path must be str')
        
        mecab_option = f"-d {dic_path}" if dic_path else ''
        self.tagger = MeCab.Tagger(mecab_option)
    
    def parse(self, text: str) -> List[List[str]]:
        """テキストを形態素解析"""
        parsed = self.tagger.parse(text)
        return [re.split('[,\t]', p) for p in parsed.split("\n")][:-2]

    def _format_reading(self, original: str, reading: str) -> str:
        """漢字と読み/発音を指定フォーマットで結合"""
        left_brace, right_brace = self.braces
        left_delimiter, right_delimiter = self.delimiters
        return f"{left_brace}{original}{left_delimiter}{reading}{right_delimiter}{right_brace}"

    
    def _convert_text(self, sentence: str, reading_index: int, to_hiragana: bool = False) -> str:
        """テキストを変換
        
        Args:
            sentence: 変換する文章
            reading_index: 読みまたは発音のインデックス (-2: 読み, -1: 発音)
            to_hiragana: True=ひらがなに変換, False=カタカナのまま
        """
        parseds = self.parse(sentence)
        result = []
        
        for parsed in parseds:
            if re.search(r"[0-9\u4e00-\u9fff]", parsed[0]):
                reading = parsed[reading_index]
                if to_hiragana:
                    reading = jaconv.kata2hira(reading)
                result.append(self._format_reading(parsed[-3], reading))
            else:
                result.append(parsed[0])

        return "".join(result)
    
    def yomi_hiragana(self, sentence: str) -> str:
        """漢字の読みをひらがなで表示"""
        return self._convert_text(sentence, -2, to_hiragana=True)

    def yomi_katakana(self, sentence: str) -> str:
        """漢字の読みをカタカナで表示"""
        return self._convert_text(sentence, -2, to_hiragana=False)

    def hatuon_hiragana(self, sentence: str) -> str:
        """漢字の発音をひらがなで表示"""
        return self._convert_text(sentence, -1, to_hiragana=True)

    def hatuon_katakana(self, sentence: str) -> str:
        """漢字の発音をカタカナで表示"""
        return self._convert_text(sentence, -1, to_hiragana=False)