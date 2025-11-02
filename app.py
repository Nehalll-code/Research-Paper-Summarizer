"""
Research Paper Summarizer - Streamlit Web Application
Beautiful UI with custom components - FIXED VERSION
"""
import streamlit as st
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.paper_retrieval import PaperRetriever
from src.pdf_extractor import extract_text_from_pdf_url
from src.summarizer import PaperSummarizer
from src.ui_components import (
    load_custom_css, header_with_icon, stat_card, info_box,
    success_box, warning_box, error_box, summary_box
)

# Page config
st.set_page_config(
    page_title="Research Paper Summarizer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_custom_css()

# Initialize session state
if 'papers' not in st.session_state:
    st.session_state.papers = []
if 'summaries' not in st.session_state:
    st.session_state.summaries = []
if 'meta_summary' not in st.session_state:
    st.session_state.meta_summary = None

# Header
header_with_icon(
    "Research Paper Summarizer",
    "📚",
    "AI-powered paper summarization with PEGASUS-ArXiv"
)

st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    st.markdown("**Model Configuration**")
    use_cache = st.checkbox("🚀 Enable Model Caching", value=True)
    
    st.markdown("**Display Options**")
    show_details = st.checkbox("📋 Show Detailed Info", value=True)
    
    st.markdown("---")
    
    # Stats in sidebar
    papers_count = len(st.session_state.papers)
    summaries_count = len(st.session_state.summaries)
    
    col1, col2 = st.columns(2)
    with col1:
        stat_card("Papers", f"{papers_count}", "📄", "primary")
    with col2:
        stat_card("Summaries", f"{summaries_count}", "✨", "success")

# Main tabs
tab1, tab2, tab3 = st.tabs(["🔍 Search Papers", "📤 Upload PDFs", "✨ Summarize"])

# ==============================================================================
# TAB 1: Search Papers
# ==============================================================================
with tab1:
    header_with_icon("Search Research Papers", "🔍", "Find papers from arXiv & Semantic Scholar")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_query = st.text_input(
            "What are you looking for?",
            placeholder="e.g., 'transformer attention mechanism'",
            label_visibility="collapsed"
        )
    with col2:
        max_results = st.number_input("Results", min_value=1, max_value=10, value=5)
    with col3:
        search_btn = st.button("🔍 Search", use_container_width=True, type="primary")
    
    if search_btn:
        if search_query:
            with st.spinner("🔄 Searching for papers..."):
                try:
                    retriever = PaperRetriever()
                    papers = retriever.search(search_query, max_results=int(max_results))
                    
                    if papers:
                        st.session_state.papers = papers
                        success_box("Search Complete!", f"Found {len(papers)} papers matching your query")
                        
                        st.markdown("### 📚 Results")
                        for i, paper in enumerate(papers, 1):
                            with st.expander(f"**{i}. {paper['title'][:70]}...**", expanded=i==1):
                                if isinstance(paper.get('authors'), list):
                                    authors = ', '.join(paper['authors'][:3])
                                else:
                                    authors = str(paper.get('authors', 'N/A'))
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**👥 Authors:**  \n{authors}")
                                    st.markdown(f"**📅 Year:** {paper.get('year', 'N/A')}")
                                with col2:
                                    st.markdown(f"**🏢 Source:** {paper.get('source', 'N/A')}")
                                
                                st.markdown(f"**Abstract:**  \n{paper.get('abstract', 'N/A')[:400]}...")
                                if paper.get('pdf_url'):
                                    st.markdown(f"[📥 Download PDF]({paper['pdf_url']})")
                    else:
                        warning_box("No Results", "Try a different search query or check your internet connection")
                except Exception as e:
                    error_box("Search Error", f"Failed to search papers: {str(e)}")
        else:
            info_box("Getting Started", "Enter a search query to find research papers from arXiv and Semantic Scholar", "💡")

# ==============================================================================
# TAB 2: Upload PDFs
# ==============================================================================
with tab2:
    header_with_icon("Upload Research Papers", "📤", "Upload PDF files to extract and analyze")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
    with col2:
        pdf_from_url = st.text_input(
            "Or paste PDF URL",
            placeholder="https://example.com/paper.pdf",
            label_visibility="collapsed"
        )
    
    if uploaded_files or pdf_from_url:
        info_box("Files Ready", f"{len(uploaded_files)} file(s) selected for processing", "📁")
        
        if st.button("📖 Extract Text from PDFs", use_container_width=True, type="primary"):
            extracted_texts = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_files = len(uploaded_files) + (1 if pdf_from_url else 0)
            current_idx = 0
            
            # Process uploaded files
            for idx, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"📄 Processing: {uploaded_file.name}")
                
                with st.spinner(f"Extracting text from {uploaded_file.name}..."):
                    try:
                        temp_path = f"temp_{uploaded_file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        import PyPDF2
                        with open(temp_path, 'rb') as f:
                            pdf_reader = PyPDF2.PdfReader(f)
                            text = ""
                            for page in pdf_reader.pages:
                                text += page.extract_text() + "\n"
                        
                        text = ' '.join(text.split())
                        
                        if text and len(text) > 100:
                            extracted_texts.append({
                                'filename': uploaded_file.name,
                                'text': text,
                                'length': len(text)
                            })
                            success_box("Extracted", f"{len(text)} characters from {uploaded_file.name}")
                        else:
                            warning_box("Warning", f"Insufficient text extracted from {uploaded_file.name}")
                        
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                        
                    except Exception as e:
                        error_box("Error", f"Failed to extract from {uploaded_file.name}: {str(e)}")
                
                current_idx += 1
                progress_bar.progress(current_idx / total_files if total_files > 0 else 0)
            
            # Process URL if provided
            if pdf_from_url:
                status_text.text("🌐 Downloading from URL...")
                
                with st.spinner("Downloading and extracting from URL..."):
                    try:
                        text = extract_text_from_pdf_url(pdf_from_url)
                        
                        if text and len(text) > 100:
                            extracted_texts.append({
                                'filename': pdf_from_url.split('/')[-1],
                                'text': text,
                                'length': len(text)
                            })
                            success_box("Extracted", f"{len(text)} characters from URL")
                        else:
                            warning_box("Warning", "Insufficient text extracted from URL")
                    except Exception as e:
                        error_box("Error", f"Failed to extract from URL: {str(e)}")
                
                current_idx += 1
                progress_bar.progress(current_idx / total_files)
            
            status_text.empty()
            
            # Final result
            if extracted_texts:
                st.session_state.papers = extracted_texts
                success_box(
                    "Extraction Complete!",
                    f"Successfully extracted text from {len(extracted_texts)} file(s). Ready for summarization!"
                )
    else:
        info_box(
            "Upload Method",
            "Choose PDF files from your computer or paste a direct PDF URL",
            "📌"
        )

