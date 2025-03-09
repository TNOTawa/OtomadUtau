import customtkinter as ctk
from main_menu import MainMenu
import sys
import os

class OtomadUtau(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("OtomadUtau - 为UTAU式人力制作而生的工具箱")
        self.geometry("800x600")
        self.minsize(800, 600)
        
        # Windows风格配置
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # DPI适配
        self.tk.call('tk', 'scaling', 1.4 if self._get_dpi() > 120 else 1.0)
        
        # 初始化容器
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        
        # 加载页面系统
        self.frames = {}
        self.show_frame("MainMenu")

    def _get_dpi(self):
        """获取系统DPI"""
        try:
            from ctypes import windll
            return windll.user32.GetDpiForWindow(self.winfo_id())
        except:
            return 96
        
    def show_frame(self, page_name):
        """显示指定页面（添加模块在这里）"""
        if page_name not in self.frames:
            # 动态导入页面模块
            if page_name == "OTOGenerator":
                from modules.aulabel2oto import OTOGenerator
                self.frames[page_name] = OTOGenerator(self.container, self)
            elif page_name == "AboutMeModule":
                from modules.about_me import AboutMeModule
                self.frames[page_name] = AboutMeModule(self.container, self)
            elif page_name == "MainMenu":
                self.frames[page_name] = MainMenu(self.container, self)
        
        # 隐藏所有页面
        for frame in self.frames.values():
            frame.pack_forget()
        
        # 显示目标页面
        frame = self.frames[page_name]
        frame.pack(fill="both", expand=True)

        

if __name__ == "__main__":
    app = OtomadUtau()
    app.mainloop()