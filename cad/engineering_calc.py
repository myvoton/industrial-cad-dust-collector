# -*- coding: utf-8 -*-
"""
工程计算模块 —— 脉冲布袋除尘器设计校核
基于 GB/T 6719、JB/T 8532 标准，所有计算自动校核并输出到图纸技术特性表
"""
import math


class BaghouseCalc:
    """脉冲布袋除尘器工程计算"""

    def __init__(self, Q=50000.0, v_filter=0.96, bag_D=130, bag_L=6000,
                 n_room=6, bag_per_room=60, dp_in=1200, hp_in=1600,
                 dp_out=1200, hp_out=1600, temp=120, pressure_drop=1500,
                 power_air=0.5, pulse_valve_model="DMF-Y-76S"):
        self.Q = Q
        self.v_filter = v_filter
        self.bag_D = bag_D
        self.bag_L = bag_L
        self.n_room = n_room
        self.bag_per_room = bag_per_room
        self.dp_in = dp_in
        self.hp_in = hp_in
        self.dp_out = dp_out
        self.hp_out = hp_out
        self.temp = temp
        self.pressure_drop = pressure_drop
        self.power_air = power_air
        self.pulse_valve_model = pulse_valve_model

    @property
    def n_bag(self):
        return self.n_room * self.bag_per_room

    @property
    def bag_area(self):
        return math.pi * (self.bag_D / 1000.0) * (self.bag_L / 1000.0)

    @property
    def total_filter_area(self):
        return self.n_bag * self.bag_area

    @property
    def actual_v_filter(self):
        return (self.Q / 60.0) / self.total_filter_area

    def check_filter_velocity(self):
        v = self.actual_v_filter
        if v < 0.6:
            return f"偏低({v:.2f} m/min)，建议增加滤袋长度或减少滤袋数"
        elif v > 1.2:
            return f"偏高({v:.2f} m/min)，建议增加滤袋数或减少处理风量"
        else:
            return f"合格({v:.2f} m/min)"

    @property
    def inlet_area(self):
        return (self.dp_in / 1000.0) * (self.hp_in / 1000.0)

    @property
    def outlet_area(self):
        return (self.dp_out / 1000.0) * (self.hp_out / 1000.0)

    @property
    def inlet_velocity(self):
        return (self.Q / 3600.0) / self.inlet_area

    @property
    def outlet_velocity(self):
        return (self.Q / 3600.0) / self.outlet_area

    def check_duct_velocity(self):
        vi = self.inlet_velocity
        vo = self.outlet_velocity
        status = []
        if vi < 12:
            status.append(f"进口风速偏低({vi:.1f} m/s)")
        elif vi > 18:
            status.append(f"进口风速偏高({vi:.1f} m/s)")
        else:
            status.append(f"进口风速合格({vi:.1f} m/s)")
        if vo < 12:
            status.append(f"出口风速偏低({vo:.1f} m/s)")
        elif vo > 18:
            status.append(f"出口风速偏高({vo:.1f} m/s)")
        else:
            status.append(f"出口风速合格({vo:.1f} m/s)")
        return "；".join(status)

    @property
    def valves_per_room(self):
        return math.ceil(self.bag_per_room / 6.0)

    @property
    def total_valves(self):
        return self.valves_per_room * self.n_room

    @property
    def air_consumption_per_valve(self):
        return 0.15

    @property
    def air_consumption_per_cycle(self):
        return self.total_valves * self.air_consumption_per_valve

    @property
    def air_receiver_volume(self):
        v = self.air_consumption_per_cycle * 3 / 0.3
        return v

    @staticmethod
    def steel_plate_weight(length, width, thickness, density=7.85):
        return (length / 10.0) * (width / 10.0) * (thickness / 10.0) * density

    def calc_pressure_drop(self):
        filter_resistance = 1200
        duct_resistance = 200
        damper_resistance = 100
        total = filter_resistance + duct_resistance + damper_resistance
        return {
            "过滤阻力": filter_resistance,
            "管道阻力": duct_resistance,
            "风门阻力": damper_resistance,
            "总阻力": total,
        }

    def chimney_diameter(self, velocity=12.0):
        area = (self.Q / 3600.0) / velocity
        d = math.sqrt(4 * area / math.pi) * 1000
        return round(d, 0)

    def summary(self):
        return {
            "处理风量": f"{self.Q:.0f} m³/h",
            "总过滤面积": f"{self.total_filter_area:.1f} m²",
            "过滤风速(设计)": f"{self.v_filter:.2f} m/min",
            "过滤风速(实际)": f"{self.actual_v_filter:.2f} m/min",
            "风速校核": self.check_filter_velocity(),
            "滤袋数量": f"{self.n_bag} 条",
            "单袋面积": f"{self.bag_area:.2f} m²",
            "分室数": f"{self.n_room} 室",
            "进口风速": f"{self.inlet_velocity:.1f} m/s",
            "出口风速": f"{self.outlet_velocity:.1f} m/s",
            "风管校核": self.check_duct_velocity(),
            "脉冲阀型号": self.pulse_valve_model,
            "每室阀数": f"{self.valves_per_room} 只",
            "总阀数": f"{self.total_valves} 只",
            "单次喷吹耗气": f"{self.air_consumption_per_cycle:.2f} m³",
            "气包容积(建议)": f"{self.air_receiver_volume:.2f} m³",
            "设备阻力": f"{self.pressure_drop} Pa",
            "压缩空气压力": f"{self.power_air:.1f} MPa",
            "气体温度": f"{self.temp} ℃",
        }


