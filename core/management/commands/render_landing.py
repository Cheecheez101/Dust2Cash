from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
import sys

class Command(BaseCommand):
    help = r"Render `landing.html` and print to stdout or save to a file with --output"

    def add_arguments(self, parser):
        parser.add_argument("--output", "-o", help="Write rendered HTML to the given file path")

    def handle(self, *args, **options):
        try:
            rendered = render_to_string("landing.html")
        except TemplateDoesNotExist as e:
            raise CommandError(f"Template not found: {e}") from e
        output = options.get("output")
        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(rendered)
            self.stdout.write(self.style.SUCCESS(f"Wrote rendered template to {output}"))
        else:
            sys.stdout.write(rendered)
            self.stdout.write(self.style.SUCCESS("Template rendered successfully"))
