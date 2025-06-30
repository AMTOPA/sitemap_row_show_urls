import requests
from bs4 import BeautifulSoup
import os
import sys
import io
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import re


def configure_console():
    """配置控制台编码"""
    if sys.platform == 'win32':
        import win32console
        win32console.SetConsoleOutputCP(65001)  # 设置为UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def sanitize_filename(filename):
    """清理文件名中的非法字符"""
    return re.sub(r'[\\/*?:"<>|]', "_", filename)


def ensure_dirs():
    """确保配置和输出目录存在"""
    config_dir = './config'
    output_dir = './output'

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    return config_dir, output_dir


def get_sitemap_paths():
    """获取多个sitemap路径（本地或远程）"""
    config_dir, _ = ensure_dirs()
    config_file = os.path.join(config_dir, 'sitemap_config.txt')

    # 尝试读取历史配置
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                paths = [line.strip() for line in f if line.strip()]
                if paths and all(
                        p.startswith(('http://', 'https://')) or os.path.exists(p)
                        for p in paths
                ):
                    print("\n=== 检测到历史配置 ===")
                    for i, path in enumerate(paths, 1):
                        print(f"{i}. {path}")
                    use_history = input("\n是否使用这些路径？(y/n, 默认y): ").strip().lower()
                    if use_history in ('y', 'yes', ''):
                        return paths
        except Exception as e:
            print(f"⚠️ 配置读取失败: {e}")

    # 手动输入多个路径
    print("\n=== 请输入多个sitemap路径（每行一个，空行结束）===")
    print("可接受：")
    print("1. 本地文件路径（如 C:/sitemap.xml 或 ./sitemap.xml）")
    print("2. 网络URL（如 https://example.com/sitemap.xml）")
    print("3. 输入空行结束")

    paths = []
    while True:
        path = input(f"路径 {len(paths) + 1}: ").strip()
        if not path:
            if paths:
                break
            print("❌ 至少输入一个路径")
            continue

        # 验证路径
        if path.startswith(('http://', 'https://')):
            try:
                requests.head(path, timeout=3)
                paths.append(path)
            except:
                print("❌ 无法访问该URL，请检查网络和地址")
        elif os.path.exists(path):
            if path.endswith('.xml'):
                paths.append(path)
            else:
                print("❌ 请提供XML格式的文件")
        else:
            print("❌ 路径不存在，请检查输入")

    # 保存配置
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(paths))
    except Exception as e:
        print(f"⚠️ 配置保存失败（不影响本次使用）: {e}")

    return paths


def parse_sitemap(path, is_root=True):
    """解析单个sitemap文件/URL，支持嵌套sitemap索引"""
    try:
        if is_root:
            print(f"\n正在解析: {path}")

        if path.startswith(('http://', 'https://')):
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(path, headers=headers, timeout=10)
            response.raise_for_status()
            content = response.content
        else:
            with open(path, 'rb') as f:
                content = f.read()

        soup = BeautifulSoup(content, 'lxml-xml')

        # 检查是否是sitemap索引文件
        sitemapindex = soup.find_all('sitemap')
        if sitemapindex:
            if is_root:
                print("检测到sitemap索引文件，开始解析嵌套sitemap...")
            urls = []
            for sitemap in sitemapindex:
                loc = sitemap.find('loc')
                if loc and loc.text.strip():
                    nested_url = loc.text.strip()
                    print(f"正在处理嵌套sitemap: {nested_url}")
                    try:
                        nested_urls = parse_sitemap(nested_url, is_root=False)
                        urls.extend(nested_urls)
                    except Exception as e:
                        print(f"❌ 嵌套sitemap解析失败: {nested_url} - {str(e)}")
            return path, urls

        # 普通sitemap文件
        urls = [loc.text.strip() for loc in soup.find_all('loc') if loc.text.strip()]

        if not urls:
            raise ValueError("未找到任何有效URL")

        return path, urls

    except Exception as e:
        print(f"❌ 解析失败: {path} - {e}")
        return path, []


def parse_multiple_sitemaps(paths):
    """解析多个sitemap文件/URL，返回{路径: URL列表}的字典"""
    sitemap_urls = {}
    with tqdm(total=len(paths), desc="解析sitemap", unit="file") as pbar:
        for path in paths:
            original_path, urls = parse_sitemap(path)
            if urls:
                sitemap_urls[original_path] = urls
                pbar.set_postfix_str(f"URLs: {sum(len(v) for v in sitemap_urls.values())}")
            pbar.update(1)
    return sitemap_urls


def fetch_title(url, verbose=False):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else "无标题"
        if verbose:
            print(f"✅ 成功获取: {url} - {title}")
        return url, title
    except Exception as e:
        if verbose:
            print(f"❌ 获取失败: {url} - 错误: {str(e)}")
        return url, f"获取标题失败: {str(e)}"


