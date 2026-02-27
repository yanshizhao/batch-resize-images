from config import  LOCAL_IMAGE_PATH, OUTPUT_PATH, AK, SK, REGION, BUCKET_NAME, GRSAI_URL, API_MARK_KEY
from pathlib import Path
import sys
from tos_operations import upload_to_tos, batch_delete_tos_images
from image_downloader import download_image
from model_image_processor import get_model_handler, process_single_image


def main():
    #  命令行参数解析与校验（支持可选参数）
    usage_text = """
❌ 参数错误！正确用法:
  基础用法（使用默认比例9:16、分辨率1k）:
    python main.py <图片文件夹绝对路径> <处理类型>
    示例: python main.py /Users/xxx/A grs

  完整用法（自定义比例和分辨率）:
    python main.py <图片文件夹绝对路径> <处理类型> <图片比例> <分辨率>
    示例: python main.py /Users/xxx/A grs 3:4 2k
  支持的参数说明:
    - 模型接口平台: grs / paimart
    - 图片比例: 如 3:4、9:16、1:1 等
    - 分辨率: 如 1k、2k、4k 等（默认1k）
    """
    
    # 设置默认值
    DEFAULT_IMAGE_SIZE = "9:16"
    DEFAULT_ASPECT_RATIO = "1k"
    
    # 解析参数
    if len(sys.argv) < 3 or len(sys.argv) > 5:
        print(usage_text)
        sys.exit(1)
    
    input_folder = sys.argv[1]
    process_type = sys.argv[2].lower()

    # 可选参数：image_size和aspect_ratio
    image_size = sys.argv[3] if len(sys.argv) >=4 else DEFAULT_IMAGE_SIZE
    aspect_ratio = sys.argv[4] if len(sys.argv) >=5 else DEFAULT_ASPECT_RATIO
    
    # 校验处理类型
    if process_type not in ["grs", "paimart"]:
        print(f"❌ 不支持的处理类型: {process_type}，仅支持 grs / paimart")
        sys.exit(1)
    
    batch_delete_tos_images("temp_product/")

    # 初始化路径（自动生成输出路径：输入文件夹同级的 原文件夹名_edited）
    input_path = Path(input_folder).absolute()
    
    # 校验输入文件夹
    if not input_path.exists():
        print(f"❌ 输入文件夹不存在: {input_folder}")
        return
    if not input_path.is_dir():
        print(f"❌ 输入路径不是文件夹: {input_folder}")
        return
    
    # 自动生成输出路径
    output_folder = input_path.parent / f"{input_path.name}_{image_size.replace(':', '_')}_edited"
    print(f"📁 输出文件夹将自动创建为: {output_folder}")
    print(f"⚙️  当前配置 - 图片比例: {image_size} | 分辨率: {aspect_ratio} | 处理类型: {process_type}")
    
    # 初始化变量
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}

    # 筛选图片文件（仅文件，排除子文件夹）
    image_files = [f for f in input_path.iterdir() if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS]
    
    if not image_files:
        print("⚠️ 输入文件夹中没有找到支持的图片文件")
        return
    print(f"✅ 找到 {len(image_files)} 张图片，开始批量处理...")
    
    
    for idx, img_file in enumerate(image_files, start=1):
        print(f"\n[{idx}/{len(image_files)}]")
        process_single_image(img_file, process_type, output_folder, image_size, aspect_ratio)
    
    print(f"\n🎉 批量处理完成！所有处理后的图片已保存至: {output_folder}")

if __name__ == "__main__":
    main()