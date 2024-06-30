# AI Assistant for patients with Chronic Kidney Disease

## Part of the AI Camp Hackathon of Jun 29, 2024!

### Backend

Runs on a FastAPI backend, with langchain and pinecone for integrating the LLM functionality.
The data is taken from [here](https://www.asn-online.org/education/training/fellows/HFHS_CKD_V6.pdf)
Medical records of the particular patient is also added in the database.

To run `uvicorn main:server --reload`

### Frontend

Next.js, with simple Tailwind CSS for UI. To run `npm run dev`
