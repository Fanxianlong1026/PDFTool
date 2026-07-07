import os
import re  # 用于字符串自然排序
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pypdf import PdfReader, PdfWriter
from PIL import Image  # 图片处理库
import fitz  # 用于 PDF 高清转图片 

class PDFSwissArmyKnife:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 工具箱")
        self.root.geometry("420x460") # 优化高度以完美容纳 6 个功能按钮，留出呼吸空间
        self.root.resizable(False, False)
        
        # 界面样式
        style = ttk.Style()
        style.configure("TButton", font=("Microsoft YaHei", 10), padding=6)
        
        # 标题
        title_label = tk.Label(root, text="📚 PDF 瑞士军刀", font=("Microsoft YaHei", 18, "bold"))
        title_label.pack(pady=15)
        
        # 功能按钮容器
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill=tk.BOTH, expand=True, padx=50)
        
        ttk.Button(btn_frame, text="1. 批量合并 PDF", command=self.merge_pdf).pack(fill=tk.X, pady=6)
        ttk.Button(btn_frame, text="2. 拆分 PDF (按页提取)", command=self.split_pdf).pack(fill=tk.X, pady=6)
        ttk.Button(btn_frame, text="3. 提取特定页面", command=self.extract_pdf).pack(fill=tk.X, pady=6)
        ttk.Button(btn_frame, text="4. 添加专属水印", command=self.watermark_pdf).pack(fill=tk.X, pady=6)
        ttk.Button(btn_frame, text="5. 图片转 PDF (JPG/PNG)", command=self.image_to_pdf).pack(fill=tk.X, pady=6)
        # 逐页无损转换功能
        ttk.Button(btn_frame, text="6. PDF 页转图片 (无损高清PNG)", command=self.pdf_to_image).pack(fill=tk.X, pady=6)
        
        # 底部信息
        tk.Label(root, text="Powered by 难俟", fg="gray", font=("Arial", 8)).pack(side=tk.BOTTOM, pady=10)

    def merge_pdf(self):
        """批量合并 PDF"""
        files = filedialog.askopenfilenames(title="选择要合并的PDF文件", filetypes=[("PDF Files", "*.pdf")])
        if not files: return
        
        files = sorted(list(files), key=lambda x: [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', x)])
        
        save_path = filedialog.asksaveasfilename(title="保存合并后的文件", defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not save_path: return
        
        try:
            writer = PdfWriter()
            for pdf in files:
                writer.append(pdf)
            writer.write(save_path)
            writer.close()
            messagebox.showinfo("成功", f"成功合并 {len(files)} 个文件！\n已保存至: {save_path}")
        except Exception as e:
            messagebox.showerror("错误", f"合并失败: {str(e)}")

    def split_pdf(self):
        """将 PDF 拆分为单页文件"""
        file = filedialog.askopenfilename(title="选择要拆分的PDF文件", filetypes=[("PDF Files", "*.pdf")])
        if not file: return
        
        save_dir = filedialog.askdirectory(title="选择拆分后文件的保存文件夹")
        if not save_dir: return
        
        try:
            reader = PdfReader(file)
            base_name = os.path.splitext(os.path.basename(file))[0]
            
            for i, page in enumerate(reader.pages):
                writer = PdfWriter()
                writer.add_page(page)
                output_filename = os.path.join(save_dir, f"{base_name}_页码_{i+1}.pdf")
                writer.write(output_filename)
                writer.close()
                
            messagebox.showinfo("成功", f"成功将文件拆分为 {len(reader.pages)} 个独立的 PDF！")
        except Exception as e:
            messagebox.showerror("错误", f"拆分失败: {str(e)}")

    def extract_pdf(self):
        """提取特定的页面"""
        file = filedialog.askopenfilename(title="选择PDF文件", filetypes=[("PDF Files", "*.pdf")])
        if not file: return
        
        page_str = simpledialog.askstring("提取页面", "请输入要提取的页码（用逗号分隔，如: 1,3,5）：")
        if not page_str: return
        
        save_path = filedialog.asksaveasfilename(title="保存提取的文件", defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not save_path: return
        
        try:
            pages_to_extract = [int(p.strip()) - 1 for p in page_str.split(",") if p.strip().isdigit()]
            reader = PdfReader(file)
            writer = PdfWriter()
            
            for p in pages_to_extract:
                if 0 <= p < len(reader.pages):
                    writer.add_page(reader.pages[p])
                    
            writer.write(save_path)
            writer.close()
            messagebox.showinfo("成功", "页面提取成功！")
        except Exception as e:
            messagebox.showerror("错误", f"提取失败: {str(e)}\n请确保输入的是正确的数字格式。")

    def watermark_pdf(self):
        """给 PDF 批量打上水印"""
        messagebox.showinfo("提示", "接下来请先选择【需要打水印的源文件】，然后再选择【作为水印模板的PDF文件】。")
        
        source_file = filedialog.askopenfilename(title="第一步: 选择需要打水印的源 PDF", filetypes=[("PDF Files", "*.pdf")])
        if not source_file: return
        
        watermark_file = filedialog.askopenfilename(title="第二步: 选择水印模板 PDF", filetypes=[("PDF Files", "*.pdf")])
        if not watermark_file: return
        
        save_path = filedialog.asksaveasfilename(title="保存打好水印的文件", defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not save_path: return
        
        try:
            reader = PdfReader(source_file)
            watermark_reader = PdfReader(watermark_file)
            watermark_page = watermark_reader.pages[0]
            
            writer = PdfWriter()
            for page in reader.pages:
                page.merge_page(watermark_page)
                writer.add_page(page)
                
            writer.write(save_path)
            writer.close()
            messagebox.showinfo("成功", "专属水印添加成功！")
        except Exception as e:
            messagebox.showerror("错误", f"添加水印失败: {str(e)}")

    def image_to_pdf(self):
        """图片批量转 PDF（带自动自然排序）"""
        img_files = filedialog.askopenfilenames(
            title="选择要转换的图片（可按Ctrl多选）", 
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not img_files: return
        
        img_files = sorted(
            list(img_files), 
            key=lambda x: [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', x)]
        )
        
        save_path = filedialog.asksaveasfilename(
            title="保存生成的 PDF 文件", 
            defaultextension=".pdf", 
            filetypes=[("PDF Files", "*.pdf")]
        )
        if not save_path: return
        
        try:
            image_list = []
            for file in img_files:
                img = Image.open(file)
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    bg = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        bg.paste(img, (0, 0), img)
                    else:
                        bg.paste(img, (0, 0))
                    image_list.append(bg)
                else:
                    img = img.convert('RGB')
                    image_list.append(img)
            
            if image_list:
                first_img = image_list[0]
                append_imgs = image_list[1:]
                first_img.save(save_path, save_all=True, append_images=append_imgs)
                messagebox.showinfo("成功", f"成功将 {len(img_files)} 张图片按顺序转换为 PDF！\n已保存至: {save_path}")
        except Exception as e:
            messagebox.showerror("错误", f"图片转 PDF 失败: {str(e)}")

    def pdf_to_image(self):
        """将特定的 PDF 页面逐页无损高清转为图片"""
        file = filedialog.askopenfilename(title="选择PDF文件", filetypes=[("PDF Files", "*.pdf")])
        if not file: return
        
        page_str = simpledialog.askstring(
            "PDF 转图片", 
            "请输入要转换的页码\n(例如: 1,3 或者范围 5-10 ；留空则默认转换全部页面):"
        )
        if page_str is None: return  # 点击取消
        
        save_dir = filedialog.askdirectory(title="选择图片保存文件夹")
        if not save_dir: return
        
        try:
            # 打开 PDF 文档
            doc = fitz.open(file)
            base_name = os.path.splitext(os.path.basename(file))[0]
            
            # 解析目标页码（升级版：完美支持独立页码、连字符范围以及留空全部）
            pages_to_convert = []
            if page_str.strip() == "":
                pages_to_convert = list(range(len(doc)))
            else:
                for part in page_str.split(","):
                    part = part.strip()
                    if "-" in part:  # 处理形如 "5-10" 的范围
                        try:
                            start, end = part.split("-")
                            pages_to_convert.extend(range(int(start) - 1, int(end)))
                        except ValueError:
                            continue
                    elif part.isdigit():  # 处理单页
                        pages_to_convert.append(int(part) - 1)
            
            # 去重并升序排序，防止用户输入重复或乱序导致体验不佳
            pages_to_convert = sorted(list(set(pages_to_convert)))
            
            # 缩放矩阵控制：zoom=3 相当于将页面像素放大 3 倍渲染，输出的分辨率极高（约300DPI），清晰无毛边
            zoom = 3
            matrix = fitz.Matrix(zoom, zoom)
            
            success_count = 0
            for p in pages_to_convert:
                if 0 <= p < len(doc):
                    page = doc[p]
                    # 将页面渲染为像素图 (Pixmap)
                    pix = page.get_pixmap(matrix=matrix)
                    output_filename = os.path.join(save_dir, f"{base_name}_页码_{p+1}.png")
                    # 保存为无损 PNG 格式
                    pix.save(output_filename)
                    success_count += 1
            
            doc.close()
            
            if success_count > 0:
                messagebox.showinfo("成功", f"成功将 {success_count} 个页面转换为高清PNG图片！\n保存位置: {save_dir}")
            else:
                messagebox.showwarning("提示", "未找到有效的页码进行转换，请检查输入。")
                
        except Exception as e:
            messagebox.showerror("错误", f"转换失败: {str(e)}\n请确保已通过 `pip install pymupdf` 安装必要依赖。")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFSwissArmyKnife(root)
    root.eval('tk::PlaceWindow . center')
    root.mainloop()