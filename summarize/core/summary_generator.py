"""
摘要生成器 - 负责文本摘要生成
"""

import logging
from typing import Dict, List, Optional, Tuple
import re

logger = logging.getLogger(__name__)


class SummaryGenerator:
    """摘要生成器"""
    
    def __init__(self, config: Dict = None):
        """
        初始化摘要生成器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.models_config = self.config.get('models', {})
        
        # 摘要算法配置
        self.default_model = self.models_config.get('default_model', 'extractive')
        self.max_summary_length = self.config.get('processing', {}).get('max_summary_length', 200)
        self.min_summary_length = self.config.get('processing', {}).get('min_summary_length', 50)
        
        logger.info(f"摘要生成器初始化完成，默认模型: {self.default_model}")
    
    def summarize(self, text: str, length: str = "medium", 
                  algorithm: str = None, **kwargs) -> str:
        """
        生成摘要
        
        Args:
            text: 输入文本
            length: 摘要长度 (short/medium/long)
            algorithm: 摘要算法 (extractive/abstractive/mixed)
            **kwargs: 其他参数
            
        Returns:
            生成的摘要
        """
        try:
            if not text or len(text.strip()) < 50:
                logger.warning("输入文本过短，返回原文本")
                return text[:100] + "..." if len(text) > 100 else text
            
            # 确定算法
            algorithm = algorithm or self.default_model
            
            # 确定目标长度
            target_length = self._get_target_length(length, text)
            
            # 根据算法选择摘要方法
            if algorithm == "extractive":
                summary = self._extractive_summarize(text, target_length, **kwargs)
            elif algorithm == "abstractive":
                summary = self._abstractive_summarize(text, target_length, **kwargs)
            elif algorithm == "mixed":
                summary = self._mixed_summarize(text, target_length, **kwargs)
            else:
                logger.warning(f"未知算法 {algorithm}，使用默认提取式摘要")
                summary = self._extractive_summarize(text, target_length, **kwargs)
            
            # 后处理
            summary = self._postprocess_summary(summary, target_length)
            
            logger.info(f"摘要生成完成: 算法={algorithm}, 长度={len(summary)}字符")
            return summary
            
        except Exception as e:
            logger.error(f"摘要生成失败: {e}")
            # 返回简化版摘要
            return self._fallback_summary(text)
    
    def _get_target_length(self, length: str, text: str) -> int:
        """获取目标摘要长度"""
        text_length = len(text)
        
        length_ratios = {
            "short": 0.1,   # 10%
            "medium": 0.2,  # 20%
            "long": 0.3,    # 30%
        }
        
        ratio = length_ratios.get(length, 0.2)
        target_length = int(text_length * ratio)
        
        # 限制在最小和最大长度之间
        target_length = max(self.min_summary_length, 
                           min(self.max_summary_length, target_length))
        
        return target_length
    
    def _extractive_summarize(self, text: str, target_length: int, **kwargs) -> str:
        """提取式摘要"""
        try:
            # 简单实现：基于句子重要性评分
            
            # 分割句子
            sentences = self._split_into_sentences(text)
            
            if len(sentences) <= 3:
                # 句子太少，直接返回
                return ' '.join(sentences)
            
            # 计算句子重要性
            sentence_scores = []
            for i, sentence in enumerate(sentences):
                score = self._calculate_sentence_score(sentence, i, sentences)
                sentence_scores.append((sentence, score))
            
            # 按重要性排序
            sentence_scores.sort(key=lambda x: x[1], reverse=True)
            
            # 选择最重要的句子，直到达到目标长度
            selected_sentences = []
            current_length = 0
            
            for sentence, score in sentence_scores:
                sentence_length = len(sentence)
                if current_length + sentence_length <= target_length:
                    selected_sentences.append(sentence)
                    current_length += sentence_length
                else:
                    break
            
            # 按原始顺序重新排序
            selected_sentences = [s for s in sentences if s in selected_sentences]
            
            # 组合摘要
            summary = ' '.join(selected_sentences)
            
            return summary
            
        except Exception as e:
            logger.error(f"提取式摘要失败: {e}")
            return self._fallback_summary(text)
    
    def _abstractive_summarize(self, text: str, target_length: int, **kwargs) -> str:
        """生成式摘要（简化版）"""
        try:
            # 简化版生成式摘要
            # 实际应该使用预训练模型
            
            # 提取关键信息
            key_sentences = self._extractive_summarize(text, target_length * 2)
            
            # 重新组织和简化
            summary = self._simplify_text(key_sentences, target_length)
            
            return summary
            
        except Exception as e:
            logger.error(f"生成式摘要失败: {e}")
            # 回退到提取式摘要
            return self._extractive_summarize(text, target_length)
    
    def _mixed_summarize(self, text: str, target_length: int, **kwargs) -> str:
        """混合式摘要"""
        try:
            # 结合提取和生成
            extractive_part = self._extractive_summarize(text, target_length // 2)
            abstractive_part = self._abstractive_summarize(extractive_part, target_length // 2)
            
            # 组合
            summary = abstractive_part
            
            return summary
            
        except Exception as e:
            logger.error(f"混合式摘要失败: {e}")
            return self._extractive_summarize(text, target_length)
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """分割句子"""
        # 简单句子分割
        sentences = re.split(r'[.!?。！？]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def _calculate_sentence_score(self, sentence: str, index: int, all_sentences: List[str]) -> float:
        """计算句子重要性分数"""
        score = 0.0
        
        # 1. 位置权重（开头和结尾的句子通常更重要）
        total_sentences = len(all_sentences)
        if total_sentences > 0:
            position = index / total_sentences
            if position < 0.1 or position > 0.9:  # 开头10%或结尾10%
                score += 0.3
        
        # 2. 长度权重（中等长度的句子可能更重要）
        sentence_length = len(sentence)
        if 50 <= sentence_length <= 150:
            score += 0.2
        
        # 3. 关键词权重（包含数字、特定词汇）
        if re.search(r'\d+', sentence):  # 包含数字
            score += 0.1
        
        # 4. 疑问句或强调句
        if sentence.endswith('?') or sentence.endswith('？') or '!' in sentence or '！' in sentence:
            score += 0.1
        
        return score
    
    def _simplify_text(self, text: str, target_length: int) -> str:
        """简化文本"""
        # 简单文本简化
        # 移除冗余表达，简化句子结构
        
        sentences = self._split_into_sentences(text)
        
        if len(sentences) <= 1:
            return text
        
        # 取前几个句子，简化表达
        simplified_sentences = []
        for sentence in sentences[:3]:  # 最多取3个句子
            # 简化句子（移除修饰语等）
            simplified = self._simplify_sentence(sentence)
            simplified_sentences.append(simplified)
        
        # 组合
        simplified_text = ' '.join(simplified_sentences)
        
        # 如果还是太长，截断
        if len(simplified_text) > target_length:
            simplified_text = simplified_text[:target_length] + '...'
        
        return simplified_text
    
    def _simplify_sentence(self, sentence: str) -> str:
        """简化单个句子"""
        # 简单实现：移除一些修饰语
        
        # 移除一些常见的修饰短语（简化版）
        patterns_to_remove = [
            r'实际上，', r'事实上，', r'总的来说，', r'简而言之，',
            r'具体来说，', r'例如，', r'比如，', r'也就是说，',
        ]
        
        simplified = sentence
        for pattern in patterns_to_remove:
            simplified = re.sub(pattern, '', simplified)
        
        # 移除多余空格
        simplified = ' '.join(simplified.split())
        
        return simplified
    
    def _postprocess_summary(self, summary: str, target_length: int) -> str:
        """后处理摘要"""
        if not summary:
            return ""
        
        # 1. 确保摘要以句号结束
        if summary and summary[-1] not in '.!?。！？':
            summary += '.'
        
        # 2. 移除多余空格
        summary = ' '.join(summary.split())
        
        # 3. 确保摘要长度合适
        if len(summary) > target_length * 1.5:
            # 截断并添加省略号
            summary = summary[:target_length] + '...'
        
        return summary
    
    def _fallback_summary(self, text: str) -> str:
        """回退摘要（当其他方法失败时）"""
        if not text:
            return ""
        
        # 简单回退：取前100个字符
        if len(text) <= 150:
            return text
        
        # 取开头和结尾的一部分
        part1 = text[:75]
        part2 = text[-75:] if len(text) > 150 else ""
        
        if part2:
            return f"{part1}...{part2}"
        else:
            return part1 + "..."
    
    def batch_summarize(self, texts: List[str], length: str = "medium", 
                        algorithm: str = None) -> List[Dict]:
        """
        批量摘要
        
        Args:
            texts: 文本列表
            length: 摘要长度
            algorithm: 摘要算法
            
        Returns:
            摘要结果列表
        """
        try:
            results = []
            
            for i, text in enumerate(texts):
                try:
                    summary = self.summarize(text, length, algorithm)
                    
                    results.append({
                        'index': i,
                        'original_length': len(text),
                        'summary_length': len(summary),
                        'summary': summary,
                        'compression_ratio': round(len(summary) / len(text) if len(text) > 0 else 0, 3),
                        'success': True,
                    })
                    
                except Exception as e:
                    logger.error(f"批量摘要文本 {i} 失败: {e}")
                    results.append({
                        'index': i,
                        'error': str(e),
                        'success': False,
                    })
            
            success_count = len([r for r in results if r['success']])
            logger.info(f"批量摘要完成: {success_count}/{len(texts)} 成功")
            return results
            
        except Exception as e:
            logger.error(f"批量摘要失败: {e}")
            return [{'error': str(e), 'success': False} for _ in texts]
    
    def evaluate_summary(self, summary: str, reference: str = None, 
                        original_text: str = None) -> Dict:
        """
        评估摘要质量
        
        Args:
            summary: 生成的摘要
            reference: 参考摘要（可选）
            original_text: 原始文本（可选）
            
        Returns:
            评估结果
        """
        try:
            evaluation = {
                'summary_length': len(summary),
                'word_count': len(summary.split()),
                'sentence_count': len(self._split_into_sentences(summary)),
            }
            
            if reference:
                # 计算与参考摘要的相似度
                similarity = self._calculate_similarity(summary, reference)
                evaluation['reference_similarity'] = round(similarity, 3)
            
            if original_text:
                # 计算压缩比
                compression_ratio = len(summary) / len(original_text) if len(original_text) > 0 else 0
                evaluation['compression_ratio'] = round(compression_ratio, 3)
                
                # 计算信息覆盖率（简化版）
                coverage = self._calculate_coverage(summary, original_text)
                evaluation['information_coverage'] = round(coverage, 3)
            
            # 计算可读性（简化版）
            readability = self._calculate_readability(summary)
            evaluation['readability_score'] = round(readability, 3)
            
            # 总体评分
            overall_score = self._calculate_overall_score(evaluation)
            evaluation['overall_score'] = round(overall_score, 3)
            
            # 改进建议
            evaluation['suggestions'] = self._generate_suggestions(evaluation)
            
            return evaluation
            
        except Exception as e:
            logger.error(f"摘要评估失败: {e}")
            return {
                'error': str(e),
                'summary_length': len(summary) if summary else 0,
            }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（简化版）"""
        # 简单基于词汇重叠的相似度
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_coverage(self, summary: str, original: str) -> float:
        """计算信息覆盖率（简化版）"""
        # 基于关键词重叠的覆盖率
        from .text_processor import TextProcessor
        
        processor = TextProcessor()
        
        summary_keywords = [kw for kw, _ in processor.extract_keywords(summary, top_k=10)]
        original_keywords = [kw for kw, _ in processor.extract_keywords(original, top_k=20)]
        
        if not original_keywords:
            return 0.0
        
        covered_keywords = [kw for kw in summary_keywords if kw in original_keywords]
        
        return len(covered_keywords) / len(original_keywords) if original_keywords else 0.0
    
    def _calculate_readability(self, text: str) -> float:
        """计算可读性（简化版）"""
        # 基于句子长度和词汇复杂度的简单可读性
        sentences = self._split_into_sentences(text)
        
        if not sentences:
            return 0.0
        
        # 平均句子长度（词汇数）
        total_words = sum(len(s.split()) for s in sentences)
        avg_sentence_length = total_words / len(sentences)
        
        # 简单可读性公式
        readability = 100 - (avg_sentence_length * 3)
        
        return max(0, min(100, readability))
    
    def _calculate_overall_score(self, evaluation: Dict) -> float:
        """计算总体评分"""
        scores = []
        
        # 长度合理性（50-200字符为佳）
        length = evaluation.get('summary_length', 0)
        if 50 <= length <= 200:
            scores.append(0.9)
        elif 30 <= length < 50 or 200 < length <= 300:
            scores.append(0.7)
        else:
            scores.append(0.4)
        
        # 压缩比（0.1-0.3为佳）
        compression = evaluation.get('compression_ratio', 0)
        if 0.1 <= compression <= 0.3:
            scores.append(0.9)
        elif 0.05 <= compression < 0.1 or 0.3 < compression <= 0.5:
            scores.append(0.7)
        else:
            scores.append(0.4)
        
        # 可读性
        readability = evaluation.get('readability_score', 0) / 100
        scores.append(readability)
        
        # 信息覆盖率
        coverage = evaluation.get('information_coverage', 0)
        scores.append(coverage)
        
        # 平均分
        return sum(scores) / len(scores) if scores else 0.0
    
    def _generate_suggestions(self, evaluation: Dict) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        length = evaluation.get('summary_length', 0)
        compression = evaluation.get('compression_ratio', 0)
        readability = evaluation.get('readability_score', 0)
        coverage = evaluation.get('information_coverage', 0)
        
        if length < 50:
            suggestions.append("摘要过短，建议增加内容")
        elif length > 300:
            suggestions.append("摘要过长，建议精简内容")
        
        if compression < 0.05:
            suggestions.append("压缩比过低，摘要可能过于详细")
        elif compression > 0.5:
            suggestions.append("压缩比过高，可能丢失重要信息")
        
        if readability < 40:
            suggestions.append("可读性较低，建议简化句子结构")
        
        if coverage < 0.3:
            suggestions.append("信息覆盖率较低，建议包含更多关键信息")
        
        if not suggestions:
            suggestions.append("摘要质量良好，继续保持")
        
        return suggestions
    
    def get_generator_stats(self) -> Dict:
        """
        获取生成器统计
        
        Returns:
            生成器统计信息
        """
        return {
            'generator_version': '1.0.0',
            'default_model': self.default_model,
            'max_summary_length': self.max_summary_length,
            'min_summary_length': self.min_summary_length,
            'supported_algorithms': ['extractive', 'abstractive', 'mixed'],
            'supported_lengths': ['short', 'medium', 'long'],
            'capabilities': {
                'single_summary': True,
                'batch_summary': True,
                'summary_evaluation': True,
                'quality_suggestions': True,
            },
        }
