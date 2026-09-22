# -*- coding: utf-8 -*-
"""GB 制图模板库 v3 —— 设计院正规出图标准
关键纪律: 两套坐标严格分离
  纸面坐标(paper): 图框/标题栏/表格/技术要求 —— 单位 mm, 0..841 x 0..594
  模型坐标(model): 视图几何 —— 真实尺寸 mm, 经 set_view(ox,oy,scale) 变换到纸面
所有标注(文字/尺寸/箭头)高度均按纸面 mm 固定, 不随比例缩放
v3新增: 粗糙度/形位公差/基准代号/螺栓圆/带公差尺寸/完整焊接符号
"""
import math
import ezdxf
from ezdxf.enums import TextEntityAlignment as TA

A0 = (1189, 841)
A1 = (841, 594)
A2 = (594, 420)

_LAYERS = [("粗实线", 7, 50), ("细实线", 7, 18), ("中心线", 1, 18), ("虚线", 8, 18),
           ("尺寸线", 3, 18), ("文字", 7, 18), ("剖面线", 8, 18), ("图框线", 7, 35),
           ("表格线", 7, 18), ("下料线", 5, 50), ("引线", 6, 18), ("焊接符号", 4, 18)]

LEFT, MC, ML, MR = TA.LEFT, TA.MIDDLE_CENTER, TA.MIDDLE_LEFT, TA.MIDDLE_RIGHT


