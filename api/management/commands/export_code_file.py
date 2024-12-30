import os
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Export specified code files into a single text file or display in terminal."

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            help='Output file name. If not provided, content will be displayed in terminal.',
            default='api/product_src.txt'
        )

    def handle(self, *args, **options):
        base_dir = "api"
        product_dir = "api/product"
        file_list = [
            # "__init__.py", "apps.py", "models.py", "serializers.py",
            # "signals.py", "urls.py", "views.py"
        ]

        files_to_read = [os.path.join(base_dir, f) for f in file_list]

        for root, _, files in os.walk(product_dir):
            for file in files:
                if file.endswith(".py"):
                    files_to_read.append(os.path.join(root, file))

        content = []
        for file_path in files_to_read:
            if os.path.exists(file_path):
                content.append(f"{file_path}")
                with open(file_path, "r", encoding="utf-8") as f:
                    content.append(f.read())
                content.append("_________________")
            else:
                self.stdout.write(self.style.WARNING(f"File not found: {file_path}"))

        final_content = "\n".join(content)

        # Ghi ra file hoặc in ra terminal
        output_file = options['output']
        if output_file:
            with open(output_file, "w", encoding="utf-8") as out_file:
                out_file.write(final_content)
            self.stdout.write(self.style.SUCCESS(f"Content exported to {output_file}"))
        else:
            self.stdout.write(final_content)
