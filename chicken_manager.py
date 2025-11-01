#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
炸鸡店经营管理系统
Fried Chicken Store Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import json
import os
from datetime import datetime

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ChickenStoreManager:
    """炸鸡店经营管理系统主类"""
    
    # 城市级别预设参数
    CITY_PRESETS = {
        '一线城市': {
            'rent': 30000,
            'staff': 40000,
            'utility': 8000,
            'cost_rate': 0.45,
            'avg_price': 35,
            'avg_orders': 150
        },
        '二线城市': {
            'rent': 15000,
            'staff': 24000,
            'utility': 4500,
            'cost_rate': 0.40,
            'avg_price': 25,
            'avg_orders': 100
        },
        '三线城市': {
            'rent': 8000,
            'staff': 15000,
            'utility': 2000,
            'cost_rate': 0.35,
            'avg_price': 18,
            'avg_orders': 80
        }
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title("炸鸡店经营管理系统 v2.0")
        self.root.geometry("1200x800")
        
        # 数据存储
        self.history_file = "store_history.json"
        self.load_history()
        
        # 创建界面
        self.create_widgets()
        
    def load_history(self):
        """加载历史数据"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
        else:
            self.history = []
    
    def save_history(self, data):
        """保存历史数据"""
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append(data)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="炸鸡店经营管理系统", 
                               font=('Arial', 20, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # 左侧输入区域
        input_frame = ttk.LabelFrame(main_frame, text="经营参数设置", padding="10")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # 城市级别选择
        ttk.Label(input_frame, text="城市级别:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.city_var = tk.StringVar(value='二线城市')
        city_combo = ttk.Combobox(input_frame, textvariable=self.city_var, 
                                  values=list(self.CITY_PRESETS.keys()),
                                  state='readonly', width=15)
        city_combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        city_combo.bind('<<ComboboxSelected>>', self.on_city_change)
        
        # 加载预设按钮
        ttk.Button(input_frame, text="加载预设", 
                  command=self.load_preset).grid(row=0, column=2, padx=5)
        
        # 输入字段
        self.entries = {}
        fields = [
            ('客单价 (元)', 'price', '25'),
            ('日均单量', 'orders', '100'),
            ('营业天数/月', 'days', '30'),
            ('房租 (元/月)', 'rent', '15000'),
            ('人工成本 (元/月)', 'staff', '24000'),
            ('水电费 (元/月)', 'utility', '4500'),
            ('直接成本比例 (%)', 'cost_rate', '40'),
            ('变动成本/单 (元)', 'var_cost', '3'),
        ]
        
        for i, (label, key, default) in enumerate(fields, start=1):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(input_frame, width=20)
            entry.insert(0, default)
            entry.grid(row=i, column=1, columnspan=2, sticky=tk.W, pady=5)
            self.entries[key] = entry
        
        # 按钮区域
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=len(fields)+1, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="计算净利润", 
                  command=self.calculate_profit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="敏感性分析", 
                  command=self.sensitivity_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空结果", 
                  command=self.clear_results).pack(side=tk.LEFT, padx=5)
        
        # 右侧结果显示区域
        result_frame = ttk.LabelFrame(main_frame, text="分析结果", padding="10")
        result_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # 结果文本框
        self.result_text = tk.Text(result_frame, width=60, height=20, 
                                   font=('Courier', 10))
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, 
                                 command=self.result_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.result_text['yscrollcommand'] = scrollbar.set
        
        # 底部图表区域
        chart_frame = ttk.LabelFrame(main_frame, text="可视化分析", padding="10")
        chart_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # 创建图表画布
        self.figure = Figure(figsize=(10, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 配置网格权重
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
    
    def on_city_change(self, event):
        """城市级别改变事件"""
        pass
    
    def load_preset(self):
        """加载预设参数"""
        city = self.city_var.get()
        preset = self.CITY_PRESETS[city]
        
        self.entries['rent'].delete(0, tk.END)
        self.entries['rent'].insert(0, str(preset['rent']))
        
        self.entries['staff'].delete(0, tk.END)
        self.entries['staff'].insert(0, str(preset['staff']))
        
        self.entries['utility'].delete(0, tk.END)
        self.entries['utility'].insert(0, str(preset['utility']))
        
        self.entries['cost_rate'].delete(0, tk.END)
        self.entries['cost_rate'].insert(0, str(preset['cost_rate'] * 100))
        
        self.entries['price'].delete(0, tk.END)
        self.entries['price'].insert(0, str(preset['avg_price']))
        
        self.entries['orders'].delete(0, tk.END)
        self.entries['orders'].insert(0, str(preset['avg_orders']))
        
        messagebox.showinfo("提示", f"已加载{city}预设参数")
    
    def get_input_values(self):
        """获取输入值"""
        try:
            values = {
                'price': float(self.entries['price'].get()),
                'orders': int(self.entries['orders'].get()),
                'days': int(self.entries['days'].get()),
                'rent': float(self.entries['rent'].get()),
                'staff': float(self.entries['staff'].get()),
                'utility': float(self.entries['utility'].get()),
                'cost_rate': float(self.entries['cost_rate'].get()) / 100,
                'var_cost': float(self.entries['var_cost'].get()),
                'city': self.city_var.get()
            }
            return values
        except ValueError as e:
            messagebox.showerror("错误", "请输入有效的数值！")
            return None
    
    def calculate_profit(self):
        """计算净利润"""
        values = self.get_input_values()
        if not values:
            return
        
        # 计算各项指标
        sales = values['price'] * values['orders'] * values['days']
        direct_cost = sales * values['cost_rate']
        fixed_cost = values['rent'] + values['staff'] + values['utility']
        total_var_cost = values['var_cost'] * values['orders'] * values['days']
        gross_profit = sales - direct_cost
        net_profit = gross_profit - fixed_cost - total_var_cost
        
        gross_margin = (gross_profit / sales) * 100 if sales > 0 else 0
        net_margin = (net_profit / sales) * 100 if sales > 0 else 0
        
        # 盈亏平衡点计算
        contribution_margin = values['price'] * (1 - values['cost_rate']) - values['var_cost']
        if contribution_margin > 0:
            breakeven_orders = fixed_cost / contribution_margin
            breakeven_daily = breakeven_orders / values['days']
        else:
            breakeven_orders = 0
            breakeven_daily = 0
        
        # 显示结果
        result = f"""
{'='*60}
                    经营分析报告
{'='*60}
城市级别: {values['city']}
营业参数: 客单价 {values['price']:.2f} 元 × 日均 {values['orders']} 单 × {values['days']} 天

【收入分析】
月营业额:          {sales:>15,.2f} 元

【成本分析】
直接成本:          {direct_cost:>15,.2f} 元 ({values['cost_rate']*100:.1f}%)
固定成本:          {fixed_cost:>15,.2f} 元
  - 房租:          {values['rent']:>15,.2f} 元
  - 人工:          {values['staff']:>15,.2f} 元
  - 水电:          {values['utility']:>15,.2f} 元
变动成本:          {total_var_cost:>15,.2f} 元 ({values['var_cost']:.2f}元/单)
总成本:            {direct_cost + fixed_cost + total_var_cost:>15,.2f} 元

【利润分析】
毛利润:            {gross_profit:>15,.2f} 元
净利润:            {net_profit:>15,.2f} 元
毛利率:            {gross_margin:>15.2f} %
净利率:            {net_margin:>15.2f} %

【盈亏平衡点】
月单量:            {breakeven_orders:>15.0f} 单
日单量:            {breakeven_daily:>15.0f} 单/天
"""
        
        if net_profit < 0:
            result += f"\n⚠️  警告: 当前参数下处于亏损状态！\n"
            result += f"   建议: 提升日均单量至 {breakeven_daily:.0f} 单以上，或优化成本结构。\n"
        else:
            result += f"\n✓  盈利状态良好！继续保持。\n"
        
        result += f"{'='*60}\n"
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, result)
        
        # 保存历史记录
        self.save_history({
            'type': 'profit_calculation',
            'values': values,
            'results': {
                'sales': sales,
                'net_profit': net_profit,
                'net_margin': net_margin
            }
        })
        
        # 绘制成本结构图
        self.plot_cost_structure(values, sales, direct_cost, fixed_cost, total_var_cost, net_profit)
    
    def plot_cost_structure(self, values, sales, direct_cost, fixed_cost, var_cost, net_profit):
        """绘制成本结构图"""
        self.figure.clear()
        
        # 创建两个子图
        ax1 = self.figure.add_subplot(121)
        ax2 = self.figure.add_subplot(122)
        
        # 子图1: 成本结构饼图
        costs = [direct_cost, fixed_cost, var_cost, max(0, net_profit)]
        labels = ['直接成本', '固定成本', '变动成本', '净利润']
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        
        # 过滤掉为0的项
        filtered_data = [(cost, label, color) for cost, label, color in zip(costs, labels, colors) if cost > 0]
        if filtered_data:
            costs_filtered, labels_filtered, colors_filtered = zip(*filtered_data)
            ax1.pie(costs_filtered, labels=labels_filtered, autopct='%1.1f%%',
                   colors=colors_filtered, startangle=90)
            ax1.set_title('营业额分配结构')
        
        # 子图2: 利润对比柱状图
        categories = ['营业额', '总成本', '净利润']
        values_bar = [sales, direct_cost + fixed_cost + var_cost, net_profit]
        colors_bar = ['#4CAF50', '#F44336', '#2196F3' if net_profit > 0 else '#F44336']
        
        bars = ax2.bar(categories, values_bar, color=colors_bar, alpha=0.7)
        ax2.set_title('收支对比分析')
        ax2.set_ylabel('金额 (元)')
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:,.0f}',
                    ha='center', va='bottom' if height > 0 else 'top')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def sensitivity_analysis(self):
        """敏感性分析"""
        values = self.get_input_values()
        if not values:
            return
        
        result = f"""
{'='*60}
              客单价与单量敏感性分析
{'='*60}
基准参数: 客单价 {values['price']:.2f} 元, 日均单量 {values['orders']} 单

"""
        
        # 计算固定成本
        fixed_cost = values['rent'] + values['staff'] + values['utility']
        
        # 生成敏感性分析数据
        price_range = [-0.2, -0.1, 0, 0.1, 0.2]  # ±20%
        orders_range = [-0.2, -0.1, 0, 0.1, 0.2]  # ±20%
        
        analysis_data = []
        
        result += f"{'价格变动':<12} {'单量变动':<12} {'月营业额':<15} {'净利润':<15} {'净利率':<10}\n"
        result += f"{'-'*60}\n"
        
        for price_change in price_range:
            for orders_change in orders_range:
                curr_price = values['price'] * (1 + price_change)
                curr_orders = int(values['orders'] * (1 + orders_change))
                
                sales = curr_price * curr_orders * values['days']
                direct_cost = sales * values['cost_rate']
                total_var_cost = values['var_cost'] * curr_orders * values['days']
                net_profit = sales - direct_cost - fixed_cost - total_var_cost
                net_margin = (net_profit / sales * 100) if sales > 0 else 0
                
                analysis_data.append({
                    'price': curr_price,
                    'orders': curr_orders,
                    'profit': net_profit
                })
                
                price_label = f"{price_change:+.0%}"
                orders_label = f"{orders_change:+.0%}"
                
                result += f"{price_label:<12} {orders_label:<12} {sales:>14,.0f} {net_profit:>14,.0f} {net_margin:>9.1f}%\n"
        
        result += f"{'='*60}\n"
        result += "\n💡 分析建议:\n"
        result += "   - 价格弹性: 观察价格变动对利润的影响程度\n"
        result += "   - 单量敏感度: 评估营销投入对单量提升的必要性\n"
        result += "   - 最优组合: 寻找价格与单量的最佳平衡点\n"
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, result)
        
        # 绘制敏感性分析热力图
        self.plot_sensitivity_heatmap(analysis_data, values)
    
    def plot_sensitivity_heatmap(self, data, base_values):
        """绘制敏感性分析图"""
        self.figure.clear()
        
        # 重组数据为矩阵
        price_levels = sorted(set([d['price'] for d in data]))
        orders_levels = sorted(set([d['orders'] for d in data]))
        
        profit_matrix = []
        for price in price_levels:
            row = []
            for orders in orders_levels:
                profit = [d['profit'] for d in data if d['price'] == price and d['orders'] == orders][0]
                row.append(profit)
            profit_matrix.append(row)
        
        # 创建热力图
        ax = self.figure.add_subplot(111)
        im = ax.imshow(profit_matrix, cmap='RdYlGn', aspect='auto')
        
        # 设置坐标轴
        ax.set_xticks(range(len(orders_levels)))
        ax.set_yticks(range(len(price_levels)))
        ax.set_xticklabels([f'{o}单' for o in orders_levels], rotation=45)
        ax.set_yticklabels([f'{p:.1f}元' for p in price_levels])
        
        ax.set_xlabel('日均单量')
        ax.set_ylabel('客单价')
        ax.set_title('敏感性分析热力图 (颜色越绿利润越高)')
        
        # 添加颜色条
        cbar = self.figure.colorbar(im, ax=ax)
        cbar.set_label('净利润 (元)', rotation=270, labelpad=20)
        
        # 在每个格子中显示数值
        for i in range(len(price_levels)):
            for j in range(len(orders_levels)):
                text = ax.text(j, i, f'{profit_matrix[i][j]:,.0f}',
                             ha="center", va="center", color="black", fontsize=8)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def clear_results(self):
        """清空结果"""
        self.result_text.delete(1.0, tk.END)
        self.figure.clear()
        self.canvas.draw()


def main():
    """主函数"""
    root = tk.Tk()
    app = ChickenStoreManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()