class Sheet:
    def __init__(self, fmt=A1, unit="XX环保工程有限公司", proj="50000m3/h 脉冲布袋除尘器",
                 name="", no="", scale="1:20", mat="", wt="", idx=1, total=11,
                 date="2026-09-21"):
        self.W, self.H = fmt
        self.m, self.ml = 10.0, 25.0
        self.doc = ezdxf.new("R2018", setup=True)
        self.doc.header["$INSUNITS"] = 4
        self.doc.header["$LWDISPLAY"] = 1
        for n, c, lw in _LAYERS:
            self.doc.layers.add(n, color=c, lineweight=lw)
        try:
            self.doc.styles.add("HZ", font="simfang.ttf",
                                dxfattribs={"height": 0, "width": 0.8})
        except Exception:
            self.doc.styles.add("HZ", font="gbenor.shx",
                                dxfattribs={"height": 0, "width": 0.8,
                                            "bigfont": "gbcbig.shx"})
        self.msp = self.doc.modelspace()
        self.ox, self.oy, self.s = 0.0, 0.0, 1.0
        self._frame()
        self._title_block(unit, proj, name, no, scale, mat, wt, idx, total, date)

    def _emit_text(self, x, y, s, h, align, layer, rot=0):
        if s in (None, ""):
            return
        e = self.msp.add_text(str(s), height=h,
                              dxfattribs={"layer": layer, "style": "HZ", "rotation": rot})
        e.set_placement((x, y), align=align)

    def pt(self, x, y, s, h=3.0, align=MC, layer="文字", rot=0):
        self._emit_text(x, y, s, h, align, layer, rot)

    def pl(self, p1, p2, layer="粗实线", lt=None):
        a = {"layer": layer}
        if lt:
            a["linetype"] = lt
        self.msp.add_line(p1, p2, dxfattribs=a)

    def prect(self, x, y, w, h, layer="表格线"):
        self.msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                                close=True, dxfattribs={"layer": layer})

    def _frame(self):
        m, ml, W, H = self.m, self.ml, self.W, self.H
        self.msp.add_lwpolyline([(0, 0), (W, 0), (W, H), (0, H)], close=True,
                                dxfattribs={"layer": "图框线"})
        self.msp.add_lwpolyline([(ml, m), (W - m, m), (W - m, H - m), (ml, H - m)],
                                close=True, dxfattribs={"layer": "图框线"})
        nx = 8
        for i in range(1, nx):
            x = ml + (W - m - ml) * i / nx
            self.pl((x, m), (x, m + 5), "图框线")
            self.pl((x, H - m), (x, H - m - 5), "图框线")
            self.pt(x - (W - m - ml) / nx / 2, m + 2.8, str(i), 2.4)
        for j in range(6):
            yy = H - m - (H - 2 * m) * j / 6 - (H - 2 * m) / 12
            self.pl((ml, yy - 2.5), (ml + 5, yy - 2.5), "图框线")
            self.pt(ml + 2.8, yy, "ABCDEF"[j], 2.4)

    def _title_block(self, unit, proj, name, no, scale, mat, wt, idx, total, date):
        w = 180.0
        x0 = self.W - self.m - w
        y0 = self.m
        cws = [70, 40, 35, 35]
        vals = [name, no, mat, scale]
        labs = ["图名", "图号", "材料", "比例"]
        cx = x0
        for i in range(4):
            self.prect(cx, y0, cws[i], 22, "表格线")
            self.pt(cx + cws[i] / 2, y0 + 18.5, labs[i], 2.2)
            self.pt(cx + cws[i] / 2, y0 + 9, vals[i], 3.4)
            cx += cws[i]
        y1 = y0 + 22
        self.prect(x0, y1, w, 12, "表格线")
        self.pt(x0 + 30, y1 + 6, unit, 3.0)
        self.pl((x0 + 60, y1), (x0 + 60, y1 + 12), "表格线")
        cw = (w - 60) / 5
        for i, lb in enumerate(["设计", "校对", "审核", "工艺", "批准"]):
            cx = x0 + 60 + cw * i
            if i:
                self.pl((cx, y1), (cx, y1 + 12), "表格线")
            self.pt(cx + cw / 2, y1 + 4, lb, 2.4)
        y2 = y1 + 12
        self.prect(x0, y2, w, 11, "表格线")
        cws3 = [20, 20, 50, 45, 45]
        cx = x0
        for i, lb in enumerate(["标记", "处数", "更改文件号", "签字", "日期"]):
            self.pt(cx + cws3[i] / 2, y2 + 8.5, lb, 2.2)
            cx += cws3[i]
            if i < 4:
                self.pl((cx, y2), (cx, y2 + 11), "表格线")
        y3 = y2 + 11
        self.prect(x0, y3, w, 11, "表格线")
        cws4 = [30, 25, 25, 40, 60]
        vals4 = [f"重量 {wt}", f"共 {total} 张", f"第 {idx} 张", date, proj]
        cx = x0
        for i in range(5):
            self.pt(cx + cws4[i] / 2, y3 + 5.5, vals4[i], 2.4)
            cx += cws4[i]
            if i < 4:
                self.pl((cx, y3), (cx, y3 + 11), "表格线")
        self.msp.add_lwpolyline([(x0, y0), (x0 + w, y0), (x0 + w, y3 + 11), (x0, y3 + 11)],
                                close=True, dxfattribs={"layer": "图框线"})

    def table(self, x0, y0, cw, header, rows, h=7.0, fs=2.8, title=None):
        w = sum(cw)
        n = len(rows)
        top = y0 + h * (n + 1)
        if title:
            self.pt(x0 + w / 2, top + 3.5, title, 3.8)
        y = top - h
        cx = x0
        for i, hd in enumerate(header):
            self.prect(cx, y, cw[i], h, "表格线")
            self.pt(cx + cw[i] / 2, y + h / 2, hd, fs)
            cx += cw[i]
        for r in rows:
            y -= h
            cx = x0
            for i in range(len(cw)):
                v = str(r[i]) if i < len(r) else ""
                self.prect(cx, y, cw[i], h, "表格线")
                self.pt(cx + cw[i] / 2, y + h / 2, v, fs)
                cx += cw[i]
        self.msp.add_lwpolyline([(x0, y0), (x0 + w, y0), (x0 + w, top), (x0, top)],
                                close=True, dxfattribs={"layer": "表格线"})
        return top

    def bom(self, rows, y0=None):
        cw = [10, 30, 36, 32, 10, 24, 12, 12, 14]
        header = ["序号", "代号", "名称", "规格", "数量", "材料", "单重", "总重", "备注"]
        x0 = self.W - self.m - 180
        y0 = self.m + 56 if y0 is None else y0
        return self.table(x0, y0, cw, header, rows, h=7.0, fs=2.5)

    def notes(self, x, y, lines, h=3.0, lh=5.4, title="技术要求"):
        if title:
            self.pt(x, y, title, 4.0, align=ML)
            y -= 6
        for ln in lines:
            self.pt(x, y, ln, h, align=ML)
            y -= lh

    def set_view(self, ox, oy, s):
        self.ox, self.oy, self.s = ox, oy, s

    def v(self, x, y):
        return (self.ox + x * self.s, self.oy + y * self.s)

    def mt(self, x, y, s, h=3.0, align=MC, layer="文字", rot=0):
        px, py = self.v(x, y)
        self._emit_text(px, py, s, h, align, layer, rot)

    def mline(self, p1, p2, layer="粗实线", lt=None):
        a = {"layer": layer}
        if lt:
            a["linetype"] = lt
        self.msp.add_line(self.v(*p1), self.v(*p2), dxfattribs=a)

    def mpoly(self, pts, close=False, layer="粗实线", lt=None):
        a = {"layer": layer}
        if lt:
            a["linetype"] = lt
        self.msp.add_lwpolyline([self.v(*p) for p in pts], close=close, dxfattribs=a)

    def mrect(self, x, y, w, h, layer="粗实线", lt=None):
        self.mpoly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], close=True,
                   layer=layer, lt=lt)

    def mcirc(self, x, y, r, layer="粗实线", lt=None):
        a = {"layer": layer}
        if lt:
            a["linetype"] = lt
        self.msp.add_circle(self.v(x, y), r * self.s, dxfattribs=a)

    def mcline(self, x1, y1, x2, y2):
        self.mline((x1, y1), (x2, y2), "中心线", "CENTER")

    def mhatch(self, pts, scale=4.0):
        h = self.msp.add_hatch(color=8, dxfattribs={"layer": "剖面线"})
        h.set_pattern_fill("ANSI31", scale=scale)
        h.paths.add_polyline_path([self.v(*p) for p in pts], is_closed=True)

    def _arrow(self, tip, ang, size=2.8):
        a = math.radians(ang)
        p2 = (tip[0] - size * math.cos(a) + size * 0.3 * math.sin(a),
              tip[1] - size * math.sin(a) - size * 0.3 * math.cos(a))
        p3 = (tip[0] - size * math.cos(a) - size * 0.3 * math.sin(a),
              tip[1] - size * math.sin(a) + size * 0.3 * math.cos(a))
        self.msp.add_solid([tip, p2, p3], dxfattribs={"layer": "尺寸线"})

    def dim_h(self, x1, x2, y, d=10.0, txt=None):
        px1, py = self.v(x1, y)
        px2, _ = self.v(x2, y)
        s = -1.0 if d > 0 else 1.0
        yl = py + s * abs(d)
        L = "尺寸线"
        self.msp.add_line((px1, py + s * 1.0), (px1, yl + s * 1.5), dxfattribs={"layer": L})
        self.msp.add_line((px2, py + s * 1.0), (px2, yl + s * 1.5), dxfattribs={"layer": L})
        self.msp.add_line((px1, yl), (px2, yl), dxfattribs={"layer": L})
        self._arrow((px1, yl), 0 if px2 > px1 else 180)
        self._arrow((px2, yl), 180 if px2 > px1 else 0)
        v = txt if txt else f"{abs(x2 - x1):.0f}"
        self.pt((px1 + px2) / 2, yl + 1.8, v, 2.8)

    def dim_v(self, y1, y2, x, d=10.0, txt=None):
        px, py1 = self.v(x, y1)
        _, py2 = self.v(x, y2)
        s = -1.0 if d > 0 else 1.0
        xl = px + s * abs(d)
        L = "尺寸线"
        self.msp.add_line((px + s * 1.0, py1), (xl + s * 1.5, py1), dxfattribs={"layer": L})
        self.msp.add_line((px + s * 1.0, py2), (xl + s * 1.5, py2), dxfattribs={"layer": L})
        self.msp.add_line((xl, py1), (xl, py2), dxfattribs={"layer": L})
        self._arrow((xl, py1), 90 if py2 > py1 else 270)
        self._arrow((xl, py2), 270 if py2 > py1 else 90)
        v = txt if txt else f"{abs(y2 - y1):.0f}"
        self.pt(xl - 1.8, (py1 + py2) / 2, v, 2.8, align=MR)

    def chain_h(self, xs, y, d=10.0):
        s = -1.0 if d > 0 else 1.0
        py = self.v(0, y)[1]
        yl = py + s * abs(d)
        L = "尺寸线"
        pxs = [self.v(x, y)[0] for x in xs]
        for px in pxs:
            self.msp.add_line((px, py + s * 1.0), (px, yl + s * 1.5), dxfattribs={"layer": L})
        self.msp.add_line((pxs[0], yl), (pxs[-1], yl), dxfattribs={"layer": L})
        self._arrow((pxs[0], yl), 0)
        self._arrow((pxs[-1], yl), 180)
        for i in range(1, len(pxs) - 1):
            self._arrow((pxs[i], yl), 0)
            self._arrow((pxs[i], yl), 180)
        for i in range(len(xs) - 1):
            self.pt((pxs[i] + pxs[i + 1]) / 2, yl + 1.8, f"{xs[i + 1] - xs[i]:.0f}", 2.4)

    def balloon(self, no, x, y, tx, ty, r=3.6):
        px, py = self.v(x, y)
        qx, qy = self.v(tx, ty)
        self.msp.add_line((px, py), (qx, qy), dxfattribs={"layer": "引线"})
        self.msp.add_solid([(px, py), (px - 0.7, py), (px, py - 0.7)],
                           dxfattribs={"layer": "引线"})
        self.msp.add_circle((qx, qy), r, dxfattribs={"layer": "引线"})
        self.pt(qx, qy, str(no), 2.8)

    def leader(self, x, y, tx, ty, txt, h=2.8):
        px, py = self.v(x, y)
        qx, qy = self.v(tx, ty)
        self.msp.add_line((px, py), (qx, qy), dxfattribs={"layer": "引线"})
        if qx >= px:
            self.msp.add_line((qx, qy), (qx + 6, qy), dxfattribs={"layer": "引线"})
            self.pt(qx + 7, qy + 1.0, txt, h, align=ML)
        else:
            self.msp.add_line((qx, qy), (qx - 6, qy), dxfattribs={"layer": "引线"})
            self.pt(qx - 7, qy + 1.0, txt, h, align=MR)

    def weld(self, x, y, k):
        px, py = self.v(x, y)
        self.msp.add_lwpolyline([(px, py), (px - 5, py + 5), (px - 10, py)],
                                dxfattribs={"layer": "焊接符号"})
        self.msp.add_line((px - 5, py + 5), (px - 5, py + 9), dxfattribs={"layer": "焊接符号"})
        self.msp.add_line((px - 5, py + 9), (px + 3, py + 9), dxfattribs={"layer": "焊接符号"})
        self.pt(px + 4.5, py + 9, f"h={k}", 2.4, align=ML)

    def sec_mark(self, letter, x, y, vert=True):
        px, py = self.v(x, y)
        if vert:
            self.pl((px, py - 6), (px, py + 6), "粗实线")
            self.pt(px + 3, py, letter, 3.6)
        else:
            self.pl((px - 6, py), (px + 6, py), "粗实线")
            self.pt(px, py + 4, letter, 3.6)

    def view_label(self, x, y, txt):
        self.pt(x, y, txt, 4.2)

    # ====== v3 新增专业标注 ======
    def roughness(self, x, y, value=3.2, direction="up"):
        px, py = self.v(x, y)
        s = 3.0
        if direction == "up":
            p1 = (px - s, py - s * 1.5); p2 = (px + s, py - s * 1.5); p3 = (px, py)
        else:
            p1 = (px - s, py + s * 1.5); p2 = (px + s, py + s * 1.5); p3 = (px, py)
        self.msp.add_lwpolyline([p1, p2, p3], close=False, dxfattribs={"layer": "尺寸线"})
        ty = py + s * 2.2 if direction == "up" else py - s * 2.2
        self.pt(px, ty, f"Ra {value}", 2.2)

    def gd_tolerance(self, x, y, symbol="⊥", value="0.5", datum="A"):
        w1, w2, w3, h = 10, 14, 10, 5.0
        for i, w in enumerate([w1, w2, w3]):
            self.prect(x + sum([w1, w2, w3][:i]), y, w, h, "表格线")
        self.pt(x + w1 / 2, y + h / 2, symbol, 2.6)
        self.pt(x + w1 + w2 / 2, y + h / 2, value, 2.4)
        self.pt(x + w1 + w2 + w3 / 2, y + h / 2, datum, 2.4)

    def dim_h_tol(self, x1, x2, y, d=10.0, txt=None, tol="+0.5/-0.3"):
        self.dim_h(x1, x2, y, d, txt)
        px1, py = self.v(x1, y); px2, _ = self.v(x2, y)
        s = -1.0 if d > 0 else 1.0
        yl = py + s * abs(d)
        self.pt((px1 + px2) / 2 + 12, yl - 1.0, tol, 1.8, align=ML)

    def dim_v_tol(self, y1, y2, x, d=10.0, txt=None, tol="+0.5/-0.3"):
        self.dim_v(y1, y2, x, d, txt)
        px, py1 = self.v(x, y1); _, py2 = self.v(x, y2)
        s = -1.0 if d > 0 else 1.0
        xl = px + s * abs(d)
        self.pt(xl - 4, (py1 + py2) / 2 + 5, tol, 1.8, align=MR)

    def datum_box(self, x, y, letter="A"):
        s = 5.0
        self.prect(x, y, s, s, "表格线")
        self.pt(x + s / 2, y + s / 2, letter, 2.6)
        px, py = x + s / 2, y
        self.msp.add_lwpolyline([(px - 2, py), (px + 2, py), (px, py - 3)],
                                close=False, dxfattribs={"layer": "尺寸线"})

    def bolt_circle(self, cx, cy, r, n=8, hole_r=11):
        self.mcirc(cx, cy, r, "中心线", "CENTER")
        for i in range(n):
            ang = 2 * math.pi * i / n
            hx = cx + r * math.cos(ang)
            hy = cy + r * math.sin(ang)
            self.mcirc(hx, hy, hole_r)
        self.mcline(cx - r - 30, cy, cx + r + 30, cy)
        self.mcline(cx, cy - r - 30, cx, cy + r + 30)

    def weld_full(self, x, y, k=6, wtype="角焊"):
        px, py = self.v(x, y)
        self.msp.add_line((px - 20, py), (px + 20, py), dxfattribs={"layer": "焊接符号"})
        self.msp.add_lwpolyline([(px - 5, py), (px, py + 6), (px + 5, py)],
                                close=False, dxfattribs={"layer": "焊接符号"})
        self.pt(px + 8, py + 3, f"h={k}", 2.0, align=ML)
        self.pt(px - 12, py + 3, wtype, 2.0, align=MR)

    def rev_center(self, x, y, w, h):
        self.mcline(x - 20, y + h / 2, x + w + 20, y + h / 2)
        self.mcline(x + w / 2, y - 20, x + w / 2, y + h + 20)

    def save(self, path):
        self.doc.saveas(path)

    def png(self, path, dpi=110):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "SimSun"]
        plt.rcParams["axes.unicode_minus"] = False
        from ezdxf.addons.drawing import RenderContext, Frontend
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
        from ezdxf.addons.drawing.properties import LayoutProperties
        fig = plt.figure(figsize=(self.W / 25.4, self.H / 25.4), dpi=dpi)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor("#ffffff")
        st = self.doc.styles.get("HZ")
        orig_font = st.dxf.font
        st.dxf.font = "msyh.ttc"
        try:
            ctx = RenderContext(self.doc)
            lp = LayoutProperties(name="Model", background_color="#FFFFFF")
            Frontend(ctx, MatplotlibBackend(ax, adjust_figure=False)).draw_layout(
                self.doc.modelspace(), finalize=True, layout_properties=lp)
            fig.savefig(path, dpi=dpi, facecolor="#ffffff")
        finally:
            st.dxf.font = orig_font
        plt.close(fig)
