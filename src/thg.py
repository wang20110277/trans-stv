from abc import ABC, ABCMeta, abstractmethod
import logging
import os

logger = logging.getLogger(__name__)

class AbstractTHG(ABC):
    __metaclass__ = ABCMeta

    @abstractmethod
    def to_thg(self, driven_audio):
        pass

class SadTalker(AbstractTHG):
    def __init__(self, config):
        """
        初始化 THG（Talking Head Generation）模块。

        :param config: 配置字典，包含以下键：
            - model_name: 模型名称（默认 'wwd123/sadtalker'）
            - model_revision: 模型版本（默认 'v1.0.0'）
            - source_image: 源图像路径
            - out_dir: 输出目录（默认 './results/'）
            - preprocess: 预处理方式（默认 'full'）
            - still_mode: 是否保持静态（默认 True）
            - use_enhancer: 是否使用增强器（默认 False）
            - batch_size: 批量大小（默认 1）
            - size: 图像大小（默认 256）
            - pose_style: 姿势风格（默认 0）
            - exp_scale: 表情缩放（默认 1）
        """
        self.model_name = config.get("model_name")
        self.model_revision = config.get("model_revision")
        self.source_image = config.get("source_image")
        self.out_dir = config.get("out_dir")
        self.preprocess = config.get("preprocess")
        self.still_mode = config.get("still_mode")
        self.use_enhancer = config.get("use_enhancer")
        self.batch_size = config.get("batch_size")
        self.size = config.get("size")
        self.pose_style = config.get("pose_style")
        self.exp_scale = config.get("exp_scale")

        # 检查依赖库是否可用
        self.model_available = self._check_model_availability()

    def _check_model_availability(self):
        """
        检查模型依赖是否可用
        """
        try:
            from modelscope.pipelines import pipeline
            return True
        except ImportError:
            logger.warning("Modelscope not available, THG功能将无法使用")
            return False

    def to_thg(self, driven_audio):
        """
        生成 Talking Head 视频。

        :param driven_audio: 驱动音频文件路径
        :return: 生成的视频文件路径
        """
        # 如果模型不可用，直接返回None
        if not self.model_available:
            logger.warning("THG模型不可用，跳过数字人视频生成")
            return None
            
        try:
            from modelscope.pipelines import pipeline
        except ImportError:
            logger.error("无法导入modelscope.pipeline")
            return None

        if not os.path.exists(self.source_image):
            logger.error(f"源图像文件不存在: {self.source_image}")
            return None
        if not os.path.exists(driven_audio):
            logger.error(f"驱动音频文件不存在: {driven_audio}")
            return None

        # 创建输出目录
        os.makedirs(self.out_dir, exist_ok=True)

        # 初始化 pipeline
        try:
            inference = pipeline('talking-head', model=self.model_name, model_revision=self.model_revision)
        except Exception as e:
            logger.error(f"模型初始化失败: {e}")
            return None

        # 调用模型生成视频
        kwargs = {
            'preprocess': self.preprocess,
            'still_mode': self.still_mode,
            'use_enhancer': self.use_enhancer,
            'batch_size': self.batch_size,
            'size': self.size,
            'pose_style': self.pose_style,
            'exp_scale': self.exp_scale,
            'result_dir': self.out_dir
        }

        try:
            video_path = inference(self.source_image, driven_audio=driven_audio, **kwargs)
            logger.info(f"视频生成成功: {video_path}")
            return video_path
        except Exception as e:
            logger.error(f"视频生成失败: {e}")
            return None

def create_instance(class_name, *args, **kwargs):
    # 获取类对象
    cls = globals().get(class_name)
    if cls:
        # 创建并返回实例
        return cls(*args, **kwargs)
    else:
        raise ValueError(f"Class {class_name} not found")