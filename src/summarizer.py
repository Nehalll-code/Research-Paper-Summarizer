"""
Transformer-based text summarization using PEGASUS (arxiv variant).
Pre-trained specifically on scientific papers from ArXiv.
"""
from transformers import pipeline
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PaperSummarizer:
    """Summarizes research papers using PEGASUS-ArXiv."""
    
    def __init__(self):
        """Initialize PEGASUS-ArXiv (best for research papers)."""
        logger.info("🤖 Loading PEGASUS-ArXiv model...")
        logger.info("This model is trained specifically on research papers!")
        
        try:
            # Use pegasus-arxiv - specifically trained for research papers
            self.summarizer = pipeline(
                "summarization",
                model="google/pegasus-arxiv",  # ← Better for papers!
                device=-1
            )
            logger.info("✅ PEGASUS-ArXiv model loaded successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            raise
    
    def summarize(self, text, max_length=200, min_length=80):  # EDIT: Changed defaults 150→200, 50→80
        """Summarize text using PEGASUS-ArXiv (1024 token limit)."""
        try:
            logger.info(f"📝 Summarizing {len(text)} characters...")
            
            if not text or len(text.strip()) < 100:
                return "Text too short to summarize."
            
            # EDIT: Increased from 3000 to 3500 for more content
            # PEGASUS-ArXiv: 1024 tokens ≈ 4096 chars, use 3500 to be safe
            max_chars = 3500
            if len(text) > max_chars:
                text = text[:max_chars]
                # EDIT: Smart truncation - try to end at sentence boundary
                last_period = text.rfind('.')
                if last_period > max_chars - 200:  # If period is close to end
                    text = text[:last_period + 1]
                logger.info(f"📌 Truncated to {len(text)} characters")
            
            logger.info("Generating summary...")
            
            result = self.summarizer(
                text,
                max_length=max_length,  # EDIT: Removed min() wrapper - use parameter directly
                min_length=min_length,  # EDIT: Removed min() wrapper - use parameter directly
                do_sample=False,
                truncation=True, # EDIT: Added truncation parameter for safety
                
                # EDIT: Added these parameters to reduce repetition
                repetition_penalty=2.0,        # ← Penalize repeated tokens
                no_repeat_ngram_size=3,        # ← Don't repeat 3-word phrases
                length_penalty=2.0,            # ← Prefer longer output
                early_stopping=True,
                num_beams=4                    # ← Better quality
            )
            
            summary = result[0]['summary_text']
            
            # EDIT: Clean up weird formatting
            summary = summary.replace('<n>', '\n')  # Replace tags with newlines
            summary = summary.strip()  # Remove extra whitespace
        
            logger.info(f"✅ Summary generated ({len(summary.split())} words)")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            # EDIT: Added traceback for better debugging
            import traceback
            traceback.print_exc()
            return "Summary generation failed."
    
    def summarize_multiple(self, texts):
        """Summarize multiple papers."""
        summaries = []
        
        for i, text in enumerate(texts):
            logger.info(f"\n📄 Summarizing paper {i+1}/{len(texts)}")
            summary = self.summarize(text)
            summaries.append(summary)
        
        logger.info("\n🔗 Creating meta-summary...")
        combined = ' '.join(summaries)
        meta_summary = self.summarize(combined, max_length=250, min_length=75)
        
        return summaries, meta_summary


def test_summarizer():
    """Test the summarizer."""
    print("\n" + "="*70)
    print("TEST: PEGASUS-ArXiv Summarizer (For Research Papers)")
    print("="*70)
    
    # EDIT: More diverse sample text simulating multiple papers
    sample_text = """
    The dominant sequence transduction models are based on complex recurrent or 
    convolutional neural networks that include an encoder and a decoder. We propose 
    a new simple network architecture, the Transformer, based solely on attention 
    mechanisms, dispensing with recurrence and convolutions entirely. Experiments on 
    machine translation tasks show these models to be superior in quality while being 
    more parallelizable and requiring significantly less time to train. Our model 
    achieves 28.4 BLEU on the WMT 2014 English-to-German translation task.
    
    Neural machine translation has made significant progress in recent years.
    Deep learning models with attention mechanisms have become the standard approach.
    However, these models still face challenges with long-range dependencies and
    computational efficiency. We present improvements to address these limitations.
    
    Self-attention mechanisms allow the model to attend to different positions of the
    input sequence when computing representations. This enables better capture of
    dependencies regardless of their distance in the sequence. Multi-head attention
    further improves performance by allowing the model to jointly attend to information
    from different representation subspaces.
    
    Training efficiency is crucial for practical deployment of neural models.
    Our architecture achieves state-of-the-art performance while requiring significantly
    less training time compared to previous models. The parallelizable nature of the
    architecture enables training on multiple GPUs effectively.
    
    Experimental results demonstrate the effectiveness of our approach on multiple
    benchmark datasets. The model achieves competitive or superior performance across
    various natural language processing tasks including machine translation and
    language understanding. Future work will explore applications to other domains.
    """
    
    print("\n📥 Loading PEGASUS-ArXiv model...")
    summarizer = PaperSummarizer()
    
    print(f"\n📝 Text length: {len(sample_text)} characters")
    print(f"📝 Word count: {len(sample_text.split())} words")  # EDIT: Added word count
    print("\n🤖 Generating summary...")
    
    # EDIT: Pass explicit parameters for longer summary
    summary = summarizer.summarize(sample_text, max_length=250, min_length=100)
    
    print(f"\n✅ Summary:\n{summary}")
    print(f"\n📊 Summary length: {len(summary)} characters")  # EDIT: More descriptive
    print(f"📊 Summary word count: {len(summary.split())} words")  # EDIT: Added word count


if __name__ == "__main__":
    test_summarizer()
