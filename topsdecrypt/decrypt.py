#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
去除文件后缀脚本

功能：
    遍历目标目录下所有文件，去掉指定的后缀名。

说明：
    参数在下面的「参数配置区域」给出默认值，启动 startup.bat 时由它交互式配置并
    通过命令行参数传入；传入的参数覆盖默认值，参数顺序见 apply_cli_args()。
"""

import os
import sys


# ============================================================
# ==================== 参数配置区域 ==========================
# ============================================================

USAGE = """用法：
    python decrypt.py [目标目录] [要去掉的后缀] [是否递归] [重名处理]

示例：
    python decrypt.py "E:\\data\\out" .bak True overwrite

说明：
    参数可以省略，省略的部分使用脚本顶部配置的默认值。
    是否递归：True / False        重名处理：overwrite / skip / rename
"""

# 目标目录（要遍历的文件夹）
TARGET_DIR = r"E:\python\pycharm\PyCrypt\testb"

# 要去掉的后缀名（如 ".bak"）
SUFFIX_TO_REMOVE = ".bak"

# 是否递归遍历子目录
RECURSIVE = True

# 遇到重名文件时的处理方式：
#   "overwrite"  -> 覆盖已存在的文件
#   "skip"       -> 跳过，不处理
#   "rename"     -> 自动重命名（加 _1, _2 ...）
ON_CONFLICT = "overwrite"

# ============================================================
# ============================================================


def parse_bool(s):
    """把 True/False/1/0/yes/no 等文本解析为布尔值"""
    v = str(s).strip().lower()
    if v in ("true", "1", "yes", "y", "on"):
        return True
    if v in ("false", "0", "no", "n", "off"):
        return False
    raise SystemExit(f"错误：无法识别的布尔值：{s}（请填 True 或 False）")


def apply_cli_args(argv):
    """用命令行参数覆盖上面的默认配置（startup.bat 会按这个顺序传入）

    参数顺序：
        1  目标目录
        2  要去掉的后缀
        3  是否递归        （True / False）
        4  重名处理        （overwrite / skip / rename）

    省略或传空的参数保持上面的默认值。
    """
    global TARGET_DIR, SUFFIX_TO_REMOVE, RECURSIVE, ON_CONFLICT

    if len(argv) > 0 and argv[0].strip():
        TARGET_DIR = argv[0].strip()
    if len(argv) > 1 and argv[1].strip():
        SUFFIX_TO_REMOVE = argv[1].strip()
    if len(argv) > 2 and argv[2].strip():
        RECURSIVE = parse_bool(argv[2])
    if len(argv) > 3 and argv[3].strip():
        ON_CONFLICT = argv[3].strip().lower()


def ensure_suffix(s):
    """确保后缀以 . 开头"""
    if s and not s.startswith('.'):
        return '.' + s
    return s


def get_unique_path(path):
    """如果路径已存在，生成一个不冲突的新路径（加 _1, _2 ...）"""
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    i = 1
    while True:
        new_path = f"{base}_{i}{ext}"
        if not os.path.exists(new_path):
            return new_path
        i += 1


def process_files(target_dir, suffix, recursive=True, on_conflict="overwrite"):
    """遍历目录，去掉文件后缀"""
    suffix = ensure_suffix(suffix)

    total = 0
    success = 0
    skipped = 0
    failed = 0

    if recursive:
        walker = os.walk(target_dir)
    else:
        # 只遍历顶层目录
        try:
            entries = os.listdir(target_dir)
        except Exception as e:
            print(f"错误：无法列出目录 {target_dir}，{e}")
            sys.exit(1)
        walker = [(target_dir, [], [f for f in entries
                                    if os.path.isfile(os.path.join(target_dir, f))])]

    for root, dirs, files in walker:
        for filename in files:
            # 只处理以指定后缀结尾的文件（忽略大小写）
            if not filename.lower().endswith(suffix.lower()):
                continue

            total += 1
            src_path = os.path.join(root, filename)

            # 去掉后缀得到新文件名
            new_name = filename[:-len(suffix)]
            if not new_name:
                print(f"[跳过] 去掉后缀后文件名为空：{src_path}")
                skipped += 1
                continue

            dst_path = os.path.join(root, new_name)

            # 源和目标相同（理论上不会发生），跳过
            if os.path.normpath(src_path) == os.path.normpath(dst_path):
                print(f"[跳过] 源与目标相同：{src_path}")
                skipped += 1
                continue

            # 处理重名冲突
            if os.path.exists(dst_path):
                if on_conflict == "skip":
                    print(f"[跳过] 目标已存在：{dst_path}")
                    skipped += 1
                    continue
                elif on_conflict == "rename":
                    dst_path = get_unique_path(dst_path)
                # overwrite 模式什么都不做，直接覆盖

            try:
                os.rename(src_path, dst_path)
                # print(f"[成功] {src_path} -> {dst_path}")
                success += 1
            except Exception as e:
                print(f"[失败] {src_path} -> {dst_path}，错误：{e}")
                failed += 1

    print("\n========== 处理完成 ==========")
    print(f"匹配文件：{total}")
    print(f"成功：{success}")
    print(f"跳过：{skipped}")
    print(f"失败：{failed}")


def main():
    # 命令行参数（startup.bat 传入）覆盖默认配置
    if sys.argv[1:2] and sys.argv[1] in ("-h", "--help", "/?"):
        print(USAGE)
        return
    apply_cli_args(sys.argv[1:])

    # 参数校验
    if not TARGET_DIR or not os.path.isdir(TARGET_DIR):
        print(f"错误：目标目录不存在或不是文件夹：{TARGET_DIR}")
        sys.exit(1)

    if not SUFFIX_TO_REMOVE:
        print("错误：要去掉的后缀名不能为空")
        sys.exit(1)

    if ON_CONFLICT not in ("overwrite", "skip", "rename"):
        print(f"错误：ON_CONFLICT 参数无效：{ON_CONFLICT}")
        sys.exit(1)

    print("=== 去除文件后缀脚本 ===")
    print(f"目标目录     ：{TARGET_DIR}")
    print(f"去掉后缀     ：{SUFFIX_TO_REMOVE}")
    print(f"递归子目录   ：{RECURSIVE}")
    print(f"重名处理     ：{ON_CONFLICT}")
    print("\n开始处理...\n")

    process_files(TARGET_DIR, SUFFIX_TO_REMOVE, RECURSIVE, ON_CONFLICT)


if __name__ == "__main__":
    main()