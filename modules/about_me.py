import customtkinter as ctk
import threading
import requests
from datetime import datetime
from tkinter import filedialog, messagebox

class AboutMeModule(ctk.CTkFrame):
    """关于与开发者信息模块（含GitHub集成）"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.release_data = None  # 存储版本信息
        self.contributors = []    # 存储贡献者数据
        
        # 界面初始化后加载数据
        self.build_ui()
        self.start_loading_data()

    def build_ui(self):
        # ================= 界面结构 =================
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # 让内容区域可以扩展

        # 1. 顶部控制栏
        control_bar = ctk.CTkFrame(self)
        control_bar.grid(row=0, column=0, sticky="ew", pady=5)

        ctk.CTkButton(
            control_bar,
            text="← 返回主菜单",
            command=lambda: self.controller.show_frame("MainMenu"),
            width=100
        ).pack(side="left", padx=10)

        # 2. 主内容区 - 使用 CTkScrollableFrame
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)  # 使用 sticky="nsew" 填充剩余空间
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        title_art = r"""
      ::::::::   :::::::::::       ::::::::         :::   :::           :::        :::::::::
    :+:    :+:      :+:          :+:    :+:       :+:+: :+:+:        :+: :+:      :+:    :+:
   +:+    +:+      +:+          +:+    +:+      +:+ +:+:+ +:+      +:+   +:+     +:+    +:+ 
  +#+    +:+      +#+          +#+    +:+      +#+  +:+  +#+     +#++:++#++:    +#+    +:+  
 +#+    +#+      +#+          +#+    +#+      +#+       +#+     +#+     +#+    +#+    +#+   
#+#    #+#      #+#          #+#    #+#      #+#       #+#     #+#     #+#    #+#    #+#    
########       ###           ########       ###       ###     ###     ###    #########     
                                    
       OtomadUtau v1                      :::    :::   :::::::::::           :::       :::    ::: 
            Just a ToolBox               :+:    :+:       :+:             :+: :+:     :+:    :+:  
                                        +:+    +:+       +:+            +:+   +:+    +:+    +:+   
                                       +#+    +:+       +#+           +#++:++#++:   +#+    +:+    
                                      +#+    +#+       +#+           +#+     +#+   +#+    +#+     
                                     #+#    #+#       #+#           #+#     #+#   #+#    #+#      
                                     ########        ###           ###     ###    ########         
        """
        ctk.CTkLabel(self.scrollable_frame, 
                    text=title_art,
                    font=ctk.CTkFont(family="Courier", size=14),
                    text_color="#5E81AC").pack(pady=10)

        # 软件简介
        about_text = """
✦ 软件简介 ✦
━━━━━━━━━━━━━━━━━━━━━━
版本：v0.1 | 开发者：TNOT
━━━━━━━━━━━━━━━━━━━━━━
（注：制作中使用了AI编程）
一款为UTAU式人力制作而生的工具箱
欢迎大家提Issue和交PR！
本人第一次接触开源社区，哪些规矩要是踩雷了请指出！
━━━━━━━━━━━━━━━━━━━━━━

        """
        ctk.CTkLabel(self.scrollable_frame, 
                    text=about_text,
                    font=ctk.CTkFont(size=14),
                    justify="left").pack(pady=15)

        # 社交平台
        social_text = """
