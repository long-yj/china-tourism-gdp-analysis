import pandas as pd
from pathlib import Path

# 定义数据文件所在的目录
data_directory = Path('./data')

# 列出所有要加载的Excel文件名
excel_files = [
    "地区生产总值分省年度数据.xlsx",
    "国际旅游外汇收入（百万美元）分省年度数据.xlsx",
    "国内旅游情况年度数据.xlsx",
    "国内生成总值年度数据.xlsx",
    "接待国外游客分省年度数据.xlsx",
    "接待外国人游客分省年度数据.xlsx",
    "居民消费水平年度数据.xlsx",
    "旅游业发展情况年度数据.xlsx",
    "全国居民人均收入情况年度数据.xlsx"
]

# 创建一个字典来存储加载后的DataFrame
# 键为简化后的文件名，值为对应的DataFrame
loaded_data = {}

# 遍历文件列表，尝试加载每个Excel文件
for file_name in excel_files:
    file_path = data_directory / file_name

    try:
        # 尝试加载数据，默认第一行为列头
        df = pd.read_excel(file_path)

        # 为字典生成一个更易读的键名
        key_name = file_name.replace(".xlsx", "") \
            .replace("年度数据", "") \
            .replace("情况", "") \
            .replace("（百万美元）", "") \
            .strip()


        # 将加载成功的DataFrame存储到字典中
        loaded_data[key_name] = df

    except FileNotFoundError:
        # 如果文件未找到，静默跳过，不打印任何信息
        pass
    except Exception as e:
        # 如果加载过程中发生其他错误，静默跳过，不打印任何信息
        pass

