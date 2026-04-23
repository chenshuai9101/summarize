# Summarize v2.0.0

> 企业级文本摘要平台 - 多格式、多语言智能摘要

## 🎯 项目概述

Summarize v2.0.0 是一个企业级文本摘要平台，提供多格式输入、多语言输出、智能摘要生成和完整API服务。与Memory Enhancer深度集成，为企业用户提供高质量的文本摘要解决方案。

## ✨ 核心特性

### 📝 多格式输入支持
- **文本输入**: 直接文本内容摘要
- **URL摘要**: 网页内容自动抓取和摘要
- **文件处理**: PDF、DOC、TXT等格式文件
- **音频转录**: 音频文件转录后摘要
- **视频字幕**: 视频字幕提取和摘要

### 🌍 多语言摘要能力
- **自动语言检测**: 支持100+种语言
- **多语言摘要**: 生成目标语言摘要
- **跨语言翻译**: 摘要内容跨语言翻译
- **语言优化**: 语言特定的摘要优化

### 🎨 可定制摘要
- **长度控制**: 短、中、长摘要可选
- **风格选择**: 正式、简洁、要点式摘要
- **关键词突出**: 自动提取和突出关键词
- **情感分析**: 集成情感分析功能

### 🏢 企业级功能
- **批量处理**: 支持大规模文件批量摘要
- **API服务**: 完整的REST API接口
- **用户管理**: 多用户支持和权限控制
- **质量评估**: 摘要质量自动评估系统

## 🚀 快速开始

### 安装
```bash
# 从源码安装
git clone https://github.com/chenshuai9101/summarize.git
cd summarize
pip install -e .
```

### 基础使用
```python
from summarize import Summarizer

# 创建摘要器
summarizer = Summarizer()

# 文本摘要
text = "这是一段需要摘要的长文本内容..."
summary = summarizer.summarize(text, length="medium")
print(f"摘要: {summary}")

# URL摘要
url_summary = summarizer.summarize_url("https://example.com/article")

# 文件摘要
file_summary = summarizer.summarize_file("document.pdf")
```

### CLI工具
```bash
# 文本摘要
summarize text "长文本内容..." --length medium

# URL摘要
summarize url https://example.com --output summary.txt

# 批量处理
summarize batch ./documents/ --format pdf

# 语言检测
summarize detect "文本内容..."
```

### API服务
```bash
# 启动API服务
summarize serve --port 8000

# API调用示例
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "长文本内容...", "length": "medium"}'
```

## 🏗️ 系统架构

```
Summarize v2.0.0
├── 核心引擎层 - 文本处理、摘要生成、语言检测、质量评估
├── 接口层 - CLI、API、Python SDK、Web界面
├── 集成层 - Memory Enhancer集成、文件系统、网络服务
└── 应用层 - 内容摘要、会议记录、研究助手、新闻监控
```

## 📚 文档

- [用户指南](docs/user_guide.md) - 完整使用说明
- [API参考](docs/api_reference.md) - 详细API文档
- [开发指南](docs/development.md) - 开发和贡献指南
- [集成指南](docs/integration.md) - 系统集成说明

## 🔧 技术要求

- Python 3.8+
- Memory Enhancer (可选，增强功能)
- 网络连接 (URL摘要功能)
- 音频处理库 (音频转录功能)

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交Issue和Pull Request！详见 [贡献指南](CONTRIBUTING.md)。

## 📞 支持

- GitHub Issues: [报告问题](https://github.com/chenshuai9101/summarize/issues)
- 文档: 查看本README和各文档文件
- 社区: 参与讨论和贡献

---

*版本: 2.0.0 | 状态: 开发中 | 最后更新: 2026-04-23*
