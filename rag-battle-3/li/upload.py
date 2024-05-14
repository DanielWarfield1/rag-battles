import time, os

from pinecone import Pinecone
from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.vector_stores.pinecone import PineconeVectorStore


pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY_LI"),
)

dry_run = False


def process_file_advanced(partition, folder, index_names):
    global pc

    print(f"\n\n[LI] [partition{partition}]\tProcessing files [{folder}]")
    print(index_names)

    start = time.time()


def process_file_naive(partition, folder, index_names):
    global dry_run, pc

    print(f"\n\n[LI] [partition{partition}]\tProcessing files [{folder}] FAST")

    if dry_run:
        for index_name in index_names:
            print(f"\tPinecone [{index_name}] updated")

        return

    start = time.time()

    documents = SimpleDirectoryReader(
        folder,
    ).load_data()

    check1 = time.time()
    print(f"\tLlamaIndex [{len(documents)}] documents processed [{check1 - start:.4f}]")

    # Update multiple indices
    for index_name in index_names:
        check1 = time.time()
        storage_context = StorageContext.from_defaults(
            vector_store=PineconeVectorStore(
                pinecone_index=pc.Index(
                    index_name,
                ),
            ),
        )
        VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
        )

        check2 = time.time()
        print(f"\tPinecone [{index_name}] updated [{check2 - check1:.4f}]")

    print(
        f"[partition{partition}]\tProcessing files complete [{folder}] [{time.time() - start:.4f}]\n"
    )


def process(dry, ty, startp, content_dir, partitions):
    global dry_run

    dry_run = dry

    for j, folder in enumerate(partitions):
        if j >= startp:
            nd = f"{content_dir}{folder}"
            if ty == 2:
                index_names = [
                    f"rb3-li-advanced-partition{k}" for k in range(j, len(partitions))
                ]
                process_file_advanced(j, nd, index_names)
            else:
                index_names = [
                    f"rb3-li-naive-partition{k}" for k in range(j, len(partitions))
                ]
                process_file_naive(j, nd, index_names)

    print()
