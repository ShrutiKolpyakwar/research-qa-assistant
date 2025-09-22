import streamlit as st
import tempfile
import os
import re
from collections import Counter
import PyPDF2
import io

# Page configuration
st.set_page_config(
    page_title="Research Paper Analyzer",
    page_icon="📊",
    layout="centered"
)

# Custom CSS for clean look
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #2E86AB;
    }
    .match-highlight {
        background: #FFD166;
        padding: 2px 4px;
        border-radius: 3px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title">📊 Research Paper Analyzer</div>', unsafe_allow_html=True)
st.markdown("**Extract insights from research papers with AI-powered analysis**")

# Main function to extract text from PDF
def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.getvalue()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text, len(pdf_reader.pages)
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return "", 0

# Function to extract keywords
def extract_keywords(text, num_keywords=20):
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    # Remove common words
    stop_words = {'this', 'that', 'with', 'from', 'they', 'have', 'were', 'which', 'their', 'there'}
    word_freq = Counter([word for word in words if word not in stop_words])
    return dict(word_freq.most_common(num_keywords))

# Function for smart search
def smart_search(text, search_terms):
    results = []
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        matches = []
        
        for term in search_terms:
            if term.lower() in sentence_lower:
                # Highlight the match
                highlighted = re.sub(
                    re.escape(term), 
                    f'<span class="match-highlight">{term}</span>', 
                    sentence, 
                    flags=re.IGNORECASE
                )
                matches.append((term, highlighted))
        
        if matches:
            results.append({
                'sentence': sentence.strip(),
                'matches': [m[0] for m in matches],
                'highlighted': matches[0][1]  # Show first match highlighted
            })
    
    return results[:15]  # Return top 15 results

# Main app
def main():
    # File upload section
    st.markdown("---")
    st.header("📁 Upload Research Paper")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        # Display file info
        file_size = uploaded_file.size / 1024  # KB
        st.success(f"✅ **File uploaded:** {uploaded_file.name} ({file_size:.1f} KB)")
        
        # Extract text
        text, num_pages = extract_text_from_pdf(uploaded_file)
        
        if text:
            # Basic statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Pages", num_pages)
            with col2:
                word_count = len(text.split())
                st.metric("Words", f"{word_count:,}")
            with col3:
                char_count = len(text)
                st.metric("Characters", f"{char_count:,}")
            
            # Keyword analysis
            st.markdown("---")
            st.header("🔑 Top Keywords")
            keywords = extract_keywords(text)
            
            # Display keywords as tags
            keyword_cols = st.columns(4)
            for i, (word, freq) in enumerate(keywords.items()):
                with keyword_cols[i % 4]:
                    st.code(f"{word} ({freq})")
            
            # Advanced Search Section
            st.markdown("---")
            st.header("🔍 Advanced Search")
            
            search_option = st.radio("Search type:", 
                                   ["Quick Search", "Skill-Based Search", "Content Search"])
            
            if search_option == "Quick Search":
                search_term = st.text_input("Enter keyword to search:")
                if search_term:
                    results = smart_search(text, [search_term])
                    if results:
                        st.success(f"Found {len(results)} matches")
                        for i, result in enumerate(results):
                            st.markdown(f"**Match {i+1}:** {result['highlighted']}", unsafe_allow_html=True)
                    else:
                        st.warning("No matches found")
            
            elif search_option == "Skill-Based Search":
                st.info("Search for technical skills and competencies")
                
                # Skill categories
                skills = st.multiselect("Select skills to search:",
                    ["Machine Learning", "Deep Learning", "Python", "Data Analysis", 
                     "Neural Networks", "AI", "Statistics", "Research Methodology",
                     "Algorithm", "Model", "Framework", "Dataset"]
                )
                
                if skills:
                    results = smart_search(text, skills)
                    if results:
                        st.success(f"Found skills in {len(results)} contexts")
                        for result in results:
                            st.markdown(result['highlighted'], unsafe_allow_html=True)
                            st.caption(f"Skills found: {', '.join(result['matches'])}")
                    else:
                        st.warning("None of the selected skills were found")
            
            elif search_option == "Content Search":
                st.info("Search for specific content types")
                
                content_types = st.multiselect("Search for:",
                    ["Abstract", "Introduction", "Methodology", "Results", 
                     "Conclusion", "References", "Figures", "Tables"]
                )
                
                if content_types:
                    results = []
                    for content_type in content_types:
                        if content_type.lower() in text.lower():
                            # Find the section
                            pattern = r".{0,200}" + re.escape(content_type) + r".{0,200}"
                            matches = re.findall(pattern, text, re.IGNORECASE)
                            for match in matches[:3]:  # Show first 3 matches
                                highlighted = re.sub(
                                    re.escape(content_type), 
                                    f'<span class="match-highlight">{content_type}</span>', 
                                    match, 
                                    flags=re.IGNORECASE
                                )
                                results.append(highlighted)
                    
                    if results:
                        st.success(f"Found {len(results)} content references")
                        for i, result in enumerate(results):
                            st.markdown(f"**{i+1}.** ...{result}...", unsafe_allow_html=True)
                    else:
                        st.warning("No content sections found")
            
            # Document Insights
            st.markdown("---")
            st.header("📈 Document Insights")
            
            # Research quality indicators
            col1, col2 = st.columns(2)
            
            with col1:
                # Check for academic structure
                sections_found = []
                academic_terms = ['abstract', 'introduction', 'method', 'result', 'conclusion', 'reference']
                for term in academic_terms:
                    if term in text.lower():
                        sections_found.append(term.capitalize())
                
                st.subheader("Academic Structure")
                if sections_found:
                    st.success("Well-structured paper")
                    for section in sections_found:
                        st.write(f"✅ {section}")
                else:
                    st.warning("Limited academic structure detected")
            
            with col2:
                # Technical content analysis
                technical_terms = ['algorithm', 'model', 'data', 'analysis', 'experiment', 'framework']
                tech_count = sum(1 for term in technical_terms if term in text.lower())
                
                st.subheader("Technical Content")
                st.metric("Technical Terms", tech_count)
                if tech_count >= 4:
                    st.success("High technical content")
                elif tech_count >= 2:
                    st.info("Moderate technical content")
                else:
                    st.warning("Limited technical content")
            
            # Sample content preview
            st.markdown("---")
            st.header("📖 Content Preview")
            
            preview_option = st.selectbox("Preview section:", 
                                        ["Beginning", "Middle", "End", "Random"])
            
            if preview_option == "Beginning":
                preview_text = text[:1000] + "..." if len(text) > 1000 else text
            elif preview_option == "Middle":
                mid_point = len(text) // 2
                preview_text = text[mid_point:mid_point + 1000] + "..."
            elif preview_option == "End":
                preview_text = "..." + text[-1000:] if len(text) > 1000 else text
            else:  # Random
                import random
                start = random.randint(0, max(0, len(text) - 1000))
                preview_text = text[start:start + 1000] + "..."
            
            st.text_area("Content preview:", preview_text, height=200)

# Run the app
if __name__ == "__main__":
    main()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>📊 <b>Research Paper Analyzer</b> - Simple, Powerful, Effective</p>
    <p>Upload any research paper to extract keywords, search content, and gain insights</p>
</div>
""", unsafe_allow_html=True)