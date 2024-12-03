import geopandas as gpd
import ezdxf
from ezdxf.enums import TextEntityAlignment
from shapely.geometry import Point
import tkinter as tk
from tkinter import filedialog, messagebox


"""
说明：
1.这是一个可以实现如arcgis标注效果的程序，可以实现一些arcgis不好完成的标注样式
2.标注成果直接输出为dxf格式文件
3.本程序标注完成的样例：label_example.jpg
"""

def read_shp_file():
    global gdf
    filepath = filedialog.askopenfilename(filetypes=[("Shapefile", "*.shp")])
    if filepath:
        try:
            gdf = gpd.read_file(filepath, encoding="GBK")
            shp_path_var.set(filepath)
            messagebox.showinfo("成功", "SHP 文件读取成功！")
        except Exception as e:
            messagebox.showerror("错误", f"无法读取 SHP 文件：{e}")


def save_dxf_file():
    if gdf is None:
        messagebox.showerror("错误", "请先读取 SHP 文件！")
        return

    try:
        # 获取输入参数
        field_DLBM = DLBM_var.get()
        field_DLXH = DLXH_var.get()
        field_mj_hm2 = mj_hm2_var.get()
        text_height = float(text_height_var.get())
        text_proportion = float(text_proportion_var.get())
        #text_move = 2  # 固定值，作为示例
        #text_width = 字数 * (text_height / text_proportion)

        # 创建 DXF 文件
        doc = ezdxf.new("R2004")
        # 添加“宋体”字体样式
        if "宋体" not in doc.styles:
            doc.styles.new("宋体", dxfattribs={"font": "simsun.ttf"})  # 使用 Windows 系统常见的宋体字体文件
        msp = doc.modelspace()

        for idx, row in gdf.iterrows():
            if row.geometry.is_empty:
                continue
            centroid = row.geometry.centroid
            x, y = centroid.x, centroid.y

            # 获取字段内容
            DLBM = row.get(field_DLBM, "")
            DLXH = row.get(field_DLXH, "")
            mj_hm2 = row.get(field_mj_hm2, "")

            # 绘制“地类编码”字段  DLBM
            text_entity = msp.add_text(DLBM, dxfattribs={"height": text_height, "style": "宋体"})
            text_entity.set_placement((x, y), align=TextEntityAlignment.MIDDLE_CENTER)

            # 计算“地类编码”文字的估算长度  DLBM
            text_width = len(DLBM) * (text_height / text_proportion)

            # 绘制“地类序号”字段   序号  DLXH
            y_offset_DLXH = y + text_height * 3 / 4 + text_height * 3 / 4
            DLXH_text_entity = msp.add_text(DLXH, dxfattribs={"height": text_height, "style": "宋体"})
            DLXH_text_entity.set_placement((x, y_offset_DLXH), align=TextEntityAlignment.MIDDLE_CENTER)

            # 在“地类编码”和“地类序号”之间绘制多段线
            line_start = (x - text_width / 2 - text_height / 2, y + text_height * 3 / 4)
            line_end = (x + text_width / 2 + text_height / 2, y + text_height * 3 / 4)
            msp.add_lwpolyline([line_start, line_end])

            # 绘制“公顷面积”字段   面积  mj_hm2
            mj_hm2_width = len(str(mj_hm2))
            #x_offset_mj_hm2 = x + text_height * 4 + mj_hm2_width
            x_offset_mj_hm2 = x + text_width / 2 + text_height * 1.5 / text_proportion + ((mj_hm2_width+1) * (text_height / text_proportion)) / 2
            y_offset_mj_hm2 = y + text_height * 3 / 4
            mj_hm2_text_entity = msp.add_text(str(mj_hm2)+"㎡", dxfattribs={"height": text_height, "style": "宋体"})
            mj_hm2_text_entity.set_placement((x_offset_mj_hm2, y_offset_mj_hm2),
                                              align=TextEntityAlignment.MIDDLE_CENTER)

        # 保存 DXF 文件
        filepath = filedialog.asksaveasfilename(defaultextension=".dxf", filetypes=[("DXF Files", "*.dxf")])
        if filepath:
            doc.saveas(filepath)
            messagebox.showinfo("成功", f"DXF 文件已保存到：{filepath}")
    except Exception as e:
        messagebox.showerror("错误", f"保存 DXF 文件时出错：{e}")


# 创建 GUI
root = tk.Tk()
root.title("hpa_多段标注工具")
root.geometry("500x400")

gdf = None

# 界面元素
tk.Label(root, text="SHP 文件路径:").pack(anchor="w", padx=10, pady=5)
shp_path_var = tk.StringVar()
tk.Entry(root, textvariable=shp_path_var, state="readonly", width=50).pack(anchor="w", padx=10)

tk.Button(root, text="读取 SHP 文件", command=read_shp_file).pack(anchor="w", padx=10, pady=5)

tk.Label(root, text="字段名称设置:").pack(anchor="w", padx=10, pady=5)
DLBM_var = tk.StringVar(value="DLBM")
DLXH_var = tk.StringVar(value="DLXH")
mj_hm2_var = tk.StringVar(value="mj_hm2")
tk.Entry(root, textvariable=DLBM_var, width=20).pack(anchor="w", padx=10)
tk.Entry(root, textvariable=DLXH_var, width=20).pack(anchor="w", padx=10)
tk.Entry(root, textvariable=mj_hm2_var, width=20).pack(anchor="w", padx=10)

tk.Label(root, text="文字高度:").pack(anchor="w", padx=10, pady=5)
text_height_var = tk.StringVar(value="3")
tk.Entry(root, textvariable=text_height_var, width=20).pack(anchor="w", padx=10)

tk.Label(root, text="字符宽度估算比例:").pack(anchor="w", padx=10, pady=5)
text_proportion_var = tk.StringVar(value="1.43")
tk.Entry(root, textvariable=text_proportion_var, width=20).pack(anchor="w", padx=10)

tk.Button(root, text="保存为 DXF 文件", command=save_dxf_file).pack(anchor="w", padx=10, pady=20)

root.mainloop()
