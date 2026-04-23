# Summarize - 文本摘要技能

## 元数据

| 字段 | 值 |
|------|-----|
| **name** | summarize |
| **description** | 企业级文本摘要平台 - 多格式、多语言智能摘要，与Memory Enhancer深度集成 |
| **version** | 2.0.0 |
| **author** | 文本摘要·牧云野店 |
| **license** | MIT |
| **triggers** | 摘要,总结,概括,文本摘要,内容摘要 |

---

## 功能说明

Summarize 是一个专门为AI Agent设计的文本摘要平台，通过智能算法提供高质量的文本摘要服务。

### 核心功能

#### 1. 多格式输入支持
- **文本摘要**: 直接处理文本内容
- **URL摘要**: 自动抓取网页内容并摘要
- **文件处理**: 支持PDF、DOC、TXT等多种格式
- **音频转录**: 音频文件转录后摘要
- **视频处理**: 视频字幕提取和摘要

#### 2. 多语言摘要能力
- **语言检测**: 自动检测输入文本语言
- **多语言摘要**: 生成目标语言摘要
- **翻译集成**: 摘要内容跨语言翻译
- **语言优化**: 语言特定的摘要算法优化

#### 3. 智能摘要算法
- **提取式摘要**: 基于关键句子提取
- **生成式摘要**: 基于模型生成新摘要
- **混合算法**: 结合提取和生成的优势
- **领域自适应**: 针对不同领域优化

#### 4. 质量评估系统
- **自动评估**: ROUGE、BLEU等指标
- **人工评估**: 人工评估接口
- **质量反馈**: 基于反馈的算法优化
- **性能监控**: 摘要质量持续监控

### 技术特性

#### 架构设计
- **四层架构**: 核心引擎、接口层、集成层、应用层
- **模块化设计**: 各模块独立，易于维护和扩展
- **高性能设计**: 异步处理、缓存优化、批量处理
- **可靠设计**: 错误处理、数据备份、恢复机制

#### 性能优化
- **模型优化**: 模型压缩和量化
- **缓存机制**: 结果缓存提升性能
- **并行处理**: 支持多任务并行处理
- **资源管理**: 智能资源分配和管理

#### 安全考虑
- **数据安全**: 用户数据加密和保护
- **访问控制**: API密钥管理和限制
- **审计日志**: 完整的操作审计日志
- **隐私保护**: 用户隐私数据保护

### 使用场景

#### 1. 内容创作
- **文章摘要**: 长篇文章快速摘要
- **报告总结**: 业务报告和技术报告摘要
- **新闻摘要**: 新闻内容监控和摘要
- **博客摘要**: 博客文章内容摘要

#### 2. 学术研究
- **论文摘要**: 学术论文快速阅读
- **文献综述**: 研究文献摘要和整理
- **会议记录**: 学术会议内容摘要
- **研究笔记**: 研究笔记整理和摘要

#### 3. 企业应用
- **会议记录**: 企业会议记录摘要
- **文档管理**: 企业文档摘要和检索
- **客户反馈**: 客户反馈内容摘要
- **市场分析**: 市场报告和分析摘要

#### 4. 个人使用
- **学习笔记**: 学习内容摘要和整理
- **阅读助手**: 阅读材料快速摘要
- **知识管理**: 个人知识库内容摘要
- **信息整理**: 信息收集和整理摘要

## 快速开始

### 安装方式

#### 方式一：pip安装
```bash
pip install summarize
```

#### 方式二：源码安装
```bash
git clone https://github.com/chenshuai9101/summarize.git
cd summarize
pip install -e .
```

#### 方式三：开发环境
```bash
git clone https://github.com/chenshuai9101/summarize.git
cd summarize
pip install -e ".[dev]"
```

### 基础使用示例

#### Python API使用
```python
from summarize import Summarizer

# 初始化
summarizer = Summarizer(config_path="~/.summarize/config.json")

# 文本摘要
text = "这是一段需要摘要的长文本内容..."
summary = summarizer.summarize(
    text=text,
    length="medium",  # short/medium/long
    language="zh",    # 目标语言
    style="formal",   # 摘要风格
)

# URL摘要
url_summary = summarizer.summarize_url(
    url="https://example.com/article",
    max_length=200,
)

# 文件摘要
file_summary = summarizer.summarize_file(
    file_path="document.pdf",
    output_format="text",
)

# 批量处理
summarizer.batch_summarize(
    input_dir="./documents/",
    output_dir="./summaries/",
    file_pattern="*.pdf",
)
```

