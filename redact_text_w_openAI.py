import os
import openai
import json



error_mapping = {
    openai.error.AuthenticationError: "The service is not accessible, please try again later! [Authentication Error]",
    openai.error.RateLimitError: "Too many requests sent by the demo or server overloaded, please try again later! [RateLimit Error]",
    openai.error.InvalidRequestError: "There was a problem with the format of the request sent. We might receive this error also when the OpenAI API is overloaded. Please try again later! [InvalidRequest Error]",
    openai.error.APIConnectionError: "There was a problem with accessing the OpenAI API. Please try again later! [APIConnectionError]",
    openai.error.ServiceUnavailableError: "There was a problem with accessing the OpenAI API (service unavailable). Please try again later! [ServiceUnavailable Error]",
    openai.error.Timeout: "The response has not been received in time (timeout). Please try again later! [Timeout]",
    openai.error.OpenAIError: "Some general error with OpenAI happened. [InvalidRequest Error: 400]",
    Exception: "Some general error not related to OpenAI happened."
}

def text_to_json(filename):

    with open(filename, encoding='utf-8', mode='r') as file:
        text_data = json.load(file)
    return text_data

def construct_prompt_chat_gpt(user_input):
    
    prompt_qa_examples = text_to_json(
        os.path.join(os.getcwd(), 'static', 'prompt_qa_examples.json'))
    with open(os.path.join(os.getcwd(), 'static', 'prompt_instructions.txt'), encoding='utf8',
              mode='r') as f:
        prompt_instructions = f.read()

    messages = [
        {
            "role": "system",
            "content": "You are a tool AI helping to format, correct and redact long legal texts transcribed from speeches into text to be read by humans. You will receive the text in multiple batches."
        },
        {
            "role": "user",
            "content": prompt_instructions + '\n\n' + prompt_qa_examples[0]["q"]
        },
        {
            "role": "assistant",
            "content": prompt_qa_examples[0]["a"]
        }
    ]
    for i in range(1, len(prompt_qa_examples)):
        messages.append({
            "role": "user",
            "content": prompt_qa_examples[i]["q"]
        })
        messages.append({
            "role": "assistant",
            "content": prompt_qa_examples[i]["a"]
        })
    messages.append({
        "role": "user",
        "content": user_input
    })
    return messages

def call_openAi_redact(user_input: str, apikey: str) -> str:
    openai.api_key=apikey
    messages = construct_prompt_chat_gpt(user_input)
    try:
            completion = openai.ChatCompletion.create(
                    #model="gpt-3.5-turbo",
                    model="gpt-4",
                    #max_tokens=,
                    # when using gpt-3.5, should be 4096 minus the messages size, including prompt and max. question size
                    messages=messages,
                    temperature=0.0
            )
            response_toolbot = completion['choices'][0]['message']['content']
            return response_toolbot

    except tuple(error_mapping.keys()) as error:
        print(f"https://platform.openai.com/docs/guides/error-codes/python-library-error-types Error", error, error_mapping[type(error)])
   
