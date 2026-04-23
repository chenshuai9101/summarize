"""
CLI接口 - 命令行界面
"""

import argparse
import json
import sys
import logging
from typing import List, Dict, Optional
from pathlib import Path

from .. import Summarizer

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    """设置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )


def create_parser() -> argparse.ArgumentParser:
    """创建命令行解析器"""
    parser = argparse.ArgumentParser(
        description='Summarize CLI - 企业级文本摘要平台',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  summarize text "长文本内容..." --length medium
  summarize url https://example.com --language en
  summarize file document.txt --output summary.md
  summarize batch ./documents/ --format txt
  summarize detect "文本内容..." --detailed
        """
    )
    
    # 全局参数
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--version', action='store_true', help='显示版本')
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # text 命令
    text_parser = subparsers.add_parser('text', help='文本摘要')
    text_parser.add_argument('text', help='要摘要的文本')
    text_parser.add_argument('--length', '-l', choices=['short', 'medium', 'long'], 
                           default='medium', help='摘要长度')
    text_parser.add_argument('--language', '-lang', default='auto', help='目标语言')
    text_parser.add_argument('--style', '-s', choices=['formal', 'concise', 'bullet'],
                           default='formal', help='摘要风格')
    text_parser.add_argument('--algorithm', '-a', choices=['extractive', 'abstractive', 'mixed'],
                           help='摘要算法')
    text_parser.add_argument('--output', '-o', help='输出文件')
    
    # url 命令
    url_parser = subparsers.add_parser('url', help='URL摘要')
    url_parser.add_argument('url', help='网页URL')
    url_parser.add_argument('--length', '-l', choices=['short', 'medium', 'long'],
                          default='medium', help='摘要长度')
    url_parser.add_argument('--language', '-lang', default='auto', help='目标语言')
    url_parser.add_argument('--output', '-o', help='输出文件')
    
    # file 命令
    file_parser = subparsers.add_parser('file', help='文件摘要')
    file_parser.add_argument('file', help='文件路径')
    file_parser.add_argument('--length', '-l', choices=['short', 'medium', 'long'],
                           default='medium', help='摘要长度')
    file_parser.add_argument('--language', '-lang', default='auto', help='目标语言')
    file_parser.add_argument('--output', '-o', help='输出文件')
    
    # batch 命令
    batch_parser = subparsers.add_parser('batch', help='批量摘要')
    batch_parser.add_argument('input', help='输入目录或文件列表')
    batch_parser.add_argument('--output', '-o', required=True, help='输出目录')
    batch_parser.add_argument('--format', '-f', default='txt', 
                            choices=['txt', 'pdf', 'doc', 'md'], help='文件格式')
    batch_parser.add_argument('--recursive', '-r', action='store_true', help='递归处理')
    batch_parser.add_argument('--workers', '-w', type=int, default=4, help='工作线程数')
    
    # detect 命令
    detect_parser = subparsers.add_parser('detect', help='语言检测')
    detect_parser.add_argument('text', help='要检测的文本')
    detect_parser.add_argument('--detailed', '-d', action='store_true', help='详细输出')
    
    # evaluate 命令
    eval_parser = subparsers.add_parser('evaluate', help='摘要评估')
    eval_parser.add_argument('summary', help='要评估的摘要')
    eval_parser.add_argument('--reference', '-r', help='参考摘要')
    eval_parser.add_argument('--original', '-o', help='原始文本')
    
    # stats 命令
    stats_parser = subparsers.add_parser('stats', help='系统统计')
    
    # serve 命令
    serve_parser = subparsers.add_parser('serve', help='启动API服务')
    serve_parser.add_argument('--host', default='0.0.0.0', help='主机地址')
    serve_parser.add_argument('--port', '-p', type=int, default=8000, help='端口号')
    serve_parser.add_argument('--workers', '-w', type=int, default=4, help='工作进程数')
    
    return parser


def format_output(data, format_type='json'):
    """格式化输出"""
    if format_type == 'json':
        return json.dumps(data, indent=2, ensure_ascii=False)
    else:
        # 简单文本格式
        if isinstance(data, dict):
            lines = []
            for key, value in data.items():
                if isinstance(value, (list, dict)):
                    value = json.dumps(value, ensure_ascii=False)
                lines.append(f"{key}: {value}")
            return "\n".join(lines)
        elif isinstance(data, list):
            return "\n".join(str(item) for item in data)
        else:
            return str(data)


