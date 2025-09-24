# -*- coding: utf-8 -*-
"""
HTML文档生成器

使用Jinja2模板生成HTML格式的API文档。
"""

import os

from drf_resource.documentation.settings import API_DOCS_SETTINGS
from jinja2 import Environment, FileSystemLoader, select_autoescape


class HTMLDocumentationGenerator:
    """
    HTML文档生成器
    """

    def __init__(self, documentation_generator):
        self.doc_generator = documentation_generator
        self.setup_jinja2()

    def setup_jinja2(self):
        """设置Jinja2环境"""
        # 模板目录
        template_dirs = [
            os.path.join(os.path.dirname(__file__), "templates"),
        ]

        # 添加用户自定义模板目录
        user_template_dirs = API_DOCS_SETTINGS.get("TEMPLATES", {}).get("DIRS", [])
        template_dirs.extend(user_template_dirs)

        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dirs),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate_html_docs(self, output_dir, force=False):
        """生成HTML文档"""
        # 生成文档数据
        docs_data = self.doc_generator.generate_documentation_data()

        # 生成主页面
        self._generate_index_page(docs_data, output_dir, force)

        # 生成API详情页面
        self._generate_api_detail_pages(docs_data, output_dir, force)

        # 复制静态文件
        self._copy_static_files(output_dir)

    def _generate_index_page(self, docs_data, output_dir, force):
        """生成主页面"""
        template = self.jinja_env.get_template("api_docs_index.html")

        html_content = template.render(docs_data=docs_data, settings=API_DOCS_SETTINGS)

        output_file = os.path.join(output_dir, "index.html")
        if os.path.exists(output_file) and not force:
            return

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _generate_api_detail_pages(self, docs_data, output_dir, force):
        """生成API详情页面"""
        template = self.jinja_env.get_template("api_detail.html")

        detail_dir = os.path.join(output_dir, "api")
        if not os.path.exists(detail_dir):
            os.makedirs(detail_dir)

        for module_name, module_info in docs_data["modules"].items():
            for api_info in module_info["apis"]:
                html_content = template.render(
                    api_info=api_info,
                    module_info=module_info,
                    docs_data=docs_data,
                    settings=API_DOCS_SETTINGS,
                )

                filename = f"{module_name}_{api_info['name']}.html"
                output_file = os.path.join(detail_dir, filename)

                if os.path.exists(output_file) and not force:
                    continue

                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(html_content)

    def _copy_static_files(self, output_dir):
        """复制静态文件"""
        static_dir = os.path.join(output_dir, "static")
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)

        # 生成CSS文件
        self._generate_css_file(static_dir)

        # 生成JavaScript文件
        self._generate_js_file(static_dir)

    def _generate_css_file(self, static_dir):
        """生成CSS文件"""
        css_content = """
/* API文档样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 40px 0;
    text-align: center;
    margin-bottom: 30px;
    border-radius: 8px;
}

.header h1 {
    font-size: 2.5rem;
    margin-bottom: 10px;
}

.header p {
    font-size: 1.1rem;
    opacity: 0.9;
}

.sidebar {
    width: 300px;
    background: white;
    border-radius: 8px;
    padding: 20px;
    margin-right: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    height: fit-content;
    position: sticky;
    top: 20px;
}

.content {
    flex: 1;
    background: white;
    border-radius: 8px;
    padding: 30px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.main-layout {
    display: flex;
    gap: 20px;
}

.api-module {
    margin-bottom: 30px;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    overflow: hidden;
}

.module-header {
    background: #f8f9fa;
    padding: 15px 20px;
    border-bottom: 1px solid #e9ecef;
}

.module-title {
    font-size: 1.3rem;
    color: #495057;
    margin-bottom: 5px;
}

.module-description {
    color: #6c757d;
    font-size: 0.9rem;
}

.api-list {
    padding: 0;
}

.api-item {
    list-style: none;
    border-bottom: 1px solid #f1f3f4;
    padding: 15px 20px;
    transition: background-color 0.2s;
}

.api-item:hover {
    background-color: #f8f9fa;
}

.api-item:last-child {
    border-bottom: none;
}

.api-method {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    margin-right: 10px;
}

.method-get { background: #d4edda; color: #155724; }
.method-post { background: #d1ecf1; color: #0c5460; }
.method-put { background: #fff3cd; color: #856404; }
.method-delete { background: #f8d7da; color: #721c24; }

.api-name {
    font-weight: 600;
    color: #495057;
    text-decoration: none;
}

.api-name:hover {
    color: #007bff;
}

.api-description {
    color: #6c757d;
    font-size: 0.9rem;
    margin-top: 5px;
}

.api-tags {
    margin-top: 8px;
}

.tag {
    display: inline-block;
    background: #e9ecef;
    color: #495057;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.75rem;
    margin-right: 5px;
}

.search-box {
    width: 100%;
    padding: 10px;
    border: 1px solid #ced4da;
    border-radius: 4px;
    margin-bottom: 20px;
    font-size: 14px;
}

.filter-section {
    margin-bottom: 20px;
}

.filter-title {
    font-weight: 600;
    margin-bottom: 10px;
    color: #495057;
}

.filter-item {
    display: block;
    margin-bottom: 5px;
    color: #6c757d;
    text-decoration: none;
    padding: 5px 0;
    transition: color 0.2s;
}

.filter-item:hover {
    color: #007bff;
}

.stats {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 4px;
    margin-bottom: 20px;
}

.stat-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
}

.deprecated {
    opacity: 0.6;
    position: relative;
}

.deprecated::after {
    content: ' (已废弃)';
    color: #dc3545;
    font-size: 0.8rem;
}

@media (max-width: 768px) {
    .main-layout {
        flex-direction: column;
    }
    
    .sidebar {
        width: 100%;
        margin-right: 0;
        margin-bottom: 20px;
        position: static;
    }
    
    .header h1 {
        font-size: 2rem;
    }
}
"""

        css_file = os.path.join(static_dir, "api_docs.css")
        with open(css_file, "w", encoding="utf-8") as f:
            f.write(css_content)

    def _generate_js_file(self, static_dir):
        """生成JavaScript文件"""
        js_content = """
// API文档交互功能
document.addEventListener('DOMContentLoaded', function() {
    // 搜索功能
    const searchBox = document.getElementById('searchBox');
    if (searchBox) {
        searchBox.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const apiItems = document.querySelectorAll('.api-item');
            
            apiItems.forEach(item => {
                const apiName = item.querySelector('.api-name').textContent.toLowerCase();
                const apiDesc = item.querySelector('.api-description');
                const description = apiDesc ? apiDesc.textContent.toLowerCase() : '';
                
                if (apiName.includes(searchTerm) || description.includes(searchTerm)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
    
    // 分类过滤
    const categoryFilters = document.querySelectorAll('.category-filter');
    categoryFilters.forEach(filter => {
        filter.addEventListener('click', function(e) {
            e.preventDefault();
            const category = this.dataset.category;
            
            // 移除其他active状态
            categoryFilters.forEach(f => f.classList.remove('active'));
            this.classList.add('active');
            
            // 过滤API
            const apiItems = document.querySelectorAll('.api-item');
            apiItems.forEach(item => {
                if (category === 'all' || item.dataset.category === category) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
    
    // 标签过滤
    const tagFilters = document.querySelectorAll('.tag-filter');
    tagFilters.forEach(filter => {
        filter.addEventListener('click', function(e) {
            e.preventDefault();
            const tag = this.dataset.tag;
            
            const apiItems = document.querySelectorAll('.api-item');
            apiItems.forEach(item => {
                const tags = item.dataset.tags ? item.dataset.tags.split(',') : [];
                if (tags.includes(tag)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
});
"""

        js_file = os.path.join(static_dir, "api_docs.js")
        with open(js_file, "w", encoding="utf-8") as f:
            f.write(js_content)
