# main_menu.py
import customtkinter as ctk

class MainMenu(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="transparent")
        
        # 功能模块配置
        self.modules = [
            {"name": "OTO 工厂", "icon": "🎵", "color": "#2E7D32", "page": "OTOGenerator"},
            {"name": "关于", "icon": "❓", "color": "#1565C0", "page": "AboutMeModule"},
        ]
        
        # 主容器
        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 创建模块网格
        self.create_module_grid()

    def create_module_grid(self):
        """创建模块化网格布局"""
        # 配置网格参数
        columns = 4
        for i in range(columns):
            self.main_container.grid_columnconfigure(i, weight=1)
        
        # 动态生成模块卡片
        for index, module in enumerate(self.modules):
            col = index % columns
            row = index // columns
            
            card = ModuleCard(
                parent=self.main_container,
                name=module["name"],
                icon=module["icon"],
                color=module["color"],
                command=lambda p=module["page"]: self.controller.show_frame(p) if p else None
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

class ModuleCard(ctk.CTkFrame):
    """自定义模块卡片组件"""
    def __init__(self, parent, name, icon, color, command=None):
        super().__init__(parent, width=150, height=150, corner_radius=15)
        self._command = command
        
        # 样式配置
        self.configure(border_width=2, border_color="#444444", fg_color="#333333")
        
        # 主容器
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, padx=20, pady=20)
        
        # 图标部分
        self.icon_label = ctk.CTkLabel(
            self.container,
            text=icon,
            font=("Arial", 48),
            fg_color=color,
            corner_radius=20,
            width=100,
            height=100
        )
        self.icon_label.pack(pady=(0, 15))
        
        # 名称标签
        self.name_label = ctk.CTkLabel(
            self.container,
            text=name,
            font=("Microsoft YaHei", 14),
            wraplength=160
        )
        self.name_label.pack()
        
        # 绑定点击事件
        self.bind("<Button-1>", self.on_click)
        self.icon_label.bind("<Button-1>", self.on_click)
        self.name_label.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        """处理点击事件"""
        self._command()
