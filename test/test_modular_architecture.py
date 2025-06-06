import unittest

class TestModularArchitecture(unittest.TestCase):
    def test_imports(self):
        try:
            import app.adapters.aider_adapter
            import app.analytics.metrics_extractor
            import app.context.context_extractor
            import app.core.conflict_detector
            import app.core.logging
            import app.cost.cost_manager
            import app.models.model_registry
            import app.resilience.aider_mcp_resilience
            import app.services.health_checks.config_validation_checks
        except ImportError as e:
            self.fail(f"Import failed: {e}")

if __name__ == "__main__":
    unittest.main()
