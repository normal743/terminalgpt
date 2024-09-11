from openai import OpenAI
import requests
import json
import subprocess
import time
import os

# 设置环境变量
os.environ["OPENAI_API_KEY"] = "your-api-key"

def execute_command(code, mode="1"):
    command = code
    print()
    print(f"执行命令: {command}")
    print()
    if mode == "test":
        print(f"你即将执行的程序是：{command}")
        print("该程序将在10s后自动执行")
        print("使用Control+C停止")

        # 倒计时
        for i in range(10, 0, -1):
            time.sleep(1)
            if i <= 3:
                print(f"程序将在{i}s后执行")
    
    # 使用 shell.run 执行命令
    try:
        # 使用 subprocess.run 执行命令，捕获输出
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        
        # 检查返回码并返回结果
        if result.returncode == 0:
            return result.stdout
        else:
            return result.stderr
    except subprocess.CalledProcessError as e:
        # 处理 subprocess 运行中的错误，返回错误代码和消息
        return f"Error code: {e.returncode}, stderr: {e.stderr}"
    except Exception as e:
        # 处理其他可能的异常
        return f"Unexpected error: {str(e)}"


# 配置 OpenAI API 密钥

'''
the following are the api you can use:（get them in enveriment）
Google_Search_API
SCE_ID
the following are the api you can use:（get them in enveriment）
Google_Search_API
SCE_ID
'''

DEFAULT_PROMPT = """
你是一个名为Star的AI助手，作为Steven的个人AI帮手。

你的特点是能使用terminal获得的信息就不会问Steven。
but if u get error mutiple times, please ask user for help
"""
client = OpenAI()
def chat_with_ai(messages, temperature=1, max_tokens=256, top_p=1, frequency_penalty=0, presence_penalty=0):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "execute_command",
                    "description": "Execute a block of terminal code and return the result.(mac)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "The terminal code to be executed. shell = True, exec by subprocess"
                            }
                        },
                        "required": [
                            "code"
                        ],
                        "additionalProperties": False
                    },
                    "strict": False
                }
            },
        ],
        response_format={
            "type": "text"
        }
    )
    return response

def tool_use(tool_calls,conversation_history,debug=False):
            response_content = None
            conversation_history.append({"role": "assistant", "content": response_content,"tool_calls": tool_calls})
            if debug:
                print(tool_calls)
            i = 1
            for tool_call in tool_calls:
                if debug:
                    print(f"Tool call {i}")
                i = i+1
                tool_call_id = tool_call.id
                function_name = tool_call.function.name
                function_arguments = tool_call.function.arguments
                arguments_dict = json.loads(function_arguments)
                code = arguments_dict.get('code')
                if function_name != "execute_command":
                    result = "unknown function"
                else:
                    result = execute_command(code)
                    conversation_history.append({"role": "tool", "content": result,"tool_call_id" : tool_call_id}) 
                if debug:
                    print(f"{i-1}'s result: {result}")  
            # Fetch the updated chat response
            response = chat_with_ai(conversation_history)
            response_content = response.choices[0].message.content
       
            if response.choices[0].message.content is None:
                tool_use(response.choices[0].message.tool_calls,conversation_history,debug)
            else:
                if debug:
                    print(f"response is {response.choices[0].message.content}")
            
                

def main():
    
    conversation_history = [{"role": "system", "content": DEFAULT_PROMPT}]
    debug = False
    while True:
        user_input = input("You: ")
        conversation_history.append({"role": "user", "content": user_input})
        
        # Fetch chat response
        response = chat_with_ai(conversation_history)
        # Process the stream
        response_content = response.choices[0].message.content
        count = 1
        if response_content == None:
            # Extract tool calls, if any    
            count = count + 1
            tool_use(response.choices[0].message.tool_calls,conversation_history,debug)
            response = chat_with_ai(conversation_history)
            response_content = response.choices[0].message.content

        response_content = response.choices[0].message.content
        print(f"Star: {response_content}")

        if debug:
            print()
            print(f"response is {response}")
            print()
            print(f"conversation_history is {conversation_history}")
            print()
        if response_content == None:
            print("how could this possible")
            print("how could this possible")
            print("how could this possible")
            print("how could this possible")
            
        conversation_history.append({"role": "assistant", "content": response_content})
         
        if debug:
            print(conversation_history)

if __name__ == "__main__":
    main()
