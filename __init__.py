import os
import sys
from . import custom_nodes
from . import math_nodes
from . import tool_nodes
from .constants import prefixName

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dependencies"))

import logging
console_handler = logging.StreamHandler()
logging.root.addHandler(console_handler)
console_handler.setFormatter(
    logging.Formatter('%(asctime)s.%(msecs)03d [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s'))


WEB_DIRECTORY = "web"

NODE_CLASS_MAPPINGS = {
    f"{prefixName}LoadImageToBase64": tool_nodes.LoadImageToBase64,
    f"{prefixName}WorkflowMetadataConfig": tool_nodes.WorkflowMetadataConfigNode,
    f"{prefixName}CTool_ImageWorkflowMetadataNode": tool_nodes.ImageWorkflowMetadataNode,
    f"{prefixName}CTool_ImageWorkflowMetadataTestNode": tool_nodes.ImageWorkflowMetadataTestNode,
    f"{prefixName}CTool_ImageMaskNode": tool_nodes.ImageMaskNode,
    f"{prefixName}CTool_ImageMaskTestNode": tool_nodes.ImageMaskTestNode,
    f"{prefixName}CTool_GenerateImageMaskNode": tool_nodes.GenerateImageMaskNode,
    f"{prefixName}CTool_GetImageInfoNode": tool_nodes.ImageInfoNode,
    f"{prefixName}CTool_SleepNode": tool_nodes.SleepNode,
    f"{prefixName}CTool_MakeLoraSelectStackNode": tool_nodes.MakeLoraSelectStackNode,
    f"{prefixName}CTool_LoraSelectNode": tool_nodes.LoraSelectNode,

    f"{prefixName}CTool_MathIntClampNode": math_nodes.MathIntClampNode,
    f"{prefixName}CTool_MathFloatClampNode": math_nodes.MathFloatClampNode,
    f"{prefixName}CTool_MathFloatScaleNode": math_nodes.MathFloatScaleNode,

    f"{prefixName}CMaster_InputImage": custom_nodes.InputImageNode,
    f"{prefixName}CMaster_InputMaskImageNode": custom_nodes.InputMaskImageNode,
    f"{prefixName}CMaster_InputString": custom_nodes.InputStringNode,
    f"{prefixName}CMaster_InputEnumString": custom_nodes.InputEnumStringNode,
    f"{prefixName}CMaster_InputInt": custom_nodes.InputIntNode,
    f"{prefixName}CMaster_InputRangeInt": custom_nodes.InputRangeIntNode,
    f"{prefixName}CMaster_InputEnumInt": custom_nodes.InputEnumIntNode,
    f"{prefixName}CMaster_InputBoolean": custom_nodes.InputBooleanNode,
    f"{prefixName}CMaster_InputFloat": custom_nodes.InputFloatNode,
    f"{prefixName}CMaster_InputRangeFloat": custom_nodes.InputRangeFloatNode,
    f"{prefixName}CMaster_InputEnumFloat": custom_nodes.InputEnumFloatNode,
    f"{prefixName}CMaster_InputCheckpoint": custom_nodes.InputCheckpointNode,
    f"{prefixName}CMaster_InputLoraNode": custom_nodes.InputLoraNode,

    f"{prefixName}CMaster_OutputImage": custom_nodes.OutputImageNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    f"{prefixName}LoadImageToBase64": "加载图片(测试)",
    f"{prefixName}WorkflowMetadataConfig": "工作流配置节点",
    f"{prefixName}CTool_MakeLoraSelectStackNode": "制作Lora选择器",
    f"{prefixName}CTool_LoraSelectNode": "Lora选择器",
    f"{prefixName}CTool_GenerateImageMaskNode": "遮罩生成",
    f"{prefixName}CTool_ImageWorkflowMetadataNode": "图片元数据",
    f"{prefixName}CTool_ImageWorkflowMetadataTestNode": "图片元数据(测试)",
    f"{prefixName}CTool_SleepNode": "延迟图片(测试)",
    f"{prefixName}CTool_ImageMaskNode": "遮罩数据",
    f"{prefixName}CTool_ImageMaskTestNode": "遮罩数据(测试)",
    f"{prefixName}CTool_GetImageInfoNode": "图片信息",

    f"{prefixName}CTool_MathIntClampNode": "整数约束",
    f"{prefixName}CTool_MathFloatClampNode": "浮点数约束",
    f"{prefixName}CTool_MathFloatScaleNode": "浮点数等比缩放",

    f"{prefixName}CMaster_InputCheckpoint": "模型输入",
    f"{prefixName}CMaster_InputLoraNode": "Lora模型输入",
    f"{prefixName}CMaster_InputImage": "图片输入",
    f"{prefixName}CMaster_InputMaskImageNode": "遮罩图片输入",
    f"{prefixName}CMaster_InputString": "文本输入",
    f"{prefixName}CMaster_InputEnumString": "枚举输入",
    f"{prefixName}CMaster_InputInt": "整数输入",
    f"{prefixName}CMaster_InputEnumInt": "整数枚举输入",
    f"{prefixName}CMaster_InputRangeInt": "范围整数输入",
    f"{prefixName}CMaster_InputBoolean": "布尔值输入",
    f"{prefixName}CMaster_InputFloat": "浮点数输入",
    f"{prefixName}CMaster_InputEnumFloat": "浮点数枚举输入",
    f"{prefixName}CMaster_InputRangeFloat": "范围浮点数输入",
    f"{prefixName}CMaster_OutputImage": "图片输出",
}

all = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
