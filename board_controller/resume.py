"""断点续传管理"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path


class ResumeManager:
    """断点续传管理器

    管理测试过程的检查点，支持中断后恢复执行
    """

    def __init__(self, session_id: Optional[str] = None):
        """
        Args:
            session_id: 会话ID，如果不指定则自动生成
        """
        self.session_id = session_id or self._generate_session_id()
        self.checkpoint_dir = Path.home() / ".chip-fault-locator" / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def _generate_session_id(self) -> str:
        """生成会话ID"""
        return datetime.now().strftime('%Y%m%d-%H%M%S')

    def _get_checkpoint_file(self) -> Path:
        """获取检查点文件路径"""
        return self.checkpoint_dir / f"{self.session_id}.json"

    def save_checkpoint(
        self,
        checkpoint_id: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """保存检查点

        Args:
            checkpoint_id: 检查点ID
            data: 检查点数据
            metadata: 元数据（可选）

        Returns:
            是否保存成功
        """
        try:
            checkpoint = {
                "session_id": self.session_id,
                "checkpoint_id": checkpoint_id,
                "timestamp": datetime.now().isoformat(),
                "data": data,
                "metadata": metadata or {}
            }

            checkpoint_file = self._get_checkpoint_file()
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"保存检查点失败: {e}")
            return False

    def load_checkpoint(self, checkpoint_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """加载检查点

        Args:
            checkpoint_id: 检查点ID，如果为None则加载最新检查点

        Returns:
            检查点数据，如果不存在返回None
        """
        try:
            checkpoint_file = self._get_checkpoint_file()
            if not checkpoint_file.exists():
                return None

            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)

            # 如果指定了checkpoint_id，验证是否匹配
            if checkpoint_id is not None:
                if checkpoint.get("checkpoint_id") != checkpoint_id:
                    return None

            return checkpoint.get("data")
        except Exception as e:
            print(f"加载检查点失败: {e}")
            return None

    def has_checkpoint(self) -> bool:
        """检查是否有检查点"""
        return self._get_checkpoint_file().exists()

    def get_checkpoint_info(self) -> Optional[Dict[str, Any]]:
        """获取检查点信息"""
        data = self.load_checkpoint()
        if data is None:
            return None

        return {
            "session_id": self.session_id,
            "has_checkpoint": True,
            "data": data
        }

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """列出所有检查点

        Returns:
            检查点信息列表
        """
        checkpoints = []

        try:
            for file in self.checkpoint_dir.glob("*.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        checkpoint = json.load(f)
                        checkpoints.append({
                            "session_id": checkpoint.get("session_id"),
                            "checkpoint_id": checkpoint.get("checkpoint_id"),
                            "timestamp": checkpoint.get("timestamp"),
                            "file": str(file.name)
                        })
                except:
                    pass

            # 按时间戳排序
            checkpoints.sort(key=lambda x: x["timestamp"], reverse=True)
            return checkpoints
        except Exception as e:
            print(f"列出检查点失败: {e}")
            return []

    def delete_checkpoint(self) -> bool:
        """删除当前会话的检查点

        Returns:
            是否删除成功
        """
        try:
            checkpoint_file = self._get_checkpoint_file()
            if checkpoint_file.exists():
                checkpoint_file.unlink()
            return True
        except Exception as e:
            print(f"删除检查点失败: {e}")
            return False

    def clear_all_checkpoints(self) -> bool:
        """清除所有检查点

        Returns:
            是否清除成功
        """
        try:
            for file in self.checkpoint_dir.glob("*.json"):
                file.unlink()
            return True
        except Exception as e:
            print(f"清除所有检查点失败: {e}")
            return False

    async def resume(self) -> Dict[str, Any]:
        """从检查点恢复

        Returns:
            恢复结果
        """
        data = self.load_checkpoint()
        if data:
            return {
                "success": True,
                "session_id": self.session_id,
                "data": data
            }

        return {
            "success": False,
            "error": "No checkpoint found"
        }

    def export_checkpoint(self, file_path: str) -> bool:
        """导出检查点到文件

        Args:
            file_path: 导出文件路径

        Returns:
            是否导出成功
        """
        try:
            import shutil
            checkpoint_file = self._get_checkpoint_file()
            if checkpoint_file.exists():
                shutil.copy2(checkpoint_file, file_path)
                return True
            return False
        except Exception as e:
            print(f"导出检查点失败: {e}")
            return False

    def import_checkpoint(self, file_path: str) -> bool:
        """从文件导入检查点

        Args:
            file_path: 导入文件路径

        Returns:
            是否导入成功
        """
        try:
            import shutil

            with open(file_path, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)

            # 更新session_id
            self.session_id = checkpoint.get("session_id", self._generate_session_id())

            checkpoint_file = self._get_checkpoint_file()
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"导入检查点失败: {e}")
            return False
