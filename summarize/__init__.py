"""
Summarize - 企业级文本摘要平台

版本: 2.0.0
作者: 文本摘要·牧云野店
许可证: MIT
"""

__version__ = "2.0.0"
__author__ = "文本摘要·牧云野店"
__license__ = "MIT"

from .core.text_processor import TextProcessor
from .core.summary_generator import SummaryGenerator
from .core.language_detector import LanguageDetector
from .core.quality_evaluator import QualityEvaluator

from .interfaces.cli import main as cli_main
from .interfaces.api import SummarizeAPI

from .integrations.memory_enhancer_integration import MemoryEnhancerIntegration
from .integrations.file_system_integration import FileSystemIntegration
from .integrations.web_integration import WebIntegration

from .applications.content_summarizer import ContentSummarizer
from .applications.meeting_summarizer import MeetingSummarizer
from .applications.research_assistant import ResearchAssistant
from .applications.news_monitor import NewsMonitor

import json
import os
from pathlib import Path


class Summarizer:
    """摘要器主类"""
    
    def __init__(self, config_path=None):
        """
        初始化摘要器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        
        # 初始化核心组件
        self.text_processor = TextProcessor(self.config)
        self.summary_generator = SummaryGenerator(self.config)
        self.language_detector = LanguageDetector(self.config)
        self.quality_evaluator = QualityEvaluator(self.config)
        
        # 初始化集成组件
        self.memory_integration = None
        self.file_integration = None
        self.web_integration = None
        
        if self.config.get('integration', {}).get('memory_enhancer_enabled', False):
            self.memory_integration = MemoryEnhancerIntegration(self.config)
        
        if self.config.get('integration', {}).get('file_system_enabled', True):
            self.file_integration = FileSystemIntegration(self.config)
        
        if self.config.get('integration', {}).get('web_scraping_enabled', True):
            self.web_integration = WebIntegration(self.config)
        
        # 初始化应用组件
        self.content_summarizer = ContentSummarizer(self.config)
        self.meeting_summarizer = MeetingSummarizer(self.config)
        self.research_assistant = ResearchAssistant(self.config)
        self.news_monitor = NewsMonitor(self.config)
        
        print(f"Summarize v{__version__} 初始化完成")
    
    def _load_config(self, config_path):
        """加载配置"""
        default_config = {
            "processing": {
                "default_language": "auto",
                "default_length": "medium",
                "default_style": "formal",
                "max_input_length": 10000,
                "min_summary_length": 50,
                "max_summary_length": 500,
            },
            "models": {
                "default_model": "extractive",
                "extractive_model": "bert-extractive",
                "abstractive_model": "t5-small",
                "language_detection_model": "fasttext",
            },
            "performance": {
                "cache_enabled": True,
                "cache_size": 1000,
                "batch_size": 10,
                "max_workers": 4,
                "timeout_seconds": 30,
            },
            "integration": {
                "memory_enhancer_enabled": True,
                "memory_enhancer_path": str(Path.home() / ".openclaw" / "workspace" / "nexus"),
                "file_system_enabled": True,
                "web_scraping_enabled": True,
            },
            "api": {
                "enabled": True,
                "host": "0.0.0.0",
                "port": 8000,
                "rate_limit": 100,
                "auth_required": False,
            },
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 深度合并配置
                    self._deep_merge(default_config, user_config)
            except Exception as e:
                print(f"警告: 加载配置文件失败 {config_path}: {e}")
        
        return default_config
    
    def _deep_merge(self, base, update):
        """深度合并字典"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def summarize(self, text, length="medium", language="auto", style="formal", algorithm=None):
        """
        摘要文本
        
        Args:
            text: 输入文本
            length: 摘要长度
            language: 目标语言
            style: 摘要风格
            algorithm: 摘要算法
            
        Returns:
            摘要结果
        """
        try:
            # 处理文本
            processed_text = self.text_processor.clean_text(text)
            
            # 检测语言
            if language == "auto":
                lang_result = self.language_detector.detect(processed_text)
                language = lang_result.get('detected_language', 'unknown')
            
            # 生成摘要
            summary = self.summary_generator.summarize(
                text=processed_text,
                length=length,
                algorithm=algorithm,
            )
            
            # 评估质量
            evaluation = self.quality_evaluator.evaluate(summary, original_text=text)
            
            # 保存到记忆系统（如果启用）
            memory_id = None
            if self.memory_integration:
                memory_id = self.memory_integration.save_summary(
                    summary=summary,
                    original_text=text,
                    metadata={
                        "length": length,
                        "language": language,
                        "style": style,
                        "algorithm": algorithm or "default",
                    }
                )
            
            return {
                "success": True,
                "summary": summary,
                "language": language,
                "length": len(summary),
                "compression_ratio": round(len(summary) / len(text) if len(text) > 0 else 0, 3),
                "evaluation": evaluation,
                "memory_id": memory_id,
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text_length": len(text) if text else 0,
            }
    
    def summarize_url(self, url, length="medium", language="auto"):
        """
        摘要URL内容
        
        Args:
            url: 网页URL
            length: 摘要长度
            language: 目标语言
            
        Returns:
            摘要结果
        """
        try:
            if not self.web_integration:
                return {
                    "success": False,
                    "error": "网页集成未启用",
                }
            
            # 获取网页内容
            content_result = self.web_integration.fetch_url_content(url)
            if not content_result.get('success', False):
                return content_result
            
            content = content_result.get('content', '')
            
            # 摘要内容
            return self.summarize(content, length, language)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
            }
    
    def summarize_file(self, file_path, length="medium", language="auto"):
        """
        摘要文件内容
        
        Args:
            file_path: 文件路径
            length: 摘要长度
            language: 目标语言
            
        Returns:
            摘要结果
        """
        try:
            if not self.file_integration:
                return {
                    "success": False,
                    "error": "文件系统集成未启用",
                }
            
            # 读取文件内容
            content_result = self.file_integration.read_file(file_path)
            if not content_result.get('success', False):
                return content_result
            
            content = content_result.get('content', '')
            
            # 摘要内容
            result = self.summarize(content, length, language)
            result['file_path'] = file_path
            result['file_size'] = content_result.get('file_size', 0)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path,
            }
    
    def batch_summarize(self, texts, length="medium", language="auto"):
        """
        批量摘要
        
        Args:
            texts: 文本列表
            length: 摘要长度
            language: 目标语言
            
        Returns:
            批量摘要结果
        """
        try:
            results = []
            
            for i, text in enumerate(texts):
                result = self.summarize(text, length, language)
                result['index'] = i
                results.append(result)
            
            success_count = len([r for r in results if r.get('success', False)])
            
            return {
                "success": True,
                "total": len(texts),
                "success_count": success_count,
                "failed_count": len(texts) - success_count,
                "results": results,
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "total": len(texts),
                "success_count": 0,
                "failed_count": len(texts),
            }
    
    def detect_language(self, text, detailed=False):
        """
        检测语言
        
        Args:
            text: 输入文本
            detailed: 是否返回详细结果
            
        Returns:
            语言检测结果
        """
        return self.language_detector.detect(text, detailed)
    
    def evaluate_summary(self, summary, reference=None, original_text=None):
        """
        评估摘要质量
        
        Args:
            summary: 生成的摘要
            reference: 参考摘要
            original_text: 原始文本
            
        Returns:
            评估结果
        """
        return self.quality_evaluator.evaluate(summary, reference, original_text)
    
    def get_stats(self):
        """
        获取统计信息
        
        Returns:
            统计信息
        """
        return {
            "version": __version__,
            "config": {
                "processing": self.config.get('processing', {}),
                "models": self.config.get('models', {}),
                "integration": {
                    "memory_enhancer_enabled": self.memory_integration is not None,
                    "file_system_enabled": self.file_integration is not None,
                    "web_scraping_enabled": self.web_integration is not None,
                },
            },
            "component_stats": {
                "text_processor": self.text_processor.get_processing_stats(),
                "summary_generator": self.summary_generator.get_generator_stats(),
                "language_detector": self.language_detector.get_supported_languages(),
                "quality_evaluator": self.quality_evaluator.get_evaluator_stats(),
            },
        }


__all__ = [
    "Summarizer",
    "TextProcessor",
    "SummaryGenerator",
    "LanguageDetector",
    "QualityEvaluator",
    "MemoryEnhancerIntegration",
    "FileSystemIntegration",
    "WebIntegration",
    "ContentSummarizer",
    "MeetingSummarizer",
    "ResearchAssistant",
    "NewsMonitor",
    "cli_main",
    "SummarizeAPI",
]
