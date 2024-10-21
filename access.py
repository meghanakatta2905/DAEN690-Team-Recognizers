from flask import Flask, request, jsonify, render_template
import pandas as pd
from openai import OpenAI

# Initialize OpenAI client with your API key
client = OpenAI(api_key="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")

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index3.html')

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
    class_csv_file_path = "C:/Users/cheth/OneDrive/Desktop/capstone/class_api_result_data.csv"
    subclass_csv_file_path = "C:/Users/cheth/OneDrive/Desktop/capstone/subclass_api_result_data.csv"
    pic_csv_file_path = "C:/Users/cheth/OneDrive/Desktop/capstone/pic_api_result_data.csv"

    # Read CSV files into dataframes
    industry_csv = pd.read_csv(industry_csv_file_path)
    class_csv = pd.read_csv(class_csv_file_path)
    subclass_csv = pd.read_csv(subclass_csv_file_path)
    pic_csv = pd.read_csv(pic_csv_file_path)

    # Convert CSVs to JSON for use in prompts
    industry_data = industry_csv.to_json(orient='records')
    class_data = class_csv.to_json(orient='records')
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
                        "text": f"Can you tell the industry code of this product based on these images? Use the following FDA industry data: {industry_data}. Only output the industry code.",
                    },
                    *[{"type": "image_url", "image_url": {"url": img_data}} for img_data in image_data_list]
                ],
            }
        ],
        max_tokens=400
    )

    # Step 2: Get the Class Code
    response_class = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Can you tell the class code of this product based on these images? Use the following FDA class data: {class_data}. Only output the class code.",
                    },
                    *[{"type": "image_url", "image_url": {"url": img_data}} for img_data in image_data_list]
                ],
            }
        ],
        max_tokens=400
    )

    # Step 3: Get the Subclass Code
    response_subclass = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Can you tell the subclass code of this product based on these images? Use the following FDA subclass data: {subclass_data}. Only output the subclass code.",
                    },
                    *[{"type": "image_url", "image_url": {"url": img_data}} for img_data in image_data_list]
                ],
            }
        ],
        max_tokens=400
    )

    # Step 4: Get the PIC Code
    response_PIC = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Can you tell the PIC code of this product based on these images? Use the following FDA PIC data: {pic_data}. Only output the PIC code.",
                    },
                    *[{"type": "image_url", "image_url": {"url": img_data}} for img_data in image_data_list]
                ],
            }
        ],
        max_tokens=400
    )

    # Step 5: Get the Product Code using the Industry Code
    industry_code = response_industry.choices[0].message.content.strip()

    # Load the Product CSV corresponding to the Industry Code
    # Since the files are in the same directory, we can access them using their names only
    product_csv_file_path = f"product_data_industry_{industry_code}.csv"

    # Load the CSV for the corresponding Industry ID
    product_csv = pd.read_csv(product_csv_file_path)

    # Convert the product CSV to JSON to pass to OpenAI
    product_data = product_csv.to_json(orient='records')

    # Step 6: Get the Product Code
    response_product = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Can you tell the product code of this product based on these images? Use the following FDA product data: {product_data}. Only output the product code.",
                    },
                    *[{"type": "image_url", "image_url": {"url": img_data}} for img_data in image_data_list]
                ],
            }
        ],
        max_tokens=400
    )

    # Extract all responses
    class_code = response_class.choices[0].message.content.strip()
    subclass_code = response_subclass.choices[0].message.content.strip() if include_subclass else "No subclass provided"
    pic_code = response_PIC.choices[0].message.content.strip()
    product_code = response_product.choices[0].message.content.strip()

    # Combine FDA codes with product code
    fda_code = f"{industry_code} {class_code} {subclass_code} {pic_code} {product_code}"

    # Build response object
    fda_code_data = {
        'industry': industry_code,
        'class': class_code,
        'subclass': subclass_code,
        'PIC': pic_code,
        'product': product_code,  # Include the product code here
        'fda_code': fda_code
    }

    return fda_code_data

if __name__ == '__main__':
    app.run(debug=True)
