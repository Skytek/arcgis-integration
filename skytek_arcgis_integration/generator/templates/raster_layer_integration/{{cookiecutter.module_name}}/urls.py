from generic_map_api.routers import MapApiRouter
from django.urls import path

from . import views

router = MapApiRouter()
router.register({{ cookiecutter.module_name | literal }}, views.{{ cookiecutter.model_name }}ApiView, basename={{ cookiecutter.module_name | literal }})

urlpatterns = router.urls
urlpatterns += [
    path("image/<int:id>/<str:filename>", views.image, name="{{ cookiecutter.module_name }}-image-download")
]
