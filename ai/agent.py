import os
from urllib import response
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner

load_dotenv()

class NetworkSecurityAgent:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is not set in the environment variables.")
        self.agent = Agent(
            name="security_expert",
            model="gemini-2.5-flash",
            instruction="You are a network security agent. Answer strictly on user's question"
        )
        self.runner = InMemoryRunner(agent=self.agent)

    async def analyze_query(self, user_question : str, network_data : list) -> str:
        prompt = f"""
        Analyze the following user question and network data, and provide a detailed answer for a user's question.

        User Question: {user_question}
        Network Data: {network_data}

        If asked, please provide insights, potential vulnerabilities, and recommendations for securing the network.
        Be kind and informative in your response - your answer must be direct and helpful.

        For a questions that go beyond the scope of you being a network agent answer that it goes beyond your scope.
        An exception is a situation in which the user engages in so-called small talk - in such cases, answer their question normally.

        Keep it concise (max 3-4 paragraphs).
        In return, provide a string type asnwer.
        """
        try:
            response = await self.runner.run_debug(prompt)
            
            text_parts = []
            
            for event in response:
                if hasattr(event, 'content') and hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
            
            final_answer = "".join(text_parts).strip()
            
            return final_answer if final_answer else "AI did not return a valid answer."
            
        except Exception as e:
            return "Error during AI analysis: " + str(e)