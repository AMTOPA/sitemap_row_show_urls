import requests
from bs4 import BeautifulSoup
import os
import sys
import io


def configure_console():
    """配置控制台编码"""
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def get_sitemap_path():
    """获取sitemap路径（本地或远程）"""
    config_file = 'sitemap_config.txt'

    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                path = f.read().strip()
                if path and (path.startswith(('http://', 'https://')) or os.path.exists(path)):
                    return path
        except Exception as e:
            print(f"⚠️ 配置读取失败: {e}")

    print("\n=== 请提供sitemap路径 ===")
    print("可接受：")
    print("1. 本地文件路径（如 C:/sitemap.xml 或 ./sitemap.xml）")
    print("2. 网络URL（如 https://math-enthusiast.top/sitemap.xml）")

    while True:
        path = input("请输入sitemap路径: ").strip()
        if not path:
            continue

        # 验证路径
        if path.startswith(('http://', 'https://')):
            try:
                requests.head(path, timeout=3)
                break
            except:
                print("❌ 无法访问该URL，请检查网络和地址")
        elif os.path.exists(path):
            if path.endswith('.xml'):
                break
            print("❌ 请提供XML格式的文件")
        else:
            print("❌ 路径不存在，请检查输入")

    # 保存配置
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(path)
    except Exception as e:
        print(f"⚠️ 配置保存失败（不影响本次使用）: {e}")

    return path


def parse_sitemap(path):
    """解析sitemap文件/URL"""
    try:
        print(f"\n正在解析: {path}")

        if path.startswith(('http://', 'https://')):
            # 处理网络sitemap
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(path, headers=headers, timeout=10)
            response.raise_for_status()
            content = response.content
        else:
            # 处理本地文件
            with open(path, 'rb') as f:
                content = f.read()

        # 解析XML
        soup = BeautifulSoup(content, 'lxml-xml')
        urls = [loc.text for loc in soup.find_all('loc') if loc.text.strip()]

        if not urls:
            raise ValueError("未找到任何有效URL")

        return urls

    except Exception as e:
        print(f"❌ 解析失败: {e}")
        return None


def save_urls(urls, filename='urls.txt'):
    """保存URL到文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(url + '\n' for url in urls)
        return True
    except Exception as e:
        print(f"❌ 文件保存失败: {e}")
        return False


if __name__ == "__main__":
    try:
        configure_console()
        path = get_sitemap_path()
        urls = parse_sitemap(path)

        if urls and save_urls(urls):
            count = len(urls)
            print(f"\n✅ 成功提取 {count} 个URL")

            # 显示结果
            if count <= 20:
                print("\n全部URL列表：")
                print('\n'.join(urls[:20]))
            else:
                print("\n前20个URL：")
                print('\n'.join(urls[:20]))
                print(f"\n...完整列表已保存到 urls.txt（共 {count} 个URL）")

    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生未预期错误: {e}")
        sys.exit(1)