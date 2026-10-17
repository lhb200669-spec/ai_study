"""学生管理系统 —— 命令行界面入口，运行：python main.py"""
from __future__ import annotations

import logging
import unicodedata

from manager import (
    DuplicateStudentError,
    StudentManager,
    StudentNotFoundError,
)
from student import Student

DATA_FILE = "students.json"

MENU = """
==============================================================
                  学 生 管 理 系 统
==============================================================
   1. 添加学生          2. 删除学生          3. 修改学生
   4. 查询学生          5. 显示全部          6. 成绩排序
   7. 统计信息          8. 导出 CSV          0. 退出系统
==============================================================
"""

COLUMNS = [("学号", 12), ("姓名", 10), ("年龄", 6),
           ("性别", 6), ("专业", 16), ("成绩", 8)]


# ==================== 输入辅助 ====================
def input_text(prompt: str, default: str | None = None) -> str:
    while True:
        hint = f"{prompt}" + (f"[{default}]" if default is not None else "") + "："
        value = input(hint).strip()
        if value:
            return value
        if default is not None:
            return default
        print("  ✗ 输入不能为空，请重新输入")

def input_int(prompt: str, low: int, high: int, default: int | None = None) -> int:
    while True:
        hint = f"{prompt}" + (f"[{default}]" if default is not None else "") + "："
        raw = input(hint).strip()
        if not raw and default is not None:
            return default
        try:
            value = int(raw)
        except ValueError:
            print(f"  ✗ 请输入 {low}~{high} 的整数")
            continue
        if low <= value <= high:
            return value
        print(f"  ✗ 请输入 {low}~{high} 的整数")

def input_float(prompt: str, low: float, high: float,
                default: float | None = None) -> float:
    while True:
        hint = f"{prompt}" + (f"[{default}]" if default is not None else "") + "："
        raw = input(hint).strip()
        if not raw and default is not None:
            return default
        try:
            value = float(raw)
        except ValueError:
            print(f"  ✗ 请输入 {low}~{high} 的数字")
            continue
        if low <= value <= high:
            return value
        print(f"  ✗ 请输入 {low}~{high} 的数字")

def input_gender(prompt: str, default: str | None = None) -> str:
    while True:
        hint = f"{prompt}" + (f"[{default}]" if default else "") + "："
        raw = input(hint).strip()
        if not raw and default:
            return default
        if raw in ("男", "女"):
            return raw
        if raw.lower() in ("m", "f"):
            return "男" if raw.lower() == "m" else "女"
        print("  ✗ 性别只能是 男 / 女")

# ==================== 表格渲染（中文对齐） ====================
def _disp_width(text: str) -> int:
    """计算字符串的显示宽度，中日韩字符占 2 列"""
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
               for ch in str(text))

def _pad(text, width: int, align: str = "left") -> str:
    text = str(text)
    space = max(0, width - _disp_width(text))
    if align == "right":
        return " " * space + text
    if align == "center":
        left = space // 2
        return " " * left + text + " " * (space - left)
    return text + " " * space

def print_students(students: list[Student]) -> None:
    if not students:
        print("\n  （没有匹配的学生记录）")
        return

    sep = "+" + "+".join("-" * (w + 2) for _, w in COLUMNS) + "+"
    header = "|" + "|".join(
        " " + _pad(title, w, "center") + " " for title, w in COLUMNS
    ) + "|"

    print(sep)
    print(header)
    print(sep)
    for s in students:
        cells = [s.sid, s.name, s.age, s.gender, s.major, f"{s.score:.1f}"]
        row = "|" + "|".join(
            " " + _pad(v, w, "right" if i == 5 else "left") + " "
            for i, (v, (_, w)) in enumerate(zip(cells, COLUMNS))
        ) + "|"
        print(row)
    print(sep)
    print(f"  共 {len(students)} 条记录")

# ==================== 功能实现 ====================
def handle_add(manager: StudentManager) -> None:
    print("\n--- 添加学生 ---")
    while True:
        sid = input_text("学号")
        if manager.exists(sid):
            print(f"  ✗ 学号 {sid} 已存在，请重新输入")
            continue
        break

    student = Student(
        sid=sid,
        name=input_text("姓名"),
        age=input_int("年龄", 1, 150),
        gender=input_gender("性别"),
        major=input_text("专业"),
        score=input_float("成绩", 0, 100),
    )
    manager.add(student)
    print(f"  ✓ 添加成功：{student}")

