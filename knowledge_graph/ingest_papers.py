from create_basic_chunks import create_basic_chunks
from create_paper_nodes import create_paper_nodes
from create_author_nodes import create_author_nodes



if __name__ == "__main__":

    files = ["./papers/AlphaStar Unplugged Large-Scale Offline Reinforcement Learning-2308.03526.json",
            "./papers/Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm-1712.01815.json"]

    # papers by Oriol Vinyals
    # files = ["./papers/Classification Accuracy Score for Conditional Generative Models-1905.10887.json",
    #          "./papers/Connecting Generative Adversarial Networks and Actor-Critic Methods-1610.01945.json",
    #          "./papers/A Neural Conversational Model-1506.05869.json",
    #          "./papers/Krylov Subspace Descent for Deep Learning-1111.4259.json",
    #          "./papers/Adversarial Evaluation of Dialogue Models-1701.08198.json",
            # ]
    create_basic_chunks(files)
    create_paper_nodes()
    create_author_nodes()
