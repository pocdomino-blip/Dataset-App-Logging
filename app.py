import streamlit as st
import os
from pathlib import Path
from domino_data.datasets import DatasetClient, DatasetConfig

# Set page config
st.set_page_config(
    page_title="Domino Dataset Explorer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Domino Dataset Explorer")
st.markdown("Test the new Domino dataset as a datasource feature by exploring dataset contents.")

# Create input section
st.header("Dataset Configuration")

col1, col2 = st.columns([2, 1])

with col1:
    dataset_id = st.text_input(
        "Dataset ID",
        placeholder="Enter full dataset ID (e.g., dataset-dataset_app-68a615244aa567002f494c75)",
        help="Enter the complete dataset ID including the prefix and hash"
    )

with col2:
    snapshot_id = st.text_input(
        "Snapshot ID (Optional)",
        placeholder="Enter snapshot ID",
        help="Leave empty to use the read/write snapshot"
    )

# Show the dataset ID that will be used
if dataset_id:
    st.info(f"Dataset ID: `{dataset_id}`")

# Add explore button
if st.button("🔍 Explore Dataset", type="primary", disabled=not dataset_id):
    if dataset_id:
        # Add debug section
        st.header("🔍 Debug Information")
        debug_expander = st.expander("Click to view debug details", expanded=False)
        
        with debug_expander:
            # Show all available headers
            st.subheader("Request Headers:")
            try:
                headers = dict(st.context.headers)
                for key, value in headers.items():
                    if key.lower() == 'authorization':
                        # Show partial token for security
                        if len(value) > 20:
                            masked_value = value[:10] + "..." + value[-10:]
                        else:
                            masked_value = value[:5] + "..."
                        st.code(f"{key}: {masked_value}")
                    else:
                        st.code(f"{key}: {value}")
            except Exception as e:
                st.error(f"Could not access headers: {e}")
            
            st.subheader("Dataset Information:")
            st.code(f"Dataset ID: {dataset_id}")
            if snapshot_id:
                st.code(f"Snapshot ID: {snapshot_id}")
        
        try:
            with st.spinner("Connecting to dataset..."):
                # Get authorization token from request headers (following the example)
                # Handle case where request might not be available in some contexts
                try:
                    auth_header = st.context.headers.get('Authorization', '')
                except:
                    # Fallback for testing environments
                    auth_header = ''
                
                with debug_expander:
                    st.subheader("Token Processing:")
                    if auth_header:
                        st.success(f"✅ Authorization header found (length: {len(auth_header)})")
                        if auth_header.startswith('Bearer '):
                            st.success("✅ Header has 'Bearer ' prefix")
                            auth_token = auth_header[7:]  # Remove 'Bearer ' prefix
                            st.success(f"✅ Extracted token (length: {len(auth_token)})")
                        else:
                            st.warning("⚠️ Header doesn't start with 'Bearer ', using full header as token")
                            auth_token = auth_header
                        
                        # Show first and last few characters for debugging
                        if len(auth_token) > 20:
                            token_preview = auth_token[:10] + "..." + auth_token[-10:]
                        else:
                            token_preview = auth_token[:5] + "..."
                        st.code(f"Token preview: {token_preview}")
                    else:
                        st.error("❌ No Authorization header found")
                        auth_token = None
                
                if not auth_token:
                    st.error("❌ Authorization token not found in request headers.")
                    st.info("💡 Make sure you're running this in a Domino environment where the token is automatically provided.")
                else:
                    with debug_expander:
                        st.subheader("Client Initialization:")
                        st.info("Initializing DatasetClient...")
                    
                    # Initialize the dataset client (following your working example)
                    client = DatasetClient(token=auth_token)
                    
                    with debug_expander:
                        st.success("✅ DatasetClient initialized")
                        st.info(f"Attempting to get dataset: '{dataset_id}'")
                    
                    dataset = client.get_dataset(dataset_id)
                    
                    with debug_expander:
                        st.success(f"✅ Dataset '{dataset_id}' retrieved successfully")
                    
                    # Update with specific snapshot if provided
                    if snapshot_id:
                        dataset.update(config=DatasetConfig(snapshot_id=snapshot_id))
                        st.success(f"✅ Connected to dataset '{dataset_id}' with snapshot '{snapshot_id}'")
                    else:
                        st.success(f"✅ Connected to dataset '{dataset_id}' (using read/write snapshot)")
                    
                    # List files in the dataset
                    st.header("📁 Dataset Contents")
                    
                    with st.spinner("Loading files..."):
                        try:
                            files = dataset.list_files()
                            
                            with debug_expander:
                                st.subheader("Raw Files Response:")
                                st.code(f"Type: {type(files)}")
                                st.code(f"Length: {len(files) if hasattr(files, '__len__') else 'N/A'}")
                                if files:
                                    st.code(f"First item type: {type(files[0]) if len(files) > 0 else 'N/A'}")
                                    st.code(f"First few items: {str(files[:3]) if len(files) > 0 else 'Empty'}")
                        
                        except Exception as list_error:
                            st.error(f"❌ Error listing files: {str(list_error)}")
                            with debug_expander:
                                st.subheader("List Files Error:")
                                st.code(str(list_error))
                            files = None
                    
                    if files:
                        st.success(f"Found {len(files)} files in the dataset")
                        
                        # Simple file display - just show the raw file objects/paths
                        st.subheader("📋 Files Found:")
                        
                        # Try to display files in a simple way first
                        try:
                            for i, file_item in enumerate(files):
                                # Handle different possible file object types
                                if hasattr(file_item, 'name'):
                                    file_display = file_item.name
                                elif hasattr(file_item, 'path'):
                                    file_display = file_item.path
                                elif isinstance(file_item, str):
                                    file_display = file_item
                                else:
                                    file_display = str(file_item)
                                
                                st.write(f"{i+1}. {file_display}")
                                
                                # Show debug info for first few files
                                if i < 3:
                                    with debug_expander:
                                        st.write(f"File {i+1} debug:")
                                        st.code(f"Type: {type(file_item)}")
                                        st.code(f"Dir: {dir(file_item)}")
                                        st.code(f"Str representation: {str(file_item)}")
                        
                        except Exception as display_error:
                            st.error(f"❌ Error displaying files: {str(display_error)}")
                            with debug_expander:
                                st.subheader("Display Error:")
                                st.code(str(display_error))
                            
                            # Fallback: just show raw objects
                            st.write("Raw file objects:")
                            for i, file_item in enumerate(files):
                                st.write(f"{i+1}. {repr(file_item)}")
                    
                    else:
                        st.info("📭 No files found in this dataset")
                    
        except Exception as e:
            st.error(f"❌ Error connecting to dataset: {str(e)}")
            st.info("💡 Make sure you're running this in a Domino environment with proper authentication")

# Add some helpful information
st.sidebar.header("ℹ️ About")
st.sidebar.markdown("""
This app demonstrates the Domino dataset as datasource feature.

**How to use:**
1. Enter your full dataset ID (format: dataset-name-hash)
2. Optionally specify a snapshot ID
3. Click "Explore Dataset" to list files
4. Use the tabs to view files in different formats
5. Download or preview individual files

**Dataset ID Format:**
Use the complete dataset ID like: `dataset-dataset_app-68a615244aa567002f494c75`

**Note:** This requires running in a Domino environment with proper authentication headers.
""")

# Footer
st.markdown("---")
st.markdown("*Built for testing Domino's dataset as datasource feature*")