def fetch_titles_for_sitemap(urls, max_workers=10, progress_type='bar'):
    """为单个sitemap的URL列表获取标题"""
    url_titles = []
    if progress_type == 'bar':
        with tqdm(total=len(urls), desc="获取标题", unit="URL") as pbar:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(fetch_title, url, False): url for url in urls}
                for future in as_completed(futures):
                    url = futures[future]
                    try:
                        url, title = future.result()
                        url_titles.append((url, title))
                        pbar.update(1)
                        pbar.set_postfix_str(f"最新: {title[:20]}...")
                    except Exception as e:
                        url_titles.append((url, f"处理出错: {str(e)}"))
                        pbar.update(1)
    else:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(fetch_title, url, True): url for url in urls}
            for future in as_completed(futures):
                url = futures[future]
                try:
                    url, title = future.result()
                    url_titles.append((url, title))
                except Exception as e:
                    print(f"❌ 处理 {url} 时出错: {e}")
                    url_titles.append((url, f"处理出错: {str(e)}"))

    return url_titles


def save_sitemap_data(sitemap_urls, sitemap_titles=None):
    """保存每个sitemap的数据到单独文件"""
    _, output_dir = ensure_dirs()

    for path, urls in sitemap_urls.items():
        # 生成基础文件名
        if path.startswith(('http://', 'https://')):
            base_name = sanitize_filename(path.split('//')[1].replace('/', '_'))
        else:
            base_name = sanitize_filename(os.path.basename(path).replace('.xml', ''))

        # 保存URL列表
        urls_filename = os.path.join(output_dir, f"{base_name}—urls.txt")
        try:
            with open(urls_filename, 'w', encoding='utf-8') as f:
                f.writelines(url + '\n' for url in urls)
            print(f"✅ {path} 的URL列表已保存到 {urls_filename}")
        except Exception as e:
            print(f"❌ {path} 的URL列表保存失败: {e}")

        # 保存带标题的URL列表（如果提供）
        if sitemap_titles and path in sitemap_titles:
            titles_filename = os.path.join(output_dir, f"{base_name}—UrlsWithTitles.txt")
            try:
                with open(titles_filename, 'w', encoding='utf-8') as f:
                    for url, title in sitemap_titles[path]:
                        f.write(f"{url}\t{title}\n")
                print(f"✅ {path} 的带标题URL列表已保存到 {titles_filename}")
            except Exception as e:
                print(f"❌ {path} 的带标题URL列表保存失败: {e}")


def get_progress_preference():
    """获取用户对进度显示方式的偏好"""
    print("\n=== 进度显示选项 ===")
    print("1. 进度条模式 (适合大量URL)")
    print("2. 逐个输出模式 (适合少量URL)")

    while True:
        choice = input("请选择进度显示方式 (1/2): ").strip()
        if choice == '1':
            return 'bar'
        elif choice == '2':
            return 'verbose'
        else:
            print("❌ 无效输入，请选择1或2")


if __name__ == "__main__":
    try:
        configure_console()
        paths = get_sitemap_paths()
        sitemap_urls = parse_multiple_sitemaps(paths)

        if not sitemap_urls:
            print("❌ 未提取到任何有效URL")
            sys.exit(1)

        total_urls = sum(len(urls) for urls in sitemap_urls.values())
        print(f"\n✅ 成功提取 {total_urls} 个URL（来自 {len(sitemap_urls)} 个sitemap）")

        # 保存原始URL列表（每个sitemap单独文件）
        save_sitemap_data(sitemap_urls)

        # 询问用户是否需要获取标题
        get_titles = input("\n是否要获取网页标题？(y/n, 默认y): ").strip().lower()
        if get_titles in ('y', 'yes', ''):
            progress_type = get_progress_preference()
            start_time = time.time()

            # 为每个sitemap获取标题
            sitemap_titles = {}
            for path, urls in sitemap_urls.items():
                print(f"\n正在处理 {path} 的URL...")
                url_titles = fetch_titles_for_sitemap(urls, progress_type=progress_type)
                sitemap_titles[path] = url_titles

            elapsed_time = time.time() - start_time

            # 保存带标题的URL列表（每个sitemap单独文件）
            save_sitemap_data(sitemap_urls, sitemap_titles)

            # 显示结果摘要
            print(f"\n⏱️ 处理完成，总耗时: {elapsed_time:.2f}秒")
            success_count = sum(
                1 for titles in sitemap_titles.values()
                for _, title in titles
                if not title.startswith('获取标题失败')
            )
            print(f"📊 统计: {total_urls}个URL | 成功获取标题: {success_count}")

            # 显示部分结果
            for path in list(sitemap_urls.keys())[:3]:  # 最多显示前3个sitemap的样例
                print(f"\n=== {path} 的结果样例 ===")
                for url, title in sitemap_titles[path][:5]:
                    print(f"{url} - {title}")
                if len(sitemap_titles[path]) > 5:
                    print(f"...（共 {len(sitemap_titles[path])} 条，完整结果见文件）")
        else:
            print("\n已跳过获取标题步骤")
            # 显示部分URL样例
            for path in list(sitemap_urls.keys())[:3]:
                print(f"\n=== {path} 的URL样例 ===")
                print('\n'.join(sitemap_urls[path][:5]))
                if len(sitemap_urls[path]) > 5:
                    print(f"...（共 {len(sitemap_urls[path])} 条，完整结果见文件）")

    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生未预期错误: {e}")
        sys.exit(1)