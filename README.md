# 🥗 Diet Advisor AI Chatbot

A personalized **AI-powered diet advisor chatbot** that provides users with tailored diet recommendations and meal plans. Built with a modern AI stack using **LangChain**, **LangGraph**, **Gemini LLM**, and **Next.js + FastAPI**.

---

## 📌 Overview

This chatbot leverages state-of-the-art AI to guide users in making healthier diet choices. It analyzes user inputs, retrieves relevant nutritional context, intelligently routes queries through specialized tools, and returns custom meal plans or advice—all in real time.

---

## 🧠 Tech Stack

| Layer               | Technology                  |
|--------------------|-----------------------------|
| **Programming Language** | Python             |
| **LLM & Embeddings** | Gemini (Google)             |
| **Memory & Vector Store** | Pinecone                   |
| **Agent Framework** | LangChain + LangGraph       |
| **Frontend**        | Next.js                     |
| **Backend API**     | FastAPI                     |

---

## 🔁 LangGraph Workflow

The AI agent is powered by a **LangGraph-based workflow** with the following structure:


### 1. **Context Retrieval**
- Fetches relevant prior conversation context or nutritional data from **Pinecone** using embeddings powered by **Gemini**.

### 2. **LLM**
- Gemini LLM interprets the user query and identifies intent.

### 3. **Tool Router**
- Dynamically routes the request to the appropriate **LangChain tool**, such as:
  - `diet_recommendations` — generates daily diet advice.
  - `recipe_fetcher` — fetches recipes using external APIs like TheMealDB.
  - `nut_content_fetcher` — retrieves nutritional information for food items.

### 4. **Pinecone Storage**
- Logs interactions, context, and tool outputs in vector format for future retrieval.

### 5. **Response Formatter**
- Cleans and structures the final AI response for display in the frontend chat UI.

---

## 🌐 Frontend

- Built with **Next.js**.
- Real-time chat interface connected to the backend.
- Optimized for responsiveness and smooth user experience.

---

## 🚀 Backend

- Developed using **FastAPI**.
- Handles:
  - User profile submissions.
  - Chat interactions and routing to LangGraph.
  - Communication with Pinecone and external APIs.

---

## 🛠️ Key Features

- 🔄 **Context-Aware Conversations**  
- 🍽️ **Personalized Meal Plans**  
- 📋 **Nutrition-Focused Advice**  
- 🌱 **Tool-Based Modular Architecture**  
- 💾 **Long-Term Memory with Pinecone**  
- ✨ **Clean and Expandable Codebase**

---

## 🔧 Future Enhancements

- Add loading states and improved chat UX in frontend.
- Support for multi-turn conversations and health goal tracking.
- Integration with wearable health devices and calendars.

---

## 📁 Project Structure

```bash
/
├── backend/
│   ├── main.py             # FastAPI server
│   ├── nodes/
│   ├── tools/
│   ├── config.py
│   ├── state.py
│   ├── workflow.py    # LangGraph workflow & tools
├── frontend/
│   └── nextjs-app/         # React + Next.js chat interface
└── README.md               # You're here!

