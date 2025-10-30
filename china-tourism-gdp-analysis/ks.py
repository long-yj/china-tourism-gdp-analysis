import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from functools import reduce  # 用于合并多个DataFrame

# --- 1. 数据加载部分 (与你提供的代码一致) ---

# 定义数据文件所在的目录
data_directory = Path('./data')

# 确保数据目录存在
if not data_directory.exists():
    print(f"Error: Data directory '{data_directory}' not found. Please create it and place your Excel files inside.")
    exit()  # 如果数据目录不存在，则退出程序

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
print("--- 正在加载数据文件 ---")
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
        print(f"成功加载: {key_name}")

    except FileNotFoundError:
        print(f"警告: 文件未找到 - {file_name}，已跳过。")
    except Exception as e:
        print(f"警告: 加载文件 {file_name} 时发生错误: {e}，已跳过。")

print("\n--- 数据加载完成 ---")
print("已加载的数据集:")
for k in loaded_data.keys():
    print(f"- {k}")

# --- 配置 Matplotlib 以支持中文显示和图像保存 ---
# 优先使用 seaborn 的样式，然后再进行个性化设置
plt.style.use('seaborn-v0_8-darkgrid')  # 使用一个漂亮且适合数据分析的风格

# 设置中文字体
# 在Windows系统上，'Microsoft YaHei'（微软雅黑）通常是可用的
# 'SimHei'（黑体）是另一个常见的备选字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']

# 解决在中文环境下保存图像时，负号'-'显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False

# 再次确认中文字体配置，并提供更详细的调试信息
try:
    fig_test, ax_test = plt.subplots(figsize=(2, 1))
    ax_test.set_title('中文测试', fontsize=12)
    plt.close(fig_test)
    print("中文字体配置成功。将使用所设定的字体生成图表。")
except Exception as e:
    print(f"警告: 默认中文字体配置失败: {e}")
    print("尝试查找系统可用的中文字体...")
    import matplotlib.font_manager as fm

    # 获取所有可用字体
    font_list = [f.name for f in fm.fontManager.ttflist]
    # 查找常见的中文字体
    available_chinese_fonts = [font for font in font_list if
                               'SimHei' in font or 'YaHei' in font or '黑体' in font or '雅黑' in font or '宋体' in font or '楷体' in font]

    if available_chinese_fonts:
        print(f"找到以下可用的中文字体: {list(set(available_chinese_fonts))}")
        # 将找到的字体设为matplotlib的默认字体
        plt.rcParams['font.sans-serif'] = available_chinese_fonts
        print("已尝试使用系统自动查找的字体。如果仍然存在问题，请确保您的系统中安装了这些字体。")
    else:
        print("警告：在您的系统中未能自动找到任何可用的中文字体。图表中的中文可能无法正常显示。")
        print("请尝试手动安装 'Microsoft YaHei' (微软雅黑) 或 'SimHei' (黑体) 字体。")

# 创建保存图片的目录
output_dir = Path('./analysis_plots')
output_dir.mkdir(parents=True, exist_ok=True)
print(f"\n分析结果图片将保存至: {output_dir}")

plot_counter = 0  # 用于统计图片数量


def save_plot(fig, title_prefix=""):
    """保存当前图形并更新计数器"""
    global plot_counter
    plot_counter += 1
    # 清理标题以作为文件名，避免特殊字符，并限制长度
    max_filename_len = 50  # 限制文件名长度
    filename = "".join(c for c in title_prefix if c.isalnum() or c in [' ', '_', '-']).strip()
    if len(filename) > max_filename_len:
        filename = filename[:max_filename_len] + "..."  # 截断过长的文件名
    if not filename:  # 防止空文件名
        filename = f"plot_{plot_counter}"

    plt.tight_layout()
    try:
        fig.savefig(output_dir / f"{filename}_{plot_counter}.png", dpi=300, bbox_inches='tight')
        print(f"  保存图片: {filename}_{plot_counter}.png")
    except Exception as e:
        print(f"  警告: 无法保存图片 '{filename}_{plot_counter}.png': {e}")
    plt.close(fig)  # 关闭图形以释放内存，避免内存占用过高


# --- 2. 数据初步查看与清洗与重塑 ---
print("\n--- 数据初步查看与清洗与重塑 ---")

processed_data = {}


def process_dataframe(key, df):
    """
    处理DataFrame：识别ID列和年份列，将宽格式数据转换为长格式，并进行数据清洗。
    """
    # 识别ID变量（'地区' 或 '指标'）
    id_vars = []
    if '地区' in df.columns:
        id_vars.append('地区')
    if '指标' in df.columns:
        id_vars.append('指标')

    # 识别年份列（形如 'YYYY年' 或纯数字年份）
    year_columns_raw = []
    for col in df.columns:
        if isinstance(col, (int, str)):
            # 匹配 'YYYY年' 格式
            if isinstance(col, str) and col.endswith('年') and col[:-1].isdigit():
                year_columns_raw.append(col)
            # 匹配 纯数字年份 (例如 2005, 2010)
            elif isinstance(col, int) and col >= 1900 and col <= 2050:
                year_columns_raw.append(col)
            # 对于2024年这种可能为空的年份，也识别，但会在dropna时去除
            elif isinstance(col, str) and col.isdigit() and int(col) >= 1900 and int(col) <= 2050:
                year_columns_raw.append(col)

    # 检查是否有年份列，并按年份降序排列以便melt时保持顺序
    if not year_columns_raw:
        print(f"警告: 数据集 '{key}' 未找到有效的年份列。原始列: {df.columns.tolist()}")
        return None

    # 将年份列名转换为字符串，以防有的年份是整数类型
    year_columns_raw = [str(col) for col in year_columns_raw]
    year_columns_raw.sort(key=lambda x: int(x.replace('年', '')), reverse=False)  # 按年份升序排序

    if not id_vars:  # 理论上不应出现此情况，因为数据应有地区或指标
        print(f"警告: 数据集 '{key}' 未找到ID列 ('地区'或'指标')。原始列: {df.columns.tolist()}")
        return None

    # 使用 melt 将宽格式数据转换为长格式
    try:
        melted_df = df.melt(id_vars=id_vars,
                            value_vars=year_columns_raw,  # 明确指定要融化的列
                            var_name='Year_Raw',  # 原始年份列名
                            value_name='Value')  # 转换后的值列名
    except Exception as e:
        print(f"错误: 对数据集 '{key}' 进行 melt 操作失败: {e}")
        return None

    # 将 'Year_Raw' 转换为整数 'Year'
    melted_df['Year'] = melted_df['Year_Raw'].astype(str).str.replace('年', '').astype(int)

    # 丢弃原始的年份列
    melted_df.drop(columns=['Year_Raw'], inplace=True)

    # 统一 ID 列名
    if '地区' in melted_df.columns:
        melted_df.rename(columns={'地区': 'Province'}, inplace=True)
    if '指标' in melted_df.columns:
        melted_df.rename(columns={'指标': 'Indicator'}, inplace=True)

    # 将 'Value' 列转换为数值型
    # 尝试去除数值中的非数字字符（例如"亿元"、"万人次"等尾缀，如果它们被错误地包含在数值中）
    if melted_df['Value'].dtype == 'object':
        # 只保留数字、小数点和负号
        melted_df['Value'] = melted_df['Value'].astype(str).str.replace(r'[^\d.-]', '', regex=True)
    melted_df['Value'] = pd.to_numeric(melted_df['Value'], errors='coerce')  # 无法转换的值设为 NaN

    # 移除包含 NaN 值或年份的行
    initial_rows_count = len(melted_df)
    melted_df.dropna(subset=['Value', 'Year'], inplace=True)
    if len(melted_df) < initial_rows_count:
        print(f"  数据集 '{key}': 已移除包含 NaN 值或无法解析的行 ({initial_rows_count - len(melted_df)} 行)。")

    # 移除省份数据中的汇总行，并清理省份名称 (移除"省"、"市"、"自治区"等字样)
    if 'Province' in melted_df.columns:
        initial_rows_count = len(melted_df)
        melted_df['Province'] = melted_df['Province'].astype(str).str.replace(
            '省|市|自治区|特别行政区|壮族|回族|维吾尔|蒙古|藏族', '', regex=True).str.strip()
        # 再次过滤汇总行
        melted_df = melted_df[~melted_df['Province'].isin(['全国', '合计', '全部', '总计', '港澳台地区', ''])].copy()
        if len(melted_df) < initial_rows_count:
            print(f"  数据集 '{key}': 已移除 '全国'/'合计' 等汇总行并清理省份名称。")

    # 按年份和ID列排序
    if 'Province' in melted_df.columns:
        melted_df.sort_values(by=['Year', 'Province'], inplace=True)
    elif 'Indicator' in melted_df.columns:
        melted_df.sort_values(by=['Year', 'Indicator'], inplace=True)
    else:
        melted_df.sort_values(by='Year', inplace=True)

    print(f"  数据集 '{key}' 转换成功。新列: {melted_df.columns.tolist()}")
    return melted_df


