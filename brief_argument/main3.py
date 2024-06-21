import asyncio
from playwright.async_api import async_playwright
import urllib.parse
import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import openai
import os

from brief_argument.models import RelevantCitationsPassage, StatementEmbeddings

# Set your OpenAI API key
openai.api_key = os.getenv("OPEN_AI")


async def search_and_scrape_caselaw(custom_var, constant_var):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            search_query = f"{custom_var} {constant_var}"
            encoded_query = urllib.parse.quote(search_query)
            google_url = f"https://www.google.com/search?q={encoded_query}"

            await page.goto(google_url, wait_until="networkidle", timeout=60000)

            # Wait for and click the Indian Kanoon link
            await page.wait_for_selector(
                '//a[contains(@href, "indiankanoon.org")]', timeout=10000
            )
            indian_kanoon_links = await page.query_selector_all(
                '//a[contains(@href, "indiankanoon.org")]'
            )
            if indian_kanoon_links:
                await indian_kanoon_links[0].click()
            else:
                print(f"No Indian Kanoon link found for '{custom_var}'.")
                return

            # Wait for the content to load
            await page.wait_for_load_state("networkidle", timeout=30000)

            # Use JavaScript to get the main content, preserving structure
            main_content = await page.evaluate(
                """
                () => {
                    const mainDiv = document.querySelector('.judgments');
                    if (!mainDiv) {
                        console.log("No .judgments class found!");
                        return null;
                    }

                    const unwantedSelectors = [
                        '.ad_doc', '.docsource_main', '.doc_title', '.doc_citations',
                        '.doc_bench', 'script', 'style', 'noscript', '.ad_'
                    ];

                    unwantedSelectors.forEach(selector => {
                        mainDiv.querySelectorAll(selector).forEach(el => el.remove());
                    });

                    // Convert HTML structure to a format we can parse in Python
                    const contentJson = [];
                    mainDiv.childNodes.forEach(node => {
                        if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
                            contentJson.push({ type: 'text', content: node.textContent.trim() });
                        } else if (node.nodeName === 'BLOCKQUOTE') {
                            contentJson.push({ type: 'quote', content: node.textContent.trim() });
                        } else if (node.nodeName === 'PRE') {
                            contentJson.push({ type: 'pre', content: node.textContent.trim() });
                        } else if (node.nodeType === Node.ELEMENT_NODE && node.textContent.trim()) {
                            contentJson.push({ type: 'text', content: node.textContent.trim() });
                        }
                    });

                    return JSON.stringify(contentJson);
                }
            """
            )

            if main_content:
                content_list = eval(main_content)  # Convert JSON string to Python list
                formatted_text = format_content(content_list)
                print(f"Extracted text for '{custom_var}':")
                print(formatted_text)
                return formatted_text
            else:
                print(f"Failed to extract content for '{custom_var}'.")
                return ""

        except Exception as e:
            print(f"Error processing '{custom_var}': {e}")
            return ""

        finally:
            await browser.close()


async def search_and_scrape_statutes(custom_var, constant_var):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            search_query = f"{custom_var} {constant_var}"
            encoded_query = urllib.parse.quote(search_query)
            google_url = f"https://www.google.com/search?q={encoded_query}"

            await page.goto(google_url, wait_until="networkidle", timeout=60000)

            # Wait for and click the Indian Kanoon link
            await page.wait_for_selector(
                '//a[contains(@href, "indiankanoon.org")]', timeout=10000
            )
            indian_kanoon_links = await page.query_selector_all(
                '//a[contains(@href, "indiankanoon.org")]'
            )
            if indian_kanoon_links:
                await indian_kanoon_links[0].click()
            else:
                print(f"No Indian Kanoon link found for '{custom_var}'.")
                return

            # Wait for the content to load
            await page.wait_for_load_state("networkidle", timeout=30000)

            # Use JavaScript to get the main content, preserving structure
            main_content = await page.evaluate(
                """
                () => {
                    const mainDiv = document.querySelector('.akoma-ntoso');
                    if (!mainDiv) {
                        console.log("No .akoma-ntoso class found!");
                        return null;
                    }

                    const unwantedSelectors = [
                        '.ad_doc', '.doc_citations',
                        '.doc_bench', 'script', 'style', 'noscript', '.ad_'
                    ];

                    unwantedSelectors.forEach(selector => {
                        mainDiv.querySelectorAll(selector).forEach(el => el.remove());
                    });

                    return mainDiv.innerHTML;
                }
            """
            )

            if main_content:
                cleaned_text = clean_text(main_content)
                formatted_text = format_content(
                    [{"type": "text", "content": cleaned_text}]
                )
                print(f"Extracted text for '{custom_var}':")
                print(formatted_text)
                return formatted_text
            else:
                print(f"Failed to extract content for '{custom_var}'.")
                return ""

        except Exception as e:
            print(f"Error processing '{custom_var}': {e}")
            return ""

        finally:
            await browser.close()


