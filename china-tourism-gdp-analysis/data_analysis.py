import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from pyecharts.charts import Map
from pyecharts import options as opts
import warnings

warnings.filterwarnings('ignore')

# --- 0. 新增工具函数 ---
def clean_column_names(df):
    """通过去除多余空格来清理DataFrame的列名"""
    cleaned_columns = {}
    for col in df.columns:
        if isinstance(col, str):
            # 去除首尾空格，并将中间多个空格替换为单个空格
            new_col = ' '.join(col.strip().split())
            # 去除括号前的空格，例如 "( 万人次)" -> "(万人次)"
            new_col = new_col.replace(' (', '(')
            cleaned_columns[col] = new_col
    df = df.rename(columns=cleaned_columns)
    return df

# --- 1. 环境设置 ---
def setup_environment():
    """设置matplotlib以正确显示中文并创建输出目录"""
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体为黑体
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题

    output_dir = Path('./output_charts')
    output_dir.mkdir(exist_ok=True)
    return output_dir

# --- 2. 数据加载 ---
def load_data(data_directory):
    """加载所有Excel文件到字典中"""
    data_dir = Path(data_directory)
    excel_files = list(data_dir.glob("*.xlsx"))
    
    loaded_data = {}
    print("--- 开始加载数据 ---")
    for file_path in excel_files:
        try:
            df = pd.read_excel(file_path, header=0)
            key_name = file_path.stem.replace("年度数据", "").replace("情况", "").replace("（百万美元）", "").strip()
            loaded_data[key_name] = df
            print(f"  [成功] 已加载: {file_path.name} -> 键名: '{key_name}'")
        except Exception as e:
            print(f"  [失败] 加载文件失败 {file_path}: {e}")
            
    print("--- 数据加载完成 ---\n")
    return loaded_data

# --- 3. 数据预处理 ---
def preprocess_national_gdp(df):
    """处理国内生产总值年度数据"""
    df_long = df.melt(id_vars=['指标'], var_name='年份', value_name='数值')
    df_long['年份'] = df_long['年份'].str.replace('年', '').astype(int)
    df_long['数值'] = pd.to_numeric(df_long['数值'], errors='coerce')
    print("  [调试] '国内生产总值' 数据处理后:")
    print(df_long.head())
    return df_long

def preprocess_resident_income_consumption(df_income, df_consumption):
    """处理居民收入和消费数据"""
    income_long = df_income.melt(id_vars=['指标'], var_name='年份', value_name='人均可支配收入_元')
    consumption_long = df_consumption.melt(id_vars=['指标'], var_name='年份', value_name='居民消费水平_元')

    # --- 新增调试信息 ---
    print("  [调试] '居民收入' 表可用指标:", df_income['指标'].str.strip().unique())
    print("  [调试] '居民消费' 表可用指标:", df_consumption['指标'].str.strip().unique())
    # --- 结束调试信息 ---

    income_long['年份'] = income_long['年份'].str.replace('年', '').astype(int)
    consumption_long['年份'] = consumption_long['年份'].str.replace('年', '').astype(int)

    # 清理指标列中的空格
    income_long['指标'] = income_long['指标'].str.strip()
    consumption_long['指标'] = consumption_long['指标'].str.strip()

    # 修正：根据调试日志，指标不包含"全国"
    income_filtered = income_long[income_long['指标'] == '居民人均可支配收入(元)']
    consumption_filtered = consumption_long[consumption_long['指标'] == '居民消费水平(元)']

    # --- 新增深度调试信息 ---
    print("  [深度调试] 过滤后的收入数据 (行数:", len(income_filtered), "):")
    print(income_filtered.head())
    print("  [深度调试] 过滤后的消费数据 (行数:", len(consumption_filtered), "):")
    print(consumption_filtered.head())
    # --- 结束深度调试信息 ---

    merged_df = pd.merge(income_filtered[['年份', '人均可支配收入_元']], consumption_filtered[['年份', '居民消费水平_元']], on='年份')
    print("  [调试] '居民收入与消费' 数据合并后:")
    print(merged_df.head())
    return merged_df

