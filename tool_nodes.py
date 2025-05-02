import folder_paths
from PIL.ImageFile import ImageFile
import base64
import node_helpers
from PIL import Image
from io import BytesIO
import os
import torch
import numpy as np
from torch import Tensor
from .constants import categoryName


class WorkflowMetadataConfigNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "code": ("STRING", {"multiline": False, "default": "服务代号"}),
                "name": ("STRING", {"multiline": False, "default": "服务名称"}),
                "type": (["默认", "局部重绘", "放大", "局部修复"], {"default": "默认"}),
                "modelType": (["SD1.5", "SDXL", "FLUX", "其他"], {"default": "其他"}),
                "description": ("STRING", {"multiline": True, "default": ""}),
                "maxWidth": ("INT", {"default": 2048, "min": 1, "max": 0xffffff, "tooltip": "最大宽度"}),
                "maxHeight": ("INT", {"default": 2048, "min": 1, "max": 0xffffff, "tooltip": "最大高度"}),
                "groupInfo": ("STRING", {"multiline": True, "default": "", "tooltip": "分组配置"}),
            },
        }

    RETURN_TYPES = ()
    CATEGORY = f"{categoryName}/配置"
    FUNCTION = "output_func"

    def output_func(self):
        return ()


class LoadImageToBase64:
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        return {"required":
                    {"image": (sorted(files), {"image_upload": True})},
                }

    CATEGORY = f"{categoryName}/调试"

    RETURN_TYPES = ("STRING",)
    FUNCTION = "load_image"

    def load_image(self, image):
        try:
            image_path = folder_paths.get_annotated_filepath(image)

            img: ImageFile = node_helpers.pillow(Image.open, image_path)
            image_data = BytesIO()
            img.save(image_data, format="PNG")
            image_data_bytes = image_data.getvalue()

            return (base64.b64encode(image_data_bytes).decode('utf-8'),)
        except Exception as e:
            print(f"raised exception: LoadImageToBase64")
            raise e


class MakeLoraSelectStackNode:
    @classmethod
    def INPUT_TYPES(s):
        max_lora_num = 10
        inputs = {
            "required": {

            },
            "optional": {
                "optional_lora_stack": ("LORA_SELECT_STACK",)
            },
        }

        for i in range(1, max_lora_num + 1):
            inputs["optional"][f"lora_{i}_match_text"] = (
                "STRING", {"multiline": False, "default": ""})
            inputs["optional"][f"lora_{i}_name"] = (
                ["None"] + folder_paths.get_filename_list("loras"), {"default": "None"})
            inputs["optional"][f"lora_{i}_strength"] = (
                "FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01})

        return inputs

    max_lora_num = 10
    RETURN_TYPES = ("LORA_SELECT_STACK",)
    RETURN_NAMES = ("lora_select",)
    CATEGORY = f"{categoryName}/工具"
    FUNCTION = "make_lora_select"

    def make_lora_select(self, optional_lora_stack=None, **kwargs):
        if not kwargs:
            return ([],)
        loras = []
        if optional_lora_stack is not None:
            loras.extend([l for l in optional_lora_stack if l[0] != "None"])

        for i in range(1, self.max_lora_num):
            lora_name = kwargs.get(f"lora_{i}_name")
            lora_match_text = kwargs.get(f"lora_{i}_match_text")

            if not lora_name or lora_name == "None" or lora_match_text == "None" or not lora_match_text:
                continue

            strength = float(kwargs.get(f"lora_{i}_strength"))

            loras.append((lora_match_text, lora_name, strength))

        return (loras,)


class LoraSelectNode:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "OutputAudio"}),
                "loras": ("LORA_SELECT_STACK",)
            },

        }

    RETURN_TYPES = ("LORA_STACK",)
    RETURN_NAMES = ("lora_stack",)
    CATEGORY = f"{categoryName}/工具"
    FUNCTION = "lora_select"

    def lora_select(self, prompt: str, loras):
        if not loras:
            return ([],)
        lora_stack = []
        stacks = []
        for lora in loras:
            lora_match_text, lora_name, strength = lora
            if not lora_name or lora_name == "None" or lora_match_text == "None" or not lora_match_text:
                continue
            if lora_name in stacks:
                continue
            text: str = lora_match_text
            arr = text.split(",")
            for e in arr:
                if e.strip() == "":
                    continue
                if e.strip() in prompt:
                    lora_stack.append((lora_name, strength, strength))
                    stacks.append(lora_name)
                    break

        if len(lora_stack) > 0:
            return (lora_stack,)
        else:
            return (None,)


class ImageWorkflowMetadataNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "hidden": {
                "document_width": ("INT", {"default": 0}),
                "document_height": ("INT", {"default": 0}),
                "has_selection": ("BOOLEAN", {"default": False}),
                "selection_x": ("INT", {"default": 0}),
                "selection_y": ("INT", {"default": 0}),
                "selection_width": ("INT", {"default": 0}),
                "selection_height": ("INT", {"default": 0}),
            },
        }

    RETURN_TYPES = ("INT", "INT", "BOOLEAN", "INT", "INT", "INT", "INT")
    RETURN_NAMES = ("文档宽度", "文档高度", "是否存在选区", "选区位置X", "选区位置Y", "选区宽度", "选区高度")
    CATEGORY = f"{categoryName}/工具"
    FUNCTION = "output_func"

    def output_func(self, document_width=0, document_height=0, has_selection=False,
                    selection_x=0, selection_y=0,
                    selection_width=0, selection_height=0):
        return (
        document_width, document_height, has_selection, selection_x, selection_y, selection_width, selection_height)


class ImageWorkflowMetadataTestNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "document_width": ("INT", {"default": 0}),
                "document_height": ("INT", {"default": 0}),
                "has_selection": ("BOOLEAN", {"default": False}),
                "selection_x": ("INT", {"default": 0}),
                "selection_y": ("INT", {"default": 0}),
                "selection_width": ("INT", {"default": 0}),
                "selection_height": ("INT", {"default": 0}),
            },
        }

    RETURN_TYPES = ("INT", "INT", "BOOLEAN", "INT", "INT", "INT", "INT")
    RETURN_NAMES = ("文档宽度", "文档高度", "是否存在选区", "选区位置X", "选区位置Y", "选区宽度", "选区高度")
    CATEGORY = f"{categoryName}/调试"
    FUNCTION = "output_func"

    def output_func(self, document_width=0, document_height=0, has_selection=False,
                    selection_x=0, selection_y=0,
                    selection_width=0, selection_height=0):
        return (
        document_width, document_height, has_selection, selection_x, selection_y, selection_width, selection_height)


class ImageMaskNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "hidden": {
                "has_mask": ("BOOLEAN", {"default": False}),
                "mask_image": ("STRING", {"multiline": False}),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "BOOLEAN")
    RETURN_NAMES = ("image", "mask", "是否存在遮罩")
    CATEGORY = f"{categoryName}/工具"
    FUNCTION = "input_image"

    def input_image(self, has_mask, mask_image):
        if not has_mask:
            return None, None, False
        try:
            imgdata = base64.b64decode(mask_image)
            img = Image.open(BytesIO(imgdata))
            img = np.array(img).astype(np.float32) / 255.0
            img = torch.from_numpy(img)
            if img.dim() == 3:  # RGB(A) input, use red channel
                img = img[:, :, 0]
            return self.read_image(mask_image), img.unsqueeze(0), has_mask
        except Exception as e:
            print(f"Exception raised: ImageMaskNode")
            raise e

    def read_image(self, image: str):
        imgdata = base64.b64decode(image)
        img = Image.open(BytesIO(imgdata))

        img = img.convert("RGB")
        img = np.array(img).astype(np.float32) / 255.0
        img = torch.from_numpy(img)[None,]

        return img


class ImageMaskTestNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "has_mask": ("BOOLEAN", {"default": False}),
                "mask_image": ("STRING", {"multiline": False}),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "BOOLEAN")
    RETURN_NAMES = ("image", "mask", "是否存在遮罩")
    CATEGORY = f"{categoryName}/调试"
    FUNCTION = "input_image"

    def input_image(self, has_mask, mask_image):
        if not has_mask:
            return None, None, False
        try:
            imgdata = base64.b64decode(mask_image)
            img = Image.open(BytesIO(imgdata))
            img = np.array(img).astype(np.float32) / 255.0
            img = torch.from_numpy(img)
            if img.dim() == 3:  # RGB(A) input, use red channel
                img = img[:, :, 0]
            return self.read_image(mask_image), img.unsqueeze(0), has_mask
        except Exception as e:
            print(f"Exception raised: ImageMaskTestNode")
            raise e

    def read_image(self, image: str):
        imgdata = base64.b64decode(image)
        img = Image.open(BytesIO(imgdata))

        img = img.convert("RGB")
        img = np.array(img).astype(np.float32) / 255.0
        img = torch.from_numpy(img)[None,]

        return img


class GenerateImageMaskNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "options": (["固定值", "百分比"], {"default": "固定值"}),
                "inner_edge_width": ("INT", {"default": 5, "tooltip": "固定边缘宽度"}),
                "inner_edge_height": ("INT", {"default": 5, "tooltip": "固定边缘高度"}),
                "inner_edge_width_percent": (
                "FLOAT", {"default": 0.18, "min": 0, "max": 0.5, "step": 0.01, "tooltip": "固定边缘宽度百分比"}),
                "inner_edge_height_percent": (
                "FLOAT", {"default": 0.18, "min": 0, "max": 0.5, "step": 0.01, "tooltip": "固定边缘高度百分比"}),
            }
        }

    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)
    CATEGORY = f"{categoryName}/工具"
    FUNCTION = "input_image"

    def input_image(self, image: Tensor, options: str, inner_edge_width: int, inner_edge_height: int,
                    inner_edge_width_percent: float,
                    inner_edge_height_percent: float):
        if options == "百分比":
            inner_edge_width = int(inner_edge_width_percent * image.shape[2])
            inner_edge_height = int(inner_edge_height_percent * image.shape[1])
        inner_width = image.shape[2] - inner_edge_width * 2
        inner_height = image.shape[1] - inner_edge_height * 2
        inner_width = max(0, min(image.shape[2], inner_width))
        inner_height = max(0, min(image.shape[1], inner_height))
        if inner_width > 0 and inner_height > 0:
            img = np.zeros((image.shape[1], image.shape[2],), dtype=np.float32)
            img[inner_edge_height:inner_edge_height + inner_height + 1,
            inner_edge_width:inner_edge_width + inner_width + 1, ] = 1.0
            img = torch.from_numpy(img)
            return (img.unsqueeze(0),)

        else:
            img = np.ones((image.shape[1], image.shape[2],), dtype=np.float32)
            img = torch.from_numpy(img)
            return (img.unsqueeze(0),)


class ImageInfoNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("INT", "INT", "INT")
    RETURN_NAMES = ("宽度", "高度", "通道")
    CATEGORY = f"{categoryName}/工具"
    FUNCTION = "input_image"

    def input_image(self, image: Tensor):
        return image.shape[1:]


class SleepNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "seconds": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 100.0, "step": 0.01}),
                "image": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE",)

    CATEGORY = f"{categoryName}/调试"
    FUNCTION = "sleep"

    def sleep(self, seconds, image):
        import time
        time.sleep(seconds)
        return (image,)
