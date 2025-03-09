import csv
import os
from collections import defaultdict
from pydub import AudioSegment
import customtkinter as ctk
from tkinter import filedialog, messagebox
from utils import parse_time

class OTOGenerator(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.audio_path = ""
        self.csv_path = ""
        self.debug_log = []  # 初始化日志存储
        
        # 创建返回按钮
        back_btn = ctk.CTkButton(self, text="← 返回主菜单", 
                               command=lambda: controller.show_frame("MainMenu"),
                               width=100)
        back_btn.pack(anchor="nw", padx=10, pady=10)
        
        # 主界面布局
        self.create_widgets()
        
    def create_widgets(self):
        """创建OTO生成器界面"""
        # 文件选择部分
        file_frame = ctk.CTkFrame(self)
        file_frame.pack(pady=10, fill="x", padx=10)

        ctk.CTkButton(file_frame, text="1. 选择音频文件", command=self.select_audio).pack(side="left", padx=5)
        ctk.CTkButton(file_frame, text="2. 选择标记文件", command=self.select_csv).pack(side="left", padx=5)

        # 参数输入
        param_frame = ctk.CTkFrame(self)
        param_frame.pack(pady=10, fill="x", padx=10)

        ctk.CTkLabel(param_frame, text="Overlap (ms):").grid(row=0, column=0, padx=5)
        self.overlap_entry = ctk.CTkEntry(param_frame, width=120)
        self.overlap_entry.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(param_frame, text="Consonant 比例:").grid(row=0, column=2, padx=5)
        self.ratio_entry = ctk.CTkEntry(param_frame, width=120)
        self.ratio_entry.grid(row=0, column=3, padx=5)

        # 进度条
        self.progress = ctk.CTkProgressBar(self, mode='indeterminate')

        # 日志显示
        self.console = ctk.CTkTextbox(self, width=750, height=200)
        self.console.pack(pady=10, padx=10)

        # 结果操作按钮
        self.result_frame = ctk.CTkFrame(self)
        ctk.CTkButton(
            self.result_frame,
            text="打开输出目录",
            command=self.open_output_dir
        ).pack(side="left", padx=5)

        # 生成按钮
        ctk.CTkButton(self, text="生成 oto.ini", command=self.generate).pack(pady=10)

    def select_audio(self):
        self.audio_path = filedialog.askopenfilename(filetypes=[("音频文件", "*.wav *.mp3")])
        self.log(f"已选择音频文件: {os.path.basename(self.audio_path)}")

    def select_csv(self):
        self.csv_path = filedialog.askopenfilename(filetypes=[("CSV 文件", "*.csv")])
        self.log(f"已选择标记文件: {os.path.basename(self.csv_path)}")

    def log(self, message):
        """日志记录并更新界面"""
        self.debug_log.append(message)
        self.console.insert("end", message + "\n")
        self.console.see("end")
        self.update()

    def validate_inputs(self):
        """验证输入有效性"""
        if not os.path.exists(self.audio_path):
            raise ValueError("请先选择音频文件")
        if not os.path.exists(self.csv_path):
            raise ValueError("请先选择标记文件")
        
        try:
            self.overlap = float(self.overlap_entry.get())
            self.ratio = float(self.ratio_entry.get())
            if not 0 <= self.ratio <= 1:
                raise ValueError("Consonant 比例必须在0-1之间")
        except ValueError as e:
            raise ValueError(f"参数错误: {e}")

    def process_csv(self):
        """核心处理逻辑"""
        # 读取音频时长
        audio = AudioSegment.from_file(self.audio_path)
        total_duration = len(audio)
        self.log(f"音频总时长: {total_duration}ms")

        # 解析CSV数据
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
        self.log(f"成功解析 {len(cues)} 个标记")

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
                'pre_utterance': pre_utterance or self.overlap,
                'left_blank': cue['start'],
                'right_blank': total_duration - cue['end'],
                'consonant': (cue['duration'] - (pre_utterance or 0)) * self.ratio,
                'overlap': self.overlap
            }

            # 处理别名冲突
            base_name = cue['name']
            alias_map[base_name] += 1
            alias = base_name if alias_map[base_name] == 1 else f"{base_name}{alias_map[base_name]-1}"

            # 构建条目
            entry = (
                f"{os.path.basename(self.audio_path)}="
                f"{alias},"
                f"{parameters['left_blank']},"
                f"{parameters['consonant']},"
                f"{parameters['right_blank']},"
                f"{parameters['pre_utterance']},"
                f"{parameters['overlap']}"
            )
            oto_entries.append(entry)
            self.log(f"处理完成: {alias} | {entry}")

        return oto_entries

    def generate(self):
        try:
            self.console.delete("1.0", "end")
            self.validate_inputs()
            oto_entries = self.process_csv()
            
            # 保存文件
            output_path = os.path.join(os.path.dirname(self.audio_path), "oto.ini")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(oto_entries))
            
            messagebox.showinfo("完成", f"成功生成 {len(oto_entries)} 个条目\n保存路径: {output_path}")
            self.log("处理完成！")
            
        except Exception as e:
            messagebox.showerror("错误", str(e))
            self.log(f"错误: {e}")

    def open_output_dir(self):
        """打开输出目录"""
        path = os.path.abspath(os.path.dirname(self.audio_path))
        os.startfile(path)

if __name__ == "__main__":
    app = OTOGenerator()
    app.mainloop()
