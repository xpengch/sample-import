# skills/log_parser/skill.py
import re
from typing import Dict, List
from core.skill import Skill, SkillResult
from core.context import Context

class LogParserSkill(Skill):
    """日志解析技能 - 使用纯规则解析"""

    @property
    def name(self) -> str:
        return "log_parser"

    def can_handle(self, context: Context) -> bool:
        return context.raw_log is not None and len(context.raw_log) > 0

    def execute(self, context: Context) -> SkillResult:
        """解析日志文件"""
        parsed = {
            "errors": [],
            "warnings": [],
            "info": [],
            "timestamps": [],
            "raw_lines": []
        }

        # 基本解析模式
        error_pattern = r'\[ERROR\]\s*(.+)'
        warn_pattern = r'\[WARN\]\s*(.+)'
        info_pattern = r'\[INFO\]\s*(.+)'
        timestamp_pattern = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})'

        for line in context.raw_log.split('\n'):
            line = line.strip()
            if not line:
                continue

            parsed["raw_lines"].append(line)

            # 提取时间戳
            ts_match = re.search(timestamp_pattern, line)
            if ts_match:
                parsed["timestamps"].append(ts_match.group(1))

            # 提取错误
            if '[ERROR]' in line:
                match = re.search(error_pattern, line)
                if match:
                    parsed["errors"].append({
                        "message": match.group(1),
                        "line": line
                    })

            # 提取警告
            elif '[WARN]' in line:
                match = re.search(warn_pattern, line)
                if match:
                    parsed["warnings"].append({
                        "message": match.group(1),
                        "line": line
                    })

            # 提取信息
            elif '[INFO]' in line:
                match = re.search(info_pattern, line)
                if match:
                    parsed["info"].append(match.group(1))

        context.parsed_data = parsed

        return SkillResult(
            success=True,
            data={
                "total_lines": len(parsed["raw_lines"]),
                "error_count": len(parsed["errors"]),
                "warning_count": len(parsed["warnings"]),
                "info_count": len(parsed["info"])
            }
        )