⚡ 与我联系 ⚡
━━━━━━━━━━━━━━━━━━━━━━
GitHub  ▸ github.com/TNOTawa
BiliBili▸ space.bilibili.com/1673962232
QQ      ▸ 1028235739
邮箱    ▸ tnot123@outlook.com
        """
        ctk.CTkLabel(self.scrollable_frame, 
                    text=social_text,
                    font=ctk.CTkFont(family="Consolas", size=14),
                    text_color="#88C0D0",
                    justify="left").pack(pady=10)

        # 版本声明
        ctk.CTkLabel(self.scrollable_frame,
                    text="© 2025 TNOTawa | MIT License | see the 'LICENSE' file for details",
                    font=ctk.CTkFont(size=10),
                    text_color="#4C566A").pack(side="bottom", pady=15)
        # ================= 新增版本信息区域 =================
        self.version_frame = ctk.CTkFrame(self.scrollable_frame)
        self.version_frame.pack(fill="x", pady=10)
        
        # 版本信息加载状态
        self.version_label = ctk.CTkLabel(
            self.version_frame, 
            text="🔄 正在获取版本信息...",
            text_color="#EBCB8B"
        )
        self.version_label.pack()
        
        # ================= 新增贡献者区域 ====================
        self.contributors_frame = ctk.CTkFrame(self.scrollable_frame)
        self.contributors_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            self.contributors_frame,
            text="🌟 项目贡献者",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w")
        
        scrollbar = ctk.CTkScrollbar(self.contributors_frame)
        scrollbar.pack(side="right", fill="y")

        self.contributors_text = ctk.CTkTextbox(
            self.contributors_frame, 
            height=80,
            activate_scrollbars=False
        )
        self.contributors_text.pack(fill="x")


    def start_loading_data(self):
        """启动数据加载线程"""
        threading.Thread(
            target=self.fetch_github_data, 
            daemon=True
        ).start()

    def fetch_github_data(self):
        """从GitHub API获取数据"""
        try:
            # 获取最新版本
            releases_url = f"https://api.github.com/repos/TNOTawa/OtomadUtau/releases"
            releases = requests.get(releases_url).json()
            if releases:
                latest_release = releases[0]
                self.release_data = {
                    "tag": latest_release["tag_name"],
                    "date": datetime.strptime(
                        latest_release["published_at"], 
                        "%Y-%m-%dT%H:%M:%SZ"
                    ).strftime("%Y-%m-%d"),
                    "notes": latest_release["body"]
                }

            # 获取贡献者
            contributors_url = f"https://api.github.com/repos/TNOTawa/OtomadUtau/contributors"
            self.contributors = requests.get(contributors_url).json()

            # 更新UI
            self.after(0, self.update_ui_with_data)

        except Exception as e:
            self.after(0, lambda e=e: self.show_data_error(str(e)))  # 直接在 lambda 中捕获 e

    def update_ui_with_data(self):
        """用API数据更新界面"""
        # 更新版本信息
        if self.release_data:
            version_text = (
                f"✅ 最新版本: {self.release_data['tag']} "
                f"(发布日期: {self.release_data['date']})\n"
                f"📝 更新日志: {self.release_data['notes'][:150]}..."
            )
            self.version_label.configure(
                text=version_text,
                text_color="#A3BE8C"
            )
            
            # 添加检查更新按钮
            ctk.CTkButton(
                self.version_frame,
                text="立即更新",
                command=self.check_for_update,
                width=80
            ).pack(side="right", padx=10)
        
        # 更新贡献者列表
        if self.contributors:
            contributors_list = "  ".join(
                [f"👤 {user['login']}" for user in self.contributors]
            )
            self.contributors_text.insert("1.0", contributors_list)
            
    def check_for_update(self):
        """版本更新检查逻辑"""
        current_version = "v2.1.0"  # 应从实际配置读取
        if self.release_data and self.release_data["tag"] > current_version:
            messagebox.showinfo(
                "发现新版本",
                f"最新版本 {self.release_data['tag']} 可用！\n"
                f"更新内容：\n{self.release_data['notes'][:300]}..."
            )
        else:
            messagebox.showinfo("提示", "当前已是最新版本")

    def show_data_error(self, error_msg):
        """显示数据加载错误"""
        self.version_label.configure(
            text=f"oopz……数据加载失败！: {error_msg}",
            text_color="#BF616A"
        )

if __name__ == "__main__":
    # 模块单独测试（开发时使用）
    ctk.set_appearance_mode("System")
    test_app = ctk.CTk()
    test_app.geometry("800x600")
    AboutMeModule(test_app, None).pack(fill="both", expand=True)
    test_app.mainloop()