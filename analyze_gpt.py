import requests

def analyze_gpt(API_KEY, API_URL, PROXY, MODEL, hex_data):
    api_key = API_KEY
    url = API_URL
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    prompt = "请根据我给出的一段可读文本的前64个字节的16进制编码格式，推断这个可读文本具体是什么编码格式。请必须告诉我编码格式，以及是这个编码格式的原因。"
    prompt += str(hex_data)
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000,
        "temperature": 0.3,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
    proxies = {
        "http": PROXY,
        "https": PROXY,
    }
    try:
        # 判断用不用代理
        if PROXY is None or PROXY != "":
            print("用代理的analyze_gpt")
            response = requests.post(url, headers=headers, json=data, proxies=proxies)
        else:
            print("不用代理的analyze_gpt")
            response = requests.post(url, headers=headers, json=data)

        # Check if the request was successful
        if response.status_code == 200:
            # Extract the generated text from the response
            generated_text = response.json()['choices'][0]['message']['content']
            print(generated_text)
            return generated_text
        else:
            # Handle the error
            print(f"Request failed with status code {response.status_code}")
            generated_text = f"Request failed with status code {response.status_code}"
            return generated_text
    except:
        print("analyze_gpt抛出错误，已忽略")