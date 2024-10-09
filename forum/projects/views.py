from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Project
from .serializers import ProjectSerializer
from django.shortcuts import render, get_object_or_404


class ProjectListCreateView(generics.ListCreateAPIView):
    """
    API view to retrieve and create project instances.

    This view provides GET and POST methods to list existing projects
    and create new ones. It requires the user to be authenticated.

    Attributes:
        queryset (QuerySet): A queryset of all Project instances.
        serializer_class (Serializer): The serializer used to validate
        and serialize Project data.
        permission_classes (list): A list of permission classes
        that determine access rights.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to create a new project.

        Validates the incoming request data and saves a new Project
        instance if the data is valid. Returns the serialized data
        of the created project or error messages if validation fails.

        Args:
            request (Request): The HTTP request object containing
                the data to create a new project.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A response containing the serialized project
            data with a 201 status code if successful, or error
            messages with a 400 status code if validation fails.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectHistoryView(generics.ListAPIView):
    """
    API view to retrieve the history of project instances.

    This view provides a GET method to list all historical records
    of projects. It uses the ProjectSerializer to serialize the
    history data.

    Attributes:
        queryset (QuerySet): A queryset of all historical Project instances.
        serializer_class (Serializer): The serializer used to serialize
            Project history data.
    """

    queryset = Project.history.all()
    serializer_class = ProjectSerializer


def project_history_view(request, project_id):
    """
    Render the history of a specific project.

    This function retrieves the specified project by its ID and
    fetches its history. It then renders the project history
    template with the project and its historical data.

    Args:
        request (HttpRequest): The HTTP request object.
        project_id (UUID): The unique identifier of the project.

    Returns:
        HttpResponse: A rendered HTML page showing the project's
        history.
    """
    project = get_object_or_404(Project, project_id=project_id)
    history = project.history.all()

    return render(request, 'projects/project_history.html', {'project': project, 'history': history})
