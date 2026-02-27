from config import GRSAI_API_KEY, GRSAI_URL, API_MARK_KEY
import requests

def call_nano_banana(
    image_url: str,
    prompt: str,
    imageSize: str,
    aspectRatio: str,
):
    """
    调用 Nano Banana pro 模型进行图像编辑。

    参数:
        image_url (str): 图像的url
        prompt (str): 提示词
        imageSize(str): 图像尺寸
        aspectRatio(str): 输出图像比例

    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer " + GRSAI_API_KEY,
    }

    payload = {
                "model": "nano-banana",
                "prompt": prompt,
                "aspectRatio": imageSize, #图片尺寸比例
                "imageSize": aspectRatio,#图片分辨率
                "urls": [image_url],
                "webHook": "-1",
                "shutProgress": False
                }
    print("payload:", payload)
    try:
        # 发送POST请求
        response = requests.post(
            url=GRSAI_URL,
            json=payload,
            headers=headers,
        )
        # 检查HTTP响应状态码
        response.raise_for_status()
        print(f"响应状态码: {response.status_code}")
        return response.json()
    except requests.exceptions.RequestException as e:
        # 捕获请求相关的所有异常（网络错误、状态码错误等）
        print(f"请求AI接口失败: {e}")
        return None
    
    except ValueError as e:
        # 捕获JSON解析失败的异常
        print(f"解析接口返回数据失败: {e}")
        return None
        
def call_nano_banana_apimart(
    image_url: str,
    prompt: str,
    imageSize: str,
    aspectRatio: str,
    token=API_MARK_KEY
):
    """
    调用 Nano Banana pro 模型进行图像编辑。

    参数:
        image_url (str): 图像的url
        prompt (str): 提示词
        imageSize(str): 图像长宽比
        aspectRatio(str): 图像分辨率

    """

    url = "https://api.apimart.ai/v1/images/generations"

    payload = {
        "model": "gemini-2.5-flash-image-preview",
        "prompt": prompt,
        "size": imageSize,
        "n": 1,
        "urls": image_url,
        "resolution": aspectRatio
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    #print(payload)
    #print(f"\n【{image_url}】：{prompt}")
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
