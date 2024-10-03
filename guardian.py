import time

import ExecutionEngine.chatgpt as chatgpt
from configs import *
import Infra.util as util
from Infra.hierarchy import SemanticHierarchy, TotalVisibleHierarchy, VisibleHierarchy
from ExecutionEngine.screen_control import AndroidController
from typing import List, Tuple, Callable
from Infra.infra import TestCase, EventSeq, Event, Widget
from Memory.context import Context, ContextManager
from Agents.agent import Agent

from DomainKnowledgeLoader.error_handler import block_failed_action, restore_state, empty_action_set
from DomainKnowledgeLoader.optimizer import avoid_loop, avoid_repetition, avoid_out_of_app
from DomainKnowledgeLoader.validator import llm_reflection,loop_detection, out_of_app


class Guardian:
    target_context: Context
    target: str
    controller: AndroidController
    app: str
    pkg: str
    attempt_cnt: int
    def __init__(self, _app, _pkg, _target: str, _port:str, _generation_limit=10):
        self.app = _app
        self.pkg = _pkg
        self.target = _target
        self.agent = Agent(_app, _target) # LLM agent contains the LLM driver
        self.context_manager = ContextManager(_pkg, _app, _target) # Context manager is the memory driver
        self.controller = AndroidController(_port) # Android controller is the UI driver
        self.domain_knowledge = {'optimizer':{"avoid_loop":avoid_loop, "avoid_repetition":avoid_repetition,"avoid_out_of_app":avoid_out_of_app}, \
            'validator':{"llm_reflection":llm_reflection, "loop_detection":loop_detection, "out_of_app":out_of_app}, \
            'error_handler':{"block_failed_action":block_failed_action, "restore_state":restore_state, "empty_action_set":empty_action_set}}
        self.attempt_cnt = 0
        self.generation_limit = _generation_limit = 100

    def mainLoop(self) -> EventSeq:
        
        self.context_manager.init_context(self.controller)

        while self.attempt_cnt < self.generation_limit:
            events = self.domain_knowledge['error_handler']['empty_action_set'](self.context_manager.get_current_events(), self.context_manager)
    
                
            event = self.agent.plan(events)  # get the UI event to execute from the LLM agent
              
            event.act(self.controller)
            self.context_manager.update_history(event)
            time.sleep(1)

            
            # check if still in app
            if self.domain_knowledge['validator']['out_of_app'](self.pkg, self.controller):
                self.domain_knowledge['optimizer']['avoid_out_of_app'](self.context_manager)
                #TODO self.domain_knowledge['error_handler']['restore_state'](self.context_manager)
                util.restart_app(pkg=self.pkg)
                time.sleep(4)
                if self.domain_knowledge['validator']['out_of_app'](self.pkg, self.controller):
                    raise ValueError("Restart Failed!")
            
            currentContext = self.context_manager.PreUpdateContext(self.controller)    
            # check loop and repetition
            if self.domain_knowledge['validator']['loop_detection'](self.context_manager,currentContext):
                self.domain_knowledge['optimizer']['avoid_loop'](self.context_manager,currentContext)
            else:
                self.context_manager.PostUpdateContext(currentContext)
            
            
            self.attempt_cnt += 1

        return EventSeq(self.context_manager.getCurHistory())

    def genTestCase(self) -> TestCase:
        return TestCase(self.mainLoop(), [context.hierarchy for context in  self.contexts])


if __name__ == "__main__":
    # pass
    INFODISTILL = InformationDistillationConf.NONE
    app = "Music player"
    pkg = "com.simplemobiletools.musicplayer"
    target = "set the sleep timer for 5 minutes"
    port = "emulator-5554"
# 
    testCase = Guardian(app, pkg, target, port).genTestCase()
    print(testCase._events)
    for event in testCase._events:
        event.dump(True)
        print(event)
