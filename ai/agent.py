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
            instruction="You are a network security expert. Analyze the following user question and network data, and provide a detailed answer"
        )
        self.runner = InMemoryRunner(agent=self.agent)

    async def analyze_query(self, user_question : str, network_data : list) -> str:
        prompt = f"""
        Analyze the following user question and network data, and provide a detailed answer.

        User Question: {user_question}
        Network Data: {network_data}

        Please provide insights, potential vulnerabilities, and recommendations for securing the network.
        Be kind and informative in your response - your answer must be direct and helpful.

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