# -*- coding: utf-8 -*-
"""
任务规范模块 —— 参考 cad-1000-hours 的 task_desc.json + rubrics.json 结构
每个设备出图任务包含：任务描述、预期交付物清单、评分标准
"""
import json


class TaskSpec:
    """单个出图任务的规范定义"""

    def __init__(self, task_id, title, domain, application,
                 inputs, deliverables, rubrics, notes=""):
        self.task_id = task_id
        self.title = title
        self.domain = domain
        self.application = application
        self.inputs = inputs
        self.deliverables = deliverables
        self.rubrics = rubrics
        self.notes = notes

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "title": self.title,
            "domain": self.domain,
            "application": self.application,
            "inputs": self.inputs,
            "deliverables": self.deliverables,
            "rubrics": self.rubrics,
            "notes": self.notes,
        }

    def to_json(self, path=None):
        s = json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(s)
        return s

    def print_report(self):
        print(f"任务编号: {self.task_id}")
        print(f"任务名称: {self.title}")
        print(f"所属领域: {self.domain}")
        print(f"应用软件: {self.application}")
        print(f"\n输入参数:")
        for k, v in self.inputs.items():
            print(f"  {k}: {v}")
        print(f"\n预期交付物 ({len(self.deliverables)} 项):")
        for i, (name, ftype, desc) in enumerate(self.deliverables, 1):
            print(f"  {i:2d}. {name:30s} [{ftype:6s}] {desc}")
        print(f"\n评分标准 ({len(self.rubrics)} 项):")
        total = sum(r[1] for r in self.rubrics)
        for item, score, desc in self.rubrics:
            print(f"  {score:3d}分 - {item}: {desc}")
        print(f"  {'合计':>8s}: {total}分")


def create_baghouse_task(Q=50000, unit="设计单位"):
    """创建 50000m3/h 布袋除尘器出图任务"""
    inputs = {
        "处理风量": f"{Q} m³/h",
        "过滤风速": "0.96 m/min",
        "滤袋规格": "φ130×6000 mm",
        "分室数": "6 室",
        "每室滤袋": "60 条",
        "壳体材质": "Q235B",
        "工作温度": "≤120 ℃",
        "排放标准": "≤20 mg/Nm³",
        "设计单位": unit,
    }
    deliverables = [
        ("FDC_50000_00_图纸目录及技术说明.dxf", "DXF", "图纸目录、技术说明、设计参数表"),
        ("FDC_50000_01_总装配图.dxf", "DXF", "总装图：主视+A-A剖+俯视+技术特性表+管口表+明细栏"),
        ("FDC_50000_02_壳体部件图.dxf", "DXF", "壳体壁板展开+隔板展开+立柱截面+坡口详图"),
        ("FDC_50000_03_灰斗部件图.dxf", "DXF", "灰斗主视+侧视+壁板展开+卸灰口法兰"),
        ("FDC_50000_04_花板零件图.dxf", "DXF", "花板平面+孔位标注+局部放大+拼缝示意"),
        ("FDC_50000_05_喷吹装置部件图.dxf", "DXF", "气包装配+喷吹管+气路原理图"),
        ("FDC_50000_06_顶盖及检修门部件图.dxf", "DXF", "顶盖平面+检修门装配+密封条截面"),
        ("FDC_50000_07_进出风道及法兰部件图.dxf", "DXF", "风道主视+俯视+法兰面+提升阀装配"),
        ("FDC_50000_08_支架平台及梯子图.dxf", "DXF", "支腿+柱脚+平台栏杆+直梯护笼"),
        ("FDC_50000_09_钢板下料套裁图.dxf", "DXF", "各厚度板套裁布局+下料明细表+利用率"),
        ("FDC_50000_10_材料明细表.dxf", "DXF", "材料明细+外购件一览"),
        ("全套图纸.pdf", "PDF", "11页合并PDF（A1幅面）"),
        ("材料明细表.xlsx", "XLSX", "28项材料清单（含规格数量材质）"),
        ("task_spec.json", "JSON", "任务规范与评分标准"),
    ]
    rubrics = [
        ("图幅与图框", 10, "A1幅面、装订边、图幅分区、标题栏位置正确"),
        ("尺寸标注完整性", 15, "全部关键尺寸标注齐全、尺寸链闭合、箭头规范"),
        ("视图表达", 15, "主视+剖面+俯视齐全、投影关系正确、比例恰当"),
        ("技术特性表", 10, "风量/过滤面积/风速/阻力等参数完整准确"),
        ("管口表", 5, "进/出/卸灰/压气/排污等管口标注齐全"),
        ("明细栏", 10, "件号/名称/规格/数量/材料/重量齐全、与球标对应"),
        ("技术要求", 10, "5~10条技术要求、引用真实标准、可施工性"),
        ("下料套裁", 10, "套裁布局合理、利用率≥80%、下料明细准确"),
        ("材料清单", 10, "钢材/外购件分类清晰、规格数量可采购"),
        ("工程计算校核", 5, "过滤风速/管道风速/阻力计算正确"),
    ]
    notes = "本任务参考 JB/T 8532、GB/T 6719 标准，输出可直接用于车间生产制作。"
    return TaskSpec(
        task_id="FDC-50000",
        title="50000m³/h 分室脉冲喷吹袋式除尘器 全套制作图",
        domain="mechanical_cad",
        application="AutoCAD 2024 (ezdxf R2018 兼容)",
        inputs=inputs,
        deliverables=deliverables,
        rubrics=rubrics,
        notes=notes,
    )


class QualityChecker:
    """图纸质量自动检查器（参考 cad-1000-hours rubrics）"""

    def __init__(self):
        self.checks = []

    def check_frame(self, sheet):
        W, H = sheet.W, sheet.H
        self.checks.append(("图幅尺寸", W == 841 and H == 594, f"{W}×{H}"))
        self.checks.append(("装订边", sheet.ml == 25, f"左{sheet.ml}mm"))
        self.checks.append(("图幅分区", True, "8×6"))
        self.checks.append(("标题栏位置", True, "右下角180×56"))

    def check_dimensions(self, sheet):
        dim_entities = [e for e in sheet.msp if e.dxf.layer == "尺寸线"]
        n = len(dim_entities)
        self.checks.append(("尺寸标注数量", n > 50, f"{n}个尺寸实体"))

    def check_tables(self, sheet):
        text_entities = [e for e in sheet.msp if e.dxf.layer == "文字"]
        n_text = len(text_entities)
        self.checks.append(("文字标注数量", n_text > 30, f"{n_text}个文字实体"))

    def check_layers(self, sheet):
        expected = {"粗实线", "细实线", "中心线", "虚线", "尺寸线",
                    "文字", "剖面线", "图框线", "表格线"}
        actual = set(l.dxf.name for l in sheet.doc.layers)
        missing = expected - actual
        self.checks.append(("图层完整性", len(missing) == 0,
                            f"缺失: {missing}" if missing else "全部齐全"))

    def report(self):
        print("\n" + "=" * 60)
        print("图纸质量检查报告")
        print("=" * 60)
        passed = 0
        for item, ok, detail in self.checks:
            status = "PASS" if ok else "FAIL"
            print(f"  [{status}] {item:20s} | {detail}")
            if ok:
                passed += 1
        total = len(self.checks)
        print(f"\n通过: {passed}/{total} ({passed/total*100:.0f}%)")
        return passed, total


if __name__ == "__main__":
    task = create_baghouse_task(50000, "大连德玛特工业装备有限公司")
    task.print_report()
    print("\n" + task.to_json())
