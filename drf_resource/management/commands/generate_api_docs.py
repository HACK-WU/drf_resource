# -*- coding: utf-8 -*-
"""
生成API文档的Django管理命令

使用方法:
python manage.py generate_api_docs
python manage.py generate_api_docs --output-format openapi
python manage.py generate_api_docs --output-format html
"""

import json
import os

from django.core.management.base import BaseCommand, CommandError
from drf_resource.documentation.generator import DocumentationGenerator
from drf_resource.documentation.settings import API_DOCS_SETTINGS


class Command(BaseCommand):
    help = "Generate API documentation for DRF Resource framework"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-format",
            type=str,
            choices=["html", "openapi", "json"],
            default="html",
            help="Output format (default: html)",
        )

        parser.add_argument(
            "--output-dir",
            type=str,
            default=API_DOCS_SETTINGS.get("OUTPUT_DIR"),
            help="Output directory",
        )

        parser.add_argument(
            "--force",
            action="store_true",
            help="Force regeneration even if files exist",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("开始生成API文档..."))

        try:
            generator = DocumentationGenerator()

            # 收集API资源
            self.stdout.write("正在收集API资源...")
            collected_apis = generator.collect_api_resources()

            if not collected_apis:
                self.stdout.write(self.style.WARNING("未找到任何API资源"))
                return

            self.stdout.write(
                self.style.SUCCESS(f"成功收集到 {len(collected_apis)} 个API模块")
            )

            # 创建输出目录
            output_dir = options["output_dir"]
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                self.stdout.write(f"创建输出目录: {output_dir}")

            # 根据格式生成文档
            output_format = options["output_format"]

            if output_format == "openapi":
                self._generate_openapi_docs(generator, output_dir, options["force"])
            elif output_format == "json":
                self._generate_json_docs(generator, output_dir, options["force"])
            else:  # html
                self._generate_html_docs(generator, output_dir, options["force"])

            self.stdout.write(self.style.SUCCESS("API文档生成完成!"))

        except Exception as e:
            raise CommandError(f"生成API文档失败: {e}")

    def _generate_openapi_docs(self, generator, output_dir, force):
        """生成OpenAPI格式文档"""
        output_file = os.path.join(output_dir, "openapi.json")

        if os.path.exists(output_file) and not force:
            self.stdout.write(
                self.style.WARNING(f"文件已存在: {output_file}, 使用 --force 强制覆盖")
            )
            return

        self.stdout.write("正在生成OpenAPI文档...")
        schema = generator.generate_openapi_schema()

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(schema, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(f"OpenAPI文档已保存到: {output_file}"))

    def _generate_json_docs(self, generator, output_dir, force):
        """生成JSON格式文档"""
        output_file = os.path.join(output_dir, "api_docs.json")

        if os.path.exists(output_file) and not force:
            self.stdout.write(
                self.style.WARNING(f"文件已存在: {output_file}, 使用 --force 强制覆盖")
            )
            return

        self.stdout.write("正在生成JSON文档...")
        docs_data = generator.generate_documentation_data()

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(docs_data, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(f"JSON文档已保存到: {output_file}"))

    def _generate_html_docs(self, generator, output_dir, force):
        """生成HTML格式文档"""
        from .html_generator import HTMLDocumentationGenerator

        html_generator = HTMLDocumentationGenerator(generator)
        html_generator.generate_html_docs(output_dir, force)

        self.stdout.write(self.style.SUCCESS(f"HTML文档已保存到: {output_dir}"))