#### CLI工具使用
```bash
# 文本摘要
summarize text "长文本内容..." --length medium --output summary.txt

# URL摘要
summarize url https://example.com/article --language en --style concise

# 文件摘要
summarize file document.pdf --format markdown --keywords

# 批量处理
summarize batch ./input/ --recursive --output ./output/ --workers 4

# 语言检测
summarize detect "文本内容..." --detailed

# 质量评估
summarize evaluate summary.txt --reference reference.txt
```

#### API服务使用
```bash
# 启动服务
summarize serve --host 0.0.0.0 --port 8000 --workers 4

# API调用示例
# 文本摘要
curl -X POST http://localhost:8000/api/v1/summarize/text \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "text": "长文本内容...",
    "length": "medium",
    "language": "zh"
  }'

# URL摘要
curl -X POST http://localhost:8000/api/v1/summarize/url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "max_length": 150
  }'

# 批量摘要
curl -X POST http://localhost:8000/api/v1/summarize/batch \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf"
```

### 高级功能

#### 自定义摘要模型
```python
from summarize.core import SummaryGenerator

# 创建自定义模型
custom_model = SummaryGenerator(
    model_name="custom-model",
    model_path="./models/custom/",
    config={
        "max_length": 150,
        "min_length": 30,
        "temperature": 0.7,
    }
)

# 使用自定义模型
summary = custom_model.summarize(
    text=long_text,
    custom_prompt="请用简洁的语言摘要以下内容:",
)
```

#### 质量评估和优化
```python
from summarize.core import QualityEvaluator

# 创建质量评估器
evaluator = QualityEvaluator()

# 评估摘要质量
scores = evaluator.evaluate(
    summary=generated_summary,
    reference=reference_summary,
    metrics=["rouge", "bleu", "bertscore"]
)

# 获取改进建议
suggestions = evaluator.get_improvement_suggestions(
    summary=generated_summary,
    scores=scores,
    target_metrics={"rouge1": 0.8, "rouge2": 0.6}
)
```

#### 与Memory Enhancer集成
```python
from summarize.integrations import MemoryEnhancerIntegration

# 创建集成
memory_integration = MemoryEnhancerIntegration()

# 摘要保存到记忆系统
memory_id = memory_integration.save_summary(
    summary=summary,
    original_text=original_text,
    metadata={
        "source": "web_article",
        "language": "zh",
        "summary_length": len(summary),
    },
    tags=["摘要", "文章", "学习"],
)

# 从记忆系统检索相关摘要
related_summaries = memory_integration.search_related_summaries(
    query="相关主题",
    limit=10,
    min_relevance=0.7,
)
```

## 配置选项

### 配置文件
默认配置文件位置：`~/.summarize/config.json`

### 主要配置项
```json
{
  "processing": {
    "default_language": "auto",
    "default_length": "medium",
    "default_style": "formal",
    "max_input_length": 10000,
    "min_summary_length": 50,
    "max_summary_length": 500
  },
  "models": {
    "extractive_model": "bert-extractive",
    "abstractive_model": "t5-small",
    "language_detection_model": "fasttext",
    "translation_model": "opus-mt"
  },
  "performance": {
    "cache_enabled": true,
    "cache_size": 1000,
    "batch_size": 10,
    "max_workers": 4,
    "timeout_seconds": 30
  },
  "integration": {
    "memory_enhancer_enabled": true,
    "memory_enhancer_path": "~/.openclaw/workspace/nexus/",
    "file_system_enabled": true,
    "web_scraping_enabled": true
  },
  "api": {
    "enabled": true,
    "host": "0.0.0.0",
    "port": 8000,
    "rate_limit": 100,
    "auth_required": false
  }
}
```

### 环境变量
```bash
export SUMMARIZE_CONFIG_PATH="/path/to/config.json"
export SUMMARIZE_LOG_LEVEL="INFO"
export SUMMARIZE_CACHE_DIR="/tmp/summarize_cache"
export SUMMARIZE_API_KEY="your_api_key_here"
```

## 错误处理

### 常见错误及解决方案