# 处理所有加载的DataFrame
for key, df in loaded_data.items():
    processed_df = process_dataframe(key, df.copy())
    if processed_df is not None:
        processed_data[key] = processed_df
    else:
        print(f"跳过分析数据集 '{key}' (处理失败)。")

# 更新 loaded_data 为已处理的数据，供后续分析使用
loaded_data = processed_data

print("\n--- 数据清洗与重塑完成，开始分析 ---")
print("已处理的数据集 (前5行示例):")
for k, df in loaded_data.items():
    if not df.empty:
        print(f"\n--- {k} ---")
        print(df.head())
    else:
        print(f"\n--- {k} (空或处理失败) ---")


# 定义辅助函数，用于从"指标"类数据集中提取特定指标的数据
def get_national_indicator_data(df_name, indicator_substrings, loaded_data_dict=loaded_data):
    df = loaded_data_dict.get(df_name)
    if df is None or df.empty or 'Indicator' not in df.columns:
        print(f"警告: 数据集 '{df_name}' 不存在或格式不正确，无法提取指标。")
        return None

    # 使用正则表达式匹配包含任一子字符串的指标
    # 注意：使用 .astype(str) 防止 Indicator 列中存在非字符串类型的数据导致 .str 访问器失败
    filtered_df = df[
        df['Indicator'].astype(str).str.contains('|'.join(indicator_substrings), na=False, regex=True)].copy()

    if filtered_df.empty:
        print(f"警告: 数据集 '{df_name}' 中未找到与 '{indicator_substrings}' 匹配的指标。")
        # 备选方案：如果该数据集通常只包含一个主要指标（如"国内生成总值"文件），
        # 即使找不到匹配，也返回整个数据集（假设它就是目标指标）。
        if df['Indicator'].nunique() == 1:
            print(f"  数据集 '{df_name}' 仅包含一个指标 ('{df['Indicator'].iloc[0]}')，将其作为目标数据。")
            return df[['Year', 'Value']].set_index('Year').sort_index()
        return None

    # 如果找到多个匹配指标，通常需要将其转换为宽格式以便多线绘制或选择特定列
    # 优先选择最匹配的指标，例如对于GDP，优先选择包含"总"的
    if filtered_df['Indicator'].nunique() > 1:
        # 更新和扩展关键词，使其更精确，并按优先级排序
        priority_keywords = [
            '国内生产总值(亿元)', '国内生产总值', '人均国内生产总值',  # GDP
            '居民人均可支配收入(元)', '居民人均可支配收入',  # 收入
            '居民消费水平(元)', '居民消费水平',  # 消费
            '国内游客(百万人次)', '国内旅游人数', '国内游客',  # 国内游客
            '国内旅游总花费(亿元)', '国内旅游收入',  # 国内收入
            '入境游客(万人次)', '入境过夜游客(万人次)', # 入境游客
            '国民总收入(亿元)', '总'  # 通用关键词
        ]
        
        primary_indicator = next((ind for keyword in priority_keywords
                                  for ind in filtered_df['Indicator'].unique() if keyword == ind), None)
        
        # 如果完全匹配不到，再进行模糊匹配
        if not primary_indicator:
            primary_indicator = next((ind for keyword in priority_keywords
                                      for ind in filtered_df['Indicator'].unique() if keyword in ind), None)


        if primary_indicator:
            print(f"  数据集 '{df_name}' 找到多个匹配指标，选择主要指标 '{primary_indicator}'。")
            return filtered_df[filtered_df['Indicator'] == primary_indicator][['Year', 'Value']].set_index(
                'Year').sort_index()
        else:
            print(
                f"  数据集 '{df_name}' 找到多个匹配指标，但未能识别出主要指标，将透视处理。匹配指标: {filtered_df['Indicator'].unique().tolist()}")
            return filtered_df.pivot_table(index='Year', columns='Indicator', values='Value').sort_index()
    else:  # 只有一个匹配指标
        return filtered_df[['Year', 'Value']].set_index('Year').sort_index()


# --- 3. 宏观经济发展趋势分析 (折线图、增长率图) ---
print("\n--- 3. 宏观经济发展趋势分析 ---")

# 国内生产总值
national_gdp_data_processed = get_national_indicator_data('国内生成总值', ['国内生产总值', 'GDP', '生产总值'])
gdp_value_col = None  # 用于存储实际的GDP数值列名（在DataFrame中可能是'Value'或特定指标名）

