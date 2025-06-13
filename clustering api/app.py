import streamlit as st
import tempfile
import os
from typing import List, Dict

# Import your functions
from clusterdata import transcript, summarize_with_perplexity, ClusterData

# Configure page
st.set_page_config(
    page_title="🧠 Socrates: Lecture Notes RAG System",
    page_icon="🧠",
    layout="wide"
)

# Initialize session state FIRST - before any other Streamlit commands
if "processed_data" not in st.session_state:
    st.session_state.processed_data = None
if "processing_complete" not in st.session_state:
    st.session_state.processing_complete = False

# NOW you can use the rest of your code
st.title("🧠 Socrates: Lecture Notes RAG System")
st.markdown("*Transform your lectures into intelligent, searchable knowledge*")

# Initialize cluster processor
@st.cache_resource
def load_cluster_processor():
    return ClusterData()

cluster_processor = load_cluster_processor()

# Rest of your code remains exactly the same...
# File upload section
st.header("📁 Upload Lecture Audio")
uploaded_file = st.file_uploader(
    "Choose an audio file",
    type=['mp3', 'wav', 'ogg', 'm4a', 'flac'],
    help="Upload your lecture recording in any common audio format"
)

# Processing section
if uploaded_file is not None:
    # Display file info
    st.success(f"✅ Uploaded: {uploaded_file.name} ({uploaded_file.size / 1024 / 1024:.2f} MB)")
    
    # Audio player
    st.audio(uploaded_file, format=f"audio/{uploaded_file.name.split('.')[-1]}")
    
    # Process button
    if st.button("🚀 Process Lecture", type="primary"):
        with st.spinner("🔄 Processing your lecture... This may take a few minutes"):
            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    temp_file_path = tmp_file.name
                
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Step 1: Transcription
                status_text.text("🎤 Transcribing audio with Deepgram...")
                progress_bar.progress(20)
                transcript_result = transcript(temp_file_path)
                
                if not transcript_result:
                    st.error("❌ Failed to transcribe audio. Please check your Deepgram API key.")
                    os.unlink(temp_file_path)
                    st.stop()
                
                # Step 2: Convert to sentences for clustering
                status_text.text("📝 Processing transcript...")
                progress_bar.progress(35)
                sentences = transcript_result.split('. ')
                
                # Step 3: Get embeddings and clustering
                status_text.text("🧩 Creating embeddings...")
                progress_bar.progress(50)
                sentences, reduced_embeddings = cluster_processor.get_reduced_embeddings(sentences)
                
                status_text.text("🔍 Clustering topics...")
                progress_bar.progress(65)
                cluster_data = cluster_processor.get_clusters(sentences, reduced_embeddings)
                
                # Step 4: Summarize clusters
                status_text.text("📋 Summarizing clusters...")
                progress_bar.progress(80)
                cluster_summaries = cluster_processor.summarize_clusters(cluster_data)
                
                # Step 5: Overall summary
                status_text.text("📄 Creating overall summary...")
                progress_bar.progress(90)
                overall_summary = summarize_with_perplexity(transcript_result)
                
                # Complete
                progress_bar.progress(100)
                status_text.text("✅ Processing complete!")
                
                # Store results in session state
                st.session_state.processed_data = {
                    "transcript": transcript_result,
                    "clusters": cluster_data,
                    "cluster_summaries": cluster_summaries,
                    "overall_summary": overall_summary,
                    "sentences": sentences
                }
                st.session_state.processing_complete = True
                
                # Clean up temp file
                os.unlink(temp_file_path)
                
                st.success("🎉 Processing completed successfully!")
                
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
                if 'temp_file_path' in locals():
                    try:
                        os.unlink(temp_file_path)
                    except:
                        pass

