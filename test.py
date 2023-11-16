def analyze_gpt(API_KEY, API_URL, PROXY, MODEL, hex_data):
    # 设置API访问的密钥和请求头
    api_key = API_KEY
    url = API_URL
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    # 构建发送给API的提示信息，要求推断编码格式
    prompt = "请根据我给出的一段可读文本的前64个字节的16进制编码格式，推断这个可读文本具体是什么编码格式。请必须告诉我编码格式，以及是这个编码格式的原因。"
    prompt += str(hex_data)  # 添加实际的16进制数据
    # 构建请求的数据体
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000,
        "temperature": 0.3,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
    # 如果需要，设置代理服务器
    proxies = {
        "http": PROXY,
        "https": PROXY,
    }
    try:
        # 发送POST请求到API
        if PROXY is None or PROXY != "":
            print("用代理的analyze_gpt")
            response = requests.post(url, headers=headers, json=data, proxies=proxies)
        else:
            print("不用代理的analyze_gpt")
            response = requests.post(url, headers=headers, json=data)
        # 检查请求是否成功
        if response.status_code == 200:
            # 从响应中提取生成的文本
            generated_text = response.json()['choices'][0]['message']['content']
            print(generated_text)
            return generated_text  # 返回推测结果
        else:
            # 处理错误
            print(f"Request failed with status code {response.status_code}")
            return f"Request failed with status code {response.status_code}"
    except Exception as e:
        print(f"analyze_gpt抛出错误: {e}")
        return "Error occurred in analyze_gpt"
