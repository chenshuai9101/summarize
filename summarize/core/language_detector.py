"""
语言检测器 - 负责语言检测和翻译
"""

import logging
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class LanguageDetector:
    """语言检测器"""
    
    def __init__(self, config: Dict = None):
        """
        初始化语言检测器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.models_config = self.config.get('models', {})
        
        # 语言代码映射
        self.language_codes = {
            'zh': '中文',
            'en': '英文',
            'ja': '日文',
            'ko': '韩文',
            'fr': '法文',
            'de': '德文',
            'es': '西班牙文',
            'ru': '俄文',
            'ar': '阿拉伯文',
            'pt': '葡萄牙文',
        }
        
        # 语言特征（简化版）
        self.language_patterns = {
            'zh': r'[\u4e00-\u9fff]',  # 中文字符
            'en': r'[a-zA-Z]',         # 英文字母
            'ja': r'[\u3040-\u309f\u30a0-\u30ff]',  # 日文假名
            'ko': r'[\uac00-\ud7af]',  # 韩文字符
            'ar': r'[\u0600-\u06ff]',  # 阿拉伯字符
            'ru': r'[\u0400-\u04ff]',  # 西里尔字符
        }
        
        logger.info("语言检测器初始化完成")
    
    def detect(self, text: str, detailed: bool = False) -> Dict:
        """
        检测文本语言
        
        Args:
            text: 输入文本
            detailed: 是否返回详细结果
            
        Returns:
            语言检测结果
        """
        try:
            if not text or len(text.strip()) < 10:
                return {
                    'detected_language': 'unknown',
                    'confidence': 0.0,
                    'message': '文本过短，无法准确检测',
                }
            
            # 清理文本
            cleaned_text = self._clean_text(text)
            
            # 检测语言
            language_scores = self._calculate_language_scores(cleaned_text)
            
            # 获取最高分语言
            if language_scores:
                best_language = max(language_scores.items(), key=lambda x: x[1])
                detected_lang = best_language[0]
                confidence = best_language[1]
            else:
                detected_lang = 'unknown'
                confidence = 0.0
            
            # 构建结果
            result = {
                'detected_language': detected_lang,
                'language_name': self.language_codes.get(detected_lang, '未知'),
                'confidence': round(confidence, 3),
                'text_length': len(text),
                'cleaned_length': len(cleaned_text),
            }
            
            if detailed:
                result['language_scores'] = {
                    lang: round(score, 3)
                    for lang, score in sorted(language_scores.items(), 
                                             key=lambda x: x[1], reverse=True)[:5]
                }
                result['language_hints'] = self._extract_language_hints(text)
                result['character_distribution'] = self._analyze_character_distribution(text)
            
            logger.info(f"语言检测完成: {detected_lang} (置信度: {confidence:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"语言检测失败: {e}")
            return {
                'detected_language': 'unknown',
                'confidence': 0.0,
                'error': str(e),
            }
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除数字、标点、多余空格
        cleaned = re.sub(r'[0-9\s\W_]+', ' ', text)
        cleaned = ' '.join(cleaned.split())
        return cleaned
    
    def _calculate_language_scores(self, text: str) -> Dict[str, float]:
        """计算语言分数"""
        if not text:
            return {}
        
        scores = {}
        total_chars = len(text)
        
        if total_chars == 0:
            return {}
        
        # 检查每种语言的特征字符
        for lang_code, pattern in self.language_patterns.items():
            matches = re.findall(pattern, text)
            match_count = len(matches)
            
            # 计算比例
            proportion = match_count / total_chars if total_chars > 0 else 0
            
            # 调整分数（考虑语言特定特征）
            if proportion > 0.1:  # 至少10%的字符匹配
                scores[lang_code] = proportion
            elif proportion > 0.01:  # 少量匹配
                scores[lang_code] = proportion * 0.5  # 降低置信度
        
        # 如果没有明显匹配，尝试基于词汇的方法
        if not scores:
            # 检查常见词汇
            lang_from_words = self._detect_from_common_words(text)
            if lang_from_words:
                scores[lang_from_words] = 0.3  # 较低置信度
        
        # 确保分数在0-1之间
        for lang in scores:
            scores[lang] = min(1.0, max(0.0, scores[lang]))
        
        return scores
    
    def _detect_from_common_words(self, text: str) -> Optional[str]:
        """从常见词汇检测语言"""
        # 常见词汇列表（简化版）
        common_words = {
            'en': {'the', 'and', 'you', 'that', 'have', 'for', 'not', 'with', 'this', 'but'},
            'zh': {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人'},
            'ja': {'の', 'に', 'は', 'を', 'が', 'で', 'た', 'し', 'て', 'と'},
            'ko': {'이', '가', '을', '를', '은', '는', '에', '에서', '으로', '의'},
            'fr': {'le', 'la', 'et', 'de', 'un', 'une', 'est', 'pour', 'que', 'dans'},
            'de': {'der', 'die', 'das', 'und', 'in', 'den', 'von', 'zu', 'mit', 'sich'},
        }
        
        text_lower = text.lower()
        word_counts = {}
        
        for lang, words in common_words.items():
            count = sum(1 for word in words if word in text_lower)
            if count > 0:
                word_counts[lang] = count
        
        if word_counts:
            # 返回出现次数最多的语言
            return max(word_counts.items(), key=lambda x: x[1])[0]
        
        return None
    
    def _extract_language_hints(self, text: str) -> List[str]:
        """提取语言提示"""
        hints = []
        
        # 检查字符范围
        if re.search(r'[\u4e00-\u9fff]', text):
            hints.append("包含中文字符")
        
        if re.search(r'[a-zA-Z]', text):
            hints.append("包含英文字母")
        
        if re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
            hints.append("包含日文假名")
        
        if re.search(r'[\uac00-\ud7af]', text):
            hints.append("包含韩文字符")
        
        # 检查标点使用
        if '。' in text or '，' in text:
            hints.append("使用中文标点")
        
        if '. ' in text or ', ' in text:
            hints.append("使用英文标点")
        
        # 检查常见短语
        common_phrases = {
            'zh': ['因为', '所以', '但是', '然后', '如果'],
            'en': ['because', 'therefore', 'however', 'then', 'if'],
            'ja': ['なぜなら', 'だから', 'しかし', 'それから', 'もし'],
        }
        
        for lang, phrases in common_phrases.items():
            for phrase in phrases:
                if phrase in text:
                    hints.append(f"包含{self.language_codes.get(lang, lang)}常见短语")
                    break
        
        return hints[:5]  # 最多返回5个提示
    
    def _analyze_character_distribution(self, text: str) -> Dict:
        """分析字符分布"""
        if not text:
            return {}
        
        distribution = {}
        total_chars = len(text)
        
        # 字符类型统计
        char_types = {
            'chinese': len(re.findall(r'[\u4e00-\u9fff]', text)),
            'latin': len(re.findall(r'[a-zA-Z]', text)),
            'digit': len(re.findall(r'[0-9]', text)),
            'punctuation': len(re.findall(r'[^\w\s]', text)),
            'space': len(re.findall(r'\s', text)),
            'other': total_chars - sum([
                len(re.findall(r'[\u4e00-\u9fff]', text)),
                len(re.findall(r'[a-zA-Z]', text)),
                len(re.findall(r'[0-9]', text)),
                len(re.findall(r'[^\w\s]', text)),
                len(re.findall(r'\s', text)),
            ]),
        }
        
        # 计算比例
        for char_type, count in char_types.items():
            if total_chars > 0:
                distribution[char_type] = {
                    'count': count,
                    'percentage': round(count / total_chars * 100, 2)
                }
        
        return distribution
    
    def translate(self, text: str, target_lang: str, source_lang: str = None) -> Dict:
        """
        翻译文本（简化版）
        
        Args:
            text: 输入文本
            target_lang: 目标语言
            source_lang: 源语言（自动检测如果未提供）
            
        Returns:
            翻译结果
        """
        try:
            if not text:
                return {
                    'success': False,
                    'error': '输入文本为空',
                }
            
            # 如果未提供源语言，自动检测
            if not source_lang:
                detection_result = self.detect(text)
                source_lang = detection_result.get('detected_language', 'unknown')
                source_confidence = detection_result.get('confidence', 0.0)
            else:
                source_confidence = 1.0
            
            # 简化版翻译（实际应该使用翻译API）
            # 这里返回模拟翻译结果
            translated_text = self._simulate_translation(text, source_lang, target_lang)
            
            result = {
                'success': True,
                'original_text': text,
                'translated_text': translated_text,
                'source_language': source_lang,
                'target_language': target_lang,
                'source_confidence': source_confidence,
                'translation_length': len(translated_text),
                'note': '这是简化版翻译，实际应使用专业翻译服务',
            }
            
            logger.info(f"翻译完成: {source_lang} -> {target_lang}, 长度: {len(text)} -> {len(translated_text)}")
            return result
            
        except Exception as e:
            logger.error(f"翻译失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'original_text': text,
                'source_language': source_lang,
                'target_language': target_lang,
            }
    
    def _simulate_translation(self, text: str, source_lang: str, target_lang: str) -> str:
        """模拟翻译（简化版）"""
        # 在实际应用中应该使用真正的翻译API
        # 这里返回带标记的模拟翻译
        
        if source_lang == target_lang:
            return text  # 相同语言，无需翻译
        
        # 模拟翻译标记
        translation_markers = {
            ('zh', 'en'): '[Translated to English] ',
            ('en', 'zh'): '[翻译成中文] ',
            ('ja', 'en'): '[Translated from Japanese] ',
            ('ko', 'en'): '[Translated from Korean] ',
            ('fr', 'en'): '[Translated from French] ',
            ('de', 'en'): '[Translated from German] ',
            ('es', 'en'): '[Translated from Spanish] ',
            ('ru', 'en'): '[Translated from Russian] ',
        }
        
        marker = translation_markers.get((source_lang, target_lang), f'[Translated from {source_lang} to {target_lang}] ')
        
        # 返回带标记的文本（简化版）
        return marker + text[:100] + "..." if len(text) > 100 else text
    
    def batch_detect(self, texts: List[str]) -> List[Dict]:
        """
        批量语言检测
        
        Args:
            texts: 文本列表
            
        Returns:
            检测结果列表
        """
        try:
            results = []
            
            for i, text in enumerate(texts):
                try:
                    detection_result = self.detect(text, detailed=True)
                    detection_result['index'] = i
                    detection_result['original_length'] = len(text)
                    detection_result['success'] = True
                    
                    results.append(detection_result)
                    
                except Exception as e:
                    logger.error(f"批量检测文本 {i} 失败: {e}")
                    results.append({
                        'index': i,
                        'error': str(e),
                        'success': False,
                    })
            
            success_count = len([r for r in results if r['success']])
            logger.info(f"批量语言检测完成: {success_count}/{len(texts)} 成功")
            return results
            
        except Exception as e:
            logger.error(f"批量语言检测失败: {e}")
            return [{'error': str(e), 'success': False} for _ in texts]
    
    def get_supported_languages(self) -> Dict:
        """
        获取支持的语言
        
        Returns:
            支持的语言信息
        """
        return {
            'supported_languages': list(self.language_codes.keys()),
            'language_names': self.language_codes,
            'detection_methods': ['character_pattern', 'common_words', 'punctuation'],
            'translation_capabilities': {
                'simulated_translation': True,
                'real_translation': False,  # 需要集成真正翻译API
                'batch_processing': True,
            },
            'detector_version': '1.0.0',
        }
    
    def validate_language_code(self, lang_code: str) -> bool:
        """
        验证语言代码
        
        Args:
            lang_code: 语言代码
            
        Returns:
            是否有效
        """
        return lang_code in self.language_codes
    
    def get_language_info(self, lang_code: str) -> Dict:
        """
        获取语言信息
        
        Args:
            lang_code: 语言代码
            
        Returns:
            语言信息
        """
        if lang_code not in self.language_codes:
            return {
                'valid': False,
                'error': f'不支持的语言代码: {lang_code}',
            }
        
        return {
            'valid': True,
            'code': lang_code,
            'name': self.language_codes[lang_code],
            'detectable': lang_code in self.language_patterns,
            'has_translation': lang_code in ['zh', 'en', 'ja', 'ko', 'fr', 'de', 'es', 'ru'],
            'character_example': self._get_character_example(lang_code),
        }
    
    def _get_character_example(self, lang_code: str) -> str:
        """获取字符示例"""
        examples = {
            'zh': '中文示例',
            'en': 'English example',
            'ja': '日本語の例',
            'ko': '한국어 예시',
            'fr': 'Exemple français',
            'de': 'Deutsches Beispiel',
            'es': 'Ejemplo español',
            'ru': 'Русский пример',
            'ar': 'مثال عربي',
            'pt': 'Exemplo português',
        }
        
        return examples.get(lang_code, 'No example available')
