import pandas as pd
import fitz
import re
import os
import pickle
from tqdm import tqdm
from openai import OpenAI
from datetime import datetime
from scipy.spatial.distance import cosine
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
import cchardet

# Flask app configuration
UPLOAD_FOLDER = 'uploads'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#-- BASIC FUNTIONS

def print_line(optional=""):
    try:
        rows, columns = os.get_terminal_size()
        print('-' * columns + optional)
    except OSError:
        print('-' * 50 + optional)

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def save_data(data, filename):
    with open(filename, 'wb') as file:
        pickle.dump(data, file)
    print(f"Data saved to {filename}")

def load_data(filename):
    with open(filename, 'rb') as file:
        return pickle.load(file)

def inspect_pickle(file_path, inspect_n=1):
    # Load the DataFrame from a pickle file
    try:
        df = pd.read_pickle(file_path)
    except Exception as e:
        print(f"Failed to load the DataFrame: {e}")
        return

    # Display basic information
    print_line(f"inspecting {file_path}")
    print(f"Total Rows: {df.shape[0]}")
    #print(f"Total Columns: {df.shape[1]}")
    #print(f"DataFrame Size: {df.memory_usage(deep=True).sum()} bytes")
    #print(f"\nTop {inspect_n} Rows:")
    #print(df.head(inspect_n))
    print(f"\nBottom {inspect_n} Rows:")
    print(df.tail(inspect_n))

def apikey():
    return open("key.txt", "r").read().strip("\n")

def get_embedding(text, embedding_model):
    client  = OpenAI(api_key=apikey())
    response = client.embeddings.create(
        input=text,
        model=embedding_model
    )
    return response.data[0].embedding

#-- PROCESSING PDF TO TEXT WITH EMBEDDINGS

def process_pdf_text(text, regex, min_words, embedding_model):
    # Split the text into sentences based on regex, aggregating incomplete sentences
    sentences = re.split(regex, text)
    adjusted_sentences = []
    for sentence in sentences:
        if len(sentence.split()) < min_words and adjusted_sentences:
            adjusted_sentences[-1] += ' ' + sentence
        else:
            adjusted_sentences.append(sentence)
    
    # Embed each sentence and create a list of data
    return [(sentence, get_embedding(sentence, embedding_model)) for sentence in adjusted_sentences]

def process_pdfs(directory_path     ="Doc/", 
                 save_directory     ="Saved/", 
                 embedding_model    ="text-embedding-3-small", 
                 split_regex        =r'\.\s+(?=[A-Z])', 
                 min_words          =3):
    
    os.makedirs(save_directory, exist_ok=True)
    pdf_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.pdf')]

    for pdf_file in tqdm(pdf_files, desc="Processing PDFs", leave=False):
        pdf_path = os.path.join(directory_path, pdf_file)
        save_path = os.path.join(save_directory, os.path.splitext(pdf_file)[0] + ".pkl")

        if not os.path.exists(save_path):
            doc = fitz.open(pdf_path)
            data_list = []

            for page_num in tqdm(range(doc.page_count), desc=f"Embedding {os.path.basename(pdf_path)}", leave=False):
                # Extract raw bytes for text from the PDF
                raw_text = doc[page_num].get_text("text")#.encode('utf-8')
                
                # Detect encoding
                #encoding_result = cchardet.detect(raw_text)
                #encoding = encoding_result['encoding'] if encoding_result['encoding'] else 'utf-8'  # Fallback to 'utf-8' if encoding is None
                #text = raw_text.decode(encoding)


                page_data = process_pdf_text(raw_text, split_regex, min_words, embedding_model)
                data_list.extend([(os.path.basename(pdf_file), page_num + 1, i+1, s[0], s[1]) for i, s in enumerate(page_data)])

            # Save the data to a DataFrame then to a Pickle file
            df = pd.DataFrame(data_list, columns=['File', 'Page', 'Sentence Index', 'Sentence', 'Embedded Sentence'])
            df.to_pickle(save_path)
        else:
            tqdm.write(f"Skipping {pdf_file}, already processed.")

#-- USER QUERY PROCESSING