def clean_text(text):
    # Remove HTML tags using regular expressions
    cleaned_text = re.sub(r"<[^>]*>", "", text)

    # Remove extra whitespace and newlines
    cleaned_text = re.sub(r"\s+", " ", cleaned_text)
    cleaned_text = re.sub(r"\n+", "\n", cleaned_text)

    # Remove leading/trailing whitespace
    cleaned_text = cleaned_text.strip()

    # Split the text into paragraphs based on newline characters
    paragraphs = cleaned_text.split("\n")

    # Process each paragraph
    processed_paragraphs = []
    for paragraph in paragraphs:
        # Remove any remaining leading/trailing whitespace
        paragraph = paragraph.strip()

        # Check if the paragraph starts with a number followed by a dot
        match = re.match(r"^(\d+)\.\s*(.*)", paragraph)
        if match:
            # If it matches, separate the number and the text
            number = match.group(1)
            text = match.group(2)
            processed_paragraphs.append(f"{number}. {text}")
        else:
            # If it doesn't match, keep the paragraph as is
            processed_paragraphs.append(paragraph)

    # Join the processed paragraphs back into a single string
    cleaned_text = "\n".join(processed_paragraphs)

    return cleaned_text


def format_content(content_list):
    formatted_text = ""
    for item in content_list:
        if item["type"] == "text":
            text = item["content"].strip()
            if text:
                # Add the paragraph text as is
                formatted_text += text + "\n\n"
        elif item["type"] == "quote":
            # Add the quote text as is
            formatted_text += item["content"].strip() + "\n\n"
    return formatted_text.strip()


# async def process_caselaw_list(caselaw_list, constant_var):
#     all_texts = []
#     for custom_var in caselaw_list:
#         extracted_text = await search_and_scrape_caselaw(custom_var, constant_var)
#         all_texts.append(extracted_text)
#     return all_texts


async def process_caselaw_and_statutes_list(
    caselaw_list, statutes_list, constant_var, book_id
):
    all_formatted_text = []
    all_doc_names = []

    if caselaw_list:
        for custom_var in caselaw_list:
            formatted_text = await search_and_scrape_caselaw(custom_var, constant_var)
            all_formatted_text.append(formatted_text)
            all_doc_names.append(custom_var)
            print("\n" + "-" * 50 + "\n")
    else:
        print("No caselaw list provided. Skipping caselaw processing.")

    if statutes_list:
        for custom_var in statutes_list:
            formatted_text = await search_and_scrape_statutes(custom_var, constant_var)
            all_formatted_text.append(formatted_text)
            all_doc_names.append(custom_var)
            print("\n" + "-" * 50 + "\n")
    else:
        print("No statutes list provided. Skipping statutes processing.")
    # return all_formatted_text, all_doc_names
    if all_formatted_text:
        process_documents(all_formatted_text, all_doc_names, book_id)
    else:
        print("No formatted text available for processing.")


def chunk_text(text, chunk_size=400, overlap=200):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)
    return chunks


def get_embedding(texts):
    response = openai.embeddings.create(input=texts, model="text-embedding-3-large")
    return [np.array(e.embedding) for e in response.data]


def process_documents(formatted_texts, doc_names, book_id, batch_size=20):
    all_chunks = []
    all_embeddings = []
    chunk_doc_mapping = []  # To map each chunk to its document

    for formatted_text, doc_name in zip(formatted_texts, doc_names):
        # print(f"Processing document: {doc_name}")
        chunks = chunk_text(formatted_text)
        all_chunks.extend(chunks)
        chunk_doc_mapping.extend([doc_name] * len(chunks))

    # Process chunks in batches
    batch_embeddings = []
    for i in range(0, len(all_chunks), batch_size):
        batch_chunks = all_chunks[i : i + batch_size]
        print(f"Processing batch {i // batch_size + 1}")
        batch_embedding = get_embedding(batch_chunks)
        batch_embeddings.extend(batch_embedding)

    all_embeddings = np.vstack(batch_embeddings)

    # Save embeddings, chunks, and mappings for the caselaws and statutes
    os.makedirs(f"embeddings_and_chunks_store/", exist_ok=True)
    np.save(
        f"embeddings_and_chunks_store/all_chunk_embeddings.npy",
        all_embeddings,
    )
    np.save(
        f"embeddings_and_chunks_store/all_chunks.npy",
        np.array(all_chunks, dtype=object),
    )
    np.save(
        f"embeddings_and_chunks_store/chunk_doc_mapping.npy",
        np.array(chunk_doc_mapping, dtype=object),
    )

    print("Embeddings, chunks, and mappings saved successfully.")
    return all_chunks, all_embeddings, chunk_doc_mapping


