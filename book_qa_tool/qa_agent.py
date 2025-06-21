from pathlib import Path
from typing import List, Optional

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from PIL import Image
from pydantic import BaseModel, ConfigDict, Field

from book_qa_tool.clients import client
from book_qa_tool.document_utils import extract_random_k_consecutive_pages_as_images
from book_qa_tool.image_utils import encode_images_to_base64
from book_qa_tool.logger import logger


class QAPair(BaseModel):
    """Defines the structure for a question and answer pair."""

    book: str = Field(description="Book name and page")
    question: str = Field(description="The generated question from the document.")
    answer: str = Field(description="The corresponding answer to the question.")


class QAGenerationAgentState(BaseModel):
    """Manages the state of the Q&A generation agent."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    folder_path: Path
    selected_pdf: Optional[Path] = Field(default=None)
    k: int
    pages_as_images: List[Image.Image] = Field(default_factory=list, repr=False)
    qa_pair: Optional[QAPair] = Field(default=None)


class QAGenerationAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.graph = self.build_agent()

    @staticmethod
    def extract_pages_as_images_node(state: QAGenerationAgentState) -> dict:
        """Node to extract pages from a PDF as images."""
        logger.info("Node 'extract_pages_as_images': Starting extraction.")
        folder_path = state.folder_path
        k = state.k
        selected_pdf, images = extract_random_k_consecutive_pages_as_images(
            folder_path, k
        )
        return {"pages_as_images": images, "selected_pdf": selected_pdf}

    def generate_qa_from_images_node(self, state: QAGenerationAgentState) -> dict:
        """Node to generate a Q&A pair from images using a multimodal LLM."""
        logger.info("Node 'generate_qa_from_images': Generating Q&A.")
        images = state.pages_as_images
        if not images:
            raise ValueError("No images found in the state to generate Q&A from.")

        encoded_images = encode_images_to_base64(images)

        prompt_messages = [
            HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": f"""
                        You are an expert assistant. Your task is to generate a single, insightful question and a corresponding detailed answer based *only* on the content of the provided image(s).

                        Please adhere to the following rules:
                        1.  Generate one question and one answer.
                        2.  The question should be something that can be answered solely from the information present in the image(s).
                        3.  The answer should be comprehensive and directly derived from the image content.
                        4.  The Question should be in the format of a job interview question.
                        5.  The question and answer should be understandable without having to look at the images.
                        6.  The answer should be like a job interview answer and be as detailed as possible. Use markdown.
                        
                        Images are from this book: {state.selected_pdf.stem}
                        """,
                    }
                ]
                + [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img}"},
                    }
                    for img in encoded_images
                ]
            )
        ]
        local_client = self.llm_client.with_structured_output(QAPair)

        response = local_client.invoke(prompt_messages)
        print(response)
        return {"qa_pair": response}

    def build_agent(self):
        """Builds the agent's graph using langgraph."""
        builder = StateGraph(QAGenerationAgentState)

        builder.add_node("extract_pages", self.extract_pages_as_images_node)
        builder.add_node("generate_qa", self.generate_qa_from_images_node)

        builder.add_edge(START, "extract_pages")
        builder.add_edge("extract_pages", "generate_qa")
        builder.add_edge("generate_qa", END)

        return builder.compile()


def get_agent_graph():
    agent = QAGenerationAgent(llm_client=client)

    return agent.graph


if __name__ == "__main__":
    books_folder = Path(__file__).parents[1] / "books"

    # Initialize the agent
    qa_agent = QAGenerationAgent(llm_client=client)

    # Define the initial state for the agent
    initial_state = {"folder_path": books_folder, "k": 10}

    # Run the agent
    final_state = qa_agent.graph.invoke(initial_state)

    print("\n--- Generated Q&A ---")
    print(f"Answer: {final_state['selected_pdf']}")
    print(f"Question: {final_state['qa_pair'].question}")
    print(f"Answer: {final_state['qa_pair'].answer}")
    print("---------------------\n")