if national_gdp_data_processed is not None and not national_gdp_data_processed.empty:
    if 'Value' in national_gdp_data_processed.columns:  # 如果是单系列数据
        gdp_value_col = '国内生产总值'
        national_gdp_data_processed.rename(columns={'Value': gdp_value_col}, inplace=True)
    elif national_gdp_data_processed.shape[1] > 0:  # 如果是透视表（多指标）
        # 尝试从透视表中找到最能代表总GDP的列
        gdp_col_candidates = ['国内生产总值(亿元)', '国内生产总值', 'GDP']  # 优先顺序
        gdp_value_col = next((col for col in gdp_col_candidates if col in national_gdp_data_processed.columns), None)
        if gdp_value_col:
            national_gdp_data_processed.rename(columns={gdp_value_col: '国内生产总值'}, inplace=True)
            gdp_value_col = '国内生产总值'
        else:
            print("警告: 无法从 '国内生成总值' 数据中识别出明确的总GDP列。")
            gdp_value_col = national_gdp_data_processed.columns[
                0] if national_gdp_data_processed.columns.tolist() else None  # 实在找不到就取第一个

    if gdp_value_col and gdp_value_col in national_gdp_data_processed.columns:
        # Plot 1: 中国国内生产总值 (GDP) 年度趋势
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.lineplot(x=national_gdp_data_processed.index, y=national_gdp_data_processed[gdp_value_col], marker='o',
                     ax=ax, label='中国GDP')
        ax.set_title('中国国内生产总值 (GDP) 年度趋势')
        ax.set_xlabel('年份')
        ax.set_ylabel(
            f'GDP ({gdp_value_col.split("(")[-1].replace(")", "") if "(" in gdp_value_col else "单位未知"})')  # 尝试提取单位
        ax.ticklabel_format(style='plain', axis='y')
        ax.grid(True)
        save_plot(fig, '中国GDP总量年度趋势')

        # 计算并绘制GDP年度增长率
        national_gdp_data_processed['GDP_Growth_Rate'] = national_gdp_data_processed[gdp_value_col].pct_change() * 100
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.lineplot(x=national_gdp_data_processed.index, y=national_gdp_data_processed['GDP_Growth_Rate'], marker='o',
                     ax=ax, color='orange')
        ax.set_title('中国国内生产总值 (GDP) 年度增长率')
        ax.set_xlabel('年份')
        ax.set_ylabel('增长率 (%)')
        ax.axhline(0, color='grey', linestyle='--', linewidth=0.8)
        ax.grid(True)
        save_plot(fig, '中国GDP年度增长率')
    else:
        print("警告: '国内生成总值' 数据无法用于GDP趋势分析。")
else:
    print("警告: '国内生成总值' 数据集缺失或处理失败，跳过GDP分析。")

# 居民收入与消费水平
resident_income_data_processed = get_national_indicator_data('全国居民人均收入', ['人均可支配收入', '居民人均收入'])
resident_consumption_data_processed = get_national_indicator_data('居民消费水平', ['居民消费水平', '人均消费支出'])

income_col_name = None
consumption_col_name = None

# 尝试从收入数据中提取总收入列
if resident_income_data_processed is not None and not resident_income_data_processed.empty:
    if 'Value' in resident_income_data_processed.columns:
        income_col_name = '居民人均可支配收入'
        resident_income_data_processed.rename(columns={'Value': income_col_name}, inplace=True)
    elif resident_income_data_processed.shape[1] > 0:
        income_col_candidates = ['居民人均可支配收入(元)', '全国居民人均可支配收入', '居民人均收入']
        income_col_name = next((col for col in income_col_candidates if col in resident_income_data_processed.columns),
                               None)
        if income_col_name:
            resident_income_data_processed.rename(columns={income_col_name: '居民人均可支配收入'}, inplace=True)
            income_col_name = '居民人均可支配收入'
        else:
            print("警告: 无法从 '全国居民人均收入' 数据中识别出明确的人均收入列。")
            income_col_name = resident_income_data_processed.columns[
                0] if resident_income_data_processed.columns.tolist() else None

# 尝试从消费数据中提取总消费列
if resident_consumption_data_processed is not None and not resident_consumption_data_processed.empty:
    if 'Value' in resident_consumption_data_processed.columns:
        consumption_col_name = '居民消费水平'
        resident_consumption_data_processed.rename(columns={'Value': consumption_col_name}, inplace=True)
    elif resident_consumption_data_processed.shape[1] > 0:
        consumption_col_candidates = ['居民消费水平(元)', '居民人均消费支出', '居民消费水平']
        consumption_col_name = next(
            (col for col in consumption_col_candidates if col in resident_consumption_data_processed.columns), None)
        if consumption_col_name:
            resident_consumption_data_processed.rename(columns={consumption_col_name: '居民消费水平'}, inplace=True)
            consumption_col_name = '居民消费水平'
        else:
            print("警告: 无法从 '居民消费水平' 数据中识别出明确的消费水平列。")
            consumption_col_name = resident_consumption_data_processed.columns[
                0] if resident_consumption_data_processed.columns.tolist() else None

merged_economic_df = None
if income_col_name and consumption_col_name:
    # 确保取到的数据是单列且索引为Year
    df_income_plot = resident_income_data_processed[
        [income_col_name]] if income_col_name in resident_income_data_processed.columns else None
    df_consumption_plot = resident_consumption_data_processed[
        [consumption_col_name]] if consumption_col_name in resident_consumption_data_processed.columns else None

    if df_income_plot is not None and df_consumption_plot is not None:
        merged_economic_df = pd.merge(df_income_plot, df_consumption_plot, on='Year', how='inner')

    if merged_economic_df is not None and not merged_economic_df.empty:
        # Plot 3: 居民收入与消费水平年度趋势
        fig, ax1 = plt.subplots(figsize=(12, 6))
        sns.lineplot(x=merged_economic_df.index, y=merged_economic_df[income_col_name], marker='o', ax=ax1,
                     color='green', label=income_col_name)
        ax1.set_ylabel(income_col_name)
        ax1.ticklabel_format(style='plain', axis='y')

        ax2 = ax1.twinx()  # 创建共享X轴的第二个Y轴
        sns.lineplot(x=merged_economic_df.index, y=merged_economic_df[consumption_col_name], marker='s', ax=ax2,
                     color='purple', label=consumption_col_name)
        ax2.set_ylabel(consumption_col_name)
        ax2.ticklabel_format(style='plain', axis='y')

        fig.suptitle('中国居民人均收入与消费水平年度趋势')
        ax1.set_xlabel('年份')
        fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.9))
        ax1.grid(True)
        save_plot(fig, '中国居民收入与消费趋势')
    else:
        print("警告: 居民收入或消费数据合并后为空或无效，跳过相关分析。")
else:
    print("警告: 居民收入或消费数据集缺失、处理失败或未找到明确的数值列，跳过相关分析。")

# --- 4. 旅游业发展趋势分析 (折线图) ---
print("\n--- 4. 旅游业发展趋势分析 ---")

# 国内旅游人次与收入
# 使用更精确的关键词来匹配国内旅游人数和收入
domestic_tourists_data = get_national_indicator_data('国内旅游', ['国内游客'])
domestic_revenue_data = get_national_indicator_data('国内旅游', ['国内旅游总花费', '国内旅游收入'])

domestic_tourists_col_name = None
domestic_revenue_col_name = None

if domestic_tourists_data is not None and not domestic_tourists_data.empty and 'Value' in domestic_tourists_data.columns:
    domestic_tourists_col_name = '国内旅游人次'
    domestic_tourists_data.rename(columns={'Value': domestic_tourists_col_name}, inplace=True)

if domestic_revenue_data is not None and not domestic_revenue_data.empty and 'Value' in domestic_revenue_data.columns:
    domestic_revenue_col_name = '国内旅游收入'
    domestic_revenue_data.rename(columns={'Value': domestic_revenue_col_name}, inplace=True)

