from generic_map_api.routers import MapApiRouter

from . import views

router = MapApiRouter()
router.register({{ cookiecutter.module_name | literal }}, views.{{ cookiecutter.model_name }}ApiView, basename={{ cookiecutter.module_name | literal }})

urlpatterns = router.urls