def handle_text(args, summarizer: Summarizer):
    """处理文本摘要命令"""
    result = summarizer.summarize(
        text=args.text,
        length=args.length,
        language=args.language,
        style=args.style,
        algorithm=args.algorithm,
    )
    
    # 保存到文件（如果指定）
    if args.output and result.get('success', False):
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result['summary'])
            result['output_file'] = args.output
        except Exception as e:
            result['output_error'] = str(e)
    
    return result


def handle_url(args, summarizer: Summarizer):
    """处理URL摘要命令"""
    result = summarizer.summarize_url(
        url=args.url,
        length=args.length,
        language=args.language,
    )
    
    # 保存到文件（如果指定）
    if args.output and result.get('success', False):
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result.get('summary', ''))
            result['output_file'] = args.output
        except Exception as e:
            result['output_error'] = str(e)
    
    return result


def handle_file(args, summarizer: Summarizer):
    """处理文件摘要命令"""
    result = summarizer.summarize_file(
        file_path=args.file,
        length=args.length,
        language=args.language,
    )
    
    # 保存到文件（如果指定）
    if args.output and result.get('success', False):
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result.get('summary', ''))
            result['output_file'] = args.output
        except Exception as e:
            result['output_error'] = str(e)
    
    return result


def handle_batch(args, summarizer: Summarizer):
    """处理批量摘要命令"""
    # 这里应该是实际的批量处理逻辑
    # 暂时返回模拟结果
    
    return {
        "success": True,
        "operation": "batch_summarize",
        "input": args.input,
        "output": args.output,
        "format": args.format,
        "recursive": args.recursive,
        "workers": args.workers,
        "note": "批量处理功能需要文件系统集成实现",
    }


def handle_detect(args, summarizer: Summarizer):
    """处理语言检测命令"""
    result = summarizer.detect_language(
        text=args.text,
        detailed=args.detailed,
    )
    
    return result


def handle_evaluate(args, summarizer: Summarizer):
    """处理摘要评估命令"""
    result = summarizer.evaluate_summary(
        summary=args.summary,
        reference=args.reference,
        original_text=args.original,
    )
    
    return result


def handle_stats(args, summarizer: Summarizer):
    """处理统计命令"""
    return summarizer.get_stats()


def handle_serve(args, summarizer: Summarizer):
    """处理服务命令"""
    # 这里应该是实际的API服务启动逻辑
    # 暂时返回模拟结果
    
    return {
        "success": True,
        "operation": "serve",
        "host": args.host,
        "port": args.port,
        "workers": args.workers,
        "note": "API服务功能需要Web框架集成实现",
        "api_endpoints": [
            "GET /api/v1/health",
            "POST /api/v1/summarize/text",
            "POST /api/v1/summarize/url",
            "POST /api/v1/summarize/file",
            "POST /api/v1/detect/language",
            "POST /api/v1/evaluate/summary",
        ],
    }


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.verbose)
    
    # 显示版本
    if args.version:
        from .. import __version__
        print(f"Summarize v{__version__}")
        return 0
    
    # 如果没有命令，显示帮助
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        # 初始化摘要器
        summarizer = Summarizer(config_path=args.config)
        
        # 处理命令
        handlers = {
            'text': handle_text,
            'url': handle_url,
            'file': handle_file,
            'batch': handle_batch,
            'detect': handle_detect,
            'evaluate': handle_evaluate,
            'stats': handle_stats,
            'serve': handle_serve,
        }
        
        if args.command in handlers:
            result = handlers[args.command](args, summarizer)
            print(format_output(result))
            
            # 返回适当的退出码
            return 0 if result.get('success', False) else 1
        else:
            print(f"未知命令: {args.command}")
            return 1
            
    except Exception as e:
        logger.error(f"命令执行失败: {e}")
        print(format_output({
            "success": False,
            "error": str(e),
        }))
        return 1


if __name__ == '__main__':
    sys.exit(main())