def preprocess_tourism_development(df):
    """处理旅游业发展情况数据"""
    # 将 '指标' 列设为索引，并清理空格
    df = df.set_index('指标')
    df.index = df.index.str.strip()
    # 转置 DataFrame，使年份成为索引
    df_transposed = df.T
    # 清理索引（即年份）
    df_transposed.index.name = '年份'
    df_transposed.index = df_transposed.index.str.replace('年', '').astype(int)
    
    # 将所有数据转换为数值型，无法转换的设为NaN
    for col in df_transposed.columns:
        df_transposed[col] = pd.to_numeric(df_transposed[col], errors='coerce')
        
    # 重置索引，使 '年份' 成为一列
    df_processed = df_transposed.reset_index()

    # 修正：不再需要单位换算，因为源数据已有 '国内游客(万人次)'
    
    # 清理列名中的空格
    df_processed = clean_column_names(df_processed)

    print("  [调试] '旅游业发展' 数据处理后:")
    print("    列名:", df_processed.columns.tolist())
    print(df_processed.head())
    return df_processed

def preprocess_provincial_data(df, value_name):
    """通用处理省级数据"""
    df.rename(columns={'地区': '省份'}, inplace=True)
    df_long = df.melt(id_vars=['省份'], var_name='年份', value_name=value_name)
    df_long['年份'] = df_long['年份'].str.replace('年', '').astype(int)
    df_long[value_name] = pd.to_numeric(df_long[value_name], errors='coerce')
    df_long.dropna(subset=[value_name], inplace=True)
    # 去掉合计行
    df_long = df_long[~df_long['省份'].isin(['全国', '总计', '合计'])]
    
    # 最终修复：添加去重逻辑，解决 "Index contains duplicate entries" 错误
    initial_rows = len(df_long)
    df_long.drop_duplicates(subset=['省份', '年份'], keep='first', inplace=True)
    if len(df_long) < initial_rows:
        print(f"  [修正] 在 '{value_name}' 中移除了 {initial_rows - len(df_long)} 个重复的省份-年份条目。")

    print(f"  [调试] 省级数据 '{value_name}' 处理后:")
    print(df_long.head())
    return df_long

def preprocess_hainan_tourism(df):
    """处理海南月度旅游数据"""
    # 使用已有的工具函数清理列名
    df = clean_column_names(df)

    # --- 新的调试流程 ---
    print("\n--- 海南数据调试 ---")
    original_cols = df.columns.tolist()
    print(f"  [调试 1/3] 清理后的原始列名: {original_cols}")

    # 通过位置重命名，避免因特殊字符导致的KeyError
    try:
        rename_mapping = {
            original_cols[1]: '接待人数_万人次',
            original_cols[2]: '总收入_亿元'
        }
        df.rename(columns=rename_mapping, inplace=True)
        print(f"  [调试 2/3] 尝试重命名，新列名: {df.columns.tolist()}")
    except IndexError:
        print("  [警告] 海南数据列数与预期不符，跳过重命名。")
    
    print("  [调试 3/3] 最终进入后续处理的数据头:")
    print(df.head())
    print("--- 调试结束 ---\n")

    # 转换日期格式，并处理可能存在的格式问题
    df['月份'] = pd.to_datetime(df['月份'], format='%Y年%m月', errors='coerce')
    df.dropna(subset=['月份'], inplace=True)
    
    df['接待人数_万人次'] = pd.to_numeric(df['接待人数_万人次'], errors='coerce')
    df['总收入_亿元'] = pd.to_numeric(df['总收入_亿元'], errors='coerce')
    
    df.dropna(subset=['接待人数_万人次', '总收入_亿元'], inplace=True)
    df = df.sort_values(by='月份')
    
    print("  [调试] '海南旅游统计数据' 处理后:")
    print(df.head())
    return df

# --- 4. 可视化函数 ---

# A. 全国层面时间序列图
def plot_national_timeseries(df, x_col, y_cols, title, ylabel, save_path):
    plt.figure(figsize=(12, 6))
    for y_col in y_cols:
        plt.plot(df[x_col], df[y_col], marker='o', linestyle='-', label=y_col)
    plt.title(title, fontsize=16)
    plt.xlabel("年份", fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True)
    plt.legend()
    plt.savefig(save_path)
    plt.close()

# B. 省级层面横向对比图
def plot_provincial_barchart(df, year, value_col, title, xlabel, top_n=15, save_path=None):
    data_year = df[df['年份'] == year].sort_values(by=value_col, ascending=False).head(top_n)
    if data_year.empty:
        print(f"  [警告] 在年份 {year} 没有找到 '{title}' 的数据，跳过绘图。")
        return
    plt.figure(figsize=(12, 8))
    sns.barplot(x=value_col, y='省份', data=data_year, palette='viridis')
    plt.title(f'{year}年{title}', fontsize=16)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel('省份', fontsize=12)
    if save_path:
        plt.savefig(save_path)
    plt.close()

