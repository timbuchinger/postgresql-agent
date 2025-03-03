import streamlit as st

from agent import PostgreSQLAgent


# Initialize the PostgreSQL Agent (will be reused for all queries)
@st.cache_resource
def get_agent():
    return PostgreSQLAgent()

def main():
    st.title("PostgreSQL Query Assistant")

    # Initialize agent in session state if not already present
    if 'agent' not in st.session_state:
        with st.spinner("Initializing agent..."):
            st.session_state.agent = get_agent()

    # User input section
    st.markdown("""
    ### Ask a question about your database
    Examples:
    - "Show me the schema of the users table"
    - "How many orders were placed in the last week?"
    - "What are the top 5 products by revenue?"
    """)

    # Create a text input for the user's question
    question = st.text_area("Enter your question:", height=100, max_chars=500)

    # Add a button to submit the question
    if st.button("Get Answer"):
        if not question:
            st.error("Please enter a question.")
        else:
            try:
                with st.spinner("Processing your question..."):
                    # Get response from agent
                    response = st.session_state.agent.query_database(question)

                    # Display the response
                    st.markdown("### Answer")
                    st.write(response)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
