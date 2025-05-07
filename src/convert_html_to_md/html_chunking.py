from bs4 import BeautifulSoup
from utils import html_cleaning

def chunk_html_by_headings(html_content, heading_tags=["h2"]):
    """
    按照指定的标题标签将HTML内容分块，最小单位为页面
    
    参数:
    - html_content: 完整的HTML内容字符串
    - heading_tags: 用于分块的标题标签列表，如["h1", "h2", "h3"]
                   包含特殊字符串"table"时，会将表格元素（<div class="table">和<table>）作为分块点
    
    返回:
    - 分块后的HTML内容列表和每个块开始页面的原始页码列表
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 找到所有页面元素
    pages = soup.select('div.page')
    
    if not pages:
        # 如果找不到页面，就将整个HTML作为一个chunk返回
        return [html_content], [1]
    
    # 标记每个页面是否包含指定标题标签或表格
    page_is_heading_start = [False] * len(pages)
    
    for i, page in enumerate(pages):
        for tag in heading_tags:
            if tag.lower() == "table":
                # 查找表格元素
                # 1. 有class="table"的div（常见表示法）
                table_divs = page.find_all('div', class_='table')
                # 2. 标准HTML表格标签
                tables = page.find_all('table')
                # print(table_divs, tables)
                
                if table_divs or tables:
                    page_is_heading_start[i] = True
                    break
            else:
                # 普通标题标签
                if page.find(tag):
                    page_is_heading_start[i] = True
                    break
    
    # 确保第一个页面总是一个块的开始
    page_is_heading_start[0] = True
    
    # 根据标记将页面分组为块
    chunks = []
    chunk_start_pages = []  # 存储每个块的开始页码
    current_chunk = []
    
    for i, page in enumerate(pages):
        if page_is_heading_start[i]:
            # 如果当前页面包含标题标签，且不是第一个块
            if current_chunk:
                # 将之前累积的页面作为一个块保存
                chunks.append(current_chunk)
                # 开始新的块
                current_chunk = []
            
            # 记录当前块开始的原始页码（使用1-based索引）
            chunk_start_pages.append(i + 1)
            
        # 将当前页面添加到当前块中
        # 找到页面前的页面分隔符(如果存在)
        page_break = page.find_previous_sibling('div', class_='page-break')
        if page_break:
            current_chunk.append(str(page_break))
        current_chunk.append(str(page))
    
    # 添加最后一个块
    if current_chunk:
        chunks.append(current_chunk)
    
    # 将每个块中的页面列表合并为完整的HTML字符串
    html_chunks = []
    for chunk in chunks:
        chunk_html = "".join(chunk)
        html_chunks.append(chunk_html)
    
    return html_chunks, chunk_start_pages

if __name__ == '__main__':
    
    # 加载HTML内容
    with open('../../assets/test.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    html = html_cleaning(html_content, clean_svg = True, clean_base64 = True)

    # 使用h2标签作为分块标志
    chunks, chunk_start_pages = chunk_html_by_headings(html_content, heading_tags=["h2", "table"])
    # print(chunks)
    # 打印分块结果
    print(f"分成了{len(chunks)}个块")
    for i, chunk in enumerate(chunks):
        print(f"块 {i+1} 长度: {len(chunk)} 字符")
        print("start at: ", chunk_start_pages[i])
        print(chunk)


        
        