def query_documents(query, chunks, embeddings, chunk_doc_mapping, law_obj, top_n=50):
    query_embedding = get_embedding_query(query)
    similarity_scores = cosine_similarity(query_embedding.reshape(1, -1), embeddings)[0]

    # Get the top N most similar chunks
    top_n_indices = similarity_scores.argsort()[-top_n:][::-1]

    # Retrieve the most relevant chunks, their scores, and document names
    relevant_passages = [
        (chunks[idx], embeddings[idx].tolist(), similarity_scores[idx], chunk_doc_mapping[idx])
        for idx in top_n_indices
    ]

    # Print the relevant passages
    # print("Relevant Passages:")
    relevant = []
    for i, (passage, embeddings, score, doc_name) in enumerate(relevant_passages, 1):
        # print(f"Passage {i} (Document: {doc_name}, Similarity Score: {score:.4f}):")
        # print(passage)
        # print(embeddings)
        # print()
        relevant.append(
            {
                "doc_name": doc_name,
                "passage": passage,
                "embeddings": embeddings,
                "score": score,
                "husbury_file": law_obj,
            }
        )

    return relevant


# citation lists
# caselaw_list = [
#     "Kesavananda Bharati Sripadagalvaru vs State Of Kerala",
# ]

# statutes_list = [
#     "Indian Penal Code",
# ]

# constant_variable = "Indian kanoon"
# book_id = "book_143"  # Unique identifier for each run

# asyncio.run(process_caselaw_and_statutes_list(caselaw_list, statutes_list, constant_variable, book_id))

# Query or statement of law
# query = "Torture in police custody Torture in police custody is an obvious disregard to human rights. The state has a duty to re-educate the constabulary and inculcate a respect for the human person and also punish"


def get_embedding_query(text):
    response = openai.embeddings.create(input=[text], model="text-embedding-3-large")
    return np.array(response.data[0].embedding)


def process_query(query):
    # Generate embeddings for the query
    query_embedding = get_embedding_query(query)

    # Save the query embedding
    # os.makedirs(f"statement_and_embedding_store/{book_id}", exist_ok=True)
    # np.save(f"statement_and_embedding_store/{book_id}/query_embedding.npy", query_embedding)

    print("Query embedding saved successfully.")
    return query_embedding


# Process the query
# query_embedding = process_query(query, book_id)

# Load the saved embeddings, chunks, and mappings for the caselaws and statutes
# embeddings = np.load(f"embeddings_and_chunks_store/{book_id}/all_chunk_embeddings.npy")
# chunks = np.load(f"embeddings_and_chunks_store/{book_id}/all_chunks.npy", allow_pickle=True)
# chunk_doc_mapping = np.load(f"embeddings_and_chunks_store/{book_id}/chunk_doc_mapping.npy", allow_pickle=True)

# Get relevant passages
# query_documents(query, chunks, embeddings, chunk_doc_mapping)


def final_function(caselaw_list, statutes_list, book_id, law_obj):
    asyncio.run(
        process_caselaw_and_statutes_list(
            caselaw_list, statutes_list, "Indian kanoon", book_id
        )
    )

    statement_embeddings = process_query(law_obj.statement)
    # try:
    StatementEmbeddings.objects.create(
        embeddings=statement_embeddings, husbury_file=law_obj
    )
    # except:
    #     return "Something Went Wrong in the Statements!!!"

    # return all_formatted_text, all_doc_names
    # relevant_passage = process_documents(all_formatted_text, all_doc_names, book_id, law_obj)
    # Process the query
    # Load the saved embeddings, chunks, and mappings for the caselaws and statutes (to retrieve relevant passages based on a query, the previously saved embeddings, chunks, and chunk-document mappings need to be loaded into memory.)
    embeddings = np.load(
        f"embeddings_and_chunks_store/all_chunk_embeddings.npy"
    )
    chunks = np.load(
        f"embeddings_and_chunks_store//all_chunks.npy", allow_pickle=True
    )
    chunk_doc_mapping = np.load(
        f"embeddings_and_chunks_store/chunk_doc_mapping.npy", allow_pickle=True
    )
    relevant_passage = query_documents(law_obj.statement, chunks, embeddings, chunk_doc_mapping, law_obj)

    # Get relevant passages
    # try:
    relevant_passage = [
        RelevantCitationsPassage(**data_item) for data_item in relevant_passage
    ]
    RelevantCitationsPassage.objects.bulk_create(relevant_passage)
    return True
    # except:
    #     return "Something Went Wrong!!!"
