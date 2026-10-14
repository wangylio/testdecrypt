#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件遍历与内容复制脚本

功能：
    1. 遍历指定输入路径下的所有文件（递归）
    2. 排除指定后缀类型的文件
    3. 在输出路径下创建 "原文件名 + 指定后缀名" 的新文件
    4. 读取原文件内容并写入新文件

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
    python encrypt.py [输入路径] [输出路径] [排除的后缀] [目标后缀] [保留目录结构]

示例：
    python encrypt.py "E:\\data\\in" "E:\\data\\out" ".log,.tmp" .bak True

说明：
    参数可以省略，省略的部分使用脚本顶部配置的默认值。
    排除的后缀：逗号分隔，传 - 表示不排除
    保留目录结构：True / False
"""

# 输入路径（要遍历的源文件夹）
INPUT_DIR = r"E:\python\pycharm\PyCrypt\sourcecode\testa"

# 输出路径（输出文件存放的文件夹）
OUTPUT_DIR = r"E:\python\pycharm\PyCrypt\sourcecode\testb"

# 要排除的后缀类型（逗号分隔，如 ".log,.tmp"；留空表示不排除）
EXCLUDE_SUFFIXES_STR = ".log,.tmp"

# 目标后缀名（新文件名 = 原文件名 + 该后缀，如 ".bak"）
TARGET_SUFFIX = ".bak"

# 是否保留原目录结构（True: 输出保留子目录结构；False: 全部平铺到输出目录）
KEEP_DIR_STRUCTURE = True

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
        1  输入路径
        2  输出路径
        3  要排除的后缀    （逗号分隔；传 - 表示不排除）
        4  目标后缀
        5  保留目录结构    （True / False）

    省略或传空的参数保持上面的默认值。
    """
    global INPUT_DIR, OUTPUT_DIR, EXCLUDE_SUFFIXES_STR, TARGET_SUFFIX
    global KEEP_DIR_STRUCTURE

    if len(argv) > 0 and argv[0].strip():
        INPUT_DIR = argv[0].strip()
    if len(argv) > 1 and argv[1].strip():
        OUTPUT_DIR = argv[1].strip()
    if len(argv) > 2:
        # 排除后缀允许为空（- 表示留空），所以不判断是否为空
        value = argv[2].strip()
        EXCLUDE_SUFFIXES_STR = "" if value == "-" else value
    if len(argv) > 3 and argv[3].strip():
        TARGET_SUFFIX = argv[3].strip()
    if len(argv) > 4 and argv[4].strip():
        KEEP_DIR_STRUCTURE = parse_bool(argv[4])


def parse_suffixes(s):
    """将逗号分隔的后缀字符串解析为集合，统一小写，并确保以 . 开头"""
    result = set()
    if not s:
        return result
    for item in s.split(','):
        item = item.strip().lower()
        if not item:
            continue
        if not item.startswith('.'):
            item = '.' + item
        result.add(item)
    return result


def ensure_dir(path):
    """确保目录存在"""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def process_files(input_dir, output_dir, exclude_suffixes, target_suffix,
                  keep_structure=True):
    """遍历文件并复制内容"""
    # 确保目标后缀以 . 开头
    if target_suffix and not target_suffix.startswith('.'):
        target_suffix = '.' + target_suffix

    ensure_dir(output_dir)

    total = 0
    success = 0
    skipped = 0
    failed = 0

    for root, dirs, files in os.walk(input_dir):
        for filename in files:
            total += 1
            src_path = os.path.join(root, filename)

            # 排除后缀检查（忽略大小写）
            _, ext = os.path.splitext(filename)
            if ext.lower() in exclude_suffixes:
                print(f"[跳过] 排除后缀：{src_path}")
                skipped += 1
                continue

            # 新文件名 = 原文件名 + 目标后缀
            new_name = filename + target_suffix

            # 确定输出目录
            if keep_structure:
                rel_path = os.path.relpath(src_path, input_dir)
                rel_dir = os.path.dirname(rel_path)
                out_dir = os.path.join(output_dir, rel_dir) if rel_dir else output_dir
            else:
                out_dir = output_dir

            ensure_dir(out_dir)
            dst_path = os.path.join(out_dir, new_name)

            # 读取原文件内容并写入新文件（二进制方式，避免编码问题）
            try:
                with open(src_path, 'rb') as fsrc:
                    data = fsrc.read()
                with open(dst_path, 'wb') as fdst:
                    fdst.write(data)
                # print(f"[成功] {src_path} -> {dst_path}")
                success += 1
            except Exception as e:
                print(f"[失败] {src_path} -> {dst_path}，错误：{e}")
                failed += 1

    print("\n========== 处理完成 ==========")
    print(f"总计文件：{total}")
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
    if not INPUT_DIR or not os.path.isdir(INPUT_DIR):
        print(f"错误：输入路径不存在或不是文件夹：{INPUT_DIR}")
        sys.exit(1)

    if not OUTPUT_DIR:
        print("错误：输出路径不能为空")
        sys.exit(1)

    if not TARGET_SUFFIX:
        print("错误：目标后缀名不能为空")
        sys.exit(1)

    exclude_suffixes = parse_suffixes(EXCLUDE_SUFFIXES_STR)

    print("=== 文件内容复制脚本 ===")
    print(f"输入路径     ：{INPUT_DIR}")
    print(f"输出路径     ：{OUTPUT_DIR}")
    print(f"排除后缀     ：{exclude_suffixes if exclude_suffixes else '（无）'}")
    print(f"目标后缀     ：{TARGET_SUFFIX}")
    print(f"保留目录结构 ：{KEEP_DIR_STRUCTURE}")
    print("\n开始处理...\n")

    process_files(INPUT_DIR, OUTPUT_DIR, exclude_suffixes, TARGET_SUFFIX,
                  KEEP_DIR_STRUCTURE)


if __name__ == "__main__":
    main()