import streamlit as st
import openai
import pandas as pd
import os
import time
from kaggle.api.kaggle_api_extended import KaggleApi
from googlesearch import search

# --- Set Up OpenAI API Key Securely ---
openai.api_key = "use your own api here"
if not openai.api_key:
    st.warning("⚠️ OpenAI API key not found. Please set the API key as an environment variable.")

# --- Streamlit UI ---
st.title("🚀 AI & GenAI Use Case Research")

# User Inputs
company_name = st.text_input("Enter Company Name", "Infosys")
industry_name = st.text_input("Enter Industry Name", "IT")

if st.button("Generate AI Research Report"):
    st.write("🔍 Researching AI trends and company insights...")

    # --- Agent 1: Web Search for Industry & Company Trends ---
    def search_web(query, num_results=3):
        """Perform Google search and return a list of result links."""
        results = []
        try:
            for result in search(query, num_results=num_results):
                results.append(result)
                time.sleep(1)  # Avoid hitting rate limits
        except Exception as e:
            st.warning(f"⚠️ Web search failed: {e}")
        return results

    # Generate search queries
    industry_query = f"AI trends in {company_name} {industry_name} site:forbes.com OR site:venturebeat.com OR site:{company_name.lower()}.com"
    company_query = f"{company_name} AI strategy site:{company_name.lower()}.com OR site:businessinsider.com"

    # Perform web search
    industry_trends = search_web(industry_query)
    company_focus = search_web(company_query)

    st.success("✅ Industry & Company Research Complete!")

    # --- Agent 2: Generate AI Use Cases with OpenAI ---
    st.write("🧠 Generating AI Use Cases...")
    prompt = (
        f"Based on the latest AI trends in {industry_name} and the business focus of {company_name}, "
        "suggest top AI and Generative AI use cases that can improve operations, customer experience, and efficiency. "
        "Provide a concise list."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        use_cases = response['choices'][0]['message']['content'].strip().split("\n")
    except Exception as e:
        st.warning(f"⚠️ OpenAI API call failed: {e}")
        use_cases = []

    if not use_cases:
        st.warning("⚠️ No AI use cases generated. Check OpenAI API key or response.")
        use_cases = ["N/A"]

    st.success("✅ Use Cases Generated!")

    # --- Agent 3: Collect AI Dataset Resources from Kaggle ---
    st.write("📊 Searching for relevant AI datasets on Kaggle...")

    # Initialize Kaggle API
    try:
        api = KaggleApi()
        api.authenticate()
    except Exception as e:
        st.warning(f"⚠️ Kaggle authentication failed: {e}")
        api = None

    datasets = []

    if api:
        for use_case in use_cases:
            if use_case.strip() != "N/A":
                query = " ".join(use_case.split()[:3])  # Extract first 3 words for better search
                try:
                    kaggle_results = api.dataset_list(search=query, sort_by="votes")
                    dataset_links = [f"https://www.kaggle.com/datasets/{dataset.ref}" for dataset in kaggle_results[:3]]
                    datasets.append(", ".join(dataset_links) if dataset_links else "No dataset found")
                except Exception:
                    datasets.append("No dataset found")
            else:
                datasets.append("N/A")  # Keep alignment

    st.success("✅ Dataset Collection Complete!")

    # --- Create Final Data Structure ---
    use_cases_data = {
        "Use Cases": [uc.split(":")[0] if ":" in uc else uc for uc in use_cases],  
        "Description": use_cases,  
        "Reference": datasets
    }

    # --- Generate Excel Report ---
    st.write("📄 Generating Final Report in Excel Format...")

    use_cases_df = pd.DataFrame(use_cases_data)
    industry_trends_df = pd.DataFrame(industry_trends, columns=["Industry Trends Links"])
    company_focus_df = pd.DataFrame(company_focus, columns=["Company Focus Area Links"])

    output_file_path = f"AI_Use_Case_Report_{company_name}.xlsx"
    with pd.ExcelWriter(output_file_path, engine="xlsxwriter") as writer:
        use_cases_df.to_excel(writer, sheet_name="Use Cases Feasibility Check", index=False)
        industry_trends_df.to_excel(writer, sheet_name="References of Articles_Resource", index=False)
        company_focus_df.to_excel(writer, sheet_name="Company Focus Areas", index=False)

    st.success(f"✅ Report Generated: {output_file_path}")

    # Provide Download Button
    with open(output_file_path, "rb") as file:
        st.download_button(label="📥 Download AI Research Report", data=file, file_name=output_file_path)

    st.success("🎯 AI Research Process Complete!")