# Display results
if st.session_state.processing_complete and st.session_state.processed_data:
    st.header("📊 Processing Results")
    
    # Create tabs for different outputs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Transcript", "🧩 Topic Clusters", "📋 Cluster Summaries", "📄 Overall Summary"])
    
    with tab1:
        st.subheader("Full Transcript")
        transcript_text = st.session_state.processed_data["transcript"]
        
        # Display transcript in expandable text area
        st.text_area(
            "Transcribed Text",
            value=transcript_text,
            height=400,
            disabled=True
        )
        
        # Stats
        word_count = len(transcript_text.split())
        sentence_count = len(st.session_state.processed_data["sentences"])
        st.metric("Word Count", word_count)
        st.metric("Sentence Count", sentence_count)
        
        # Download button for transcript
        st.download_button(
            label="📥 Download Transcript",
            data=transcript_text,
            file_name="lecture_transcript.txt",
            mime="text/plain"
        )
    
    with tab2:
        st.subheader("Topic Clusters")
        clusters = st.session_state.processed_data["clusters"]
        
        if clusters:
            st.info(f"Found {len(clusters)} topic clusters in your lecture")
            
            for i, cluster_text in enumerate(clusters):
                with st.expander(f"📌 Cluster {i+1}", expanded=False):
                    st.write(cluster_text)
                    st.caption(f"Length: {len(cluster_text.split())} words")
        else:
            st.warning("No clusters were generated. Try with a longer audio file.")
        
        # Download button for clusters
        if clusters:
            clusters_text = "\n\n".join([f"CLUSTER {i+1}:\n{cluster}" for i, cluster in enumerate(clusters)])
            st.download_button(
                label="📥 Download Clusters",
                data=clusters_text,
                file_name="lecture_clusters.txt",
                mime="text/plain"
            )
    
    with tab3:
        st.subheader("Cluster Summaries")
        cluster_summaries = st.session_state.processed_data["cluster_summaries"]
        
        if cluster_summaries:
            for i, summary in enumerate(cluster_summaries):
                with st.container():
                    st.markdown(f"**📌 Topic {i+1} Summary:**")
                    st.info(summary)
                    st.divider()
        else:
            st.warning("No cluster summaries available.")
        
        # Download button for summaries
        if cluster_summaries:
            summaries_text = "\n\n".join([f"TOPIC {i+1} SUMMARY:\n{summary}" for i, summary in enumerate(cluster_summaries)])
            st.download_button(
                label="📥 Download Summaries",
                data=summaries_text,
                file_name="cluster_summaries.txt",
                mime="text/plain"
            )
    
    with tab4:
        st.subheader("Overall Lecture Summary")
        overall_summary = st.session_state.processed_data["overall_summary"]
        
        if overall_summary:
            st.success("📄 Complete Lecture Summary")
            st.markdown(overall_summary)
        else:
            st.warning("Overall summary not available.")
        
        # Download button for overall summary
        if overall_summary:
            st.download_button(
                label="📥 Download Overall Summary",
                data=overall_summary,
                file_name="lecture_overall_summary.txt",
                mime="text/plain"
            )

# Sidebar with app info and controls
with st.sidebar:
    st.header("ℹ️ About Socrates")
    st.markdown("""
    **Socrates** transforms your lecture recordings into:
    - 📝 **Accurate transcripts** using Deepgram
    - 🧩 **Topic clusters** using HDBSCAN
    - 📋 **Intelligent summaries** using Perplexity AI
    
    Simply upload your audio and let AI do the work!
    """)
    
    # API Status
    st.header("🔧 API Status")
    deepgram_key = os.environ.get('DEEPGRAM_API_KEY')
    if deepgram_key:
        st.success("✅ Deepgram API Key loaded")
    else:
        st.error("❌ Deepgram API Key missing")
    
    if st.session_state.processing_complete:
        st.success("✅ Lecture processed successfully!")
        if st.button("🔄 Process New Lecture"):
            st.session_state.processed_data = None
            st.session_state.processing_complete = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("*Built with ❤️ using Streamlit*")
    
    # Technical details
    with st.expander("🔧 Technical Details"):
        st.markdown("""
        - **Transcription**: Deepgram Nova-2 model
        - **Embeddings**: GTE-Small sentence transformer
        - **Clustering**: HDBSCAN with UMAP dimensionality reduction
        - **Summarization**: Perplexity AI Sonar-Pro model
        """)

# Footer
st.markdown("---")
st.markdown("**Note**: Make sure your `.env` file contains your `DEEPGRAM_API_KEY` for transcription to work.")
