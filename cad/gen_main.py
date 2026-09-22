# -*- coding: utf-8 -*-
"""主控: 生成 11 张图 -> 范围校验 -> 渲染 PNG"""
import os
import ezdxf
from ezdxf import bbox
import sheets_a
import sheets_b
from dev_params import OUT

SHEETS = [
    (sheets_a.sheet00, "FDC_50000_00_图纸目录及技术说明"),
    (sheets_a.sheet01, "FDC_50000_01_总装配图"),
    (sheets_a.sheet02, "FDC_50000_02_壳体部件图"),
    (sheets_a.sheet03, "FDC_50000_03_灰斗部件图"),
    (sheets_a.sheet04, "FDC_50000_04_花板零件图"),
    (sheets_b.sheet05, "FDC_50000_05_喷吹装置部件图"),
    (sheets_b.sheet06, "FDC_50000_06_顶盖及检修门部件图"),
    (sheets_b.sheet07, "FDC_50000_07_进出风道及法兰部件图"),
    (sheets_b.sheet08, "FDC_50000_08_支架平台及梯子图"),
    (sheets_b.sheet09, "FDC_50000_09_钢板下料套裁图"),
    (sheets_b.sheet10, "FDC_50000_10_材料明细表"),
]


def validate(s, name):
    """所有图元必须落在图框内(含 2mm 容差)"""
    ext = bbox.extents(s.msp)
    lo, hi = ext.extmin, ext.extmax
    bad = []
    if lo.x < -2 or lo.y < -2:
        bad.append(f"越界下限 ({lo.x:.1f},{lo.y:.1f})")
    if hi.x > s.W + 2 or hi.y > s.H + 2:
        bad.append(f"越界上限 ({hi.x:.1f},{hi.y:.1f})")
    n = len(list(s.msp))
    status = "!! " + "; ".join(bad) if bad else "OK"
    print(f"{name}: {n} 实体, 范围 ({lo.x:.1f},{lo.y:.1f})~({hi.x:.1f},{hi.y:.1f}) [{status}]")
    return not bad


def main():
    results = []
    for fn, name in SHEETS:
        s = fn()
        dxf = os.path.join(OUT, name + ".dxf")
        s.save(dxf)
        png = os.path.join(OUT, name + ".png")
        try:
            s.png(png, dpi=180)
            png_ok = True
        except Exception as e:
            png_ok = False
            print(f"{name}: PNG 渲染失败 {e}")
        ok = validate(s, name)
        results.append((name, ok, png_ok))
    n_bad = sum(1 for _, ok, _ in results if not ok)
    print(f"\n完成 {len(results)} 张, 范围校验未过 {n_bad} 张")


if __name__ == "__main__":
    main()
