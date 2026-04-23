"""
质量评估器 - 负责摘要质量评估
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from collections import Counter

logger = logging.getLogger(__name__)


class QualityEvaluator:
    """质量评估器"""
    
    def __init__(self, config: Dict = None):
        """
        初始化质量评估器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.evaluation_config = self.config.get('evaluation', {})
        
        # 评估指标权重
        self.metric_weights = {
            'coherence': 0.25,
            'relevance': 0.25,
            'conciseness': 0.20,
            'readability': 0.15,
            'grammar': 0.15,
        }
        
        logger.info("质量评估器初始化完成")
    
    def evaluate(self, summary: str, reference: Optional[str] = None,
                original_text: Optional[str] = None) -> Dict:
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
            if not summary:
                return {
                    'success': False,
                    'error': '摘要为空',
                    'overall_score': 0.0,
                }
            
            evaluation = {
                'summary_length': len(summary),
                'word_count': len(summary.split()),
                'sentence_count': self._count_sentences(summary),
            }
            
            # 计算各项指标
            metrics = {}
            
            # 1. 连贯性
            metrics['coherence'] = self._evaluate_coherence(summary)
            
            # 2. 相关性（如果有原始文本）
            if original_text:
                metrics['relevance'] = self._evaluate_relevance(summary, original_text)
            else:
                metrics['relevance'] = 0.7  # 默认值
            
            # 3. 简洁性
            metrics['conciseness'] = self._evaluate_conciseness(summary, original_text)
            
            # 4. 可读性
            metrics['readability'] = self._evaluate_readability(summary)
            
            # 5. 语法正确性
            metrics['grammar'] = self._evaluate_grammar(summary)
            
            # 如果有参考摘要，计算相似度
            if reference:
                similarity = self._calculate_similarity(summary, reference)
                evaluation['reference_similarity'] = round(similarity, 3)
                metrics['similarity'] = similarity
            
            # 计算总体分数
            overall_score = self._calculate_overall_score(metrics)
            
            # 构建结果
            evaluation.update({
                'success': True,
                'metrics': {k: round(v, 3) for k, v in metrics.items()},
                'overall_score': round(overall_score, 3),
                'quality_level': self._get_quality_level(overall_score),
                'strengths': self._identify_strengths(metrics),
                'weaknesses': self._identify_weaknesses(metrics),
                'improvement_suggestions': self._generate_suggestions(metrics, summary),
            })
            
            logger.info(f"质量评估完成: 总体分数={overall_score:.3f}")
            return evaluation
            
        except Exception as e:
            logger.error(f"质量评估失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'summary_length': len(summary) if summary else 0,
                'overall_score': 0.0,
            }
    
    def _count_sentences(self, text: str) -> int:
        """计算句子数量"""
        sentences = re.split(r'[.!?。！？]+', text)
        return len([s for s in sentences if s.strip()])
    
    def _evaluate_coherence(self, summary: str) -> float:
        """评估连贯性"""
        try:
            sentences = self._split_into_sentences(summary)
            
            if len(sentences) <= 1:
                return 0.8  # 单句摘要通常连贯
            
            # 检查连接词使用
            connectors = ['而且', '并且', '然后', '接着', '因此', '所以', '但是', '然而',
                         'and', 'but', 'however', 'therefore', 'then', 'furthermore']
            
            connector_count = sum(1 for sentence in sentences 
                                 if any(connector in sentence for connector in connectors))
            
            # 检查指代一致性
            pronoun_coherence = self._check_pronoun_coherence(sentences)
            
            # 计算连贯性分数
            sentence_coherence = min(1.0, connector_count / len(sentences) * 2)
            coherence_score = (sentence_coherence + pronoun_coherence) / 2
            
            return max(0.0, min(1.0, coherence_score))
            
        except Exception as e:
            logger.error(f"连贯性评估失败: {e}")
            return 0.5
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """分割句子"""
        sentences = re.split(r'[.!?。！？]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _check_pronoun_coherence(self, sentences: List[str]) -> float:
        """检查指代一致性"""
        # 简化版指代一致性检查
        pronouns = ['它', '他', '她', '他们', '它们', '这个', '这些',
                   'it', 'he', 'she', 'they', 'this', 'these', 'that', 'those']
        
        pronoun_count = 0
        clear_reference_count = 0
        
        for sentence in sentences:
            for pronoun in pronouns:
                if pronoun in sentence:
                    pronoun_count += 1
                    # 简化检查：如果句子包含名词，认为指代清晰
                    if any(word.isalpha() and len(word) > 3 for word in sentence.split()):
                        clear_reference_count += 1
        
        if pronoun_count == 0:
            return 0.8  # 没有代词，一致性高
        
        return clear_reference_count / pronoun_count if pronoun_count > 0 else 0.5
    
    def _evaluate_relevance(self, summary: str, original_text: str) -> float:
        """评估相关性"""
        try:
            # 提取关键词
            summary_keywords = self._extract_keywords(summary, top_n=10)
            original_keywords = self._extract_keywords(original_text, top_n=20)
            
            if not original_keywords:
                return 0.5
            
            # 计算关键词重叠
            overlap = set(summary_keywords).intersection(set(original_keywords))
            relevance_score = len(overlap) / len(original_keywords)
            
            # 调整分数（考虑摘要长度）
            summary_ratio = len(summary) / len(original_text) if len(original_text) > 0 else 0
            if summary_ratio < 0.1:
                relevance_score *= 0.8  # 过短摘要可能丢失相关性
            elif summary_ratio > 0.5:
                relevance_score *= 0.9  # 过长摘要可能包含无关内容
            
            return max(0.0, min(1.0, relevance_score))
            
        except Exception as e:
            logger.error(f"相关性评估失败: {e}")
            return 0.5
    
    def _extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """提取关键词"""
        # 简单关键词提取（基于词频）
        words = re.findall(r'\b\w+\b', text.lower())
        
        # 过滤停用词
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
                     'the', 'and', 'a', 'an', 'in', 'on', 'at', 'to', 'for'}
        filtered_words = [w for w in words if w not in stop_words and len(w) > 1]
        
        # 计算词频
        word_freq = Counter(filtered_words)
        
        # 返回最常见的词
        return [word for word, _ in word_freq.most_common(top_n)]
    
    def _evaluate_conciseness(self, summary: str, original_text: Optional[str]) -> float:
        """评估简洁性"""
        try:
            if not original_text:
                # 没有原始文本，基于摘要自身评估
                sentences = self._split_into_sentences(summary)
                avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
                
                # 理想句子长度：10-20词
                if 10 <= avg_sentence_length <= 20:
                    return 0.9
                elif 5 <= avg_sentence_length < 10 or 20 < avg_sentence_length <= 30:
                    return 0.7
                else:
                    return 0.4
            
            # 有原始文本，基于压缩比评估
            compression_ratio = len(summary) / len(original_text) if len(original_text) > 0 else 0
            
            # 理想压缩比：0.1-0.3
            if 0.1 <= compression_ratio <= 0.3:
                return 0.9
            elif 0.05 <= compression_ratio < 0.1 or 0.3 < compression_ratio <= 0.5:
                return 0.7
            else:
                return 0.4
            
        except Exception as e:
            logger.error(f"简洁性评估失败: {e}")
            return 0.5
    
    def _evaluate_readability(self, summary: str) -> float:
        """评估可读性"""
        try:
            sentences = self._split_into_sentences(summary)
            
            if not sentences:
                return 0.5
            
            # 计算平均句子长度
            word_counts = [len(sentence.split()) for sentence in sentences]
            avg_sentence_length = sum(word_counts) / len(word_counts)
            
            # 计算长词比例
            words = ' '.join(sentences).split()
            long_words = [w for w in words if len(w) > 6]
            long_word_ratio = len(long_words) / len(words) if words else 0
            
            # 简单可读性公式
            readability = 100 - (avg_sentence_length * 3) - (long_word_ratio * 100)
            readability = max(0, min(100, readability))
            
            # 转换为0-1分数
            readability_score = readability / 100
            
            return readability_score
            
        except Exception as e:
            logger.error(f"可读性评估失败: {e}")
            return 0.5
    
    def _evaluate_grammar(self, summary: str) -> float:
        """评估语法正确性"""
        try:
            # 简化版语法检查
            
            sentences = self._split_into_sentences(summary)
            
            if not sentences:
                return 0.5
            
            error_count = 0
            total_checks = 0
            
            for sentence in sentences:
                # 检查1: 句子是否以大写字母开头（英文）
                if re.search(r'[a-zA-Z]', sentence):
                    if sentence and sentence[0].isalpha() and not sentence[0].isupper():
                        error_count += 1
                    total_checks += 1
                
                # 检查2: 是否有明显语法错误模式
                error_patterns = [
                    r'\s+\.',  # 空格后直接跟句号
                    r',\s*,',  # 连续逗号
                    r'\.\s*\.',  # 连续句号
                ]
                
                for pattern in error_patterns:
                    if re.search(pattern, sentence):
                        error_count += 1
                        total_checks += 1
            
            if total_checks == 0:
                return 0.7  # 没有检查项，返回中等分数
            
            error_ratio = error_count / total_checks
            grammar_score = 1.0 - error_ratio
            
            return max(0.0, min(1.0, grammar_score))
            
        except Exception as e:
            logger.error(f"语法评估失败: {e}")
            return 0.5
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        # 简单基于词汇重叠的相似度
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_overall_score(self, metrics: Dict) -> float:
        """计算总体分数"""
        weighted_sum = 0.0
        total_weight = 0.0
        
        for metric_name, score in metrics.items():
            weight = self.metric_weights.get(metric_name, 0.1)
            weighted_sum += score * weight
            total_weight += weight
        
        # 如果有相似度指标，额外考虑
        if 'similarity' in metrics:
            weighted_sum += metrics['similarity'] * 0.2
            total_weight += 0.2
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _get_quality_level(self, score: float) -> str:
        """获取质量等级"""
        if score >= 0.8:
            return "优秀"
        elif score >= 0.6:
            return "良好"
        elif score >= 0.4:
            return "一般"
        else:
            return "需要改进"
    
    def _identify_strengths(self, metrics: Dict) -> List[str]:
        """识别优势"""
        strengths = []
        
        if metrics.get('coherence', 0) >= 0.8:
            strengths.append("连贯性好")
        
        if metrics.get('relevance', 0) >= 0.8:
            strengths.append("相关性强")
        
        if metrics.get('conciseness', 0) >= 0.8:
            strengths.append("简洁明了")
        
        if metrics.get('readability', 0) >= 0.8:
            strengths.append("可读性高")
        
        if metrics.get('grammar', 0) >= 0.8:
            strengths.append("语法正确")
        
        if not strengths:
            # 如果没有明显优势，找相对较好的
            best_metric = max(metrics.items(), key=lambda x: x[1])
            if best_metric[1] >= 0.6:
                strengths.append(f"{best_metric[0]}表现较好")
        
        return strengths[:3]  # 最多返回3个优势
    
    def _identify_weaknesses(self, metrics: Dict) -> List[str]:
        """识别弱点"""
        weaknesses = []
        
        if metrics.get('coherence', 0) < 0.5:
            weaknesses.append("连贯性需要加强")
        
        if metrics.get('relevance', 0) < 0.5:
            weaknesses.append("相关性不足")
        
        if metrics.get('conciseness', 0) < 0.5:
            weaknesses.append("不够简洁")
        
        if metrics.get('readability', 0) < 0.5:
            weaknesses.append("可读性较低")
        
        if metrics.get('grammar', 0) < 0.5:
            weaknesses.append("语法需要改进")
        
        return weaknesses[:3]  # 最多返回3个弱点
    
    def _generate_suggestions(self, metrics: Dict, summary: str) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 基于弱点的建议
        if metrics.get('coherence', 0) < 0.6:
            suggestions.append("使用连接词改善句子连贯性")
        
        if metrics.get('relevance', 0) < 0.6:
            suggestions.append("确保摘要包含原文关键信息")
        
        if metrics.get('conciseness', 0) < 0.6:
            suggestions.append("删除冗余信息，使摘要更简洁")
        
        if metrics.get('readability', 0) < 0.6:
            suggestions.append("使用更简单的词汇和短句")
        
        if metrics.get('grammar', 0) < 0.6:
            suggestions.append("检查并修正语法错误")
        
        # 基于摘要特征的建议
        sentences = self._split_into_sentences(summary)
        if len(sentences) < 2:
            suggestions.append("考虑将摘要分为多个句子")
        elif len(sentences) > 5:
            suggestions.append("摘要可能过长，考虑精简")
        
        word_count = len(summary.split())
        if word_count < 30:
            suggestions.append("摘要可能过短，考虑增加关键信息")
        elif word_count > 200:
            suggestions.append("摘要可能过长，考虑删除次要信息")
        
        if not suggestions:
            suggestions.append("摘要质量良好，继续保持")
        
        return suggestions[:5]  # 最多返回5个建议
    
    def batch_evaluate(self, summaries: List[str], references: List[str] = None,
                      original_texts: List[str] = None) -> List[Dict]:
        """
        批量评估
        
        Args:
            summaries: 摘要列表
            references: 参考摘要列表（可选）
            original_texts: 原始文本列表（可选）
            
        Returns:
            评估结果列表
        """
        try:
            results = []
            
            for i, summary in enumerate(summaries):
                try:
                    reference = references[i] if references and i < len(references) else None
                    original = original_texts[i] if original_texts and i < len(original_texts) else None
                    
                    evaluation = self.evaluate(summary, reference, original)
                    evaluation['index'] = i
                    
                    results.append(evaluation)
                    
                except Exception as e:
                    logger.error(f"批量评估摘要 {i} 失败: {e}")
                    results.append({
                        'index': i,
                        'error': str(e),
                        'success': False,
                    })
            
            success_count = len([r for r in results if r.get('success', False)])
            logger.info(f"批量评估完成: {success_count}/{len(summaries)} 成功")
            return results
            
        except Exception as e:
            logger.error(f"批量评估失败: {e}")
            return [{'error': str(e), 'success': False} for _ in summaries]
    
    def compare_summaries(self, summaries: List[Dict]) -> Dict:
        """
        比较多个摘要
        
        Args:
            summaries: 摘要信息列表，每个元素包含'summary'和可选的'name'
            
        Returns:
            比较结果
        """
        try:
            if not summaries:
                return {
                    'success': False,
                    'error': '没有摘要可比较',
                }
            
            # 评估每个摘要
            evaluated_summaries = []
            for i, summary_info in enumerate(summaries):
                summary = summary_info.get('summary', '')
                name = summary_info.get('name', f'摘要_{i+1}')
                evaluation = self.evaluate(summary)
                evaluation['name'] = name
                evaluation['summary_preview'] = summary[:100] + '...' if len(summary) > 100 else summary
                evaluated_summaries.append(evaluation)
            
            # 找出最佳摘要
            valid_evaluations = [e for e in evaluated_summaries if e.get('success', False)]
            if valid_evaluations:
                best_summary = max(valid_evaluations, key=lambda x: x.get('overall_score', 0))
            else:
                best_summary = None
            
            # 构建比较结果
            comparison = {
                'success': True,
                'total_summaries': len(summaries),
                'valid_summaries': len(valid_evaluations),
                'summary_comparison': evaluated_summaries,
                'best_summary': best_summary,
                'metrics_comparison': self._compare_metrics(valid_evaluations),
                'recommendation': self._generate_comparison_recommendation(valid_evaluations),
            }
            
            logger.info(f"摘要比较完成: 比较了 {len(summaries)} 个摘要")
            return comparison
            
        except Exception as e:
            logger.error(f"摘要比较失败: {e}")
            return {
                'success': False,
                'error': str(e),
            }
    
    def _compare_metrics(self, evaluations: List[Dict]) -> Dict:
        """比较指标"""
        if not evaluations:
            return {}
        
        metrics_comparison = {}
        
        # 收集所有指标
        all_metrics = set()
        for eval_result in evaluations:
            if 'metrics' in eval_result:
                all_metrics.update(eval_result['metrics'].keys())
        
        # 比较每个指标
        for metric in all_metrics:
            metric_values = []
            for eval_result in evaluations:
                if 'metrics' in eval_result and metric in eval_result['metrics']:
                    metric_values.append({
                        'name': eval_result.get('name', '未知'),
                        'value': eval_result['metrics'][metric],
                        'overall_score': eval_result.get('overall_score', 0),
                    })
            
            if metric_values:
                # 找出最佳值
                best_value = max(metric_values, key=lambda x: x['value'])
                worst_value = min(metric_values, key=lambda x: x['value'])
                avg_value = sum(v['value'] for v in metric_values) / len(metric_values)
                
                metrics_comparison[metric] = {
                    'average': round(avg_value, 3),
                    'best': {
                        'name': best_value['name'],
                        'value': round(best_value['value'], 3),
                    },
                    'worst': {
                        'name': worst_value['name'],
                        'value': round(worst_value['value'], 3),
                    },
                    'range': round(best_value['value'] - worst_value['value'], 3),
                }
        
        return metrics_comparison
    
    def _generate_comparison_recommendation(self, evaluations: List[Dict]) -> Dict:
        """生成比较推荐"""
        if not evaluations:
            return {'message': '没有有效的摘要可推荐'}
        
        # 按总体分数排序
        sorted_evaluations = sorted(evaluations, key=lambda x: x.get('overall_score', 0), reverse=True)
        
        best = sorted_evaluations[0]
        worst = sorted_evaluations[-1]
        
        recommendation = {
            'best_summary': best.get('name', '最佳摘要'),
            'best_score': round(best.get('overall_score', 0), 3),
            'worst_summary': worst.get('name', '最差摘要'),
            'worst_score': round(worst.get('overall_score', 0), 3),
            'score_difference': round(best.get('overall_score', 0) - worst.get('overall_score', 0), 3),
            'key_differences': self._identify_key_differences(best, worst),
            'suggested_improvements': self._suggest_improvements_from_comparison(sorted_evaluations),
        }
        
        return recommendation
    
    def _identify_key_differences(self, best: Dict, worst: Dict) -> List[str]:
        """识别关键差异"""
        differences = []
        
        best_metrics = best.get('metrics', {})
        worst_metrics = worst.get('metrics', {})
        
        for metric in best_metrics:
            if metric in worst_metrics:
                diff = best_metrics[metric] - worst_metrics[metric]
                if diff > 0.2:  # 显著差异
                    differences.append(f"{metric}: {best.get('name')} 比 {worst.get('name')} 高 {diff:.2f}")
        
        return differences[:3]  # 最多返回3个关键差异
    
    def _suggest_improvements_from_comparison(self, evaluations: List[Dict]) -> List[str]:
        """从比较中提出改进建议"""
        if len(evaluations) < 2:
            return ["需要更多摘要进行比较分析"]
        
        suggestions = []
        
        # 分析每个指标的分布
        all_metrics = {}
        for eval_result in evaluations:
            for metric, value in eval_result.get('metrics', {}).items():
                if metric not in all_metrics:
                    all_metrics[metric] = []
                all_metrics[metric].append(value)
        
        # 找出需要改进的指标
        for metric, values in all_metrics.items():
            avg_value = sum(values) / len(values)
            if avg_value < 0.6:  # 平均分较低的指标
                suggestions.append(f"整体{metric}需要改进，平均分: {avg_value:.2f}")
        
        if not suggestions:
            suggestions.append("所有摘要质量都较好，继续保持")
        
        return suggestions[:3]  # 最多返回3个建议
    
    def get_evaluator_stats(self) -> Dict:
        """
        获取评估器统计
        
        Returns:
            评估器统计信息
        """
        return {
            'evaluator_version': '1.0.0',
            'evaluation_metrics': list(self.metric_weights.keys()),
            'metric_weights': self.metric_weights,
            'quality_levels': {
                '优秀': '>= 0.8',
                '良好': '0.6 - 0.8',
                '一般': '0.4 - 0.6',
                '需要改进': '< 0.4',
            },
            'capabilities': {
                'single_evaluation': True,
                'batch_evaluation': True,
                'summary_comparison': True,
                'improvement_suggestions': True,
            },
        }
