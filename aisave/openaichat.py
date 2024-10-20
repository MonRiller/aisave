import openai, os

class Chat():
    def __init__(self, key, sysinfo):
        self.key = key
        self.sysinfo = sysinfo
        self.messages = [{"role": "system", "content": f"You are a helpeful and concise AI assistant. Your purpose is to help a user assess the security vulnerabilities in a system. The system is described by the following JSON object. A component is any hardware, software, concept, or other component type that contributes to the system. These components may depend on other components as notated by the components dependencies. A vulnerability is any CVE or custom vulnerability associated with one or multiple components. A functionality is a requirement of a system, it is dependent on certain components. Vulnerabilities have a score relating to the risk incurred by that vulnerability, and functionalities have a score related to the importance of the functionality. Here is the json: {json.dumps(sysinfo)}"}]

    def chat(message):
        os.environ['OPENAI_API_KEY'] = self.key
        self.messages.append({"role": "user", "content": message})
        completion = client.chat.completions.create(model="gpt-4o", messages=self.messages)
        msg = completion.choices[0].message
        self.messages.append({"role": "assistant", "content": msg})
        return msg