def send_and_receive_message(user_message,
                             pre_prompt,
                             print_chat=False, 
                             model="gpt-3.5-turbo",
                             chat_inject_agreement=True):
    client  = OpenAI(api_key=apikey())
    
    # Create the message sequence for the chat model
    if chat_inject_agreement:
        messages = [
            {"role": "system", "content": pre_prompt},
            {"role": "assistant", "content": "Ok"},
            {"role": "user", "content": user_message},
        ]
    else:
        messages = [
            {"role": "system", "content": pre_prompt},
            {"role": "user", "content": user_message},
        ]

    # Create the chat completion with the specified model
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model,
    )

    # Retrieve the response
    if chat_completion.choices and chat_completion.choices[0].message:
        chat_response = chat_completion.choices[0].message.content
    else:
        chat_response = "No response"

    # Print the conversation flow
    if print_chat:
        #print(f"Pre-Prompt: {pre_prompt}")
        print(f"User: {user_message}\nChat: {chat_response}")
    return chat_response

def process_user_query(save_path="Saved/query_history.pkl",
                       pre_prompt="",
                       model="gpt-3.5-turbo",
                       embedding_model="text-embedding-3-small",
                       user_prompt="",
                       print_chat=False):
    
    # Load existing data if available
    if os.path.exists(save_path):
        results_df = pd.read_pickle(save_path)
    else:
        results_df = pd.DataFrame(columns=['Timestamp', 'User Input', 'Query Text', 'Query Embedded'])

    try:
        if user_prompt.lower() == 'input':
            user_input = input("What would you like to know? ")
        else:
            user_input = user_prompt
        
        # Check if the query has already been processed
        existing_queries = results_df[results_df['User Input'] == user_input]
        if not existing_queries.empty:
            # Existing data found, fetch the last entry
            last_query = existing_queries.iloc[-1]
            print(f"Fetching existing data for this query.")
            if print_chat:
                print(f"User: {user_input}\nChat: {last_query['Query Text']}")
            return {
                'User Input': user_input,
                'Query Text': last_query['Query Text'],
                'Query Embedded': last_query['Query Embedded']
            }

        # If no existing data, proceed with processing
        query_text = send_and_receive_message(
            user_message=user_input,
            pre_prompt=pre_prompt,
            print_chat=print_chat,
            model=model,
            chat_inject_agreement=True)

        # Embedding the query
        query_embedded = get_embedding(query_text, embedding_model)

        # Current timestamp
        now = datetime.now()

        # Appending the results to the DataFrame
        new_entry = pd.DataFrame({
            'Timestamp': [now],
            'User Input': [user_input],
            'Query Text': [query_text],
            'Query Embedded': [query_embedded]
        })

        # Concatenate the new entry with the existing DataFrame
        results_df = pd.concat([results_df, new_entry], ignore_index=True)

        # Save the results progressively
        results_df.to_pickle(save_path)

        return {
            'User Input': user_input,
            'Query Text': query_text,
            'Query Embedded': query_embedded
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

#-- Comparison calculation and return

def load_and_concatenate(directory="Saved", file_names=None):
    # List all pickle files in the directory
    if file_names == None:
        files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.pkl')]
    else:
        file_names_pkl = [file.replace('.pdf', '.pkl') for file in file_names]
        files = [os.path.join(directory, file) for file in file_names_pkl if file.endswith('.pkl')]
    
    # Load and concatenate all DataFrames
    df_list = [pd.read_pickle(file) for file in files]
    return pd.concat(df_list, ignore_index=True)

def get_surrounding_sentences(df, index, radius):
    # Calculate bounds
    lower_bound = max(0, index - radius)
    upper_bound = min(len(df), index + radius + 1)
    return df.iloc[lower_bound:upper_bound]

def return_similar_sentences(last_query_info, 
                             top_x          =5, 
                             context_y      =2, 
                             directory      ="Saved", 
                             results_path   ="similar_results.pkl",
                             print_results  =True,
                             filenames = None):
    df = load_and_concatenate(directory, filenames)

    # Normalize embeddings and calculate cosine similarity
    query_embedding = last_query_info['Query Embedded']
    df['Cosine Similarity'] = df['Embedded Sentence'].apply(lambda x: 1 - cosine(x, query_embedding))

    # Sort DataFrame by similarity score in descending order and take the top X results
    top_sentences = df.sort_values(by='Cosine Similarity', ascending=False).head(top_x)

    # DataFrame to store the results
    columns = ['Timestamp', 'User Input', 'Query Text', 'Document', 'Similarity', 'Page', 'Text']
    results_df = pd.DataFrame(columns=columns)

    # Generate results and format them
    result_index = 0
    for _, row in top_sentences.iterrows():
        result_index        += 1
        index               = row.name
        surrounding_df      = get_surrounding_sentences(df, index, context_y)
        surrounding_text = " ".join(surrounding_df['Sentence']).replace('\n', ' ')
        result_row = {
            'Timestamp':    datetime.now(),
            'User Input':   last_query_info['User Input'],
            'Query Text':   last_query_info['Query Text'],
            'Document':     row['File'],
            'Similarity':   row['Cosine Similarity'],
            'Page':         row['Page'],
            'Text':         surrounding_text
        }
        results_df = pd.concat([results_df, pd.DataFrame([result_row])], ignore_index=True)

        if print_results:
            print_line(f"Result {result_index}/{top_x} Similarity {row['Cosine Similarity']:.2f} found in document {row['File']} Page {row['Page']} - text: ")
            print(f"{surrounding_text}")

    # Load existing results if they exist and append new results
    if os.path.exists(results_path):
        existing_results_df = pd.read_pickle(results_path)
        combined_results_df = pd.concat([existing_results_df, results_df], ignore_index=True)
    else:
        combined_results_df = results_df

    # Save the updated results to a pickle file
    combined_results_df.to_pickle(results_path)
    return results_df

def nlp_summary(user_query,
                found_fragments,
                model,
                summary_prompt,
                include_meta    =False,
                print_context   =False,
                print_response  =True):
    
# Pobieranie tekstu zapytania użytkownika
    user_query_text = user_query['User Input']

    # Przygotowanie DataFrame z fragmentami
    df = found_fragments
    if include_meta:
        df['Formatted'] = df.apply(lambda row: f"(Fragment {row.name + 1}: {row['Document']} Page {row['Page']})\n\"{row['Text']}\"", axis=1)
    else:
        df['Formatted'] = df.apply(lambda row: f"\"{row['Text']}\"", axis=1)

    # Łączenie fragmentów w jeden tekst
    found_fragments_text = "\n".join(df['Formatted'].tolist())
    postprompt_with_fragments = summary_prompt + "\n" + found_fragments_text
    
    if print_context:
        print_line("Podany kontekst:")
        print(postprompt_with_fragments)
    if print_response:
        print_line("Odpowiedź czatu:")

    # Wysyłanie tekstu do modelu NLP i odbieranie odpowiedzi
    chats_response = send_and_receive_message(user_query_text, 
                                              postprompt_with_fragments, 
                                              print_chat=print_response, 
                                              model=model,
                                              chat_inject_agreement=True)

    # Konstrukcja DataFrame z wynikami
    results_df = pd.DataFrame({
        'Timestamp': [datetime.now()],
        'summary_prompt': [summary_prompt],
        'found_fragments': [found_fragments_text],
        'user_query_text': [user_query_text],
        'chats_response': [chats_response]
    })

    # Obsługa pliku pickle
    pickle_filename = 'Logs/log_chatsummary.pkl'
    try:
        existing_df = pd.read_pickle(pickle_filename)
        final_df = pd.concat([existing_df, results_df], ignore_index=True)
    except FileNotFoundError:
        final_df = results_df

    # Zapisanie DataFrame do pliku pickle
    final_df.to_pickle(pickle_filename)

    return chats_response

#-- FLASK FUNCTIONS

app = Flask(__name__)
CORS(app)

@app.route('/send-message', methods=['POST'])
def send_message():
    try:
        user_message = request.json['message']
        response_data = send_and_receive_message(user_message, '')
        print(response_data)
       
        return response_data, 200, {'Content-Type': 'application/text'}
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return 'No file part', 400
        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400
        if file:
            file_data = file.read()
            with open('uploaded_file.pdf', 'wb') as f:
                f.write(file_data)
            return 'File uploaded successfully', 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