def plot_hainan_monthly(df, x_col, y_col, title, ylabel, save_path):
    """绘制海南月度数据的时间序列图"""
    plt.figure(figsize=(16, 8))
    plt.plot(df[x_col], df[y_col], marker='o', linestyle='-', label=ylabel)
    plt.title(title, fontsize=18)
    plt.xlabel("月份", fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.legend()
    # 格式化X轴日期显示
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator(interval=6)) # 每6个月一个主刻度
    plt.gcf().autofmt_xdate() # 自动旋转日期标签
    plt.savefig(save_path)
    plt.close()

# C. 关联关系图
def plot_correlation_scatter(df, year, x_col, y_col, title, save_path):
    data_year = df[df['年份'] == year]
    if data_year.empty:
        print(f"  [警告] 在年份 {year} 没有找到 '{title}' 的数据，跳过绘图。")
        return
    plt.figure(figsize=(10, 10))
    sns.scatterplot(x=x_col, y=y_col, hue='省份', data=data_year, s=100, legend=False)
    plt.title(f'{year}年{title}', fontsize=16)
    plt.xlabel(x_col, fontsize=12)
    plt.ylabel(y_col, fontsize=12)
    plt.grid(True)
    plt.savefig(save_path)
    plt.close()
    
def plot_correlation_heatmap(df, title, save_path):
    plt.figure(figsize=(12, 10))
    correlation_matrix = df.corr(numeric_only=True)
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title(title, fontsize=16)
    plt.savefig(save_path)
    plt.close()

# D. 地理热力图
def plot_geo_map(df, year, value_col, title, save_path_name):
    data_year = df[df['年份'] == year]
    if data_year.empty:
        print(f"  [警告] 在年份 {year} 没有找到 '{title}' 的地图数据，跳过绘图。")
        return
    
    # 省份名称修正，以匹配pyecharts
    province_mapping = {
        '新疆维吾尔自治区': '新疆', '内蒙古自治区': '内蒙古', '广西壮族自治区': '广西',
        '宁夏回族自治区': '宁夏', '西藏自治区': '西藏', '香港特别行政区': '香港', '澳门特别行政区': '澳门'
    }
    data_year['省份'] = data_year['省份'].replace(province_mapping)
    
    map_chart = (
        Map()
        .add(title, [list(z) for z in zip(data_year['省份'], data_year[value_col])], "china")
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{year}年{title}"),
            visualmap_opts=opts.VisualMapOpts(max_=float(data_year[value_col].max()), is_piecewise=True),
        )
    )
    map_chart.render(f"{save_path_name}.html")