merged_domestic_tourism_df = None
if domestic_tourists_col_name and domestic_revenue_col_name:
    merged_domestic_tourism_df = pd.merge(
        domestic_tourists_data[[domestic_tourists_col_name]],
        domestic_revenue_data[[domestic_revenue_col_name]],
        on='Year',
        how='inner'
    )

    if merged_domestic_tourism_df is not None and not merged_domestic_tourism_df.empty:
        # Plot 4: 国内旅游人次与收入年度趋势
        fig, ax1 = plt.subplots(figsize=(12, 6))
        sns.lineplot(x=merged_domestic_tourism_df.index, y=merged_domestic_tourism_df[domestic_tourists_col_name],
                     marker='o', ax=ax1, color='blue', label=domestic_tourists_col_name)
        ax1.set_ylabel(domestic_tourists_col_name)
        ax1.ticklabel_format(style='plain', axis='y')

        ax2 = ax1.twinx()
        sns.lineplot(x=merged_domestic_tourism_df.index, y=merged_domestic_tourism_df[domestic_revenue_col_name],
                     marker='s', ax=ax2, color='red', label=domestic_revenue_col_name)
        ax2.set_ylabel(domestic_revenue_col_name)
        ax2.ticklabel_format(style='plain', axis='y')

        fig.suptitle('中国国内旅游人次与收入年度趋势')
        ax1.set_xlabel('年份')
        fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.9))
        ax1.grid(True)
        save_plot(fig, '国内旅游人次与收入趋势')
    else:
        print("警告: 合并后的国内旅游数据为空。")
else:
    print("警告: '国内旅游' 数据集未找到明确的游客人次或收入列，跳过相关分析。")

# 国际旅游外汇收入与接待国外游客趋势 (需要将分省数据汇总为全国数据)
# 国际旅游外汇收入（分省）
international_fx_df_processed = loaded_data.get('国际旅游外汇收入分省')
if international_fx_df_processed is not None and 'Value' in international_fx_df_processed.columns:
    # 汇总各省数据为全国总额
    national_international_fx = international_fx_df_processed.groupby('Year')['Value'].sum().reset_index()
    national_international_fx.rename(columns={'Value': '国际旅游外汇收入'}, inplace=True)
    national_international_fx = national_international_fx.set_index('Year').sort_index()
else:
    national_international_fx = None
    print("警告: '国际旅游外汇收入分省' 数据集缺失或处理失败，无法计算全国总额。")

# 接待国外游客（分省）
foreign_visitors_df_processed = loaded_data.get('接待国外游客分省')
# 检查 '接待外国人游客分省' 是否与 '接待国外游客分省' 重复
foreigners_visitors_df_processed = loaded_data.get('接待外国人游客分省')  # 这行依然保留，但处理逻辑已优化

national_foreign_visitors = None
if foreign_visitors_df_processed is not None and 'Value' in foreign_visitors_df_processed.columns:
    national_foreign_visitors = foreign_visitors_df_processed.groupby('Year')['Value'].sum().reset_index()
    national_foreign_visitors.rename(columns={'Value': '接待国外游客人次'}, inplace=True)
    national_foreign_visitors = national_foreign_visitors.set_index('Year').sort_index()

    if foreigners_visitors_df_processed is not None and 'Value' in foreigners_visitors_df_processed.columns:
        temp_national_foreigners = foreigners_visitors_df_processed.groupby('Year')['Value'].sum()
        # 假设如果全国总和的相对差异小于1%，则视为重复
        if not temp_national_foreigners.empty and national_foreign_visitors is not None and np.isclose(
                national_foreign_visitors['接待国外游客人次'].sum(), temp_national_foreigners.sum(), rtol=0.01):
            print(
                "提示: '接待外国人游客分省' 和 '接待国外游客分省' 全国汇总数据高度相似，将只使用 '接待国外游客分省' 进行分析。")
            # 不删除Loaded_data中的，只在national_foreign_visitors_df处理时不使用
        else:
            print(
                "提示: '接待外国人游客分省' 和 '接待国外游客分省' 全国汇总数据存在明显差异，将分别处理 (在此处主要使用接待国外游客人次)。")
else:
    print("警告: '接待国外游客分省' 数据集缺失或处理失败，无法计算全国总额。")

merged_international_tourism_df = None
if national_international_fx is not None and national_foreign_visitors is not None:
    merged_international_tourism_df = pd.merge(national_international_fx, national_foreign_visitors, on='Year',
                                               how='inner')

    if not merged_international_tourism_df.empty:
        # Plot 5: 国际旅游外汇收入与接待国外游客年度趋势
        fig, ax1 = plt.subplots(figsize=(12, 6))
        sns.lineplot(x=merged_international_tourism_df.index, y=merged_international_tourism_df['国际旅游外汇收入'],
                     marker='o', ax=ax1, color='green', label='国际旅游外汇收入')
        ax1.set_ylabel('国际旅游外汇收入 (百万美元)')
        ax1.ticklabel_format(style='plain', axis='y')

        ax2 = ax1.twinx()
        sns.lineplot(x=merged_international_tourism_df.index, y=merged_international_tourism_df['接待国外游客人次'],
                     marker='s', ax=ax2, color='darkorange', label='接待国外游客人次')
        ax2.set_ylabel('接待国外游客人次 (万人次)')
        ax2.ticklabel_format(style='plain', axis='y')

        fig.suptitle('中国国际旅游外汇收入与接待国外游客年度趋势')
        ax1.set_xlabel('年份')
        fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.9))
        ax1.grid(True)
        save_plot(fig, '国际旅游收入与游客趋势')

        # Plot 6: 国际旅游外汇收入年度增长率
        merged_international_tourism_df['FX_Growth_Rate'] = merged_international_tourism_df[
                                                                '国际旅游外汇收入'].pct_change() * 100
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.lineplot(x=merged_international_tourism_df.index, y=merged_international_tourism_df['FX_Growth_Rate'],
                     marker='o', ax=ax, color='purple')
        ax.set_title('中国国际旅游外汇收入年度增长率')
        ax.set_xlabel('年份')
        ax.set_ylabel('增长率 (%)')
        ax.axhline(0, color='grey', linestyle='--', linewidth=0.8)
        ax.grid(True)
        save_plot(fig, '国际旅游外汇收入增长率')

        # Plot 7: 接待国外游客年度增长率
        merged_international_tourism_df['Visitors_Growth_Rate'] = merged_international_tourism_df[
                                                                      '接待国外游客人次'].pct_change() * 100
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.lineplot(x=merged_international_tourism_df.index, y=merged_international_tourism_df['Visitors_Growth_Rate'],
                     marker='o', ax=ax, color='teal')
        ax.set_title('中国接待国外游客年度增长率')
        ax.set_xlabel('年份')
        ax.set_ylabel('增长率 (%)')
        ax.axhline(0, color='grey', linestyle='--', linewidth=0.8)
        ax.grid(True)
        save_plot(fig, '接待国外游客增长率')
    else:
        print("警告: 国际旅游收入与游客数据合并后为空或无效。")
else:
    print("警告: 国际旅游外汇收入或接待国外游客数据集缺失或处理失败，跳过相关分析。")

# --- 5. 旅游与国民经济指标相关性分析 (散点图、热力图) ---
print("\n--- 5. 旅游与国民经济指标相关性分析 ---")

