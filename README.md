# RAG-Chat-Doc

## Local Setup:
### Backend Setup:

1. **Install Dependencies:**
   - Navigate to the root directory of the project.
   - Run the following command to install backend dependencies:
     ```
     pip install -r requirements.txt
     ```

2. **Setup Google Cloud Credentials:**
   - Install Gcloud SDK if not already installed.
   - Run the following command to authenticate with Google Cloud:
     ```
     gcloud auth application-default login
     ``` 
    And update the bucket name inside file cloud_storage_client.py

3. **Setup OpenAI Credentials:**
   - create a .env file inside root directory with the key in this format:
     ```
     OPENAI_API_KEY={your-api-key}
     ``` 
    And update the bucket name inside file cloud_storage_client.py

4. **Run the Backend:**
   - After installing dependencies and setting up Google Cloud credentials, run the backend with:
     ```
     python main.py
     ```

### Frontend Setup:

1. **Navigate to the Frontend Directory:**
   - Change directory to the React frontend:
     ```
     cd react-frontend
     ```

2. **Install Dependencies and Start the Development Server:**
   - Run the following commands sequentially to install frontend dependencies and start the development server:
     ```
     npm install
     npm start
     ```

Once both the backend and frontend are set up, you should be able to access the application locally.

## Screenshots:

![Screenshot 2024-04-20 010644](https://github.com/Adishar93/RAG-Chat-Doc/assets/39119745/4cca4520-b48c-425d-9302-5a23687c8421)
![Screenshot 2024-04-20 010842](https://github.com/Adishar93/RAG-Chat-Doc/assets/39119745/b72a9461-ab50-462a-8499-fe0d84cfa099)
![image](https://github.com/user-attachments/assets/d80dcd8e-2ad0-4a4e-8761-f560f992964a)


## Architecture and Technologies Used:

### Frontend:
The frontend of this project is built using React. It consists of two main pages:
- **Upload Content Page:** Allows users to upload PDF files or to provide Youtube Links.
- **Ask Questions Page:** Enables users to ask questions about the uploaded PDFs.

### Backend:
The backend is powered by Flask, a lightweight Python web framework. It provides three POST endpoints:
- **Upload PDFs Endpoint:** Handles the uploading of PDF files.
- **Process Youtube Link Endpoint:** Processes youtube video and stores transcript as vectors.
- **Ask Questions Endpoint:** Accepts questions from users and provides relevant answers from the processed and stored data (PDF or Video).

The backend codebase is organized into different modules based on their roles:
- **utility.py:** Contains utility functions used across the project.
- **rag.py:** Implements the Retrieval-Augmented Generation (RAG) logic.
- **cloud_storage_client.py:** Provides functionalities to interact with Google Cloud Storage.

The backend leverages the LangChain framework with OpenAI's GPT-3.5 for natural language processing tasks. PDF data is vectorized, and a similarity function is applied to efficiently retrieve information from PDFs when users ask questions. This approach reduces the number of tokens required for processing by the language model.

### Deployment:
Both the frontend and backend are deployed on separate App Engine instances. To maintain persistent vector indexes and optimize performance, Google Cloud Storage is utilized. This eliminates the need to recompute vector indices each time questions are asked about the same PDFs, ensuring efficient and reliable operation.

## Limitations & Challenges Encountered:
- While performing similarity search on a large pdf, there can be high memory usage as observed with lower tiered AppEngine instances that have low RAM.
- Since the AppEngine instances can go down to 0 after a period of inactivity, sending request at this time increases latency of first request by a lot and may lead to 502 bad gateway
- To save on recomputation of vector indices, I store them in Google Cloud storage, and retrieve them each time a question is asked about the PDF. Thus if a new instance comes up, the indices still remain saved and reusable, as the data is not stored in RAM which may get wiped out.
- Encountered an issue with ChromaDB where the data from each uploaded PDF file gets combined. Switched to FAISS.
- Prompt engineering, initially because of bad prompt was not always getting expected results. After lot of tuning, it has improved the responses.

## Assumptions:
- History of questions is not maintained when asking multiple questions on a single PDF.

## Demo Video:




https://github.com/Adishar93/RAG-Chat-Doc/assets/39119745/1e595f0a-1a87-4564-8d4c-a294fdd3a415