# ==============================================================================
# TAB 3: Summarize
# ==============================================================================
with tab3:
    header_with_icon("Generate Summaries", "✨", "AI-powered paper summarization")
    
    if not st.session_state.papers:
        warning_box(
            "No Papers Loaded",
            "Please search for papers or upload PDFs first to generate summaries"
        )
    else:
        info_box(
            "Ready to Summarize",
            f"{len(st.session_state.papers)} paper(s) loaded and ready for analysis",
            "📊"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            summary_max_length = st.slider(
                "📊 Max Summary Length (words)",
                min_value=100,
                max_value=500,
                value=300,
                step=50
            )
        with col2:
            summary_min_length = st.slider(
                "📋 Min Summary Length (words)",
                min_value=50,
                max_value=250,
                value=150,
                step=25
            )
        
        if st.button("✨ Generate Summaries", use_container_width=True, type="primary"):
            with st.spinner("🤖 Loading PEGASUS-ArXiv model..."):
                try:
                    summarizer = PaperSummarizer()
                    success_box("Model Loaded", "PEGASUS-ArXiv is ready for summarization")
                except Exception as e:
                    error_box("Model Loading Error", f"Failed to load model: {str(e)}")
                    st.stop()
            
            # Extract texts from papers
            papers_text = []
            for paper in st.session_state.papers:
                if isinstance(paper, dict):
                    if 'text' in paper:
                        papers_text.append(paper['text'])
                    elif 'abstract' in paper:
                        papers_text.append(paper['abstract'])
            
            if not papers_text:
                error_box("Error", "No text content found in loaded papers")
            elif len(papers_text) == 1:
                # Single paper summarization
                with st.spinner("📝 Summarizing paper..."):
                    try:
                        summary = summarizer.summarize(
                            papers_text[0],
                            max_length=summary_max_length,
                            min_length=summary_min_length
                        )
                        st.session_state.summaries = [summary]
                        
                        success_box(
                            "Summary Generated!",
                            f"Generated a {len(summary.split())} word summary"
                        )
                        
                        st.markdown("### 📋 Paper Summary")
                        summary_box("Summary", summary, len(summary.split()))
                        
                        # Download button
                        download_text = f"PAPER SUMMARY\n{'='*50}\n\n{summary}"
                        st.download_button(
                            label="📥 Download Summary",
                            data=download_text,
                            file_name="paper_summary.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    except Exception as e:
                        error_box("Summarization Error", f"Failed to generate summary: {str(e)}")
            else:
                # Multiple papers summarization
                with st.spinner(f"📝 Summarizing {len(papers_text)} papers..."):
                    try:
                        summaries, meta_summary = summarizer.summarize_multiple(papers_text)
                        st.session_state.summaries = summaries
                        st.session_state.meta_summary = meta_summary
                        
                        success_box(
                            "All Summaries Generated!",
                            f"Successfully processed {len(summaries)} papers"
                        )
                        
                        # Individual Summaries
                        st.markdown("### 📄 Individual Paper Summaries")
                        for i, (paper, summary) in enumerate(zip(st.session_state.papers, summaries), 1):
                            paper_name = paper.get('filename', paper.get('title', f'Paper {i}'))
                            with st.expander(
                                f"**Paper {i}: {paper_name[:60]}...**",
                                expanded=(i == 1)
                            ):
                                summary_box(f"Summary #{i}", summary, len(summary.split()))
                        
                        # Meta Summary
                        st.markdown("### 🎯 Meta-Summary (All Papers Combined)")
                        summary_box(
                            "Combined Analysis",
                            st.session_state.meta_summary,
                            len(st.session_state.meta_summary.split())
                        )
                        
                        # Download all
                        st.markdown("---")
                        
                        download_text = "RESEARCH PAPERS SUMMARIES\n"
                        download_text += "="*60 + "\n\n"
                        download_text += "INDIVIDUAL SUMMARIES\n"
                        download_text += "-"*60 + "\n\n"
                        
                        for i, summary in enumerate(st.session_state.summaries, 1):
                            download_text += f"PAPER {i}\n"
                            download_text += f"{'='*60}\n"
                            download_text += f"{summary}\n\n"
                        
                        download_text += "\nMETA-SUMMARY\n"
                        download_text += "="*60 + "\n\n"
                        download_text += st.session_state.meta_summary
                        
                        st.download_button(
                            label="📥 Download All Summaries",
                            data=download_text,
                            file_name="all_summaries.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    except Exception as e:
                        error_box("Summarization Error", f"Failed to generate summaries: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem 0'>
    <p style='color: #94a3b8; margin: 0; font-size: 1.1rem'><strong>🔬 Research Paper Summarizer</strong></p>
    <p style='color: #64748b; font-size: 0.95rem; margin: 0.5rem 0'>Powered by PEGASUS-ArXiv & Streamlit</p>
    <p style='color: #475569; font-size: 0.9rem; margin-top: 1rem'>© 2025 Research Paper Summarizer</p>
</div>
""", unsafe_allow_html=True)
