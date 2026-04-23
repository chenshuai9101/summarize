"""
文本处理器 - 负责文本预处理、清洗、标准化
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class TextProcessor:
    """文本处理器"""
    
    def __init__(self, config: Dict = None):
        """
        初始化文本处理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.processing_config = self.config.get('processing', {})
        
        # 初始化停用词
        self.stop_words = self._load_stop_words()
        
        logger.info("文本处理器初始化完成")
    
    def _load_stop_words(self) -> set:
        """加载停用词"""
        # 基础停用词（可扩展）
        stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一',
            '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着',
            '没有', '看', '好', '自己', '这', '那', '就', '但', '等', '与', '或',
            '而且', '或者', '然后', '因为', '所以', '如果', '虽然', '但是',
            'the', 'and', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'can', 'could', 'may', 'might', 'must', 'shall',
        }
        
        return stop_words
    
    def clean_text(self, text: str) -> str:
        """
        清洗文本
        
        Args:
            text: 原始文本
            
        Returns:
            清洗后的文本
        """
        try:
            if not text or not isinstance(text, str):
                return ""
            
            # 1. 移除多余空白字符
            text = re.sub(r'\s+', ' ', text)
            
            # 2. 移除特殊字符（保留基本标点）
            text = re.sub(r'[^\w\s.,!?;:()\"\'-]', ' ', text)
            
            # 3. 标准化标点
            text = re.sub(r'[。，；：！？]', lambda m: {
                '。': '.', '，': ',', '；': ';', '：': ':', '！': '!', '？': '?'
            }.get(m.group(0), m.group(0)), text)
            
            # 4. 移除URL
            text = re.sub(r'https?://\S+|www\.\S+', '', text)
            
            # 5. 移除邮箱
            text = re.sub(r'\S+@\S+\.\S+', '', text)
            
            # 6. 移除HTML标签
            text = re.sub(r'<[^>]+>', '', text)
            
            # 7. 标准化引号
            text = re.sub(r'["""\']', '"', text)
            
            # 8. 移除多余空格
            text = ' '.join(text.split())
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"文本清洗失败: {e}")
            return text if isinstance(text, str) else ""
    
    def split_sentences(self, text: str) -> List[str]:
        """
        分割句子
        
        Args:
            text: 文本内容
            
        Returns:
            句子列表
        """
        try:
            if not text:
                return []
            
            # 简单的句子分割（可改进为更智能的分割）
            # 基于标点符号分割
            sentences = re.split(r'[.!?。！？]+', text)
            
            # 清理和过滤
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # 移除过短的句子
            min_sentence_length = self.processing_config.get('min_sentence_length', 10)
            sentences = [s for s in sentences if len(s) >= min_sentence_length]
            
            return sentences
            
        except Exception as e:
            logger.error(f"句子分割失败: {e}")
            return [text] if text else []
    
    def tokenize(self, text: str, remove_stopwords: bool = True) -> List[str]:
        """
        分词
        
        Args:
            text: 文本内容
            remove_stopwords: 是否移除停用词
            
        Returns:
            词汇列表
        """
        try:
            if not text:
                return []
            
            # 简单的分词（可改进为更智能的分词）
            # 基于空格和标点分割
            tokens = re.findall(r'\b\w+\b', text.lower())
            
            if remove_stopwords:
                tokens = [t for t in tokens if t not in self.stop_words]
            
            return tokens
            
        except Exception as e:
            logger.error(f"分词失败: {e}")
            return []
    
    def calculate_text_metrics(self, text: str) -> Dict:
        """
        计算文本指标
        
        Args:
            text: 文本内容
            
        Returns:
            文本指标字典
        """
        try:
            if not text:
                return {
                    'char_count': 0,
                    'word_count': 0,
                    'sentence_count': 0,
                    'avg_sentence_length': 0,
                    'readability_score': 0,
                }
            
            # 字符数
            char_count = len(text)
            
            # 词汇数
            words = self.tokenize(text, remove_stopwords=False)
            word_count = len(words)
            
            # 句子数
            sentences = self.split_sentences(text)
            sentence_count = len(sentences)
            
            # 平均句子长度
            avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
            
            # 简单可读性分数（简化版）
            readability_score = self._calculate_readability(text, word_count, sentence_count)
            
            return {
                'char_count': char_count,
                'word_count': word_count,
                'sentence_count': sentence_count,
                'avg_sentence_length': round(avg_sentence_length, 2),
                'readability_score': round(readability_score, 2),
                'language_hint': self._detect_language_hint(text),
            }
            
        except Exception as e:
            logger.error(f"计算文本指标失败: {e}")
            return {
                'char_count': len(text) if text else 0,
                'word_count': 0,
                'sentence_count': 0,
                'avg_sentence_length': 0,
                'readability_score': 0,
            }
    
    def _calculate_readability(self, text: str, word_count: int, sentence_count: int) -> float:
        """计算可读性分数（简化版）"""
        try:
            if word_count == 0 or sentence_count == 0:
                return 0.0
            
            # 简单算法：基于平均句子长度和词汇复杂度
            avg_sentence_length = word_count / sentence_count
            
            # 计算长词比例（长度>6的词）
            words = self.tokenize(text, remove_stopwords=False)
            long_words = [w for w in words if len(w) > 6]
            long_word_ratio = len(long_words) / word_count if word_count > 0 else 0
            
            # 简化版可读性分数（0-100，越高越易读）
            readability = 100 - (avg_sentence_length * 2) - (long_word_ratio * 100)
            
            return max(0, min(100, readability))
            
        except Exception as e:
            logger.error(f"计算可读性失败: {e}")
            return 50.0  # 默认中等可读性
    
    def _detect_language_hint(self, text: str) -> str:
        """检测语言提示（简化版）"""
        try:
            if not text:
                return "unknown"
            
            # 简单基于字符的语言检测
            # 检查中文字符
            if re.search(r'[\u4e00-\u9fff]', text):
                return "zh"
            
            # 检查英文字符
            if re.search(r'[a-zA-Z]', text):
                return "en"
            
            # 其他语言（简化处理）
            return "other"
            
        except Exception as e:
            logger.error(f"语言检测失败: {e}")
            return "unknown"
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        提取关键词
        
        Args:
            text: 文本内容
            top_k: 返回关键词数量
            
        Returns:
            关键词和权重列表
        """
        try:
            if not text:
                return []
            
            # 分词（移除停用词）
            tokens = self.tokenize(text, remove_stopwords=True)
            
            if not tokens:
                return []
            
            # 计算词频
            from collections import Counter
            word_freq = Counter(tokens)
            
            # 计算TF（词频）权重
            total_words = len(tokens)
            keywords = []
            
            for word, freq in word_freq.items():
                # 简单TF权重
                tf = freq / total_words
                
                # 考虑词长（长词可能更重要）
                length_factor = min(2.0, len(word) / 5)
                
                # 综合权重
                weight = tf * length_factor
                keywords.append((word, weight))
            
            # 按权重排序
            keywords.sort(key=lambda x: x[1], reverse=True)
            
            return keywords[:top_k]
            
        except Exception as e:
            logger.error(f"提取关键词失败: {e}")
            return []
    
    def normalize_text(self, text: str, target_language: str = None) -> str:
        """
        标准化文本
        
        Args:
            text: 原始文本
            target_language: 目标语言
            
        Returns:
            标准化后的文本
        """
        try:
            if not text:
                return ""
            
            # 1. 清洗文本
            cleaned = self.clean_text(text)
            
            # 2. 分割句子
            sentences = self.split_sentences(cleaned)
            
            # 3. 标准化句子
            normalized_sentences = []
            
            for sentence in sentences:
                # 首字母大写
                if sentence and sentence[0].isalpha():
                    sentence = sentence[0].upper() + sentence[1:]
                
                # 确保句子以标点结束
                if sentence and sentence[-1] not in '.!?。！？':
                    sentence += '.'
                
                normalized_sentences.append(sentence)
            
            # 4. 重新组合
            normalized_text = ' '.join(normalized_sentences)
            
            # 5. 语言特定处理（简化版）
            if target_language == 'zh':
                # 中文特定处理
                normalized_text = re.sub(r'\s+', '', normalized_text)  # 移除空格
            elif target_language == 'en':
                # 英文特定处理
                normalized_text = re.sub(r'\s+', ' ', normalized_text)  # 标准化空格
            
            return normalized_text
            
        except Exception as e:
            logger.error(f"文本标准化失败: {e}")
            return text
    
    def batch_process(self, texts: List[str]) -> List[Dict]:
        """
        批量处理文本
        
        Args:
            texts: 文本列表
            
        Returns:
            处理结果列表
        """
        try:
            results = []
            
            for i, text in enumerate(texts):
                try:
                    # 清洗文本
                    cleaned = self.clean_text(text)
                    
                    # 计算指标
                    metrics = self.calculate_text_metrics(cleaned)
                    
                    # 提取关键词
                    keywords = self.extract_keywords(cleaned, top_k=5)
                    
                    # 标准化文本
                    normalized = self.normalize_text(cleaned)
                    
                    results.append({
                        'index': i,
                        'original_length': len(text),
                        'cleaned_length': len(cleaned),
                        'cleaned_text_preview': cleaned[:100] + '...' if len(cleaned) > 100 else cleaned,
                        'metrics': metrics,
                        'keywords': keywords,
                        'normalized_preview': normalized[:100] + '...' if len(normalized) > 100 else normalized,
                        'success': True,
                    })
                    
                except Exception as e:
                    logger.error(f"处理文本 {i} 失败: {e}")
                    results.append({
                        'index': i,
                        'error': str(e),
                        'success': False,
                    })
            
            logger.info(f"批量处理完成: {len([r for r in results if r['success']])}/{len(texts)} 成功")
            return results
            
        except Exception as e:
            logger.error(f"批量处理失败: {e}")
            return [{'error': str(e), 'success': False} for _ in texts]
    
    def get_processing_stats(self) -> Dict:
        """
        获取处理统计
        
        Returns:
            处理统计信息
        """
        return {
            'processor_version': '1.0.0',
            'stop_words_count': len(self.stop_words),
            'config': self.processing_config,
            'capabilities': {
                'text_cleaning': True,
                'sentence_splitting': True,
                'tokenization': True,
                'metrics_calculation': True,
                'keyword_extraction': True,
                'text_normalization': True,
                'batch_processing': True,
            },
        }