class NestingOptimizer:
    """钢板套裁优化（货架式 shelf algorithm）"""

    def __init__(self, sheet_width=2200, sheet_length=6000, gap=30):
        self.SW = sheet_width
        self.SL = sheet_length
        self.gap = gap

    def optimize(self, parts):
        parts_sorted = sorted(parts, key=lambda p: p[1], reverse=True)
        sheets = []
        remaining = []
        for w, h, qty in parts_sorted:
            for _ in range(qty):
                remaining.append([w, h])
        remaining.sort(key=lambda p: p[1], reverse=True)
        while remaining:
            sheet = {"parts": [], "rows": []}
            row_h = 0
            row_w = 0
            row_parts = []
            i = 0
            while i < len(remaining):
                w, h = remaining[i]
                if row_w + w + self.gap <= self.SL and h <= self.SW - row_h:
                    row_parts.append((row_w, row_h, w, h))
                    row_w += w + self.gap
                    if h > row_h:
                        row_h = h
                    remaining.pop(i)
                else:
                    i += 1
            if row_parts:
                sheet["parts"].extend(row_parts)
                row_h += self.gap
                while remaining:
                    row2_h = 0
                    row2_w = 0
                    row2_parts = []
                    i = 0
                    while i < len(remaining):
                        w, h = remaining[i]
                        if row2_w + w + self.gap <= self.SL and h <= self.SW - row_h:
                            row2_parts.append((row2_w, row_h, w, h))
                            row2_w += w + self.gap
                            if h > row2_h:
                                row2_h = h
                            remaining.pop(i)
                        else:
                            i += 1
                    if not row2_parts:
                        break
                    sheet["parts"].extend(row2_parts)
                    row_h += row2_h + self.gap
            sheets.append(sheet)
        total_area = self.SW * self.SL * len(sheets)
        used_area = sum(w * h for s in sheets for _, _, w, h in s["parts"])
        utilization = used_area / total_area * 100 if total_area > 0 else 0
        return sheets, round(utilization, 1)


if __name__ == "__main__":
    calc = BaghouseCalc(Q=50000, v_filter=0.96, bag_D=130, bag_L=6000,
                        n_room=6, bag_per_room=60)
    print("=" * 50)
    print("50000 m³/h 脉冲布袋除尘器 工程计算")
    print("=" * 50)
    for k, v in calc.summary().items():
        print(f"{k:20s}: {v}")
    print("\n" + "=" * 50)
    print("钢板套裁优化")
    print("=" * 50)
    nest = NestingOptimizer(2200, 6000)
    parts = [(2870, 2130, 18), (2740, 2130, 6), (2870, 1800, 9), (2740, 1700, 6)]
    sheets, util = nest.optimize(parts)
    print(f"套裁板数: {len(sheets)}")
    print(f"综合利用率: {util}%")
