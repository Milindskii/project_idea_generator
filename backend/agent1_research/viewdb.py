import chromadb

client = chromadb.PersistentClient(path="./vector_store")

collection = client.get_collection("research_papers")

data = collection.get()

print("Total documents:", len(data["documents"]))
print()

for i in range(len(data["documents"])):
    print("TITLE:", data["metadatas"][i]["title"])
    print("PDF:", data["metadatas"][i]["pdf"])
    print()