import uuid
from pathlib import Path
from config import GRSAI_API_KEY, API_MARK_KEY
from tos_operations import upload_to_tos
from nano_banana_caller import call_nano_banana, call_nano_banana_apimart
from response_parser import  extract_image_urls_from_response, extract_image_urls_from_response_apimart
from image_downloader import download_image

def get_model_handler(process_type):
    """
    根据处理类型获取对应的模型处理配置
    返回：(调用函数, 成功码, task_id字段名, 提取URL函数, 提取URL参数)
    """
    handlers = {
        "grs": (
            call_nano_banana,          # 模型调用函数
            0,                         # 成功响应码
            "id",                      # task_id字段名
            extract_image_urls_from_response,  # URL提取函数
            [GRSAI_API_KEY]            # URL提取函数的额外参数
        ),
        "paimart": (
            call_nano_banana_apimart,  # 模型调用函数
            200,                       # 成功响应码
            "task_id",                 # task_id字段名
            extract_image_urls_from_response_apimart,  # URL提取函数
            [API_MARK_KEY]             # URL提取函数的额外参数
        )
    }
    return handlers.get(process_type)


def process_single_image(img_file, process_type, output_folder, image_size, aspect_ratio):
    """
    处理单张图片的公共逻辑
    :param img_file: 图片文件Path对象
    :param process_type: 处理类型（grs/paimart）
    :param output_folder: 输出文件夹Path对象
    :param image_size: 图片比例（如 3:4、9:16）
    :param aspect_ratio: 图片分辨率规格（如 1k、2k）
    :return: None
    """
    print(f"--- 处理图片: {img_file.name} ---")
    output_file = None  # 初始化输出文件路径
    
    # 1. 上传图片到TOS
    try:
        remote_file_key = f"temp_product/{uuid.uuid4()}.png"
        image_url = upload_to_tos(img_file, remote_file_key)
    except Exception as e:
        print(f"❌ 上传失败 ({img_file.name}): {e}")
        return
    
    # 2. 获取模型处理配置
    handler = get_model_handler(process_type)
    if not handler:
        print(f"❌ 不支持的处理类型: {process_type}")
        return
    call_func, success_code, task_id_field, extract_func, extract_args = handler
    
    # 3. 调用模型（使用传入的image_size和aspect_ratio）
    print("=============调用 nano banana模型处理图片")
    prompt_template = """请将参考图像调整为 {image_size} 的尺寸（仅改变图像大小，不裁剪、不变形、不修改内容），
               保持原始画面内容、比例和视觉细节不变。最终输出调整后的图像."""
    prompt = prompt_template.format(image_size=image_size)
    #print("image_url:",image_url)
    try:
        response = call_nano_banana(image_url, prompt, image_size, aspect_ratio)
        #print(f"模型响应: {response}")
    except Exception as e:
        print(f"❌ 模型调用失败 ({img_file.name}): {e}")
        return
    
    # 4. 处理模型响应
    try:
        # 检查响应是否成功
        if response.get("code") != success_code:
            print(f"❌ 处理失败({process_type})：{img_file.name} | 原因：{response}")
            return
        
        # 核心修复：兼容data是列表/字典两种格式
        data = response.get("data", {})
        if isinstance(data, list):
            # 如果data是列表，取第一个元素（适配你的实际响应格式）
            if len(data) == 0:
                print(f"❌ 响应data为空列表 ({img_file.name})")
                return
            data = data[0]  # 转为字典
        
        # 检查是否包含task_id字段
        if task_id_field not in data:
            print(f"❌ 响应 data 中缺少字段「{task_id_field}」（{img_file.name}）｜当前 data: {data}")
            return
        
        # 获取task_id
        task_id = data[task_id_field]
        print(f"=============调用 nano banana模型({process_type})处理成功, {task_id}")
        
        # 提取图片URL
        image_response_url = extract_func(task_id)
        if process_type == "paimart":
            print(f"提取到的URL: {image_response_url}")
        
        if not image_response_url:
            print(f"❌ 提取图片URL失败 ({process_type}): {img_file.name}")
            return
        
        # 下载并保存图片
        output_folder.mkdir(parents=True, exist_ok=True)

        # 文件名添加比例信息，便于区分
        output_file = output_folder / f"{img_file.stem}_{image_size.replace(':', '_')}_edited.png"
        download_image(image_response_url, str(output_file))
        print(f"✅ 任务完成！图片{img_file.name} URL: {image_response_url}")
        print(f"✅ 已保存: {output_file}")
    
    except KeyError as e:
        print(f"❌ 响应数据格式错误 ({img_file.name}): 缺少字段 {e}")
        print(f"   完整响应: {response}")  # 新增：打印完整响应便于排查
    except IndexError as e:  # 新增：捕获列表索引错误
        print(f"❌ 列表索引错误 ({img_file.name}): {e}")
        print(f"   完整响应: {response}")
    except Exception as e:
        print(f"❌ 处理图片时发生未知错误 ({img_file.name}): {e}")
        print(f"   异常类型: {type(e).__name__}")  # 新增：打印异常类型
        print(f"   完整响应: {response}")  # 新增：打印完整响应便于排查