# 准备合并所有国家级宏观经济和旅游数据
dfs_for_correlation = []

if national_gdp_data_processed is not None and gdp_value_col:
    dfs_for_correlation.append(national_gdp_data_processed[[gdp_value_col]].copy())
if merged_economic_df is not None and income_col_name and consumption_col_name:
    dfs_for_correlation.append(merged_economic_df[[income_col_name, consumption_col_name]].copy())
if merged_domestic_tourism_df is not None and domestic_tourists_col_name and domestic_revenue_col_name:
    dfs_for_correlation.append(
        merged_domestic_tourism_df[[domestic_tourists_col_name, domestic_revenue_col_name]].copy())
if merged_international_tourism_df is not None:
    dfs_for_correlation.append(merged_international_tourism_df[['国际旅游外汇收入', '接待国外游客人次']].copy())

all_national_data = None
if dfs_for_correlation:
    # 确保所有待合并的DF都以 'Year' 为索引
    for i, df_item in enumerate(dfs_for_correlation):
        if df_item is not None and 'Year' not in df_item.index.name:  # 如果Year不是索引，尝试设为索引
            if 'Year' in df_item.columns:
                df_item = df_item.set_index('Year')
                dfs_for_correlation[i] = df_item
            else:
                print(f"警告: 待合并的DataFrame {i} 没有'Year'列或索引，跳过。")
                dfs_for_correlation[i] = None
    dfs_for_correlation = [df for df in dfs_for_correlation if df is not None and not df.empty]  # 移除None项和空DataFrame

    if dfs_for_correlation:
        # 使用 reduce 进行外合并，保留所有年份数据
        all_national_data = reduce(lambda left, right: pd.merge(left, right, on='Year', how='outer'),
                                   dfs_for_correlation)
        all_national_data.dropna(how='all', inplace=True)  # 移除所有列都为NaN的行
        all_national_data = all_national_data.select_dtypes(include=[np.number])  # 只保留数值列

    if all_national_data is not None and not all_national_data.empty and all_national_data.shape[1] > 1:
        # Plot 8: 国家级指标相关性热力图
        correlation_matrix = all_national_data.corr(numeric_only=True)
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, ax=ax)
        ax.set_title('国家宏观经济与旅游指标相关性矩阵')
        save_plot(fig, '国家宏观经济与旅游指标相关性热力图')

        # Plot 9: 宏观经济指标与旅游指标散点图示例 (GDP vs 国际旅游外汇收入)
        if gdp_value_col and '国际旅游外汇收入' in all_national_data.columns:
            fig, ax = plt.subplots(figsize=(10, 7))
            sns.regplot(x=all_national_data[gdp_value_col], y=all_national_data['国际旅游外汇收入'], ax=ax,
                        scatter_kws={'alpha': 0.6})
            ax.set_title(f'GDP 与 国际旅游外汇收入关系散点图')
            ax.set_xlabel(gdp_value_col)
            ax.set_ylabel('国际旅游外汇收入')
            ax.ticklabel_format(style='plain', axis='x')
            ax.ticklabel_format(style='plain', axis='y')
            save_plot(fig, 'GDP与国际旅游外汇收入散点图')

        # Plot 10: 宏观经济指标与旅游指标散点图示例 (人均收入 vs 国内旅游收入)
        if income_col_name and domestic_revenue_col_name and income_col_name in all_national_data.columns and domestic_revenue_col_name in all_national_data.columns:
            fig, ax = plt.subplots(figsize=(10, 7))
            sns.regplot(x=all_national_data[income_col_name], y=all_national_data[domestic_revenue_col_name], ax=ax,
                        scatter_kws={'alpha': 0.6})
            ax.set_title(f'居民人均收入 与 国内旅游收入关系散点图')
            ax.set_xlabel(income_col_name)
            ax.set_ylabel(domestic_revenue_col_name)
            ax.ticklabel_format(style='plain', axis='x')
            ax.ticklabel_format(style='plain', axis='y')
            save_plot(fig, '人均收入与国内旅游收入散点图')

        # Plot 11: GDP vs. 国内旅游人次
        if gdp_value_col and domestic_tourists_col_name and gdp_value_col in all_national_data.columns and domestic_tourists_col_name in all_national_data.columns:
            fig, ax = plt.subplots(figsize=(10, 7))
            sns.regplot(x=all_national_data[gdp_value_col], y=all_national_data[domestic_tourists_col_name], ax=ax,
                        scatter_kws={'alpha': 0.6}, color='darkgreen')
            ax.set_title(f'GDP 与 国内旅游人次关系散点图')
            ax.set_xlabel(gdp_value_col)
            ax.set_ylabel(domestic_tourists_col_name)
            ax.ticklabel_format(style='plain', axis='x')
            ax.ticklabel_format(style='plain', axis='y')
            save_plot(fig, 'GDP与国内旅游人次散点图')

        # Plot 12: 国际旅游外汇收入 vs 接待国外游客人次 (散点图)
        if '国际旅游外汇收入' in all_national_data.columns and '接待国外游客人次' in all_national_data.columns:
            fig, ax = plt.subplots(figsize=(10, 7))
            sns.regplot(x=all_national_data['接待国外游客人次'], y=all_national_data['国际旅游外汇收入'], ax=ax,
                        scatter_kws={'alpha': 0.6}, color='darkblue')
            ax.set_title('国际旅游外汇收入 与 接待国外游客人次关系散点图')
            ax.set_xlabel('接待国外游客人次')
            ax.set_ylabel('国际旅游外汇收入')
            ax.ticklabel_format(style='plain', axis='x')
            ax.ticklabel_format(style='plain', axis='y')
            save_plot(fig, '国际旅游收入与游客散点图')

    else:
        print("警告: 无法合并国家级宏观经济和旅游数据进行相关性分析，数据可能不完整或列数不足。")
else:
    print("警告: 缺乏足够的国家级宏观经济或旅游数据进行相关性分析。")

# --- 6. 区域差异分析 (柱状图、箱线图、时间序列分省线图) ---
print("\n--- 6. 区域差异分析 ---")

regional_gdp_df = loaded_data.get('地区生产总值分省')
regional_fx_df = loaded_data.get('国际旅游外汇收入分省')
regional_foreign_visitors_df = loaded_data.get('接待国外游客分省')

