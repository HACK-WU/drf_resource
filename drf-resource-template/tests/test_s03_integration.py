"""S-03 Integration tests for URL routing and example app generation."""
import pytest


class TestS03URLRouting:
    """TC-S03-01: URL routing configuration tests."""

    def test_urls_py_contains_resource_router(self, render_template):
        """TC-S03-01-01: urls.py exists and contains ResourceRouter."""
        project_dir = render_template()
        urls_py = project_dir / "test_project" / "urls.py"

        assert urls_py.exists(), f"urls.py not found at {urls_py}"
        content = urls_py.read_text()
        assert "ResourceRouter" in content, "urls.py should contain 'ResourceRouter'"
        assert "router.register" in content, "urls.py should contain 'router.register'"

    @pytest.mark.parametrize("enable_api_docs,expected", [
        ("yes", True),
        ("no", False),
    ])
    def test_api_docs_route_conditional_generation(self, render_template, enable_api_docs, expected):
        """TC-S03-01-02: API docs routes are conditionally generated."""
        project_dir = render_template(enable_api_docs=enable_api_docs)
        urls_py = project_dir / "test_project" / "urls.py"

        assert urls_py.exists(), f"urls.py not found at {urls_py}"
        content = urls_py.read_text()
        assert ("SpectacularAPIView" in content) == expected, (
            f"Expected 'SpectacularAPIView' {'present' if expected else 'absent'} "
            f"when enable_api_docs='{enable_api_docs}'"
        )


class TestS03ExampleApp:
    """TC-S03-02: Example app generation tests."""

    def test_example_resources_py_exists(self, render_template):
        """TC-S03-02-01: Example resources.py exists with correct content."""
        project_dir = render_template()
        resources_py = project_dir / "test_project" / "apps" / "example" / "resources.py"

        assert resources_py.exists(), f"resources.py not found at {resources_py}"
        content = resources_py.read_text()
        assert "class ExampleResource" in content, "resources.py should contain 'class ExampleResource'"
        assert "perform_request" in content, "resources.py should contain 'perform_request'"

    def test_example_viewsets_py_exists(self, render_template):
        """TC-S03-02-02: Example viewsets.py exists with correct content."""
        project_dir = render_template()
        viewsets_py = project_dir / "test_project" / "apps" / "example" / "viewsets.py"

        assert viewsets_py.exists(), f"viewsets.py not found at {viewsets_py}"
        content = viewsets_py.read_text()
        assert "class ExampleViewSet" in content, "viewsets.py should contain 'class ExampleViewSet'"
        assert "ResourceViewSet" in content, "viewsets.py should contain 'ResourceViewSet'"

    def test_example_serializers_py_exists(self, render_template):
        """TC-S03-02-03: Example serializers.py exists with correct content."""
        project_dir = render_template()
        serializers_py = project_dir / "test_project" / "apps" / "example" / "serializers.py"

        assert serializers_py.exists(), f"serializers.py not found at {serializers_py}"
        content = serializers_py.read_text()
        assert "ExampleRequestSerializer" in content, "serializers.py should contain 'ExampleRequestSerializer'"
        assert "ExampleResponseSerializer" in content, "serializers.py should contain 'ExampleResponseSerializer'"
