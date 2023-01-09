import subprocess

from django.core.management.base import BaseCommand

from skytek_arcgis_integration.generator.generator import generate_django_module


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("base-layer-url", type=str, nargs="?")
        parser.add_argument("--module-path", type=str)
        parser.add_argument("--model-name", type=str)
        parser.add_argument("--celery-app-path", type=str)
        parser.add_argument("--no-input", action="store_true")

    def handle(self, *args, **options):
        base_layer_url = options.get("base-layer-url")
        module_path = options.get("module_path")
        model_name = options.get("model_name")
        celery_app_path = options.get("celery_app_path")
        interactive = not options.get("no_input")

        output_dir, module_name = generate_django_module(
            base_layer_url=base_layer_url,
            module_path=module_path,
            model_name=model_name,
            celery_app_path=celery_app_path,
            interactive=interactive,
        )

        try:
            subprocess.run(
                ["python", "-m", "black", output_dir],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            self.stdout.write(
                self.style.SUCCESS(  # pylint: disable=no-member
                    "Successfully ran black"
                )
            )
        except subprocess.CalledProcessError:
            self.stdout.write(
                self.style.ERROR(  # pylint: disable=no-member
                    "Running black FAILED. No worries - you can run it manually later."
                )
            )

        try:
            subprocess.run(
                ["python", "-m", "isort", "--profile=black", output_dir],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            self.stdout.write(
                self.style.SUCCESS(  # pylint: disable=no-member
                    "Successfully ran isort"
                )
            )
        except subprocess.CalledProcessError:
            self.stdout.write(
                self.style.ERROR(  # pylint: disable=no-member
                    "Running isort FAILED.  No worries - you can run it manually later."
                )
            )

        self.stdout.write(
            f"All done. Now add '{module_name}' to INSTALLED_APPS in Django configuration, "
            f"run `makemigrations` and include '{module_name}.urls' in your urls configuration."
        )
