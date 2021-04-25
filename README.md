# GPT-3-classification

This is the project which made by Jarvis team.

we build the GPT-3 model to extract some certain information from unstructure data.
1. PO: the product numbers
2. Action: action to the product
3. Type: Type of products
4. Position: some data will mention some special position in certain product.

# Usage
Normally, input some mail with unstructure data, and using python to extract some key words. You will also need to export your OpenAI API key to the OPENAI_API_SECRET_KEY environment variable (this is more secure than putting it in a plaintext file):
```sh
python3 main.py -t test_data.xlsx -k 'OPENAI_API_SECRET_KEY'
```
