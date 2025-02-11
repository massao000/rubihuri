import MeCab
import re
import jaconv
from kanjize import number2kanji
from pykakasi import kakasi
from typing import List
from enum import Enum, auto


class CharacterType(Enum):
    """ルビを振る文字種の設定用列挙型"""
    HALF_WIDTH = "half"  # 半角のみ
    BOTH_WIDTH = "both"  # 半角・全角両方
    
    def __str__(self):
        return self.value
    
class Rubihuri:
    """日本語テキストの読み方と発音を変換するクラス
    漢字、数字、ローマ字に対してルビを振ることができます。
    読みが「*」の場合は元のテキストを使用します。
    """

    # 文字種のパターン定義
    PATTERNS = {
        'numbers_half': '0-9',
        'numbers_full': '０-９',
        'alphabet_half': 'a-zA-Z',
        'alphabet_full': 'ａ-ｚＡ-Ｚ',
        'kanji': r'\u4e00-\u9fff'
    }

    # TODO:空白がある場合、空白を削除する
    def __init__(
        self,
        dic_path: str = '',
        left_brace="{",
        right_brace="}",
        left_delimiter="<",
        right_delimiter=">",
        char_type: CharacterType = "both" # デフォルトは半角・全角両方
    ):
        """
        Args:
            dic_path: MeCab辞書のパス
            left_brace: 漢字を囲む左括弧
            right_brace: 漢字を囲む右括弧
            left_delimiter: 読み/発音を囲む左記号
            right_delimiter: 読み/発音を囲む右記号
            har_type: 文字種の設定 ("half"=半角のみ or "both"=半角・全角)
        """
        if char_type not in [CharacterType.HALF_WIDTH.value, CharacterType.BOTH_WIDTH.value]:
            raise ValueError(f"char_type must be either '{CharacterType.HALF_WIDTH.value}' or '{CharacterType.BOTH_WIDTH.value}'")
            
        self.braces = (left_brace, right_brace)
        self.delimiters = (left_delimiter, right_delimiter)
        self.char_type = char_type
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

    def _get_pattern(self) -> str:
        """現在の設定に基づいて正規表現パターンを生成"""
        patterns = [self.PATTERNS['kanji']]  # 漢字は常に対象
        
        # 数字とアルファベットのパターンを追加
        if self.char_type == CharacterType.BOTH_WIDTH.value:
            patterns.extend([
                self.PATTERNS['numbers_half'],
                self.PATTERNS['numbers_full'],
                self.PATTERNS['alphabet_half'],
                self.PATTERNS['alphabet_full']
            ])
        else:  # HALF_WIDTH(half)
            patterns.extend([
                self.PATTERNS['numbers_half'],
                self.PATTERNS['alphabet_half']
            ])
        
        return f"[{''.join(patterns)}]"
        
    def _needs_ruby(self, text: str) -> bool:
        """ルビが必要かどうかを判定
        
        設定された文字種に基づいて判定を行う:
        - 漢字 (常に対象)
        - 数字 (半角 or 半角・全角)
        - アルファベット (半角 or 半角・全角)
        """
        pattern = self._get_pattern()
        return bool(re.search(pattern, text))

    def _get_fallback_reading(self, parsed_token: List[str]) -> str:
        """読みがない場合の代替テキストを取得
        """
        kks = kakasi()
        
        if re.search(r'[0-9]', parsed_token[0]):
            x = number2kanji(parsed_token[0])
            hiragana_text = ''.join([word['hira'] for word in kks.convert(x)])
            return hiragana_text
            
        if parsed_token[0] != "*":
            return parsed_token[0]
        
        return "*"


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
            if self._needs_ruby(parsed[0]):
                reading = parsed[reading_index]
                
                # 読みや発音が「*」の場合の処理
                if reading == "*":
                    reading = self._get_fallback_reading(parsed)
                    
                if to_hiragana:
                    reading = jaconv.kata2hira(reading)
                else:
                    reading = jaconv.hira2kata(reading)
                result.append(self._format_reading(parsed[-0], reading))
            else:
                result.append(parsed[0])

        return "".join(result)
    
    def yomi_hiragana(self, sentence: str) -> str:
        """漢字・数字・ローマ字の読みをひらがなで表示"""
        return self._convert_text(sentence, -2, to_hiragana=True)

    def yomi_katakana(self, sentence: str) -> str:
        """漢字・数字・ローマ字の読みをカタカナで表示"""
        return self._convert_text(sentence, -2, to_hiragana=False)

    def hatuon_hiragana(self, sentence: str) -> str:
        """漢字・数字・ローマ字の発音をひらがなで表示"""
        return self._convert_text(sentence, -1, to_hiragana=True)

    def hatuon_katakana(self, sentence: str) -> str:
        """漢字・数字・ローマ字の発音をカタカナで表示"""
        return self._convert_text(sentence, -1, to_hiragana=False)
    
    def set_character_type(self, char_type: CharacterType) -> None:
        """文字種の設定を変更
        
        Args:
            char_type: 新しい文字種設定 ("half"=半角のみ or "both"=半角・全角)
        """
        if char_type not in [CharacterType.HALF_WIDTH.value, CharacterType.BOTH_WIDTH.value]:
            raise ValueError(f"char_type must be either '{CharacterType.HALF_WIDTH.value}' or '{CharacterType.BOTH_WIDTH.value}'")
        self.char_type = char_type