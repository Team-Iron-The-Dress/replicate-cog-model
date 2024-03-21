
# Push model to replicate

Please use the following docs for refernce: https://cog.run/getting-started/

*Cog works on macOS and Linux, use WSL on windows*

**Step 1**: 

Add your safetensor file in the root directory.
In `predict.py` replace `sdxl_turbo_lora.safetensors` with your filename.

**Step 2**: 

Create a model on Replicate https://replicate.com/models 
Make sure to select `Cutom Cog Model` in options.

**Step 3**:

Run the followings commands

```
cog login
cog push r8.im/{your-username}/{your-model-name}
```

# Inference on NextJS

**Step 1:**

create a Nextjs app using `npx create-next-app@latest`

Install replicate using `npm install replicate`

**Step 2:**

Create `api/predictions/route.js` file inside `app` directory.

and paste the below code in `route.js`

```js
import { NextResponse } from "next/server";
import Replicate from "replicate";

export async function POST(req) {
  if (req.method === 'POST') {
    const data = await req.json();
    const replicate = new Replicate({
      auth: "your-replicate-api-key",
    });
    const output = await replicate.run(
      "pushed-replicate-model-with-version",
      {
        input: {
          input_image_base64: data.input_image,
          mask_base64: data.mask_image,
        }
      }
    );
    console.log(output);
    return new NextResponse(JSON.stringify({ output_base64: output }));
  } else {
    return new NextResponse(JSON.stringify({ output_base64: null }));
  }
}
```

**Step 3:**

Replace the code in `page.js` with the below code

```js
"use client"
import { useState } from 'react';

export default function Home() {
  const [inputImage, setInputImage] = useState(null);
  const [maskImage, setMaskImage] = useState(null);
  const [outputImage, setOutputImage] = useState(null);

  const handleInputImage = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64String = reader.result.replace('data:', '').replace(/^.+,/, '');
        setInputImage(base64String);
      }
      reader.readAsDataURL(file);
    }

  };

  const handleMaskImage = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64String = reader.result.replace('data:', '').replace(/^.+,/, '');
        setMaskImage(base64String);
      }
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputImage || !maskImage) return;

    try {
      const response = await fetch("/api/replicate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ input_image: inputImage, mask_image: maskImage }),
      });

      const data = await response.json();
      setOutputImage(data.output_base64);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <form onSubmit={handleSubmit}>
        <label htmlFor='input_image'>Input Image</label>
        <input id='input_image' type="file" accept="image/*" onChange={handleInputImage} />
        <label htmlFor='mask_image'>Mask Image</label>
        <input type="file" accept="image/*" onChange={handleMaskImage} />
        <button type="submit">Upload</button>
      </form>
      {outputImage && (
        <div>
          <label>Output Image</label>
          <img src={`data:image/png;base64,${outputImage}`} alt="Output Image" />
        </div>
      )}
    </main>
  );
}
```

**Step 4:**

Run `npm run dev` to start the app.