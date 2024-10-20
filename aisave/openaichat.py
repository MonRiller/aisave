import openai, os, json, time
from datetime import datetime

class Chat():
    def __init__(self, sysinfo, syscore, store=False):
        os.environ['OPENAI_API_KEY'] = sysinfo["api-key"]
        self.client = openai.OpenAI()
        self.sysinfo = sysinfo
        if store and "chat" in sysinfo.keys():
            self.messages=sysinfo["chat"]
        else:
            self.messages = [{"role": "system", "content": f"You are a helpeful and concise AI assistant. Your purpose is to help a user assess the security vulnerabilities in a system. The system is described by the following JSON object. A component is any hardware, software, concept, or other component type that contributes to the system. These components may depend on other components as notated by the components dependencies. A vulnerability is any CVE or custom vulnerability associated with one or multiple components. A functionality is a requirement of a system, it is dependent on certain components. Vulnerabilities have a score relating to the risk incurred by that vulnerability, and functionalities have a score related to the importance of the functionality. A fully deterministic analysis of the system gave it a security score of {syscore} out of 100, but this analysis does not take into account the names and descriptions in the Json. Your job is to enhance the users understanding using your knowledge of cyber security and natural language processing nuances. Here is the json: {json.dumps({key: value for key, value in sysinfo.items() if key != 'api-key'})}"}]
            if store:
                sysinfo["chat"] = self.messages

    def chat(self, message):
        self.messages.append({"role": "user", "content": message})
        completion = self.client.chat.completions.create(model="gpt-4o", messages=self.messages)
        msg = completion.choices[0].message.content
        self.messages.append({"role": "assistant", "content": msg})
        return msg

    def score(self):
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "score_system",
                    "description": "Provide the user with an updated score for the system's security by modifying the deterministic score with an interpretation of the descriptions and names.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "score": {
                                "type": "number",
                                "description": "The score for the system, a float from 0.0 to 100.0 with one decimal point. 100 indicates extremely secure and 0.0 indicates extremely insecure",
                            },
                        },
                        "required": ["score"],
                        "additionalProperties": False,
                    },
                }
            }
        ]
        req_message = [{"role": "user", "content": "Please provide me an updated score for my system, using your knowledge of the descriptions and names. Answer with just the function call."}]
        completion = self.client.chat.completions.create(model="gpt-4o", messages=self.messages + req_message, tools=tools, tool_choice="required", temperature=0)
        return json.loads(completion.choices[0].message.tool_calls[0].function.arguments)["score"]

if __name__ == "__main__":
    tmp = Chat(None, json.loads(open("./out.txt", 'r').read()), 72.7)
    print(tmp.score())
