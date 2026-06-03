"""全局ensemble实例"""
_ensemble_instance = None

def get_ensemble():
    global _ensemble_instance
    if _ensemble_instance is None:
        from services.model_ensemble import ModelEnsemble
        _ensemble_instance = ModelEnsemble()
    return _ensemble_instance
