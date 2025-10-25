import streamlit as st
import tempfile
import os
import re
from collections import Counter
import PyPDF2
import io

# Page configuration
st.set_page_config(
    page_title="Research Paper & Resume Analyzer",
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
    .resume-highlight {
        background: #06D6A0;
        padding: 2px 4px;
        border-radius: 3px;
        font-weight: bold;
    }
    .insight-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .role-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #2E86AB;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title">📊 Document Analyzer</div>', unsafe_allow_html=True)
st.markdown("**Analyze Research Papers and Resumes with AI-powered insights**")

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
    stop_words = {'this', 'that', 'with', 'from', 'they', 'have', 'were', 'which', 'their', 'there', 'will', 'using'}
    word_freq = Counter([word for word in words if word not in stop_words])
    return dict(word_freq.most_common(num_keywords))

# Function for smart search
def smart_search(text, search_terms, doc_type="research"):
    results = []
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        matches = []
        
        for term in search_terms:
            if term.lower() in sentence_lower:
                # Choose highlight color based on document type
                highlight_class = "resume-highlight" if doc_type == "resume" else "match-highlight"
                highlighted = re.sub(
                    re.escape(term), 
                    f'<span class="{highlight_class}">{term}</span>', 
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

# ENHANCED: Role-Specific Analysis Function
def analyze_for_specific_role(text, target_role):
    """Analyze resume for a specific target role and provide detailed insights"""
    
    # Comprehensive role requirements database
    role_requirements = {
        'Data Scientist': {
            'core_skills': ['python', 'machine learning', 'statistics', 'sql', 'data analysis'],
            'advanced_skills': ['tensorflow', 'pytorch', 'deep learning', 'nlp', 'computer vision'],
            'tools': ['pandas', 'numpy', 'scikit-learn', 'jupyter', 'tableau'],
            'concepts': ['data cleaning', 'feature engineering', 'model deployment', 'ab testing'],
            'experience_keywords': ['data science', 'ml', 'predictive modeling', 'data mining']
        },
        'Software Engineer': {
            'core_skills': ['python', 'java', 'javascript', 'sql', 'algorithms'],
            'advanced_skills': ['system design', 'microservices', 'aws', 'docker', 'kubernetes'],
            'tools': ['git', 'jenkins', 'docker', 'postman', 'visual studio'],
            'concepts': ['ood', 'design patterns', 'ci/cd', 'rest api', 'agile'],
            'experience_keywords': ['software development', 'full stack', 'backend', 'frontend']
        },
        'Data Analyst': {
            'core_skills': ['sql', 'excel', 'python', 'tableau', 'data visualization'],
            'advanced_skills': ['power bi', 'r', 'etl', 'data warehousing', 'dashboard'],
            'tools': ['excel', 'tableau', 'power bi', 'sql', 'python'],
            'concepts': ['reporting', 'kpi', 'metrics', 'data governance', 'business intelligence'],
            'experience_keywords': ['data analysis', 'reporting', 'insights', 'analytics']
        },
        'Machine Learning Engineer': {
            'core_skills': ['python', 'machine learning', 'deep learning', 'sql', 'aws'],
            'advanced_skills': ['tensorflow', 'pytorch', 'mlops', 'model deployment', 'docker'],
            'tools': ['tensorflow', 'pytorch', 'docker', 'kubernetes', 'airflow'],
            'concepts': ['model serving', 'feature store', 'model monitoring', 'experiment tracking'],
            'experience_keywords': ['ml engineering', 'model deployment', 'mlops', 'production']
        },
        'Web Developer': {
            'core_skills': ['javascript', 'html', 'css', 'react', 'node.js'],
            'advanced_skills': ['typescript', 'redux', 'graphql', 'next.js', 'aws'],
            'tools': ['react', 'node.js', 'mongodb', 'express', 'git'],
            'concepts': ['responsive design', 'rest api', 'authentication', 'web performance'],
            'experience_keywords': ['web development', 'frontend', 'backend', 'full stack']
        },
        'DevOps Engineer': {
            'core_skills': ['aws', 'docker', 'kubernetes', 'linux', 'python'],
            'advanced_skills': ['terraform', 'ansible', 'jenkins', 'prometheus', 'grafana'],
            'tools': ['docker', 'kubernetes', 'jenkins', 'terraform', 'aws'],
            'concepts': ['ci/cd', 'infrastructure as code', 'monitoring', 'cloud security'],
            'experience_keywords': ['devops', 'cloud', 'infrastructure', 'automation']
        }
    }
    
    if target_role not in role_requirements:
        return None
    
    requirements = role_requirements[target_role]
    text_lower = text.lower()
    
    # Calculate scores for each category
    def calculate_category_score(category_skills):
        found_skills = [skill for skill in category_skills if skill in text_lower]
        return (len(found_skills) / len(category_skills)) * 100 if category_skills else 0
    
    # Calculate overall match score
    core_score = calculate_category_score(requirements['core_skills'])
    advanced_score = calculate_category_score(requirements['advanced_skills'])
    tools_score = calculate_category_score(requirements['tools'])
    concepts_score = calculate_category_score(requirements['concepts'])
    
    # Experience relevance
    exp_matches = sum(1 for keyword in requirements['experience_keywords'] if keyword in text_lower)
    experience_score = (exp_matches / len(requirements['experience_keywords'])) * 100
    
    # Weighted overall score
    overall_score = (core_score * 0.4 + advanced_score * 0.3 + tools_score * 0.15 + 
                    concepts_score * 0.10 + experience_score * 0.05)
    
    # Identify missing skills
    def get_missing_skills(skills_list):
        return [skill for skill in skills_list if skill not in text_lower]
    
    missing_core = get_missing_skills(requirements['core_skills'])
    missing_advanced = get_missing_skills(requirements['advanced_skills'])
    missing_tools = get_missing_skills(requirements['tools'])
    
    # Found skills
    found_core = [skill for skill in requirements['core_skills'] if skill in text_lower]
    found_advanced = [skill for skill in requirements['advanced_skills'] if skill in text_lower]
    
    # Generate improvement recommendations
    def generate_recommendations(missing_core, missing_advanced, overall_score):
        recommendations = []
        
        if overall_score < 50:
            recommendations.append("🚨 **Major Skills Gap** - Focus on core skills first")
        elif overall_score < 70:
            recommendations.append("⚠️ **Moderate Skills Gap** - Build on your foundation")
        else:
            recommendations.append("✅ **Strong Foundation** - Focus on advanced specialization")
        
        if missing_core:
            recommendations.append(f"🎯 **Priority**: Learn {', '.join(missing_core[:2])}")
        
        if missing_advanced:
            recommendations.append(f"📈 **Next Level**: Explore {', '.join(missing_advanced[:2])}")
        
        # Specific learning paths
        if 'aws' in missing_core + missing_advanced:
            recommendations.append("☁️ **Cloud**: Start with AWS Fundamentals certification")
        if 'docker' in missing_core + missing_advanced:
            recommendations.append("🐳 **DevOps**: Learn Docker containerization basics")
        if 'machine learning' in missing_core + missing_advanced:
            recommendations.append("🤖 **ML**: Practice with Scikit-learn and basic algorithms")
        
        return recommendations
    
    recommendations = generate_recommendations(missing_core, missing_advanced, overall_score)
    
    return {
        'overall_score': overall_score,
        'category_scores': {
            'core_skills': core_score,
            'advanced_skills': advanced_score,
            'tools': tools_score,
            'concepts': concepts_score,
            'experience': experience_score
        },
        'found_skills': {
            'core': found_core,
            'advanced': found_advanced
        },
        'missing_skills': {
            'core': missing_core,
            'advanced': missing_advanced,
            'tools': missing_tools
        },
        'recommendations': recommendations,
        'requirements': requirements
    }

# ENHANCED: Display Role-Specific Analysis
def display_role_specific_analysis(role_analysis, target_role):
    st.markdown("---")
    st.markdown(f'<div class="insight-card"><h3>🎯 {target_role} - Role Analysis</h3></div>', unsafe_allow_html=True)
    
    # Overall Score
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall Match Score", f"{role_analysis['overall_score']:.1f}%")
    with col2:
        st.metric("Core Skills Match", f"{role_analysis['category_scores']['core_skills']:.1f}%")
    with col3:
        st.metric("Experience Relevance", f"{role_analysis['category_scores']['experience']:.1f}%")
    
    # Progress bars for each category
    st.subheader("📊 Detailed Breakdown")
    for category, score in role_analysis['category_scores'].items():
        st.write(f"**{category.replace('_', ' ').title()}:** {score:.1f}%")
        st.progress(score / 100)
    
    # Found Skills
    st.subheader("✅ Skills You Have")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Core Skills:**")
        for skill in role_analysis['found_skills']['core']:
            st.success(f"✓ {skill.title()}")
    
    with col2:
        st.write("**Advanced Skills:**")
        for skill in role_analysis['found_skills']['advanced']:
            st.info(f"✓ {skill.title()}")
    
    # Missing Skills
    st.subheader("🚨 Skills to Learn")
    
    if role_analysis['missing_skills']['core']:
        st.error("**Priority - Core Skills:**")
        for skill in role_analysis['missing_skills']['core']:
            st.write(f"❌ {skill.title()}")
    
    if role_analysis['missing_skills']['advanced']:
        st.warning("**Advanced Skills to Develop:**")
        for skill in role_analysis['missing_skills']['advanced']:
            st.write(f"⚡ {skill.title()}")
    
    # Recommendations
    st.subheader("💡 Improvement Plan")
    for recommendation in role_analysis['recommendations']:
        st.write(recommendation)
    
    # Learning Resources
    st.subheader("📚 Learning Resources")
    resource_map = {
        'python': "• Codecademy Python Course\n• Real Python Tutorials\n• Python.org Documentation",
        'machine learning': "• Coursera ML by Andrew Ng\n• Fast.ai Practical Deep Learning\n• Kaggle Learn",
        'aws': "• AWS Training & Certification\n• A Cloud Guru\n• AWS Whitepapers",
        'docker': "• Docker Getting Started\n• Kubernetes.io Tutorials\n• DevOps Roadmap"
    }
    
    # Show resources for missing core skills
    missing_core_skills = role_analysis['missing_skills']['core'][:2]
    for skill in missing_core_skills:
        if skill in resource_map:
            st.write(f"**{skill.title()}:**")
            st.write(resource_map[skill])

# Basic Resume Analysis (Original)
def analyze_resume_basic(text):
    st.header("📋 Basic Resume Analysis")
    
    # Common resume sections and skills
    resume_sections = {
        'contact': ['email', 'phone', 'linkedin', 'github', 'contact'],
        'education': ['education', 'university', 'college', 'degree', 'gpa'],
        'experience': ['experience', 'work', 'internship', 'employed'],
        'skills': ['skills', 'programming', 'technical', 'languages'],
        'projects': ['projects', 'portfolio', 'github'],
        'certifications': ['certification', 'certificate', 'training']
    }
    
    # Technical skills to look for
    technical_skills = [
        'python', 'java', 'sql', 'javascript', 'html', 'css', 'react', 'node',
        'machine learning', 'ai', 'data analysis', 'pandas', 'numpy', 'tensorflow',
        'aws', 'docker', 'git', 'github', 'streamlit', 'django', 'flask'
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Resume Sections Found")
        sections_found = []
        for section, keywords in resume_sections.items():
            if any(keyword in text.lower() for keyword in keywords):
                sections_found.append(section.capitalize())
        
        for section in sections_found:
            st.success(f"✅ {section}")
        
        if len(sections_found) < 3:
            st.warning("⚠️ Limited resume structure detected")
    
    with col2:
        st.subheader("💻 Technical Skills Found")
        skills_found = []
        for skill in technical_skills:
            if skill in text.lower():
                skills_found.append(skill)
        
        if skills_found:
            for skill in skills_found[:8]:
                st.code(skill)
            if len(skills_found) > 8:
                st.info(f"+ {len(skills_found) - 8} more skills")
        else:
            st.warning("No technical skills detected")

# Main app
def main():
    # Document type selection
    st.markdown("---")
    st.header("📄 Select Document Type")
    
    doc_type = st.radio(
        "Choose what you want to analyze:",
        ["Research Paper", "Resume"],
        horizontal=True
    )
    
    st.markdown("---")
    st.header("📁 Upload Document")
    
    uploaded_file = st.file_uploader(f"Choose a {doc_type} PDF file", type="pdf")
    
    if uploaded_file is not None:
        # Display file info
        file_size = uploaded_file.size / 1024  # KB
        st.success(f"✅ **File uploaded:** {uploaded_file.name} ({file_size:.1f} KB)")
        
        # Extract text
        text, num_pages = extract_text_from_pdf(uploaded_file)
        
        if text:
            # Show appropriate analysis based on document type
            if doc_type == "Research Paper":
                # Your existing research paper analysis
                pass
            else:  # Resume
                analyze_resume_basic(text)
                
                # ENHANCED: Role-Specific Analysis Section
                st.markdown("---")
                st.header("🎯 Role-Specific Career Analysis")
                
                # Role selection
                available_roles = [
                    "Data Scientist", 
                    "Software Engineer", 
                    "Data Analyst", 
                    "Machine Learning Engineer",
                    "Web Developer",
                    "DevOps Engineer"
                ]
                
                selected_role = st.selectbox(
                    "Choose a role to analyze your resume against:",
                    available_roles
                )
                
                if selected_role:
                    with st.spinner(f"🔍 Analyzing your resume for {selected_role} role..."):
                        role_analysis = analyze_for_specific_role(text, selected_role)
                        
                        if role_analysis:
                            display_role_specific_analysis(role_analysis, selected_role)
                            
                            # Additional: Compare with other roles
                            st.markdown("---")
                            st.subheader("📈 Compare With Other Roles")
                            
                            compare_roles = st.multiselect(
                                "Select additional roles to compare:",
                                [role for role in available_roles if role != selected_role],
                                max_selections=2
                            )
                            
                            if compare_roles:
                                comparison_data = []
                                all_roles = [selected_role] + compare_roles
                                
                                for role in all_roles:
                                    analysis = analyze_for_specific_role(text, role)
                                    if analysis:
                                        comparison_data.append({
                                            'role': role,
                                            'score': analysis['overall_score']
                                        })
                                
                                # Display comparison
                                st.write("**Role Comparison Scores:**")
                                for data in comparison_data:
                                    col1, col2 = st.columns([3, 1])
                                    with col1:
                                        st.write(data['role'])
                                    with col2:
                                        st.write(f"{data['score']:.1f}%")
                                    st.progress(data['score'] / 100)
            
            # Rest of your existing code (keywords, search, preview)...
            # ... [Keep all your existing code for keywords, search, preview sections] ...

# Run the app
if __name__ == "__main__":
    main()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>📊 <b>Document Analyzer</b> - Analyze Research Papers & Resumes</p>
    <p>Upload any document to extract keywords, search content, and gain insights</p>
</div>
""", unsafe_allow_html=True)
