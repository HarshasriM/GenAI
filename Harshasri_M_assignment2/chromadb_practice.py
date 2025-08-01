import chromadb
chroma_client = chromadb.Client()

print("chromadb client created")

# create a new collection
collection = chroma_client.create_collection(name="my_collection",get_or_create=True)
print("collection created",collection)

# Listing all the collections in the database
collections = chroma_client.list_collections()
print(collections)

# Inserting a document into the collection
collection.add(
    documents=[
        "This is a document about pineapple",
        "This is a document about oranges"
    ],
    ids=["id1", "id2"]
)



# to get all the items in the collection
print(collection.get())
print()
print(collection.get("id1"))
print()

# Deleting a document from the collection
#If no ids are supplied, it will delete all items in the collection
#but we should pass atleast one id or where or where_document as parameters otherwise it will raise an Valueerror
collection.delete("id1")
print("document deleted successfully\n")



# updating a document in the collection
collection.update(
    documents=["This is about oranges"],
    ids=["id2"]
)
print("document Updated successfully\n")
print("Updated documents are:")
print(collection.get())
print()

#We can use include to decide what to show in output
print(collection.get(include=["metadatas"]))
print()
print(collection.get(include=["documents"]))
print()

# using of upsert method which updates existing items, or adds them if they don't yet exist.
collection.upsert(
    documents=["This is a document about pineapple","This is a document about Mangoes"],
    ids=["id1","id3"]
)

print("Upserted documents are:")
print(collection.get())
print()







# querying the collection

#The query method is used to search the collection for documents that match the query text.
#The query method returns a list of dictionaries, each of which represents a document that matches the query text.
#The dictionaries contain the document's id, metadata, and text.
#The query method takes the following parameters:
#query_texts: A list of strings that represent the query text. or
#query_embeddings: A list of lists of floats that represent the query embeddings.or
#query_images: A list of strings that represent the query image paths.or
#query_uris: A list of strings that represent the query URI paths.
#n_results: An integer that represents the maximum number of results to return.
#include: A list of strings that represent the types of data to include in the query results. The possible values are "documents" and "metadatas".
#where: A dictionary that represents the query filter. The keys are the names of the metadata fields, and the values are the values to match.
#where_document: A dictionary that represents the query filter. The keys are the names of the document fields, and the values are the values to match.
#
results = collection.query(
    query_texts=["pineapple"],
    n_results=1
)
results = collection.query(
    query_texts=["pineapple"],
    n_results=1,
    include=["documents"]
)
print("Query results are:")
print(results)






#working with Embeddings
#The embeddings method is used to generate embeddings for the documents in the collection.
from sentence_transformers import SentenceTransformer


# Documents to be embedded
documents = [
    "This is a document about apples",
    "This is a document about bananas",
    "This is a document about oranges",
    "This is a document about grapes",
    "This is a document about pineapples"
]

# Corresponding IDs for the documents
ids = ["id1", "id2", "id3", "id4", "id5"]

# Generate embeddings for documents
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings for the documents
embeddings = model.encode(documents)


# Add embeddings to the collection
collection.add(
    ids=ids,
    documents=documents,
    embeddings=embeddings
)

print(collection.get())

# Query text
search_list = ["apples"]

# Generate embeddings for the query text
query_embeddings = model.encode(search_list)

# Query the collection using the embeddings
results = collection.query(
    query_embeddings=query_embeddings,
    n_results=2
)

# Print the results
print(results)