# 各省GDP分析
if regional_gdp_df is not None and 'Province' in regional_gdp_df.columns and 'Value' in regional_gdp_df.columns:
    latest_year_gdp = regional_gdp_df['Year'].max()
    gdp_latest_data = regional_gdp_df[regional_gdp_df['Year'] == latest_year_gdp].sort_values(by='Value',
                                                                                              ascending=False)

    if not gdp_latest_data.empty:
        # Plot 13: 最新年份各省GDP排名 (Top N)
        top_n = 10
        fig, ax = plt.subplots(figsize=(14, 8))
        sns.barplot(x='Province', y='Value', data=gdp_latest_data.head(top_n), ax=ax, palette='viridis', hue='Province', legend=False)
        ax.set_title(f'{latest_year_gdp}年中国各省GDP排名 (Top {top_n})')
        ax.set_xlabel('省份')
        ax.set_ylabel('GDP (亿元)')
        ax.ticklabel_format(style='plain', axis='y')
        plt.xticks(rotation=45, ha='right')
        save_plot(fig, f'{latest_year_gdp}年各省GDP排名')

        # Plot 14: 选定几个省份的GDP时间趋势
        # 修正：根据数据中实际存在的省份名称进行筛选
        selected_provinces_base = ['广东', '江苏', '山东', '浙江', '河南', '四川', '北京', '上海']
        actual_gdp_provinces_in_data = regional_gdp_df['Province'].unique()
        selected_provinces_gdp_plot = [p for p in actual_gdp_provinces_in_data if
                                       any(base_name in p for base_name in selected_provinces_base)]

        if selected_provinces_gdp_plot:
            plot_df_gdp_regional = regional_gdp_df[regional_gdp_df['Province'].isin(selected_provinces_gdp_plot)]
            if not plot_df_gdp_regional.empty:
                fig, ax = plt.subplots(figsize=(14, 8))
                sns.lineplot(x='Year', y='Value', hue='Province', data=plot_df_gdp_regional, marker='o', ax=ax)
                ax.set_title(f'部分重点省份GDP年度趋势')
                ax.set_xlabel('年份')
                ax.set_ylabel('GDP (亿元)')
                ax.ticklabel_format(style='plain', axis='y')
                ax.legend(title='省份')
                ax.grid(True)
                save_plot(fig, '重点省份GDP年度趋势')
            else:
                print("警告: 选定的省份在GDP数据中不存在或数据为空。")
        else:
            print(f"警告: 未能在GDP数据中找到预设重点省份。可用省份：{actual_gdp_provinces_in_data.tolist()}")
    else:
        print("警告: 地区生产总值最新年份数据为空。")
else:
    print("警告: '地区生产总值分省' 数据集缺失或格式不正确，跳过区域GDP分析。")

# 各省国际旅游外汇收入分析
if regional_fx_df is not None and 'Province' in regional_fx_df.columns and 'Value' in regional_fx_df.columns:
    latest_year_fx = regional_fx_df['Year'].max()
    fx_latest_data = regional_fx_df[regional_fx_df['Year'] == latest_year_fx].sort_values(by='Value', ascending=False)

    if not fx_latest_data.empty:
        # Plot 15: 最新年份各省国际旅游外汇收入排名 (Top N)
        top_n_fx = 10
        fig, ax = plt.subplots(figsize=(14, 8))
        sns.barplot(x='Province', y='Value', data=fx_latest_data.head(top_n_fx), ax=ax, palette='plasma', hue='Province', legend=False)
        ax.set_title(f'{latest_year_fx}年中国各省国际旅游外汇收入排名 (Top {top_n_fx})')
        ax.set_xlabel('省份')
        ax.set_ylabel('国际旅游外汇收入 (百万美元)')
        ax.ticklabel_format(style='plain', axis='y')
        plt.xticks(rotation=45, ha='right')
        save_plot(fig, f'{latest_year_fx}年各省国际旅游外汇收入排名')

        # Plot 16: 国际旅游外汇收入分布 (箱线图)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(y=regional_fx_df['Value'].dropna(), ax=ax, color='skyblue')
        ax.set_title('中国各省国际旅游外汇收入分布')
        ax.set_ylabel('国际旅游外汇收入 (百万美元)')
        ax.ticklabel_format(style='plain', axis='y')
        save_plot(fig, '各省国际旅游外汇收入分布箱线图')

        # Plot 17: 选定几个省份的国际旅游外汇收入时间趋势
        actual_fx_provinces_in_data = regional_fx_df['Province'].unique()
        selected_provinces_fx_plot = [p for p in actual_fx_provinces_in_data if
                                      any(base_name in p for base_name in selected_provinces_base)]

        if selected_provinces_fx_plot:
            plot_df_fx_regional = regional_fx_df[regional_fx_df['Province'].isin(selected_provinces_fx_plot)]
            if not plot_df_fx_regional.empty:
                fig, ax = plt.subplots(figsize=(14, 8))
                sns.lineplot(x='Year', y='Value', hue='Province', data=plot_df_fx_regional, marker='o', ax=ax)
                ax.set_title(f'部分重点省份国际旅游外汇收入年度趋势')
                ax.set_xlabel('年份')
                ax.set_ylabel('国际旅游外汇收入 (百万美元)')
                ax.ticklabel_format(style='plain', axis='y')
                ax.legend(title='省份')
                ax.grid(True)
                save_plot(fig, '重点省份国际旅游外汇收入年度趋势')
            else:
                print("警告: 选定的省份在国际旅游外汇收入数据中不存在或数据为空。")
        else:
            print(f"警告: 未能在国际旅游外汇收入数据中找到预设重点省份。可用省份：{actual_fx_provinces_in_data.tolist()}")
    else:
        print("警告: 国际旅游外汇收入最新年份数据为空。")
else:
    print("警告: '国际旅游外汇收入分省' 数据集缺失或格式不正确，跳过区域外汇收入分析。")

# 各省接待国外游客分析
if regional_foreign_visitors_df is not None and 'Province' in regional_foreign_visitors_df.columns and 'Value' in regional_foreign_visitors_df.columns:
    latest_year_visitors = regional_foreign_visitors_df['Year'].max()
    visitors_latest_data = regional_foreign_visitors_df[
        regional_foreign_visitors_df['Year'] == latest_year_visitors].sort_values(by='Value', ascending=False)

    if not visitors_latest_data.empty:
        # Plot 18: 最新年份各省接待国外游客排名 (Top N)
        top_n_visitors = 10
        fig, ax = plt.subplots(figsize=(14, 8))
        sns.barplot(x='Province', y='Value', data=visitors_latest_data.head(top_n_visitors), ax=ax, palette='rocket', hue='Province', legend=False)
        ax.set_title(f'{latest_year_visitors}年中国各省接待国外游客排名 (Top {top_n_visitors})')
        ax.set_xlabel('省份')
        ax.set_ylabel('接待国外游客人次 (万人次)')
        ax.ticklabel_format(style='plain', axis='y')
        plt.xticks(rotation=45, ha='right')
        save_plot(fig, f'{latest_year_visitors}年各省接待国外游客排名')

        # Plot 19: 各省接待国外游客分布 (箱线图)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(y=regional_foreign_visitors_df['Value'].dropna(), ax=ax, color='lightgreen')
        ax.set_title('中国各省接待国外游客分布')
        ax.set_ylabel('接待国外游客人次 (万人次)')
        ax.ticklabel_format(style='plain', axis='y')
        save_plot(fig, '各省接待国外游客分布箱线图')

    else:
        print("警告: 接待国外游客最新年份数据为空。")
else:
    print("警告: '接待国外游客分省' 数据集缺失或格式不正确，跳过区域游客分析。")

# --- 7. 旅游业发展情况综合分析 (如果数据允许，如柱状图、面积图) ---
print("\n--- 7. 旅游业发展情况综合分析 ---")