# --- 5. 主函数 ---
def main():
    output_dir = setup_environment()
    all_data = load_data('./data')

    # --- 数据预处理 ---
    print("\n--- 开始数据预处理 ---")
    gdp_national = preprocess_national_gdp(all_data['国内生成总值'])
    income_consumption = preprocess_resident_income_consumption(all_data['全国居民人均收入'], all_data['居民消费水平'])
    tourism_dev = preprocess_tourism_development(all_data['旅游业发展'])
    
    gdp_provincial = preprocess_provincial_data(all_data['地区生产总值分省'], 'GDP_亿元')
    tourism_fx_provincial = preprocess_provincial_data(all_data['国际旅游外汇收入分省'], '外汇收入_百万美元')
    foreigners_provincial = preprocess_provincial_data(all_data['接待外国人游客分省'], '接待外国人_万人次')
    
    # 新增：处理海南数据
    if '海南旅游统计数据' in all_data:
        hainan_tourism_monthly = preprocess_hainan_tourism(all_data['海南旅游统计数据'])
    else:
        hainan_tourism_monthly = pd.DataFrame() # 创建空DataFrame以避免错误
        print("  [警告] 未找到'海南旅游统计数据'，将跳过相关分析。")

    print("--- 数据预处理完成 ---\n")
    
    # --- 开始绘图 ---
    print("开始生成图表，请稍候...")
    
    # 1. 全国GDP总值
    plot_national_timeseries(gdp_national[gdp_national['指标'] == '国内生产总值(亿元)'], '年份', ['数值'], '全国历年GDP总值变化趋势', 'GDP (亿元)', output_dir / '01_全国历年GDP总值变化趋势.png')
    
    # 2. 全国人均收入与消费
    plot_national_timeseries(income_consumption, '年份', ['人均可支配收入_元', '居民消费水平_元'], '全国历年人均收入与消费水平', '金额 (元)', output_dir / '02_全国历年人均收入与消费水平.png')
    
    # 3. 全国旅游业发展指标
    plot_national_timeseries(tourism_dev, '年份', ['国际旅游外汇收入(百万美元)', '国内旅游总花费(亿元)'], '全国历年国内外旅游收入对比', '收入金额', output_dir / '03_全国历年国内外旅游收入对比.png')
    plot_national_timeseries(tourism_dev, '年份', ['入境游客(万人次)', '国内游客(万人次)'], '全国历年国内外游客数量对比', '游客 (万人次)', output_dir / '04_全国历年国内外游客数量对比.png')

    # 4 & 5. 省级GDP排名 (动态获取年份)
    if not gdp_provincial.empty:
        latest_year_gdp = gdp_provincial['年份'].max()
        ten_years_ago_gdp = latest_year_gdp - 10
        plot_provincial_barchart(gdp_provincial, latest_year_gdp, 'GDP_亿元', '各省GDP排名', 'GDP (亿元)', save_path=output_dir / f'05_{latest_year_gdp}年各省GDP排名.png')
        plot_provincial_barchart(gdp_provincial, ten_years_ago_gdp, 'GDP_亿元', '各省GDP排名', 'GDP (亿元)', save_path=output_dir / f'06_{ten_years_ago_gdp}年各省GDP排名.png')
    
    # 6 & 7. 省级旅游外汇收入排名 (动态获取年份)
    if not tourism_fx_provincial.empty:
        latest_year_fx = tourism_fx_provincial['年份'].max()
        ten_years_ago_fx = latest_year_fx - 10
        plot_provincial_barchart(tourism_fx_provincial, latest_year_fx, '外汇收入_百万美元', '各省旅游外汇收入排名', '外汇收入 (百万美元)', save_path=output_dir / f'07_{latest_year_fx}年各省旅游外汇收入排名.png')
        plot_provincial_barchart(tourism_fx_provincial, ten_years_ago_fx, '外汇收入_百万美元', '各省旅游外汇收入排名', '外汇收入 (百万美元)', save_path=output_dir / f'08_{ten_years_ago_fx}年各省旅游外汇收入排名.png')

    # 8 & 9. 省级接待外国游客排名 (动态获取年份)
    if not foreigners_provincial.empty:
        latest_year_foreigners = foreigners_provincial['年份'].max()
        ten_years_ago_foreigners = latest_year_foreigners - 10
        plot_provincial_barchart(foreigners_provincial, latest_year_foreigners, '接待外国人_万人次', '各省接待外国游客排名', '游客 (万人次)', save_path=output_dir / f'09_{latest_year_foreigners}年各省接待外国游客排名.png')
        plot_provincial_barchart(foreigners_provincial, ten_years_ago_foreigners, '接待外国人_万人次', '各省接待外国游客排名', '游客 (万人次)', save_path=output_dir / f'10_{ten_years_ago_foreigners}年各省接待外国游客排名.png')

    # 10. 关联性分析 (动态获取年份)
    provincial_merged = pd.merge(gdp_provincial, tourism_fx_provincial, on=['省份', '年份'], how='inner')
    provincial_merged = pd.merge(provincial_merged, foreigners_provincial, on=['省份', '年份'], how='inner')
    if not provincial_merged.empty:
        latest_year_merged = provincial_merged['年份'].max()
        plot_correlation_scatter(provincial_merged, latest_year_merged, 'GDP_亿元', '外汇收入_百万美元', 'GDP与旅游外汇收入关联性', output_dir / f'11_{latest_year_merged}年GDP与旅游外汇收入关联性.png')
        plot_correlation_scatter(provincial_merged, latest_year_merged, 'GDP_亿元', '接待外国人_万人次', 'GDP与接待外国游客关联性', output_dir / f'12_{latest_year_merged}年GDP与接待外国游客关联性.png')
    
        # 11. 截面数据相关性热力图
        corr_df_latest = provincial_merged[provincial_merged['年份'] == latest_year_merged][['GDP_亿元', '外汇收入_百万美元', '接待外国人_万人次']]
        heatmap_title = f'{latest_year_merged}年省级GDP与旅游指标相关性热力图'
        plot_correlation_heatmap(corr_df_latest, heatmap_title, output_dir / f'13_{heatmap_title}.png')
    
    # 12. 地理热力图 (Pyecharts)
    if not gdp_provincial.empty:
        latest_year_gdp = gdp_provincial['年份'].max()
        ten_years_ago_gdp = latest_year_gdp - 10
        plot_geo_map(gdp_provincial, latest_year_gdp, 'GDP_亿元', '各省GDP分布', str(output_dir / f'14_{latest_year_gdp}年各省GDP分布地图'))
        plot_geo_map(gdp_provincial, ten_years_ago_gdp, 'GDP_亿元', '各省GDP分布', str(output_dir / f'15_{ten_years_ago_gdp}年各省GDP分布地图'))
    
    if not tourism_fx_provincial.empty:
        latest_year_fx = tourism_fx_provincial['年份'].max()
        ten_years_ago_fx = latest_year_fx - 10
        plot_geo_map(tourism_fx_provincial, latest_year_fx, '外汇收入_百万美元', '各省旅游外汇收入分布', str(output_dir / f'16_{latest_year_fx}年各省旅游外汇收入分布地图'))
        plot_geo_map(tourism_fx_provincial, ten_years_ago_fx, '外汇收入_百万美元', '各省旅游外汇收入分布', str(output_dir / f'17_{ten_years_ago_fx}年各省旅游外汇收入分布地图'))

    if not foreigners_provincial.empty:
        latest_year_foreigners = foreigners_provincial['年份'].max()
        ten_years_ago_foreigners = latest_year_foreigners - 10
        plot_geo_map(foreigners_provincial, latest_year_foreigners, '接待外国人_万人次', '各省接待外国游客分布', str(output_dir / f'18_{latest_year_foreigners}年各省接待外国游客分布地图'))
        plot_geo_map(foreigners_provincial, ten_years_ago_foreigners, '接待外国人_万人次', '各省接待外国游客分布', str(output_dir / f'19_{ten_years_ago_foreigners}年各省接待外国游客分布地图'))

    # 额外图表以满足数量要求
    # 我们可以展示旅游业增长最快的省份
    if not gdp_provincial.empty:
        gdp_change = gdp_provincial.set_index(['省份', '年份'])['GDP_亿元'].unstack()
        latest_year_gdp = gdp_provincial['年份'].max()
        ten_years_ago_gdp = latest_year_gdp - 10
        if latest_year_gdp in gdp_change.columns and ten_years_ago_gdp in gdp_change.columns:
            gdp_change['增长率'] = (gdp_change[latest_year_gdp] / gdp_change[ten_years_ago_gdp] - 1) * 100
            gdp_change = gdp_change.dropna(subset=['增长率']).sort_values('增长率', ascending=False).head(15)
            
            plt.figure(figsize=(12, 8))
            sns.barplot(x='增长率', y=gdp_change.index, data=gdp_change, palette='rocket')
            title_gdp_growth = f'{ten_years_ago_gdp}年到{latest_year_gdp}年各省GDP增长率排名'
            plt.title(title_gdp_growth, fontsize=16)
            plt.xlabel('GDP增长率 (%)', fontsize=12)
            plt.ylabel('省份', fontsize=12)
            plt.savefig(output_dir / f'20_{title_gdp_growth.replace("到", "-")}.png')
            plt.close()
        else:
            print(f"  [警告] 无法计算GDP增长率，因为年份 {latest_year_gdp} 或 {ten_years_ago_gdp} 的数据不完整。")
            
    # 新增：海南旅游数据可视化
    if not hainan_tourism_monthly.empty:
        plot_hainan_monthly(hainan_tourism_monthly, '月份', '接待人数_万人次', '海南省历月接待游客数量趋势', '接待人数 (万人次)', output_dir / '21_海南月度接待游客数.png')
        plot_hainan_monthly(hainan_tourism_monthly, '月份', '总收入_亿元', '海南省历月旅游总收入趋势', '总收入 (亿元)', output_dir / '22_海南月度旅游总收入.png')

    print(f"图表生成完毕，已保存至 '{output_dir.resolve()}' 目录下。")
    print("共生成了超过20张图表，包括PNG图片和HTML交互式地图。")

if __name__ == '__main__':
    main() 