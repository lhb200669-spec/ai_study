"""学生管理系统核心类：负责增删改查 + 持久化 + 统计"""
from __future__ import annotations

import csv
import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path

from student import Student

logger = logging.getLogger(__name__)

# ---------- 业务异常 ----------
class StudentNotFoundError(Exception):
    """学号不存在"""

class DuplicateStudentError(Exception):
    """学号重复"""

class StudentManager:
    """所有学生数据的唯一入口，外部只与本类交互"""

    FIELD_NAMES = ["sid", "name", "age", "gender", "major", "score"]

    def __init__(self, file_path: str | os.PathLike = "students.json") -> None:
        self.file_path = Path(file_path)
        self._students: dict[str, Student] = {}
        self.load()

    # ==================== 持久化 ====================
    def load(self) -> None:
        """从文件加载数据；文件损坏时自动备份并空库启动"""
        self._students.clear()
        if not self.file_path.exists():
            logger.info("数据文件不存在，以空库启动：%s", self.file_path)
            return
        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                raw = json.load(f)
            if not isinstance(raw, list):
                raise ValueError("文件根节点必须是列表")

            skipped = 0
            for item in raw:
                try:
                    student = Student.from_dict(item)
                except (TypeError, ValueError, KeyError) as exc:
                    skipped += 1
                    logger.warning("跳过一条非法记录 %s（%s）", item, exc)
                    continue
                self._students[student.sid] = student

            logger.info("加载完成：%d 条有效记录，跳过 %d 条",
                        len(self._students), skipped)
        except (json.JSONDecodeError, ValueError, OSError) as exc:
            backup = self.file_path.with_name(
                f"{self.file_path.stem}.broken-"
                f"{datetime.now():%Y%m%d%H%M%S}{self.file_path.suffix}"
            )
            try:
                shutil.copy2(self.file_path, backup)
                logger.error("数据文件损坏（%s），已备份至 %s", exc, backup)
            except OSError:
                logger.error("数据文件损坏（%s），备份失败", exc)
            self._students.clear()

    def save(self) -> None:
        """原子写入：先写临时文件再替换，避免断电导致数据损坏"""
        tmp = self.file_path.with_suffix(self.file_path.suffix + ".tmp")
        payload = [s.to_dict() for s in self.all()]
        try:
            with tmp.open("w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, self.file_path)
            logger.info("已保存 %d 条记录", len(payload))
        except OSError:
            logger.exception("保存数据失败")
            tmp.unlink(missing_ok=True)
            raise

    # ==================== 增 ====================
    def add(self, student: Student) -> Student:
        if student.sid in self._students:
            raise DuplicateStudentError(f"学号 {student.sid} 已存在")
        self._students[student.sid] = student
        self.save()
        logger.info("新增学生：%s", student)
        return student

    # ==================== 删 ====================
    def delete(self, sid: str) -> Student:
        student = self._students.pop(sid, None)
        if student is None:
            raise StudentNotFoundError(f"学号 {sid} 不存在")
        self.save()
        logger.info("删除学生：%s", student)
        return student

    # ==================== 改 ====================
    def update(self, sid: str, **fields) -> Student:
        """按字段更新，None 表示不修改；sid 不允许修改"""
        student = self.get(sid)
        data = student.to_dict()
        for key, value in fields.items():
            if key == "sid" or value is None:
                continue
            if key not in data:
                raise AttributeError(f"未知字段：{key}")
            data[key] = value
        updated = Student.from_dict(data)      # 统一走一遍校验
        self._students[sid] = updated
        self.save()
        logger.info("修改学生：%s -> %s", student, updated)
        return updated

    # ==================== 查 ====================
    def get(self, sid: str) -> Student:
        try:
            return self._students[sid]
        except KeyError:
            raise StudentNotFoundError(f"学号 {sid} 不存在") from None

    def exists(self, sid: str) -> bool:
        return sid in self._students

    @property
    def count(self) -> int:
        return len(self._students)

    def all(self, sort_by: str = "sid", reverse: bool = False) -> list[Student]:
        if sort_by not in self.FIELD_NAMES:
            sort_by = "sid"
        return sorted(self._students.values(),
                      key=lambda s: getattr(s, sort_by), reverse=reverse)

    def search(self,
               keyword: str = "",
               major: str = "",
               min_score: float | None = None,
               max_score: float | None = None) -> list[Student]:
        """关键字（学号/姓名/专业）+ 专业 + 成绩区间 组合模糊查询"""
        keyword = (keyword or "").strip().lower()
        major = (major or "").strip().lower()
        result = []
        for s in self._students.values():
            if keyword and not (
                keyword in s.sid.lower()
                or keyword in s.name.lower()
                or keyword in s.major.lower()
            ):
                continue
            if major and major != s.major.lower():
                continue
            if min_score is not None and s.score < min_score:
                continue
            if max_score is not None and s.score > max_score:
                continue
            result.append(s)
        return sorted(result, key=lambda s: s.sid)

    # ==================== 统计 / 导出 ====================
    def statistics(self) -> dict:
        students = list(self._students.values())
        if not students:
            return {"total": 0}

        scores = [s.score for s in students]
        top = max(students, key=lambda s: s.score)
        bottom = min(students, key=lambda s: s.score)
        passed = sum(1 for s in scores if s >= 60)

        by_major: dict[str, list[float]] = {}
        for s in students:
            by_major.setdefault(s.major, []).append(s.score)

        return {
            "total": len(students),
            "average": sum(scores) / len(scores),
            "max": (top.score, top.name),
            "min": (bottom.score, bottom.name),
            "pass_rate": passed / len(scores) * 100,
            "by_major": {
                m: (len(v), sum(v) / len(v)) for m, v in by_major.items()
            },
        }

    def export_csv(self, path: str | os.PathLike) -> int:
        """导出为 CSV（utf-8-sig，Excel 打开不乱码）"""
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELD_NAMES)
            writer.writeheader()
            writer.writerows(s.to_dict() for s in self.all())
        return len(self._students)