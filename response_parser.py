from config import GRSAI_API_KEY, GRSAI_URL_RESULT
import requests
import time

def extract_image_urls_from_response(task_id):
    while True:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer " + GRSAI_API_KEY,
        }
        print(task_id)
        data = requests.post(
                GRSAI_URL_RESULT,
                headers=headers,
                json={"id": task_id},
                ).json()["data"]
        #  3. 提取 URL
        #print(data)
        if data is not None:
            if data["status"] == "succeeded":
                return data["results"][0]["url"]
            if data["status"] == "failed":
                print("❌ 任务失败:", data)
                return None
        time.sleep(2)

def extract_image_urls_from_response_apimart(task_id):
    """
    轮询 Apimart AI 任务状态，并在完成后提取图片 URL。
    
    Args:
        task_id (str): 任务 ID
        token (str): Bearer Token
    
    Returns:
        str or None: 成功时返回图片 URL，失败或取消时返回 None
    """
    while True:
        url = f"https://api.apimart.ai/v1/tasks/{task_id}"
        #print(url)
        headers = {
            "Authorization": f"Bearer "+ API_MARK_KEY,
        }
        params = {
            "language": "zh"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json().get("data")
            
            if data is None:
                print("⚠️ 响应中无 data 字段")
                time.sleep(2)
                continue
            #print("data:", data)
            status = data.get("status")
            if status == "completed":
                # 正确路径: data -> result -> images[0] -> url[0]
                try:
                    image_url = data["result"]["images"][0]["url"][0]
                    return image_url
                except (KeyError, IndexError) as e:
                    print(f"❌ 解析 URL 失败: {e}, 原始数据: {data}")
                    return None
                    
            elif status == "failed":
                print(f"❌ 任务失败: {data}")
                return None
                
            elif status in ["pending", "processing"]:
                print(f"⏳ 任务进行中 ({status})，等待 2 秒...")
                time.sleep(2)
                continue
                
            else:
                print(f"❓ 未知状态: {status}")
                time.sleep(2)
                
        except requests.RequestException as e:
            print(f"🌐 网络请求错误: {e}")
            time.sleep(5)
        except Exception as e:
            print(f"💥 意外错误: {e}")
            time.sleep(2)

