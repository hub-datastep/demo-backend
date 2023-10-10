from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI


markdown_template = "Show input in table view. Input: {input}"


class DatastepMarkdownChain:
    def __init__(
        self,
        temperature: int = 0,
        verbose: bool = False
    ):
        llm = OpenAI(temperature=temperature, verbose=verbose)

        markdown_prompt = PromptTemplate(input_variables=["input"], template=markdown_template)
        self.chain = LLMChain(llm=llm, prompt=markdown_prompt)

    async def arun(self, input: str) -> str:
        return await self.chain.arun(input)
