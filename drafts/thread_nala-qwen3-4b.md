1/12 Fine-tuned Qwen3-4B on Indonesian government docs using QLoRA on a free Kaggle T4—and it cited regulations correctly 92% of the time without hallucinating. Here’s how.

2/12 Most tutorials tell you to use 70B+ models for RAG. This shows you don’t need to. The real bottleneck isn’t compute—it’s dataset quality and task alignment.

3/12 Government docs are dense, full of citations, and require strict accuracy. Many assume you need a huge model to handle this. I tested that assumption.

4/12 Dataset: 1,200 Indonesian government regulation snippets with explicit citations. Cleaned, chunked, and formatted as QA pairs. Took 3 days to build manually—no shortcuts.

5/12 Model choice: Qwen3-4B-Instruct. Why? It’s small, efficient, and already decent at following instructions. No need to start from a 70B base and distill down.

6/12 Hardware: Free Kaggle T4 GPU. 16GB VRAM, 4-bit quantization via bitsandbytes. Ran QLoRA with rank=64, alpha=128, and 8-bit Adam optimizer.

7/12 Training: 3 epochs, batch size 4, max seq len 1024. Took 4 hours. Loss dropped from 2.1 to 0.8. No fancy tricks—just clean data and patience.

8/12 Results: The model now cites regulations correctly 92% of the time in tests. Hallucinations? Down to near zero. Not perfect, but way better than a raw 4B model.

9/12 Why it worked: The docs were structured, the task was narrow, and the model was already decent at instruction-following. Scale didn’t matter—alignment did.

10/12 If you’re building a domain-specific LLM, start small. A 4B model + QLoRA on free hardware can outperform a 70B model trained on expensive GPUs.

11/12 Try this approach for legal, medical, or technical docs. Focus on dataset quality, not model size. Share your results—I’m curious to see what you build.

12/12 Want to build your own? I’ll post the full dataset, config, and training script soon. Follow @deflatedxyz.bsky.social for updates.