#### 1. 输入处理错误
```
错误: 输入文本过长
解决方案:
  1. 分割文本为多个部分
  2. 增加max_input_length配置
  3. 使用批量处理模式
```

#### 2. 模型加载错误
```
错误: 无法加载摘要模型
解决方案:
  1. 检查模型文件是否存在
  2. 验证模型文件完整性
  3. 重新下载或训练模型
```

#### 3. 网络连接错误
```
错误: 无法访问URL内容
解决方案:
  1. 检查网络连接
  2. 验证URL可访问性
  3. 使用本地文件替代
```

#### 4. 内存不足错误
```
错误: 内存不足处理大文件
解决方案:
  1. 使用流式处理
  2. 增加系统内存
  3. 优化处理参数
```

### 调试模式
启用详细日志：
```bash
# 设置环境变量
export SUMMARIZE_DEBUG=1
export SUMMARIZE_LOG_LEVEL="DEBUG"

# 或使用命令行参数
summarize --debug text "查询内容"
```

## 最佳实践

### 摘要质量优化
1. **输入预处理**: 确保输入文本质量
2. **参数调优**: 根据内容调整摘要参数
3. **模型选择**: 根据需求选择合适的摘要模型
4. **后处理优化**: 对生成摘要进行后处理优化

### 性能优化
1. **缓存利用**: 合理配置和使用缓存
2. **批量处理**: 使用批量处理提升效率
3. **资源管理**: 合理分配和管理系统资源
4. **异步处理**: 使用异步接口处理大量请求

### 系统集成
1. **配置统一**: 统一管理系统配置
2. **数据同步**: 定期同步集成系统数据
3. **监控告警**: 设置系统监控和告警
4. **备份恢复**: 定期备份和测试恢复

## 扩展开发

### 插件系统
```python
from summarize.plugins import BasePlugin

class CustomPlugin(BasePlugin):
    name = "custom-plugin"
    
    def on_text_preprocess(self, text):
        """文本预处理时触发"""
        # 自定义预处理逻辑
        return processed_text
    
    def on_summary_generated(self, summary, original_text):
        """摘要生成时触发"""
        # 自定义后处理逻辑
        return enhanced_summary
```

### API扩展
```python
from summarize.api import extend_api

@extend_api
def custom_endpoint():
    """自定义API端点"""
    return {"status": "custom endpoint"}
```

### 模型扩展
```python
from summarize.models import BaseSummaryModel

class CustomModel(BaseSummaryModel):
    """自定义摘要模型"""
    
    def summarize(self, text, **kwargs):
        # 自定义摘要逻辑
        return summary
    
    def train(self, training_data):
        # 自定义训练逻辑
        pass
```

## 版本兼容性

### 向后兼容
Summarize 2.x 版本保持对1.x版本API的兼容性。

### 升级指南
从1.x升级到2.x：
```bash
# 1. 备份现有配置和数据
summarize backup --output ./backup_v1/

# 2. 安装新版本
pip install --upgrade summarize

# 3. 迁移配置
summarize migrate --from v1 --to v2

# 4. 验证功能
summarize test --all
```

## 支持与贡献

### 获取帮助
- **文档**: 查看本SKILL.md和README.md
- **示例**: 查看examples/目录
- **问题**: 使用GitHub Issues报告问题
- **讨论**: 参与社区讨论

### 贡献指南
欢迎所有形式的贡献：
1. 报告问题和建议
2. 提交代码改进
3. 添加新功能
4. 完善文档
5. 分享使用经验

### 开发计划
- [ ] 可视化摘要分析界面
- [ ] 更多语言模型支持
- [ ] 实时摘要流处理
- [ ] 移动端应用
- [ ] 云服务部署

---

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 更新日志

### v2.0.0 (2026-04-23)
- ✅ 完整商业化架构实现
- ✅ 多格式输入支持
- ✅ 多语言摘要能力
- ✅ 智能摘要算法
- ✅ 与Memory Enhancer深度集成
- ✅ 完整的API和CLI接口
- ✅ 企业级功能和安全
- ✅ 详细文档和示例

### v1.0.0 (2026-04-22)
- ✅ 基础文本摘要功能
- ✅ 简单命令行工具
- ✅ 基础文档和示例

---

**Summarize** - 让每个文本都拥有精炼的摘要！

*版本: 2.0.0 | 更新日期: 2026-04-23 | 作者: 文本摘要·牧云野店*
