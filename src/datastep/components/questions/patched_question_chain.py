from typing import List

from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain_experimental.smart_llm import SmartLLMChain


class QuestionChainPatched(SmartLLMChain):
    def _ideate(
        self,
        run_manager: CallbackManagerForChainRun | None = None,
    ) -> str:
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        response = self.llm.predict(
            # Pass sekf.prompt because SmartLLMChain.ideate dont know what is promt
            # it get just text, so we give text from prompt
            text=str(self.prompt),
            callbacks=_run_manager.get_child(),
        )
        print(response)
        return response
