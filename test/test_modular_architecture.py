import unittest

class TestModularArchitecture(unittest.TestCase):
    def test_imports(self):
        try:
            import app.adapters.aider_adapter
            import app.analytics.metrics_extractor
            import app.context.context_extractor
            import app.core.conflict_detector
            import app.core.logging
            import app.core.resilience
            import app.cost.cost_manager
            import app.models.model_registry
            import app.tools.health_monitoring_tools
        except ImportError as e:
            self.fail(f"Import failed: {e}")

if __name__ == "__main__":
    unittest.main()
