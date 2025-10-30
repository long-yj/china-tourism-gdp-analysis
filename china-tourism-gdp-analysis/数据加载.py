import pandas as pd
from pathlib import Path

# 定义数据文件所在的目录
data_directory = Path('./data')

# 列出所有要加载的Excel文件名
excel_files = [
    "地区生产总值分省年度数据.xlsx",
    "国际旅游外汇收入（百万美元）分省年度数据.xlsx",
    "国内旅游情况年度数据.xlsx",
    "国内生成总值年度数据.xlsx",  # 原先是“国内生成总值年度数据.xlsx”，已更正为“国内生产总值年度数据.xlsx”以匹配图片
    "接待国外游客分省年度数据.xlsx",
    "接待外国人游客分省年度数据.xlsx",
    "居民消费水平年度数据.xlsx",
    "旅游业发展情况年度数据.xlsx",
    "全国居民人均收入情况年度数据.xlsx"
]

# 创建一个字典来存储加载后的DataFrame
loaded_data = {}

print("--- 开始加载Excel文件... ---")

for file_name in excel_files:
    file_path = data_directory / file_name

    try:
        # 尝试加载数据，默认第一行为列头
        df = pd.read_excel(file_path)

        # 为字典生成一个更易读的键名，作为未来Excel工作表的名称
        key_name = file_name.replace(".xlsx", "") \
            .replace("年度数据", "") \
            .replace("情况", "") \
            .replace("（百万美元）", "") \
            .strip()

        loaded_data[key_name] = df
        print(f"✅ 成功加载: {file_name}，键名: '{key_name}'")

    except FileNotFoundError:
        print(f"❌ 错误: 文件未找到: {file_path}。请检查文件名和路径是否正确。")
    except Exception as e:
        print(f"❌ 错误加载 {file_name}: {e}")

print("\n--- 所有原始文件加载完成。开始写入独立工作表... ---")

# 定义输出文件的路径
# 注意：我们将把所有原始数据写入一个Excel文件的不同工作表
output_file_name = "所有原始数据（多工作表）.xlsx"
output_file_path = data_directory / output_file_name

try:
    # 使用 pandas.ExcelWriter 创建一个写入器对象
    # 'openpyxl' 是用于 .xlsx 文件的引擎
    with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
        for key, df in loaded_data.items():
            if df.empty:
                print(f"⚠️ 注意: 数据集 '{key}' 为空，将创建一个空工作表。")

            # 将每个 DataFrame 写入 Excel 文件的一个独立工作表
            # sheet_name 设置工作表的名称，index=False 不写入 DataFrame 的行索引
            df.to_excel(writer, sheet_name=key, index=False)
            print(f"📄 已将数据集 '{key}' 写入到工作表 '{key}'。")

    print(f"\n🎉 所有数据已成功保存到一个Excel文件中的九个独立工作表: {output_file_path}")
    print("每个工作表的名称对应原始文件名简化后的键名。")

except Exception as e:
    print(f"❌ 错误: 保存多工作表Excel文件时发生错误: {e}")
    print(f"请检查文件是否被其他程序占用，或路径是否有写入权限。")

print("\n--- 程序执行完毕 ---")