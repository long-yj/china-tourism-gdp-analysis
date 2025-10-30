import re
import pandas as pd


def extract_tourism_data(filepath="shuj.txt"):
    """
    从指定的文本文件中提取旅游统计数据，包括月份、接待游客总人数和旅游总收入。
    """
    extracted_data = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 使用正则表达式分割文本，获取每个<文本>标签内的内容
        text_blocks = re.findall(r'<文本>(.*?)</文本>', content, re.DOTALL)

        if not text_blocks:
            print("警告：未找到任何 '<文本>...</文本>' 标签块。请检查文件格式。")
            return pd.DataFrame()

        for block_text in text_blocks:
            # 提取年份和月份
            # 匹配 "YYYY年MM月旅游统计" 或 "YYYY年M月旅游统计" 格式
            date_match = re.search(r'(\d{4}年\d{1,2}月)旅游统计', block_text)
            date_str = date_match.group(1) if date_match else "N/A"

            # 提取接待游客总人数（万人次）
            # 正则表达式不变，因为它已经能够识别之前的多种“接待人数”表述
            tourists_match = re.search(
                r'一、接待(?:游客总人数(?:（万人次）)?|旅游者总计|过夜旅游者总计(?:（万人次）)?|过夜人数合计(?:（万人次）)?)\s*(\d+\.?\d*)',
                block_text
            )
            total_tourists = float(tourists_match.group(1)) if tourists_match else None

            # 提取游客总花费（亿元）或旅游总收入（亿元）
            # 更新的正则表达式：
            # 匹配 "[二三四]、" (即"二、"、"三、"或"四、") 后面跟着：
            #   - "游客总花费"
            #   - "旅游总收入"
            #   - 新增： "旅游收入" (即"旅游"后面可选"总"再接"收入")
            # 然后是（亿元），后面是零个或多个空格，最后是数字
            spending_match = re.search(
                r'[二三四]、(?:游客总花费|旅游(?:总)?收入)（亿元）\s*(\d+\.?\d*)',
                block_text
            )
            total_spending = float(spending_match.group(1)) if spending_match else None

            # 只有当成功提取到月份和至少一个数值时才添加数据
            if date_str != "N/A" or total_tourists is not None or total_spending is not None:
                extracted_data.append({
                    '月份': date_str,
                    '接待游客总人数（万人次）': total_tourists,
                    '旅游总收入（亿元）': total_spending
                })

    except FileNotFoundError:
        print(f"错误：文件 '{filepath}' 未找到。请确保文件存在于脚本的同一目录下或提供正确路径。")
        return pd.DataFrame()  # 返回一个空DataFrame
    except Exception as e:
        print(f"发生错误：读取或处理文件时出现问题: {e}")
        # 可以在这里打印出引发错误的文本块片段，以便调试
        # print(f"错误发生时正在处理的文本块片段：\n{block_text[:500]}...")
        return pd.DataFrame()

    # 创建DataFrame
    df = pd.DataFrame(extracted_data)

    # 对数据进行排序，以确保按时间顺序显示
    if not df.empty:
        # 使用正则表达式从月份字符串中提取年份和月份数字
        def parse_date_for_sort(month_str):
            match = re.search(r'(\d{4})年(\d{1,2})月', month_str)
            if match:
                return int(match.group(1)), int(match.group(2))
            return 0, 0  # 对于“N/A”或其他无法解析的月份，返回0，0，使其排在最前面或最后面

        df['年份'], df['月份数字'] = zip(*df['月份'].apply(parse_date_for_sort))
        df = df.sort_values(by=['年份', '月份数字'], ascending=True).drop(columns=['年份', '月份数字'])

    return df


if __name__ == "__main__":
    df_tourism = extract_tourism_data()

    if not df_tourism.empty:
        output_filename = "旅游统计数据.xlsx"
        try:
            df_tourism.to_excel(output_filename, index=False)
            print(f"数据已成功保存到 '{output_filename}'")
            print("\n请注意：生成的Excel文件只包含shuj.txt中找到的数据。")
            print("如果您需要图片中所有月份的数据，请确保shuj.txt文件包含所有相关月份的详细统计文本。")
        except Exception as e:
            print(f"保存Excel文件时发生错误：{e}")
    else:
        print("未提取到任何有效数据，未生成Excel文件。")