tourism_development_df_processed = loaded_data.get('旅游业发展')
if tourism_development_df_processed is not None and 'Indicator' in tourism_development_df_processed.columns and 'Value' in tourism_development_df_processed.columns:

    # 枢轴化数据，将不同指标作为列
    tourism_pivot_df = tourism_development_df_processed.pivot_table(index='Year', columns='Indicator', values='Value')

    # 尝试寻找一些代表性的指标，或者绘制前几个
    selected_dev_cols_plot = []
    # 优先选择的指标关键词 (更新为数据中实际存在的指标)
    priority_indicators_keywords = [
        '入境游客', '入境过夜游客', '国内居民出境人数', '旅游从业人员'
    ]
    for keyword in priority_indicators_keywords:
        # 寻找包含关键词的实际列名
        matched_cols = [col for col in tourism_pivot_df.columns if keyword in str(col)]
        selected_dev_cols_plot.extend(matched_cols)
    selected_dev_cols_plot = list(set(selected_dev_cols_plot))  # 去重

    if not selected_dev_cols_plot and not tourism_pivot_df.empty:
        # 如果没有找到预设指标，就取前5个数值列
        numeric_cols_for_plot = tourism_pivot_df.select_dtypes(include=np.number).columns.tolist()
        selected_dev_cols_plot = numeric_cols_for_plot[:min(5, len(numeric_cols_for_plot))]
        if selected_dev_cols_plot:
            print(f"  未找到预设关键旅游发展指标，将绘制前 {len(selected_dev_cols_plot)} 个数值指标。")
        else:
            print("警告: '旅游业发展' 数据集中没有可绘制的数值列。")

    if selected_dev_cols_plot:
        # Plot 20: 旅游业发展各项指标年度趋势 (折线图，分图)
        fig, axes = plt.subplots(len(selected_dev_cols_plot), 1, figsize=(12, 5 * len(selected_dev_cols_plot)),
                                 sharex=True)
        if len(selected_dev_cols_plot) == 1:  # 如果只有一个子图，axes不是数组
            axes = [axes]

        for i, col in enumerate(selected_dev_cols_plot):
            sns.lineplot(x=tourism_pivot_df.index, y=tourism_pivot_df[col], marker='o', ax=axes[i],
                         color=plt.cm.tab10(i))
            axes[i].set_title(f'中国{col}年度趋势')
            axes[i].set_xlabel('年份')
            axes[i].set_ylabel(col)
            axes[i].ticklabel_format(style='plain', axis='y')
            axes[i].grid(True)

        plt.tight_layout()
        save_plot(fig, '旅游业发展主要指标趋势')

        # Plot 21: 旅游业发展指标之间的相关性热力图
        if not tourism_pivot_df.empty and tourism_pivot_df.shape[1] > 1:
            tourism_dev_corr = tourism_pivot_df.corr(numeric_only=True)
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(tourism_dev_corr, annot=True, cmap='viridis', fmt=".2f", linewidths=.5, ax=ax)
            ax.set_title('旅游业发展各项指标相关性矩阵')
            save_plot(fig, '旅游业发展指标相关性热力图')

        # Plot 22: 旅游总收入构成：国内 vs. 国际 (堆叠面积图)
        # 这部分逻辑修正为使用正确的DataFrame
        if merged_domestic_tourism_df is not None and merged_international_tourism_df is not None and \
           '国内旅游收入' in merged_domestic_tourism_df.columns and '国际旅游外汇收入' in merged_international_tourism_df.columns:

            # 注意：国内收入单位为"亿元"，国际收入为"百万美元"，此处未做汇率转换，仅为趋势对比
            combined_revenue = pd.merge(
                merged_domestic_tourism_df[['国内旅游收入']],
                merged_international_tourism_df[['国际旅游外汇收入']],
                on='Year',
                how='inner'
            ).dropna()

            if not combined_revenue.empty:
                fig, ax = plt.subplots(figsize=(12, 7))
                combined_revenue.plot.area(ax=ax, stacked=True, alpha=0.7)
                ax.set_title('中国旅游总收入构成对比：国内 vs. 国际')
                ax.set_xlabel('年份')
                ax.set_ylabel('收入 (单位不统一)')
                ax.ticklabel_format(style='plain', axis='y')
                ax.legend(title='收入来源')
                ax.grid(True)
                save_plot(fig, '旅游总收入构成_堆叠面积图')
            else:
                print("警告: 无法绘制旅游总收入构成图，国内或国际旅游收入数据合并后为空。")
        else:
            print("警告: '国内旅游收入' 或 '国际旅游外汇收入' 数据缺失，无法绘制收入构成图。")
    else:
        print("警告: '旅游业发展' 数据集中没有可绘制的数值列。")
else:
    print("警告: '旅游业发展' 数据集缺失或格式不正确，跳过综合分析。")

# --- 8. 确保达到20张图以上，添加更多分析 ---

# Plot 23: 各省GDP增长率对比 (选择几个代表性省份)
if regional_gdp_df is not None and 'Province' in regional_gdp_df.columns and 'Value' in regional_gdp_df.columns:
    # 确保每个省份都进行排序，以便正确计算pct_change
    regional_gdp_df_sorted = regional_gdp_df.sort_values(by=['Province', 'Year'])
    regional_gdp_df_sorted['Growth_Rate'] = regional_gdp_df_sorted.groupby('Province')['Value'].pct_change() * 100

    selected_provinces_growth_base = ['广东', '江苏', '上海', '北京', '四川', '湖北']  # 增加几个省份
    actual_gdp_provinces_in_data = regional_gdp_df_sorted['Province'].unique()
    selected_provinces_growth_plot = [p for p in actual_gdp_provinces_in_data if
                                      any(base_name in p for base_name in selected_provinces_growth_base)]

    if selected_provinces_growth_plot:
        plot_growth_df = regional_gdp_df_sorted[
            regional_gdp_df_sorted['Province'].isin(selected_provinces_growth_plot)].dropna(subset=['Growth_Rate'])

        if not plot_growth_df.empty:
            fig, ax = plt.subplots(figsize=(14, 8))
            sns.lineplot(x='Year', y='Growth_Rate', hue='Province', data=plot_growth_df, marker='o', ax=ax)
            ax.set_title('部分重点省份GDP年度增长率趋势')
            ax.set_xlabel('年份')
            ax.set_ylabel('增长率 (%)')
            ax.axhline(0, color='grey', linestyle='--', linewidth=0.8)
            ax.grid(True)
            ax.legend(title='省份')
            save_plot(fig, '重点省份GDP增长率趋势')
        else:
            print("警告: 无法绘制区域GDP增长率趋势图，数据不足。")
    else:
        print(
            f"警告: 未能在区域GDP数据中找到预设重点省份进行增长率分析。可用省份：{actual_gdp_provinces_in_data.tolist()}")

