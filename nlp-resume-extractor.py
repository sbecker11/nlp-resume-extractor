# implementing a system that leverages precise entity recognition
# using BERT alongside OpenAI's structured output to conform to a
# given JSON schema

import os
import json
import logging
import sys
from collections import defaultdict
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
import nltk
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv
from src.json_schema import JsonSchemaFactory
from src.pydantic_resume import PydanticResume 
from src.content_loader import load_docx_data

load_dotenv()

logging.basicConfig(
    format='%(filename)s: %(message)s',
    level=logging.INFO
)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
openai_model_name = "gpt-4o-2024-08-06"

resume_text = load_docx_data(os.getenv("RESUME_DOCX_PATH"))
resume_schema = None
try:
    
    json_factory = JsonSchemaFactory(os.getenv("RESUME_SCHEMA_PATH"))
    resume_schema = json_factory.get_validated_json_schema()
    
except json.JSONDecodeError as e:
    logging.error("Error: %s", e)
    sys.exit(1)
except ValueError as e:
    logging.error("Error: %s", e)
    sys.exit(1)
except FileNotFoundError as e:
    logging.error("Error: %s", e)
    sys.exit(1)

# Step 0.
# pick a pre-trained BERT model 
# from Hugging Face's `transformers` library 
# that's fine-tuned for NER, 

# https://huggingface.co/MANMEET75/bert-finetuned-named-entity-recognition-ner

# Step 1: Install Necessary Libraries
#  pip install transformers

# Step 2. Load the Model and Tokenizer
# load the pre-trained BERT model and its tokenizer from Hugging Face's model repository:

bert_model_name = "MANMEET75/bert-finetuned-named-entity-recognition-ner"
bert_tokenizer = AutoTokenizer.from_pretrained(bert_model_name)
bert_model = AutoModelForTokenClassification.from_pretrained(bert_model_name)

# Step 3: Tokenize Input Text

bert_inputs = bert_tokenizer(resume_text, return_tensors="pt")
bert_outputs = bert_model(**bert_inputs)

# Step 4: Perform Inference

# Run the tokenized input through the model:

# The outputs will contain logits which represent the probability distribution over possible labels for each token.

# Step 5: Decode the Outputs

# Convert the logits to actual labels:

bert_predictions = torch.argmax(bert_outputs.logits, dim=2)
bert_labels = [bert_model.config.id2label[pred.item()] for pred in bert_predictions[0]]
bert_tokens = bert_tokenizer.convert_ids_to_tokens(bert_inputs["input_ids"][0])

bert_output = list(zip(bert_tokens, bert_labels))

# Step 6: Aggregate and Interpret Results

# You'll need to align the tokens with the predictions, considering that BERT might split words into subwords:

# Download necessary NLTK data
nltk.download('punkt')
words = nltk.word_tokenize(resume_text)

results = defaultdict(list)
current_word = ""
current_label = ""
for token, label in bert_output.items():
    if token.startswith("##"):
        current_word += token[2:]
    else:
        if current_word:
            results[current_label].append(current_word)
        current_word = token
        current_label = label
if current_word:
    results[current_label].append(current_word)

# Example output
for label, words in results.items():
    print(f"{label}: {', '.join(words)}")

# These are the entities recognized in the text, 
# categorized by their labels. 

## Step 7. use the OpenAI API to generate structured output 
# based on the extracted entities, ensuring it follows the 
# JSON schema.

response = openai_client.ChatCompletion.create(
    model=openai_model_name, 
    messages=[
        {"role": "user", "content": f"Extract entities from: {resume_text}"}
    ],
    response_format={
        "type": "json_schema",
        "json_schema": json.dumps(resume_schema)
    }
)
print(response.choices[0].message['content'])

### 8. **Integration and Validation**

# - **Integration**: Combine the results from BERT NER with OpenAI's structuring capability. 
#  pre-process the BERT output to fit into the prompt for OpenAI. ??

# pre-process bert entities
def preprocess_bert_output(bert_output):
    entities = []
    current_entity = None
    for token, label in bert_output.items():
        # Assuming BERT uses 'B-' for beginning of entity, 'I-' for inside, 'O' for outside
        if label.startswith('B-'):
            if current_entity:
                entities.append(current_entity)
            current_entity = {'type': label[2:], 'text': token}
        elif label.startswith('I-') and current_entity:
            current_entity['text'] += ' ' + token
        elif label == 'O' and current_entity:
            entities.append(current_entity)
            current_entity = None
    if current_entity:
        entities.append(current_entity)
    
    # Convert to structured format
    return {'bert_entities': entities}

bert_entities = preprocess_bert_output(bert_output)
print(bert_entities)

# - **Validation**: Use a library like `pydantic` to validate if the 
# response from OpenAI conforms to your schema.

#   Assuming 'response' contains the AI's output in JSON format

openai_results = response.choices[0].message['content']
print(openai_results)

validated_pydantic_resume = PydanticResume.model_validate_json(openai_results)
print(validated_pydantic_resume)

# - **Comparison**: Compare the entities extracted by BERT 
# with the structured output from OpenAI.
print(bert_entities)
print(openai_entities)

### 9. **Error Handling and Iteration**

# - **Handle Errors**: Implement error handling for API calls, 
# model predictions, and schema validation.

# - **Iterate**: Based on the results, you might need to adjust your schema, refine your model 
# choices, or tweak how you structure your prompts.

# This approach ensures that the NLP tasks not only identify 
# entities with high precision but also return results in a 
# strictly defined format, which is crucial for applications
# requiring structured data.