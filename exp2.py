from flask import Flask, request, jsonify, render_template
import pandas as pd
from openai import OpenAI

# Initialize OpenAI client with your API key
client = OpenAI(
    api_key="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")

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index6.html')


@app.route('/get_fda_code', methods=['POST'])
def get_fda_code():
    data = request.get_json()
    images_base64 = data['images_base64']  # Array of base64-encoded images
    include_subclass = data.get('include_subclass', True)  # Include subclass by default

    # Process all the images together and return a single FDA code
    fda_code = get_FDA_code_from_images_base64(images_base64, include_subclass)

    return jsonify(fda_code)


def get_FDA_code_from_images_base64(images_base64, include_subclass=True):
    # Combine all images into one request and analyze them as a group
    image_data_list = [f"data:image/jpeg;base64,{image_base64}" for image_base64 in images_base64]

    # Load FDA data from CSVs
    industry_csv_file_path = "C:/Users/cheth/OneDrive/Desktop/capstone/industry_api_result_data.csv"
    subclass_csv_file_path = "subclassforfood.csv"
    pic_csv_file_path = "picmodified.csv"

    # Read CSV files into dataframes
    industry_csv = pd.read_csv(industry_csv_file_path)
    subclass_csv = pd.read_csv(subclass_csv_file_path)
    pic_csv = pd.read_csv(pic_csv_file_path)

    # Convert CSVs to JSON for use in prompts
    industry_data = industry_csv.to_json(orient='records')
    subclass_data = subclass_csv.to_json(orient='records')
    pic_data = pic_csv.to_json(orient='records')

    # Step 1: Get the Industry Code
    response_industry = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Can you provide the industry code of this product based on these images? Use the following FDA industry data: {industry_data}. Output only the industry code."
                    },
                    *[{"type": "image_url", "image_url": {"url": img_data}} for img_data in image_data_list]
                ],
            }
        ],
        max_tokens=100
    )
    industry_code = response_industry.choices[0].message.content.strip()

    # Get Industry Explanation Separately
    response_industry_explanation = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Explain why the following industry code '{industry_code}' was chosen based on the product images from the dataset: {industry_data}."
                    },
                    *[{"type": "image_url", "image_url": {"url": img_data}} for img_data in image_data_list]
                ],
            }
        ],
        max_tokens=200
    )
    industry_description = response_industry_explanation.choices[0].message.content.strip()

    # Step 2: Get Class Code and Explanation
    class_csv_file_path = f"class_data_industry_{industry_code}.csv"
    class_csv = pd.read_csv(class_csv_file_path)
    class_data = class_csv.to_json(orient='records')

    response_class = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Can you provide the class code of this product based on these images? Use the following FDA class data: {class_data}. Output only the class code."
                    },
                    *[{"type": "image_url", "image_url": {"url": img_data}} for img_data in image_data_list]
                ],
            }
        ],
        max_tokens=100
    )
    class_code = response_class.choices[0].message.content.strip()

    # Get Class Explanation Separately
    response_class_explanation = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Explain why the following class code '{class_code}' was chosen based on the product images from the dataset: {class_data}."
                    },
                    *[{"type": "image_url", "image_url": {"url": img_data}} for img_data in image_data_list]
                ],
            }
        ],
        max_tokens=200
    )
    class_description = response_class_explanation.choices[0].message.content.strip()

    # Step 3: Get Subclass Code and Explanation (if included)
    subclass_description = ""
    if include_subclass:
        response_subclass = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Can you provide the subclass code of this product based on these images? Use the following FDA subclass data: {subclass_data}. Output only the subclass code."
                        },
                        *[{"type": "image_url", "image_url": {"url": img_data}} for img_data in image_data_list]
                    ],
                }
            ],
            max_tokens=100
        )
        subclass_code = response_subclass.choices[0].message.content.strip()

        # Get Subclass Explanation Separately
        response_subclass_explanation = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Explain why the following subclass code '{subclass_code}' was chosen based on the product images from the dataset {subclass_data}."
                        },
                        *[{"type": "image_url", "image_url": {"url": img_data}} for img_data in image_data_list]
                    ],
                }
            ],
            max_tokens=200
        )
        subclass_description = response_subclass_explanation.choices[0].message.content.strip()
    else:
        subclass_code = "No subclass provided"

    # Step 4: Get PIC Code and Explanation
    response_PIC = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Can you provide the PIC code of this product based on these images? Use the following FDA PIC data: {pic_data}. Output only the PIC code."
                    },
                    *[{"type": "image_url", "image_url": {"url": img_data}} for img_data in image_data_list]
                ],
            }
        ],
        max_tokens=100
    )
    pic_code = response_PIC.choices[0].message.content.strip()

    response_PIC_explanation = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Explain why the following PIC code '{pic_code}' was chosen based on the product images from the pic dataset: {pic_data} ."
                    },
                    *[{"type": "image_url", "image_url": {"url": img_data}} for img_data in image_data_list]
                ],
            }
        ],
        max_tokens=200
    )
    pic_description = response_PIC_explanation.choices[0].message.content.strip()

    # Step 5: Get the Product Code and Explanation
    product_csv_file_path = f"product_data_industry_{industry_code}.csv"
    product_csv = pd.read_csv(product_csv_file_path)
    product_data = product_csv.to_json(orient='records')

    response_product = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Can you provide the product code of this product based on these images? Use the following FDA product data: {product_data}. Output only the product code."
                    },
                    *[{"type": "image_url", "image_url": {"url": img_data}} for img_data in image_data_list]
                ],
            }
        ],
        max_tokens=100
    )
    product_code = response_product.choices[0].message.content.strip()

    response_product_explanation = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Explain why the following product code '{product_code}' was chosen based on the product images from the product dataset: {product_data}."
                    },
                    *[{"type": "image_url", "image_url": {"url": img_data}} for img_data in image_data_list]
                ],
            }
        ],
        max_tokens=200
    )
    product_description = response_product_explanation.choices[0].message.content.strip()

    # Combine FDA codes with product code
    fda_code = f"{industry_code} {class_code} {subclass_code} {pic_code} {product_code}"

    # Build response object
    fda_code_data = {
        'industry': industry_code,
        'industry_description': industry_description,
        'class': class_code,
        'class_description': class_description,
        'subclass': subclass_code,
        'subclass_description': subclass_description,
        'PIC': pic_code,
        'PIC_description': pic_description,
        'product': product_code,
        'product_description': product_description,
        'fda_code': fda_code
    }

    return fda_code_data


if __name__ == '__main__':
    app.run(debug=True)
