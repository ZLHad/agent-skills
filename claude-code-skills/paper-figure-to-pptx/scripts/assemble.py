"""
assemble.py — 把当前目录下所有 Module 合并到一个多页 pptx。

工作原理：
  1) 扫描当前目录下所有形如 module*.py 的文件
  2) 依次 import 每个 module，调用其 build_module(prs) 函数
  3) 所有 slide 叠加到同一个 Presentation 对象
  4) 保存为 Combined.pptx（或自定义名）

使用方式：
  # 方式一：自动发现所有 module（按文件名排序）
  python assemble.py

  # 方式二：指定输出文件名
  python assemble.py --output MyFigure.pptx

  # 方式三：在代码里显式指定顺序
  from assemble import assemble_modules
  assemble_modules(['module1', 'module3', 'module2'], 'Combined.pptx')

要求每个 Module 文件必须：
  - 文件名形如 moduleN.py 或 module_<name>.py
  - 导出一个 build_module(prs) 函数
  - build_module 里不调用 prs.save()（保存权交给 assemble）
"""
import os
import re
import sys
import glob
import argparse
import importlib.util

from pptx import Presentation
from pptx.util import Inches


# ============================================================
# 辅助函数
# ============================================================
def _natural_sort_key(s):
    """按自然数顺序排序：module2 < module10 而非字母序 module10 < module2。"""
    return [int(t) if t.isdigit() else t.lower()
            for t in re.split(r'(\d+)', s)]


def _load_module(module_path):
    """从 .py 文件路径动态 import 模块。"""
    module_name = os.path.splitext(os.path.basename(module_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {module_path}")
    mod = importlib.util.module_from_spec(spec)
    # 加入 sys.modules 以便 helpers import 正常
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _discover_modules(directory='.', exclude=None):
    """
    自动发现目录下所有 module*.py 文件，按自然数顺序排序。

    排除：
      - assemble.py 本身
      - helpers.py
      - module_template.py
      - exclude 参数里指定的文件名（可选）
    """
    exclude = set(exclude or [])
    exclude.update(['assemble.py', 'helpers.py', 'module_template.py'])

    candidates = glob.glob(os.path.join(directory, 'module*.py'))
    candidates = [p for p in candidates
                  if os.path.basename(p) not in exclude]
    candidates.sort(key=lambda p: _natural_sort_key(os.path.basename(p)))
    return candidates


# ============================================================
# 主合并函数
# ============================================================
def assemble_modules(module_specs=None, output='Combined.pptx',
                     directory='.', slide_width=13.333, slide_height=7.5,
                     verbose=True):
    """
    合并多个 module 到一个多页 pptx。

    参数:
        module_specs: 三种可选形式
            - None: 自动发现目录下所有 module*.py
            - list of str: 模块文件名列表（如 ['module1', 'module3']）
            - list of callable: 已 import 的 build_module 函数列表
        output: 输出 pptx 文件名
        directory: 扫描/加载目录
        slide_width, slide_height: slide 尺寸（英寸）
        verbose: 打印进度

    返回:
        输出文件的绝对路径
    """
    prs = Presentation()
    prs.slide_width = Inches(slide_width)
    prs.slide_height = Inches(slide_height)

    # 解析 module_specs 到一个 build 函数列表
    build_funcs = []

    if module_specs is None:
        # 自动发现
        paths = _discover_modules(directory)
        if not paths:
            raise RuntimeError(
                f"No module*.py files found in {os.path.abspath(directory)}"
            )
        if verbose:
            print(f"Discovered {len(paths)} modules:")
            for p in paths:
                print(f"  - {os.path.basename(p)}")
        for p in paths:
            mod = _load_module(p)
            if not hasattr(mod, 'build_module'):
                raise AttributeError(
                    f"{p} does not define build_module(prs) function"
                )
            build_funcs.append((os.path.basename(p), mod.build_module))

    elif all(callable(s) for s in module_specs):
        # 已 import 的函数列表
        build_funcs = [(f.__module__, f) for f in module_specs]

    else:
        # 文件名/模块名列表
        for spec in module_specs:
            # 尝试三种路径形式
            candidates = [
                spec,
                spec + '.py',
                os.path.join(directory, spec),
                os.path.join(directory, spec + '.py'),
            ]
            path = next((c for c in candidates if os.path.isfile(c)), None)
            if path is None:
                raise FileNotFoundError(
                    f"Cannot find module file: {spec} (tried {candidates})"
                )
            mod = _load_module(path)
            if not hasattr(mod, 'build_module'):
                raise AttributeError(
                    f"{path} does not define build_module(prs) function"
                )
            build_funcs.append((os.path.basename(path), mod.build_module))

    # 依次构建每个 Module 的 slide
    for name, build in build_funcs:
        if verbose:
            print(f"Building slide: {name}")
        build(prs)

    # 保存
    output_abs = os.path.abspath(output)
    prs.save(output_abs)
    if verbose:
        print(f"\nSaved combined pptx ({len(build_funcs)} pages): {output_abs}")
    return output_abs


# ============================================================
# CLI 入口
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description='Merge all module*.py into a single multi-page pptx.'
    )
    parser.add_argument(
        '-o', '--output', default='Combined.pptx',
        help='Output pptx filename (default: Combined.pptx)'
    )
    parser.add_argument(
        '-d', '--directory', default='.',
        help='Directory to scan for modules (default: current dir)'
    )
    parser.add_argument(
        '--modules', nargs='+', default=None,
        help='Explicit module names in order (default: auto-discover)'
    )
    parser.add_argument(
        '--width', type=float, default=13.333,
        help='Slide width in inches (default: 13.333 for 16:9)'
    )
    parser.add_argument(
        '--height', type=float, default=7.5,
        help='Slide height in inches (default: 7.5)'
    )
    parser.add_argument(
        '-q', '--quiet', action='store_true',
        help='Suppress progress output'
    )
    args = parser.parse_args()

    assemble_modules(
        module_specs=args.modules,
        output=args.output,
        directory=args.directory,
        slide_width=args.width,
        slide_height=args.height,
        verbose=not args.quiet,
    )


if __name__ == '__main__':
    main()
