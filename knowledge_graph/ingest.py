from knowledge_graph.create_basic_chunks import create_basic_chunks
from knowledge_graph.create_paper_nodes import create_paper_nodes
from knowledge_graph.create_author_nodes import create_author_nodes
from knowledge_graph.create_reference_edges import create_reference_edges
import time


def add_papers_to_graph(files):
    start_time = time.time()
    create_basic_chunks(files)
    print("create_basic_chunks took:", time.time() - start_time, "seconds")
    
    start_time = time.time()
    create_paper_nodes()
    print("create_paper_nodes took:", time.time() - start_time, "seconds")
    
    start_time = time.time()
    create_author_nodes()
    print("create_author_nodes took:", time.time() - start_time, "seconds")
    
    start_time = time.time()
    create_reference_edges(files)
    print("create_reference_edges took:", time.time() - start_time, "seconds")

if __name__ == "__main__":

    files = ["./papers/AlphaStar Unplugged Large-Scale Offline Reinforcement Learning-2308.03526.json",
            "./papers/Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm-1712.01815.json"]

    start_time = time.time()
    add_papers_to_graph(files)
    print("Total processing time:", time.time() - start_time, "seconds")