def handle_delete(manager: StudentManager) -> None:
    print("\n--- 删除学生 ---")
    sid = input_text("请输入要删除的学号")
    student = manager.get(sid)          # 不存在会抛异常，由 main 统一捕获

    print("  即将删除以下学生：")
    print_students([student])
    if input("  确认删除？(y/N)：").strip().lower() != "y":
        print("  已取消删除")
        return
    manager.delete(sid)
    print("  ✓ 删除成功")

def handle_update(manager: StudentManager) -> None:
    print("\n--- 修改学生 ---")
    sid = input_text("请输入要修改的学号")
    student = manager.get(sid)

    print("  当前信息：")
    print_students([student])
    print("  （直接回车表示保持原值）")

    updated = manager.update(
        sid,
        name=input_text("姓名", default=student.name),
        age=input_int("年龄", 1, 150, default=student.age),
        gender=input_gender("性别", default=student.gender),
        major=input_text("专业", default=student.major),
        score=input_float("成绩", 0, 100, default=student.score),
    )
    print("  ✓ 修改成功：")
    print_students([updated])

def handle_query(manager: StudentManager) -> None:
    print("\n--- 查询学生 ---")
    print("   1. 按学号精确查询")
    print("   2. 按关键字模糊查询（学号 / 姓名 / 专业）")
    print("   3. 按成绩区间查询")
    choice = input("  请选择：").strip()

    if choice == "1":
        print_students([manager.get(input_text("学号"))])
    elif choice == "2":
        keyword = input_text("关键字")
        print_students(manager.search(keyword=keyword))
    elif choice == "3":
        low = input_float("最低分", 0, 100, default=0.0)
        high = input_float("最高分", low, 100, default=100.0)
        print_students(manager.search(min_score=low, max_score=high))
    else:
        print("  ✗ 无效选项")

def handle_list(manager: StudentManager) -> None:
    print("\n--- 全部学生 ---")
    print_students(manager.all())

def handle_sort(manager: StudentManager) -> None:
    print("\n--- 按成绩排序 ---")
    print("   1. 从高到低    2. 从低到高")
    choice = input("  请选择：").strip()
    if choice not in ("1", "2"):
        print("  ✗ 无效选项")
        return
    print_students(manager.all(sort_by="score", reverse=(choice == "2")))

def handle_statistics(manager: StudentManager) -> None:
    print("\n--- 统计信息 ---")
    stats = manager.statistics()
    if stats["total"] == 0:
        print("  （暂无学生数据）")
        return

    print(f"  总人数  ：{stats['total']}")
    print(f"  平均分  ：{stats['average']:.2f}")
    print(f"  最高分  ：{stats['max'][0]:.1f}（{stats['max'][1]}）")
    print(f"  最低分  ：{stats['min'][0]:.1f}（{stats['min'][1]}）")
    print(f"  及格率  ：{stats['pass_rate']:.1f}%")
    print("  按专业统计：")
    for major, (cnt, avg) in sorted(stats["by_major"].items()):
        print(f"    - {major}：{cnt} 人，平均 {avg:.1f} 分")

def handle_export(manager: StudentManager) -> None:
    print("\n--- 导出 CSV ---")
    if manager.count == 0:
        print("  （暂无数据可导出）")
        return
    path = input_text("导出文件名", default="students_export.csv")
    count = manager.export_csv(path)
    print(f"  ✓ 已导出 {count} 条记录到 {path}")

# ==================== 主循环 ====================
def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("student_manager.log", encoding="utf-8"),
            # 如想在终端也看日志，取消下一行注释即可
            # logging.StreamHandler(),
        ],
    )

    manager = StudentManager(DATA_FILE)
    actions = {
        "1": handle_add,
        "2": handle_delete,
        "3": handle_update,
        "4": handle_query,
        "5": handle_list,
        "6": handle_sort,
        "7": handle_statistics,
        "8": handle_export,
    }

    print(f"\n欢迎使用学生管理系统，当前共有 {manager.count} 名学生。")

    while True:
        print(MENU)
        try:
            choice = input("请输入功能编号：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if choice == "0":
            print("感谢使用，再见！")
            break

        action = actions.get(choice)
        if action is None:
            print("  ✗ 无效编号，请重新输入")
            continue

        try:
            action(manager)
        except StudentNotFoundError as exc:
            print(f"  ✗ {exc}")
        except DuplicateStudentError as exc:
            print(f"  ✗ {exc}")
        except (EOFError, KeyboardInterrupt):
            print("\n  操作已取消")
        except Exception as exc:  # 兜底：任何异常都不应让程序崩溃
            logging.getLogger(__name__).exception("操作异常")
            print(f"  ✗ 操作失败：{exc}")

        try:
            input("\n按回车键继续...")
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

if __name__ == "__main__":
    main()