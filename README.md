<div align="center">
<h1>Sitemap Parser Tool 🌐🔗</h1>

<a href="README_zh.md">简体中文</a>  |  ENGLISH

[![GitHub release](https://img.shields.io/github/release/AMTOPA/sitemap_row_show_urls.svg)](https://github.com/AMTOPA/sitemap_row_show_urls/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows-blue)](https://www.microsoft.com/windows)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/AMTOPA/sitemap_row_show_urls/graphs/commit-activity)
[![Blog](https://img.shields.io/badge/📖_My_Blog-math--enthusiast.top-FF5733)](https://math-enthusiast.top/)
</div>

## ✨ Project Introduction

A high-efficiency tool for extracting URLs from sitemap.xml, supporting multiple sitemaps and webpage titles extraction.

---

## 👨‍💻 Author Info
**Pengbo Lu**  
Visit my personal blog: [https://math-enthusiast.top](https://math-enthusiast.top)

---

## 🚀 Key Features
- ✅ Supports parsing multiple sitemap.xml simultaneously
- 🌍 Works with both online and local sitemap files
- 📝 Automatically saves configuration
- 📊 Smart console output control (20 items threshold)
- 📂 Automatically generates urls.txt file

---

## 🛠️ Usage Guide

1. **Install Dependencies**  
   Run `先安装必要的库.bat` (Install Required Libraries.bat)

2. **Run Program**  
   Run `整合链接.bat` (Process Links.bat)

3. **First Time Use**  
   - Enter sitemap URL (supports web URL or local path)  
   - Example inputs:  
     `https://math-enthusiast.top/sitemap.xml`  
     or `./sitemap.xml`  
   ![Input Example](fig/1.png)

4. **Configuration File**  
   Automatically generates `sitemap_config.txt` which can be manually modified

---

## 📊 Output Examples

### Few Links (≤20 items)
- Console shows all links
- Generates `urls.txt` file  
![Few Links Example](fig/2.png)

### Many Links (>20 items)
- Console shows first 20 links
- `urls.txt` contains all links  
![Many Links Example](fig/3.png)

### Parsing Failure
![Failure Example](fig/4.png)

### Local Sitemap Processing
![Local Sitemap Example](fig/5.png)

---

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details