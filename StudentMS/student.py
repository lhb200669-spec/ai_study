"""学生实体类：只负责数据本身与自身校验/序列化"""
from __future__ import annotations

from dataclasses import asdict, dataclass

@dataclass
class Student:
    """学生信息，学号 sid 作为唯一标识"""

    sid: str        # 学号
    name: str       # 姓名
    age: int        # 年龄
    gender: str     # 性别（男/女）
    major: str      # 专业
    score: float | int    # 成绩（0~100）

    # ---------- 生命周期 ----------
    def __post_init__(self) -> None:
        """对象创建后立刻做类型转换与合法性校验，杜绝脏数据"""
        self.sid = str(self.sid).strip()
        self.name = str(self.name).strip()
        self.major = str(self.major).strip()
        self.gender = str(self.gender).strip()
        self.age = int(self.age)
        self.score = float(self.score)

        if not self.sid:
            raise ValueError("学号不能为空")
        if not self.name:
            raise ValueError("姓名不能为空")
        if not 1 <= self.age <= 150:
            raise ValueError(f"年龄必须在 1~150 之间：{self.age}")
        if self.gender not in ("男", "女"):
            raise ValueError(f"性别只能是 男/女：{self.gender}")
        if not 0 <= self.score <= 100:
            raise ValueError(f"成绩必须在 0~100 之间：{self.score}")

    # ---------- 序列化 ----------
    def to_dict(self) -> dict:
        """转为可 JSON 化的字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        """从字典还原，所有校验逻辑集中在 __post_init__"""
        if not isinstance(data, dict):
            raise TypeError("学生数据必须是字典")
        if "sid" not in data:
            raise KeyError("缺少学号字段 sid")
        return cls(
            sid=data["sid"],
            name=data.get("name", ""),
            age=data.get("age", 0),
            gender=data.get("gender", ""),
            major=data.get("major", ""),
            score=data.get("score", 0.0),
        )

    # ---------- 展示 ----------
    def __str__(self) -> str:
        return (f"{self.sid} | {self.name} | {self.age}岁 | {self.gender} | "
                f"{self.major} | {self.score:.1f}分")