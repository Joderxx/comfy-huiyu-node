from .constants import categoryName

class MathIntClampNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "value": ("INT", {"min": 0, "max": 0xffffff, "step": 1}),
                "min": ("INT", {"default": 0, "min": 0, "max": 0xffffff, "step": 1}),
                "max": ("INT", {"default": 0, "min": 0, "max": 0xffffff, "step": 1}),
            }
        }

    CATEGORY = f"{categoryName}/数学"

    RETURN_TYPES = ("INT",)
    FUNCTION = "clamp_int"

    def clamp_int(self, value, min, max):
        if value < min:
            return min
        if value > max:
            return max
        return (value,)

class MathFloatClampNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "value": ("FLOAT", {"min": 0, "max": 0xffffff, "step": 0.01}),
                "min": ("FLOAT", {"default": 0, "min": 0, "max": 0xffffff, "step": 0.01}),
                "max": ("FLOAT", {"default": 0, "min": 0, "max": 0xffffff, "step": 0.01}),
            }
        }

    CATEGORY = f"{categoryName}/数学"

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "clamp_float"

    def clamp_float(self, value, min, max):
        if value < min:
            return min
        if value > max:
            return max
        return (value,)


class MathFloatScaleNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "value": ("FLOAT", {"min": 0, "max": 0xffffff, "step": 0.01}),
                "input_min": ("FLOAT", {"default": 0, "min": 0, "max": 0xffffff, "step": 0.01}),
                "input_max": ("FLOAT", {"default": 0, "min": 0, "max": 0xffffff, "step": 0.01}),
                "output_min": ("FLOAT", {"default": 0, "min": 0, "max": 0xffffff, "step": 0.01}),
                "output_max": ("FLOAT", {"default": 0, "min": 0, "max": 0xffffff, "step": 0.01}),
            }
        }

    CATEGORY = f"{categoryName}/数学"

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "clamp_float"

    def clamp_float(self, value, input_min, input_max, output_min, output_max):
        b = (input_max - input_min)
        if b == 0:
            return (output_min,)
        return ((value - input_min) / b * (output_max - output_min) + output_min,)