import folder_paths
from PIL import Image
import base64
from io import BytesIO
import torch
import numpy as np

import os

import comfy.sd
import comfy.utils
from .constants import categoryName, varPrefixName

var_prefix_name = varPrefixName

class AnyType(str):
    """A special class that is always equal in not equal comparisons. Credit to pythongosssss"""

    def __eq__(self, _) -> bool:
        return True

    def __ne__(self, __value: object) -> bool:
        return False

any = AnyType("*")

class InputCheckpointNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "var_name": ("STRING", {"multiline": False, "default": "InputCheckpoint"}),
                "ckpt_name": (
                folder_paths.get_filename_list("checkpoints"), {"tooltip": "要加载的检查点（模型）的名称。"}),
                "export": ("BOOLEAN", {"default": True}),
                "checkpoints": (
                "STRING", {"multiline": True, "default": '\n'.join(folder_paths.get_filename_list("checkpoints"))}),
            },
            "optional": {
                "description": ("STRING", {"multiline": True, "default": ""}),
                "order": ("INT", {"default": 0, "min": 0, "max": 0xffffff, "step": 1}),
                "placeholder": ("STRING", {"multiline": True, "default": ""})
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP", "VAE")

    CATEGORY = f"{categoryName}/输入"
    FUNCTION = "input_checkpoint"

    def input_checkpoint(self, var_name, ckpt_name, checkpoints, export, description="", order=0, ):
        try:
            # Split enums by comma or newline, and strip whitespace
            checkpoints = [enum.strip() for enum in checkpoints.replace('\n', ',').split(',') if enum.strip()]
            if ckpt_name not in checkpoints:
                checkpoints.append(ckpt_name)

            ckpt_path = folder_paths.get_full_path_or_raise("checkpoints", ckpt_name)
            out = comfy.sd.load_checkpoint_guess_config(ckpt_path, output_vae=True, output_clip=True,
                                                        embedding_directory=folder_paths.get_folder_paths("embeddings"))
            return out[:3]
        except Exception as e:
            print(f"raised exception: {var_name}")
            raise e


class InputLoraNode:
    def __init__(self):
        self.loaded_lora = None

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "var_name": ("STRING", {"multiline": False, "default": "InputLora"}),
                "model": ("MODEL", {"tooltip": "The diffusion model the LoRA will be applied to."}),
                "clip": ("CLIP", {"tooltip": "The CLIP model the LoRA will be applied to."}),
                "lora_name": (folder_paths.get_filename_list("loras"), {"tooltip": "加载LoRA."}),
                "strength_model": ("FLOAT", {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01,
                                             "tooltip": "如何强烈地修改扩散模型。该值可以是负的。"}),
                "strength_clip": ("FLOAT", {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01,
                                            "tooltip": "CLIP模型修改力度有多大。该值可以是负的。"}),
                "export": ("BOOLEAN", {"default": True}),
                "loras": ("STRING", {"multiline": True, "default": '\n'.join(folder_paths.get_filename_list("loras"))}),
            },
            "optional": {
                "description": ("STRING", {"multiline": True, "default": ""}),
                "order": ("INT", {"default": 0, "min": 0, "max": 0xffffff, "step": 1}),
                "placeholder": ("STRING", {"multiline": True, "default": ""})
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP")
    OUTPUT_TOOLTIPS = ("The modified diffusion model.", "The modified CLIP model.")
    FUNCTION = "load_lora"

    CATEGORY = f"{categoryName}/输入"
    DESCRIPTION = "LoRAs are used to modify diffusion and CLIP models, altering the way in which latents are denoised such as applying styles. Multiple LoRA nodes can be linked together."

    def load_lora(self, var_name, model, clip, lora_name, strength_model, strength_clip, export, loras, description="",
                  order=0):
        try:
            if strength_model == 0 and strength_clip == 0:
                return model, clip

            lora_path = folder_paths.get_full_path_or_raise("loras", lora_name)
            lora = None
            if self.loaded_lora is not None:
                if self.loaded_lora[0] == lora_path:
                    lora = self.loaded_lora[1]
                else:
                    self.loaded_lora = None

            if lora is None:
                lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
                self.loaded_lora = (lora_path, lora)

            model_lora, clip_lora = comfy.sd.load_lora_for_models(model, clip, lora, strength_model, strength_clip)
            return model_lora, clip_lora
        except Exception as e:
            print(f"raised exception: {var_name}")
            raise e

class InputImageNode:
    def __init__(self):
        self.image = None
        self.image_mask = None
        self.image_base64 = None

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "var_name": ("STRING", {"multiline": False, "default": "InputImage"}),
                "image": ("STRING", {"multiline": False}),
                "export": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "description": ("STRING", {"multiline": True, "default": ""}),
                "order": ("INT", {"default": 0, "min": 0, "max": 0xffffff, "step": 1}),
                "placeholder": ("STRING", {"multiline": True, "default": ""})
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    CATEGORY = f"{categoryName}/输入"
    FUNCTION = "input_image"

    def input_image(self, var_name, image, export, description="", order=0):
        if image is None:
            return None, None
        if image == self.image_base64:
            return self.image, self.image_mask
        try:
            imgdata = base64.b64decode(image)
            img = Image.open(BytesIO(imgdata))

            if "A" in img.getbands():
                mask = np.array(img.getchannel("A")).astype(np.float32) / 255.0
                mask = 1.0 - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")

            img = img.convert("RGB")
            img = np.array(img).astype(np.float32) / 255.0
            img = torch.from_numpy(img)[None,]

            self.image = img
            self.image_mask = mask
            self.image_base64 = image
            return self.image, self.image_mask
        except Exception as e:
            print(f"Exception raised: {var_name}")
            raise e


## 生成遮罩图层



class InputMaskImageNode:

    def __init__(self):
        self.mask_image = None
        self.mask_image_mask = None
        self.mask_image_base64 = None

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "var_name": ("STRING", {"multiline": False, "default": "InputImageMask"}),
                "image": ("STRING", {"multiline": False}),
                "export": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "description": ("STRING", {"multiline": True, "default": ""}),
                "order": ("INT", {"default": 0, "min": 0, "max": 0xffffff, "step": 1}),
                "placeholder": ("STRING", {"multiline": True, "default": ""})
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    CATEGORY = f"{categoryName}/输入"
    FUNCTION = "input_image"

    def input_image(self, var_name, image, export, description="", order=0):
        if image is None:
            return None, None
        if image == self.mask_image_base64:
            return self.mask_image, self.mask_image_mask
        try:
            imgdata = base64.b64decode(image)
            img = Image.open(BytesIO(imgdata))
            img = np.array(img).astype(np.float32) / 255.0
            img = torch.from_numpy(img)
            if img.dim() == 3:  # RGB(A) input, use red channel
                img = img[:, :, 0]
            self.mask_image = self.read_image(image)
            self.mask_image_mask = img.unsqueeze(0)
            self.mask_image_base64 = image
            return self.mask_image, self.mask_image_mask
        except Exception as e:
            print(f"Exception raised: {var_name}")
            raise e

    def read_image(self, image: str):
        imgdata = base64.b64decode(image)
        img = Image.open(BytesIO(imgdata))

        img = img.convert("RGB")
        img = np.array(img).astype(np.float32) / 255.0
        img = torch.from_numpy(img)[None,]

        return img


class InputStringNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "var_name": ("STRING", {"multiline": False, "default": "InputString"}),
                "text": ("STRING", {"multiline": True, "default": ""}),
                "export": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "description": ("STRING", {"multiline": True, "default": ""}),
                "order": ("INT", {"default": 0, "min": 0, "max": 0xffffff, "step": 1}),
                "placeholder": ("STRING", {"multiline": True, "default": ""})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    CATEGORY = f"{categoryName}/输入"
    FUNCTION = "input_string"

    def input_string(self, var_name, text, export, description="", order=0):
        return (text,)

class InputEnumStringNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "var_name": ("STRING", {"multiline": False, "default": "InputEnum"}),
                "text": ("STRING", {"multiline": False, "default": ""}),
                "export": ("BOOLEAN", {"default": True}),
                "enums": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {
                "description": ("STRING", {"multiline": True, "default": ""}),
                "order": ("INT", {"default": 0, "min": 0, "max": 0xffffff, "step": 1}),
                "placeholder": ("STRING", {"multiline": True, "default": ""})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    CATEGORY = f"{categoryName}/输入"
    FUNCTION = "input_enum_string"

    def input_enum_string(self, var_name, text, export, enums):
        # Split enums by comma or newline, and strip whitespace
        enums = [enum.strip() for enum in enums.replace('\n', ',').split(',') if enum.strip()]
        if text not in enums:
            enums.append(text)
        return (text,)


class InputBooleanNode:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "var_name": ("STRING", {"multiline": False, "default": "InputBoolean"}),
                "value": ("BOOLEAN", {"default": False}),
                "export": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "description": ("STRING", {"multiline": True, "default": ""}),
                "order": ("INT", {"default": 0, "min": 0, "max": 0xffffff, "step": 1}),
                "placeholder": ("STRING", {"multiline": True, "default": ""})
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("value",)
    CATEGORY = f"{categoryName}/输入"
    FUNCTION = "input_boolean"

    def input_boolean(self, var_name, value, export, description="", order=0):
        return (value,)


class InputIntNode:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "var_name": ("STRING", {"multiline": False, "default": "InputInt"}),
                "number": ("INT", {"default": 0, "min": 0, "max": 0xffffff, "step": 1}),
                "export": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "description": ("STRING", {"multiline": True, "default": ""}),
                "order": ("INT", {"default": 0, "min": 0, "max": 0xffffff, "step": 1}),
                "placeholder": ("STRING", {"multiline": True, "default": ""})
            }
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("number",)
    CATEGORY = f"{categoryName}/输入"
    FUNCTION = "input_int"

    def input_int(self, var_name, number, export):
        return (number,)


class InputRangeIntNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "var_name": ("STRING", {"multiline": False, "default": "InputRangeInt"}),
                "number": ("INT", {"default": 0, "min": 0, "max": 0xffffff, "step": 1}),
                "export": ("BOOLEAN", {"default": True}),
                "min": ("INT", {"default": 0, "min": 0, "max": 0xffffff, "step": 1}),
                "max": ("INT", {"default": 0, "min": 0, "max": 0xffffff, "step": 1}),
            },
            "optional": {
                "description": ("STRING", {"multiline": True, "default": ""}),
                "order": ("INT", {"default": 0, "min": 0, "max": 0xffffff, "step": 1}),
                "placeholder": ("STRING", {"multiline": True, "default": ""})
            }
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("number",)
    CATEGORY = f"{categoryName}/输入"
    FUNCTION = "input_range_int"

    def input_range_int(self, var_name, number, min, max, export, description="", order=0):
        if min > max:
            min, max = max, min
        if number < min:
            number = min
        if number > max:
            number = max
        return (number,)

class InputEnumIntNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "var_name": ("STRING", {"multiline": False, "default": "InputEnumInt"}),
                "number": ("INT", {"default": 0, "min": 0, "max": 0xffffff, "step": 1}),
                "export": ("BOOLEAN", {"default": True}),
                "enums": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {
                "description": ("STRING", {"multiline": True, "default": ""}),
                "order": ("INT", {"default": 0, "min": 0, "max": 0xffffff, "step": 1}),
                "placeholder": ("STRING", {"multiline": True, "default": ""})
            }
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("number",)
    CATEGORY = f"{categoryName}/输入"
    FUNCTION = "input_enum_int"

    def input_enum_int(self, var_name, number: int, export, enums):
        return (number,)


class InputFloatNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "var_name": ("STRING", {"multiline": False, "default": "InputFloat"}),
                "number": ("FLOAT", {"default": 0, "min": 0, "max": 0xffffff, "step": 0.01}),
                "export": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "description": ("STRING", {"multiline": True, "default": ""}),
                "order": ("INT", {"default": 0, "min": 0, "max": 0xffffff, "step": 1}),
                "placeholder": ("STRING", {"multiline": True, "default": ""})
            }
        }

    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("number",)
    CATEGORY = f"{categoryName}/输入"
    FUNCTION = "input_float"

    def input_float(self, var_name, number, export):
        return (number,)


class InputRangeFloatNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "var_name": ("STRING", {"multiline": False, "default": "InputRangeFloat"}),
                "number": ("FLOAT", {"default": 0, "min": 0, "max": 0xffffff, "step": 0.01}),
                "export": ("BOOLEAN", {"default": True}),
                "min": ("FLOAT", {"default": 0, "min": 0, "max": 0xffffff, "step": 0.01}),
                "max": ("FLOAT", {"default": 0, "min": 0, "max": 0xffffff, "step": 0.01}),
            },
            "optional": {
                "description": ("STRING", {"multiline": True, "default": ""}),
                "order": ("INT", {"default": 0, "min": 0, "max": 0xffffff, "step": 1}),
                "placeholder": ("STRING", {"multiline": True, "default": ""})
            }
        }

    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("number",)
    CATEGORY = f"{categoryName}/输入"
    FUNCTION = "input_range_float"

    def input_range_float(self, var_name, number, min, max, export):
        if min > max:
            min, max = max, min
        if number < min:
            number = min
        if number > max:
            number = max
        return (number,)


class InputEnumFloatNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "var_name": ("STRING", {"multiline": False, "default": "InputEnumFloat"}),
                "number": ("FLOAT", {"default": 0, "min": 0, "max": 0xffffff, "step": 0.01}),
                "export": ("BOOLEAN", {"default": True}),
                "enums": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {
                "description": ("STRING", {"multiline": True, "default": ""}),
                "order": ("INT", {"default": 0, "min": 0, "max": 0xffffff, "step": 1}),
                "placeholder": ("STRING", {"multiline": True, "default": ""})
            }
        }

    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("number",)
    CATEGORY = f"{categoryName}/输入"
    FUNCTION = "input_enum_float"

    def input_enum_float(self, var_name, number: int, export, enums):
        return (number,)

