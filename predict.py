import torch
import base64
from io import BytesIO
from PIL import Image
from cog import BasePredictor, Input, Path
from diffusers import AutoPipelineForInpainting

class Predictor(BasePredictor):

  def setup(self):
    pipe = AutoPipelineForInpainting.from_pretrained('stabilityai/sdxl-turbo', torch_dtype=torch.float16, variant="fp16")
    pipe.to('cuda')
    pipe.load_lora_weights("./sdxl_turbo_lora.safetensors")
    self.pipe = pipe
  
  def predict(self, input_image_base64: str = Input(description="Input base64 string"), mask_base64: str = Input(description="Mask base64 string")) -> str:

    base64_decoded = base64.b64decode(input_image_base64)
    input_image = Image.open(BytesIO(base64_decoded))

    base64_decoded = base64.b64decode(mask_base64)
    mask_image = Image.open(BytesIO(base64_decoded))
  
    output = self.pipe(
      prompt="remove wrinkles from the cloth, make shirt color black, don't operate on cloth folds, avoid changing cloth text or font prints",
      negative_prompt="wrinkled, low quality texture, degenerated texture, unintelligible text, overexposed, worst quality, low quality, jpeg artifacts, ugly, deformed, blurry, extra pockets, distorted hands",
      image=input_image,
      mask_image=mask_image,
      num_inference_steps=5,
      strength=0.5,
      guidance_scale=1
    ).images[0]
    
    buffered = BytesIO()
    output.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())

    return img_str
