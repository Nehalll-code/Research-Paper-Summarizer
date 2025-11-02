"""
Module for retrieving research papers from Semantic Scholar.
Uses the Semantic Scholar API to search for and download research papers based on given queries.
arXiv , semantic scholar, Combined


Concepts: API interaction , HTTP requests , JSON parsing (Data format API return), Error handling
"""
import arxiv
from semanticscholar import SemanticScholar
import logging
import os
import requests


#setup for logging and debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PaperRetriever:
    """Wrapper class for paper retrieval functionality."""
    
    def __init__(self):
        """Initialize paper retriever."""
        logger.info("✅ Paper retriever initialized")
    
    def search(self, query, max_results=5):
        """
        Search for papers using the search_papers function.
        
        Args:
            query (str): Search query
            max_results (int): Maximum papers to retrieve
        
        Returns:
            list: List of paper dictionaries
        """
        return search_papers(query, max_results)


def search_papers(query, max_results=5):
    """
    Search for research papers using Semantic Scholar API and arXiv API.
    
    First : searches the arXiv (reliable and free)
    Then : searches Semantic Scholar for additional papers.
    returns combined of all as results
    
    Args:
        query (str): The search query. (keywords, topics, authors, etc.)
        max_results = default:5 (could be fewer if not found more)
        
    Returns:
        list: A list of dictionaries containing paper details.list of dict
        Each paper is a dictionary with these keys:
        {
            'title': str,           # Paper title
            'authors': list,        # List of author names
            'abstract': str,        # Paper abstract/summary
            'year': int,            # Publication year
            'pdf_url': str,         # Direct link to PDF
            'paper_url': str,       # Link to paper page
            'source': str           # 'arXiv' or 'Semantic Scholar'
        }        
    """
    papers = []
    #search arXiv first
    try:
        logger.info(f"Searching arXiv for: '{query}'")
        #create search object : query, max_results,sort by relevance
        search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
        
        #iterate through results
        for result in search.results():
            paper = {
                'title': result.title,
                'authors': [author.name for author in result.authors],
                'abstract': result.summary,
                'year': result.published.year,
                'pdf_url': result.pdf_url,
                'paper_url': result.entry_id,
                'source': 'arXiv' #track src for debugging
            }
            papers.append(paper)
            logger.info(f"✅ Found: {paper['title'][:60]}...")
    except Exception as e:
        #log any errors during arXiv search
        #try semantic scholar next
        logger.error(f"❌ Error searching arXiv: {e}")
        #do not return yet, try semantic scholar next
        
    if len(papers) < max_results:
        try:
            logger.info(f"Searching Semantic Scholar for additional papers: ")
            
            #initialize semantic scholar client
            #no api key needed for basic usage
            sch = SemanticScholar()
            
            #cal how many more papers needed
            remaining = max_results - len(papers)
            
            #search semantic scholar
            search_results = sch.search_paper(query, limit=remaining)
            
            #iterate through results
            for result in search_results:
                paper = {
                    'title': result.title,
                    'authors': [author['name'] for author in result.authors] if result.authors else [],
                    'abstract': result.abstract if result.abstract else 'No abstract available',
                    'year': result.year if result.year else 'N/A',
                    'pdf_url': result.openAccessPdf['url'] if result.openAccessPdf else None,
                    'paper_url': result.url if result.url else None,
                    'source': 'Semantic Scholar'
                }
                papers.append(paper)
                logger.info(f"✅ Found: {paper['title'][:60]}...")
        except Exception as e:
            logger.error(f"❌ Error searching Semantic Scholar: {e}")
            #not to crash, just return what we have
    
    final_papers = papers[:max_results]  #ensure we do not exceed max_results
    logger.info(f"Total papers retrieved: {len(final_papers)}")
    return final_papers


#test function
def test_search():
    """
    Test the search_papers function.
    
    Usage: python -m src.paper_retrieval
    """
    print("\n" + "="*70)
    print("TEST: Paper Retrieval Module")
    print("="*70)
    
    query = "neural networks"
    print(f"\n🔍 Searching for: '{query}'")
    print(f"📊 Requesting: 3 papers\n")
    
    # Test with class (for Streamlit compatibility)
    retriever = PaperRetriever()
    papers = retriever.search(query, max_results=3)
    
    # Display results
    print(f"✅ Found {len(papers)} papers:\n")
    
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper['title']}")
        print(f"   Authors: {', '.join(paper['authors'][:2])}{'...' if len(paper['authors']) > 2 else ''}")
        print(f"   Year: {paper['year']}")
        print(f"   Source: {paper['source']}")
        print(f"   PDF: {paper.get('pdf_url', 'N/A')[:60]}...")
        print()


if __name__ == "__main__":
    test_search()