class OutputImageNode:

    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.filename_prefix = "ComfyMasterOutput_"
        self.type = "temp"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "var_name": ("STRING", {"multiline": False, "default": "OutputImage"}),
                "images": ("IMAGE", {"forceInput": True}),
                "export": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "description": ("STRING", {"multiline": True, "default": ""}),
                "order": ("INT", {"default": 0, "min": 0, "max": 0xffffff, "step": 1})
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "send_images"
    OUTPUT_NODE = True
    CATEGORY = f"{categoryName}/输出"

    def send_images(self, var_name, images, export, description="", order=0):
        try:
            var_name = var_prefix_name + var_name
            filename_prefix = self.filename_prefix + var_name
            results = []
            output_results = []
            full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
                filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])
            for i, tensor in enumerate(images):
                array = 255.0 * tensor.cpu().numpy()
                image = Image.fromarray(np.clip(array, 0, 255).astype(np.uint8))

                filename_with_batch_num = filename.replace("%batch_num%", str(i))
                file = f"{filename_with_batch_num}_{counter:06}_{str(i)}.png"

                image.save(os.path.join(full_output_folder, file), pnginfo=None, compress_level=1)
                # server = PromptServer.instance
                # server.send_sync(100002, encode_string(var_name, file), server.client_id)
                results.append({
                    "filename": file,
                    "subfolder": subfolder,
                    "type": self.type
                })
                output_results.append({
                    "var_name": var_name,
                    "batch": i,
                    "filename": file,
                    "subfolder": subfolder,
                    "type": self.type
                })
                counter += 1

            return {"ui": {
                "images": results,
                "output_images": output_results,
            }}
        except Exception as e:
            print(f"Exception: {var_name}")
            raise e