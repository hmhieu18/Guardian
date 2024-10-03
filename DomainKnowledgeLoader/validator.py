
from ExecutionEngine.screen_control import AndroidController
from Memory.context import ContextManager,Context
def loop_detection(CM:ContextManager,current_Context:Context)->bool:
    try:
        contextIdx = CM.contexts.index(current_Context)
        return True
    except ValueError:
        return False

def llm_reflection():
    pass

def out_of_app(pkg:str,controller:AndroidController):
    print("xxxxxxxx", pkg, controller.app_info())
    if pkg not in controller.app_info():
        return True
    return False