# Plot 24: 各省平均国际旅游外汇收入柱状图 (所有年份均值，Top 15)
if regional_fx_df is not None and 'Province' in regional_fx_df.columns and 'Value' in regional_fx_df.columns:
    avg_fx_per_province = regional_fx_df.groupby('Province')['Value'].mean().sort_values(ascending=False).head(15)
    if not avg_fx_per_province.empty:
        fig, ax = plt.subplots(figsize=(14, 8))
        sns.barplot(x=avg_fx_per_province.index, y=avg_fx_per_province.values, ax=ax, palette='mako', hue=avg_fx_per_province.index, legend=False)
        ax.set_title('各省平均国际旅游外汇收入 (所有年份均值, Top 15)')
        ax.set_xlabel('省份')
        ax.set_ylabel('平均国际旅游外汇收入 (百万美元)')
        ax.ticklabel_format(style='plain', axis='y')
        plt.xticks(rotation=45, ha='right')
        save_plot(fig, '各省平均国际旅游外汇收入')
    else:
        print("警告: 无法绘制各省平均国际旅游外汇收入图，数据不足。")

# Plot 25: 各省GDP与接待国外游客人次散点图 (选择最新共同年份)
if regional_gdp_df is not None and regional_foreign_visitors_df is not None and \
        'Province' in regional_gdp_df.columns and 'Value' in regional_gdp_df.columns and \
        'Province' in regional_foreign_visitors_df.columns and 'Value' in regional_foreign_visitors_df.columns:

    # 找到两个数据集中共同的年份
    common_years_gdp_visitors = list(
        set(regional_gdp_df['Year'].unique()) & set(regional_foreign_visitors_df['Year'].unique()))

    if common_years_gdp_visitors:
        analysis_year_scatter = max(common_years_gdp_visitors)  # 选择最新的共同年份

        gdp_year_data = regional_gdp_df[regional_gdp_df['Year'] == analysis_year_scatter][['Province', 'Value']].rename(
            columns={'Value': 'GDP'})
        visitors_year_data = \
        regional_foreign_visitors_df[regional_foreign_visitors_df['Year'] == analysis_year_scatter][
            ['Province', 'Value']].rename(columns={'Value': 'Visitors'})

        merged_province_scatter_data = pd.merge(gdp_year_data, visitors_year_data, on='Province', how='inner').dropna()

        if not merged_province_scatter_data.empty:
            fig, ax = plt.subplots(figsize=(12, 8))
            # 使用hue和size来增加可视化维度，并用alpha增加透明度
            sns.scatterplot(x='GDP', y='Visitors', data=merged_province_scatter_data, ax=ax, hue='Province',
                            size='Visitors', sizes=(50, 1000), alpha=0.7)

            # 为GDP和游客量最高的几个省份添加文本标签
            # 避免标签重叠，只标记少数重要的点
            for i, row in merged_province_scatter_data.nlargest(5, 'Visitors').iterrows():
                ax.text(row['GDP'] * 1.02, row['Visitors'] * 1.02, row['Province'], fontsize=9, ha='left', va='bottom')
            for i, row in merged_province_scatter_data.nlargest(5, 'GDP').iterrows():
                if row['Province'] not in merged_province_scatter_data.nlargest(5, 'Visitors')[
                    'Province'].tolist():  # 避免重复标记
                    ax.text(row['GDP'] * 1.02, row['Visitors'] * 1.02, row['Province'], fontsize=9, ha='left',
                            va='bottom')

            ax.set_title(f'{analysis_year_scatter}年各省GDP与接待国外游客人次关系')
            ax.set_xlabel(f'GDP ({analysis_year_scatter}年, 亿元)')
            ax.set_ylabel(f'接待国外游客人次 ({analysis_year_scatter}年, 万人次)')
            ax.ticklabel_format(style='plain', axis='x')
            ax.ticklabel_format(style='plain', axis='y')
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)  # 将图例移到外面
            ax.grid(True)
            save_plot(fig, f'{analysis_year_scatter}年各省GDP与接待国外游客散点图')
        else:
            print(f"警告: {analysis_year_scatter}年各省GDP与接待国外游客数据合并后为空或无效。")
    else:
        print("警告: 地区GDP与接待国外游客数据无共同年份可供分析。")

# Plot 26: 各省接待国外游客平均增长率条形图 (Top 15)
if regional_foreign_visitors_df is not None and 'Province' in regional_foreign_visitors_df.columns and 'Value' in regional_foreign_visitors_df.columns:
    regional_foreign_visitors_df_sorted = regional_foreign_visitors_df.sort_values(by=['Province', 'Year'])
    regional_foreign_visitors_df_sorted['Growth_Rate'] = regional_foreign_visitors_df_sorted.groupby('Province')[
                                                             'Value'].pct_change() * 100
    # 过滤掉无穷大或NaN的增长率，例如由于早期数据为0导致
    avg_growth_rate_visitors = \
    regional_foreign_visitors_df_sorted.replace([np.inf, -np.inf], np.nan).dropna(subset=['Growth_Rate']) \
        .groupby('Province')['Growth_Rate'].mean().sort_values(ascending=False).head(15)

    if not avg_growth_rate_visitors.empty:
        fig, ax = plt.subplots(figsize=(14, 8))
        sns.barplot(x=avg_growth_rate_visitors.index, y=avg_growth_rate_visitors.values, ax=ax, palette='cubehelix', hue=avg_growth_rate_visitors.index, legend=False)
        ax.set_title('各省平均接待国外游客人次年度增长率 (Top 15)')
        ax.set_xlabel('省份')
        ax.set_ylabel('平均增长率 (%)')
        plt.xticks(rotation=45, ha='right')
        save_plot(fig, '各省接待国外游客平均增长率')
    else:
        print("警告: 无法绘制各省接待国外游客平均增长率图，数据不足。")

# Plot 27: 旅游业发展主要设施数量趋势 (如星级饭店数量、旅行社数量)
if tourism_development_df_processed is not None and 'Indicator' in tourism_development_df_processed.columns and 'Value' in tourism_development_df_processed.columns:
    tourism_pivot_df = tourism_development_df_processed.pivot_table(index='Year', columns='Indicator', values='Value')

    facility_cols = []
    if '星级饭店数(家)' in tourism_pivot_df.columns:
        facility_cols.append('星级饭店数(家)')
    if '旅行社数(家)' in tourism_pivot_df.columns:
        facility_cols.append('旅行社数(家)')
    if 'A级旅游景区数(个)' in tourism_pivot_df.columns:
        facility_cols.append('A级旅游景区数(个)')

    if facility_cols:
        fig, axes = plt.subplots(len(facility_cols), 1, figsize=(12, 4 * len(facility_cols)), sharex=True)
        if len(facility_cols) == 1:
            axes = [axes]

        for i, col in enumerate(facility_cols):
            sns.lineplot(x=tourism_pivot_df.index, y=tourism_pivot_df[col], marker='o', ax=axes[i],
                         color=plt.cm.tab20(i))
            axes[i].set_title(f'中国{col}年度趋势')
            axes[i].set_xlabel('年份')
            axes[i].set_ylabel(col)
            axes[i].ticklabel_format(style='plain', axis='y')
            axes[i].grid(True)
        plt.tight_layout()
        save_plot(fig, '旅游业主要设施数量趋势')
    else:
        print("警告: 旅游业发展数据中未找到星级饭店数、旅行社数或A级旅游景区数等设施指标。")

print(f"\n--- 分析完成 ---")
print(f"共生成并保存了 {plot_counter} 张分析图表至 '{output_dir}' 目录。")
print("\n请查看 'analysis_plots' 目录下的图片文件。")