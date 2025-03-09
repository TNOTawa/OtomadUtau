# 1. 导入区 ================================================
import os
import csv
from collections import defaultdict
from tkinter import filedialog, messagebox
from pydub import AudioSegment
import customtkinter as ctk
from utils import parse_time

# 2. 类定义 ================================================
class OTOGenerator(ctk.CTkFrame):
    """OTO.ini生成器模块"""
    
    def __init__(self, parent, controller):
        """
        初始化方法
        :param parent: 父容器
        :param controller: 主程序控制器
        """
        super().__init__(parent)
        self.controller = controller
        
        # 3. 变量初始化 ======================================
        self.audio_path = ""          # 音频文件路径
        self.csv_path = ""            # 标记文件路径
        self.debug_log = []           # 运行日志存储
        self.config = {
            "overlap": 20,          # 默认重叠参数
            "ratio": 0.3             # 默认辅音比例
        }
        
        # 4. 界面构建 ========================================
        self.build_ui()
        
    def build_ui(self):
        """构建用户界面"""
        # 4.1 顶部控制栏 ------------------------------------
        control_bar = ctk.CTkFrame(self)
        control_bar.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            control_bar, 
            text="← 返回主菜单",
            command=lambda: self.controller.show_frame("MainMenu"),
            width=100
        ).pack(side="left")
        
        # 帮助按钮
        ctk.CTkButton(
            control_bar,
            text="帮助",
            command=self.show_help,
            fg_color="transparent",
            width=50
        ).pack(side="right")
        
        # 4.2 主内容区 --------------------------------------
        main_area = ctk.CTkFrame(self)
        main_area.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 操作提示
        note_frame = ctk.CTkFrame(main_area)
        note_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(
            note_frame, 
            text="操作步骤：1. 选择音频文件 → 2. 选择标记文件 → 3. 设置参数 → 4. 生成"
        ).grid(row=0, column=0, padx=5)
        
        # 文件选择区域
        file_frame = ctk.CTkFrame(main_area)
        file_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(
            file_frame,
            text="选择音频文件",
            command=self.select_audio
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            file_frame,
            text="选择标记文件",
            command=self.select_csv
        ).pack(side="left", padx=5)
        
        # 参数输入区域
        param_frame = ctk.CTkFrame(main_area)
        param_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(param_frame, text="重叠时间(ms):").grid(row=0, column=0, padx=5)
        self.overlap_entry = ctk.CTkEntry(param_frame, width=120)
        self.overlap_entry.insert(0, str(self.config["overlap"]))
        self.overlap_entry.grid(row=0, column=1, padx=5)
        
        ctk.CTkLabel(param_frame, text="辅音比例:").grid(row=0, column=2, padx=5)
        self.ratio_entry = ctk.CTkEntry(param_frame, width=120)
        self.ratio_entry.insert(0, str(self.config["ratio"]))
        self.ratio_entry.grid(row=0, column=3, padx=5)
        
        # 4.3 日志显示区 ------------------------------------
        self.console = ctk.CTkTextbox(main_area, height=150)
        self.console.pack(fill="x", pady=10)
        
        # 4.4 操作按钮 --------------------------------------
        action_frame = ctk.CTkFrame(main_area)
        action_frame.pack(pady=10)
        
        ctk.CTkButton(
            action_frame,
            text="生成配置文件",
            command=self.generate_oto
        ).pack(side="left", padx=20)
        
        ctk.CTkButton(
            action_frame,
            text="打开输出目录",
            command=self.open_output_dir
        ).pack(side="left", padx=20)
    
    # 5. 核心方法 ==========================================
    def select_audio(self):
        """音频文件选择方法"""
        self.audio_path = filedialog.askopenfilename(
            filetypes=[("音频文件", "*.wav *.mp3")]
        )
        if self.audio_path:
            self.log(f"已加载音频文件: {os.path.basename(self.audio_path)}")
            
    def select_csv(self):
        """标记文件选择方法"""
        self.csv_path = filedialog.askopenfilename(
            filetypes=[("CSV 文件", "*.csv")]
        )
        if self.csv_path:
            self.log(f"已加载标记文件: {os.path.basename(self.csv_path)}")

    def validate_inputs(self):
        """输入验证"""
        error_msgs = []
        if not os.path.exists(self.audio_path):
            error_msgs.append("请先选择音频文件")
        if not os.path.exists(self.csv_path):
            error_msgs.append("请先选择标记文件")
        
        try:
            self.config["overlap"] = float(self.overlap_entry.get())
        except ValueError:
            error_msgs.append("重叠时间必须为数字")
            
        try:
            self.config["ratio"] = float(self.ratio_entry.get())
            if not 0 <= self.config["ratio"] <= 1:
                error_msgs.append("辅音比例必须在0-1之间")
        except ValueError:
            error_msgs.append("辅音比例必须为数字")
            
        if error_msgs:
            raise ValueError("\n".join(error_msgs))
    
    def generate_oto(self):
        """生成主逻辑"""
        try:
            self.console.delete("1.0", "end")
            self.validate_inputs()
            oto_entries = self.process_markers()
            self.save_result(oto_entries)
            messagebox.showinfo("完成", "oto.ini 文件生成成功！")
        except Exception as e:
            messagebox.showerror("生成错误", str(e))
            self.log(f"错误: {str(e)}")
    
    # 6. 辅助方法 ==========================================
    def log(self, message):
        """统一日志记录"""
        self.debug_log.append(message)
        self.console.insert("end", message + "\n")
        self.console.see("end")
    
    def validate_inputs(self):
        """输入验证"""
        error_msgs = []
        if not os.path.exists(self.audio_path):
            error_msgs.append("请先选择音频文件")
        if not os.path.exists(self.csv_path):
            error_msgs.append("请先选择标记文件")
        
        try:
            self.config["overlap"] = float(self.overlap_entry.get())
        except ValueError:
            error_msgs.append("重叠时间必须为数字")
            
        try:
            self.config["ratio"] = float(self.ratio_entry.get())
            if not 0 <= self.config["ratio"] <= 1:
                error_msgs.append("辅音比例必须在0-1之间")
        except ValueError:
            error_msgs.append("辅音比例必须为数字")
        
        if error_msgs:
            raise ValueError("\n".join(error_msgs))
    
    def process_markers(self):
        """处理标记核心逻辑"""
        audio = AudioSegment.from_file(self.audio_path)
        total_duration = len(audio)
        self.log(f"音频总时长: {total_duration}ms")
        
        # CSV解析逻辑
        cues = []
        with open(self.csv_path, encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                try:
                    start = parse_time(row['Start'])
                    duration = parse_time(row['Duration'])
                    cues.append({
                        'name': row['Name'],
                        'start': start,
                        'end': start + duration,
                        'duration': duration
                    })
                except Exception as e:
                    self.log(f"跳过无效行: {row} | 错误: {e}")
        
        # 处理每个标记
        oto_entries = []
        alias_map = defaultdict(int)
        
        for idx, cue in enumerate(cues):
            if cue['name'] == 'r':
                continue

            # 搜索关联的r标记
            pre_utterance = None
            for r_cue in cues:
                if r_cue['name'] == 'r' and cue['start'] <= r_cue['start'] < cue['end']:
                    pre_utterance = r_cue['start'] - cue['start']
                    break

            # 计算参数
            parameters = {
                'pre_utterance': pre_utterance or self.config["overlap"],
                'left_blank': cue['start'],
                'right_blank': total_duration - cue['end'],
                'consonant': (cue['duration'] - (pre_utterance or 0)) * self.config["ratio"],
                'overlap': self.config["overlap"]
            }

            # 处理别名冲突
            base_name = cue['name']
            alias_map[base_name] += 1
            alias = base_name if alias_map[base_name] == 1 else f"{base_name}{alias_map[base_name]-1}"

            # 构建条目
            entry = (
                f"{os.path.basename(self.audio_path)}="
                f"{alias},"
                f"{parameters['left_blank']:.3f},"
                f"{parameters['consonant']:.3f},"
                f"{parameters['right_blank']:.3f},"
                f"{parameters['pre_utterance']:.3f},"
                f"{parameters['overlap']:.3f}"
            )
            oto_entries.append(entry)
            self.log(f"生成条目: {alias}")
        
        return oto_entries
    
    def save_result(self, entries):
        """保存结果文件"""
        output_path = os.path.join(
            os.path.dirname(self.audio_path), 
            "oto.ini"
        )
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(entries))
        self.log(f"文件已保存至: {output_path}")

    def open_output_dir(self):
        """打开输出目录"""
        path = os.path.abspath(os.path.dirname(self.audio_path))
        os.startfile(path)
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """使用说明：
1. 音频文件：WAV格式16位单声道文件（UTAU的音频格式要求）
2. 标记文件：需要Audition导出的CSV标记文件
3. 参数说明：
   - 重叠时间：推荐15-50ms
   - 辅音比例：0.3左右"""
        messagebox.showinfo("帮助文档", help_text)

if __name__ == "__main__":
    # 模块测试
    ctk.set_appearance_mode("System")
    test_app = ctk.CTk()
    test_app.geometry("800x600")
    OTOGenerator(test_app, None).pack(fill="both", expand=True)
    test_app.mainloop()
