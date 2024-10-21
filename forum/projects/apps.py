from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    """
    Configuration class for the 'projects' application.

    This class sets the default field type for automatically created
    primary keys (`BigAutoField`) and specifies the name of the app.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projects'


def ready(self):
    """
    This method is called when the application is ready. It ensures that
    all signal handlers from the `projects.signals` module are registered,
    allowing them to respond to relevant signals such as post-save and
    pre-delete events in the models.
    """

    import projects.signals
