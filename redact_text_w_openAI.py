import os
import openai
import json
import logging
import util

SYSTEM_PROMPT = "You are a silent AI tool helping to format the long texts that were transcribed from speeches. You format the text as follows: you break up the text into paragraphs, correct and redact. You may receive the text in multiple batches. Do not include your own text in the response, and use the original language of the text."
#gpt-3.5-turbo esetén prompt_instructions-be kerüljön bele SYSTEM_PROMPT is

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

def text_to_json(filename) -> dict:
    if os.path.getsize(filename) == 0:
        return {}
    with open(filename, encoding='utf-8', mode='r') as file:
        text_data = json.load(file)
    return text_data

def read_prompt_instructions() -> str:
    with open(os.path.join(os.getcwd(), 'static', 'prompt_instructions.txt'), encoding='utf8',
              mode='r') as f:
        prompt_instructions = f.read()
    return prompt_instructions

def read_prompt_qa_examples() -> dict:
    return text_to_json(
        os.path.join(os.getcwd(), 'static', 'prompt_qa_examples.json'))    

def construct_prompt_chat_gpt(user_input):
    prompt_instructions = read_prompt_instructions().strip()
    prompt_qa_examples = read_prompt_qa_examples()
    messages = [{
        "role": "system",
        "content": SYSTEM_PROMPT
        }]
    size_of_messages = util.return_token_length(json.dumps(messages))
    logging.info(f"prompt_size_in_message: {size_of_messages}")
    if len(prompt_qa_examples) > 0:           
        if len(prompt_instructions) > 0:            
            messages.append({
                "role": "user",
                "content": prompt_instructions + '\n\n' + prompt_qa_examples[0]["q"]
                },
                {
                "role": "assistant",
                "content": prompt_qa_examples[0]["a"]
                })
            for i in range(1, len(prompt_qa_examples)):
                messages.append({
                    "role": "user",
                    "content": prompt_qa_examples[i]["q"]
                    },
                    {
                    "role": "assistant",
                    "content": prompt_qa_examples[i]["a"]
                    })
        else:
            for example in prompt_qa_examples:
                messages.append({
                    "role": "user",
                    "content": example["q"]
                    },
                    {
                    "role": "assistant",
                    "content": example["a"]
                    })
    else:
        if len(prompt_instructions) > 0:        
            messages.append({
                "role": "user",
                "content": prompt_instructions
                })
    messages.append({
        "role": "user",
        "content": user_input
        })
    return messages


def call_openAi_redact(user_input: str, apikey: str, model_config: str = "gpt-3.5-turbo", max_completion_length: int = 2048) -> str:
    openai.api_key=apikey
    messages = construct_prompt_chat_gpt(user_input)
    logging.info(f"Messages_prompt: {messages}")
    size_of_messages = util.return_token_length(json.dumps(messages))
    logging.info(f"Messages_length_as_json_dump: {size_of_messages}")
    
    try:
            completion = openai.ChatCompletion.create(
                    model=model_config,
                    max_tokens=max_completion_length,
                    messages=messages,
                    temperature=0.0
            )
            response_toolbot = completion['choices'][0]['message']['content']
            logging.info(f"completion: {completion}")

            return response_toolbot

    except tuple(error_mapping.keys()) as error:
        print(f"https://platform.openai.com/docs/guides/error-codes/python-library-error-types Error", error, error_mapping[type(error)])
   
