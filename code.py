# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 19:22:24 2025

@author: HP
"""

import os
import openai
import requests
import markdownify
from googlesearch import search
from bs4 import BeautifulSoup
import json
import time
from kaggle.api.kaggle_api_extended import KaggleApi
import pandas as pd
import xlsxwriter


# Set API Keys
openai.api_key = "use your own api here"

# Multi-Agent System Class
class MultiAgentAIResearch:
    def __init__(self, company_name, industry_name):
        self.company_name = company_name
        self.industry_name = industry_name
        self.research_data = {}
        self.use_cases = []
        self.datasets = []
        self.references = []
        self.final_report = ""

    # Agent 1: Research the Industry and Company using Web Search
    def research_industry_and_company(self):
        print(f"🔍 Researching AI trends in {self.company_name}...")
    
        # Search for AI trends at the company instead of the industry
        industry_query = (
            f"AI trends, machine learning, generative AI, automation at {self.company_name} "
            f"site:{self.company_name.lower()}.com OR site:forbes.com OR site.businessinsider.com OR site.venturebeat.com"
        )
    
        company_query = (
            f"{self.company_name} AI strategy, AI adoption, automation, digital transformation "
            f"site:{self.company_name.lower()}.com OR site:forbes.com OR site.businessinsider.com"
        )
    
        # Perform searches
        industry_trends = self.search_web(industry_query)
        company_focus = self.search_web(company_query)
    
        # Save the research data
        self.research_data = {
            "industry_trends": industry_trends,  # Now company-focused!
            "company_focus": company_focus,
        }
        print("✅ AI Research for Company Complete!\n")


    # Web search function
    def search_web(self, query, num_results=3):
        print(f"🔍 Searching: {query}")
        results = []
        try:
            for result in search(query, num_results=num_results):
                results.append(result)
                time.sleep(1)  # Prevent hitting rate limits
        except Exception as e:
            print(f"⚠️ Web search failed: {e}")
        return results

    # Agent 2: Generate AI & GenAI Use Cases
    def generate_use_cases(self):
        print("🧠 Generating AI Use Cases...")
        prompt = (
            f"Based on the latest AI trends in {self.industry_name} and the business focus of {self.company_name}, "
            "suggest top AI and Generative AI use cases that can improve operations, customer experience, and efficiency. "
            "Provide a concise list."
        )
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        self.use_cases = response['choices'][0]['message']['content'].strip().split("\n")
        print("✅ Use Cases Generated!\n")

    # Agent 3: Collect AI Dataset Resources
    def collect_datasets(self):
        print("📊 Searching for relevant AI datasets on Kaggle...")
    
        # Authenticate Kaggle API
        api = KaggleApi()
        api.authenticate()
    
        for use_case in self.use_cases:
            # Extract relevant keywords (first 3 words) to improve search accuracy
            query = " ".join(use_case.split()[:3])  
    
            print(f"🔎 Searching Kaggle datasets for: {query}...")
    
            try:
                # Search Kaggle datasets using only relevant keywords
                datasets = api.dataset_list(search=query, sort_by="votes")
    
                if not datasets:
                    print(f"⚠️ No datasets found for '{query}'. Trying a broader search...")
    
                    # Try searching for general AI datasets as a fallback
                    datasets = api.dataset_list(search="AI dataset", sort_by="votes")
    
                for dataset in datasets[:3]:  # Only take top 3 results
                    dataset_url = f"https://www.kaggle.com/datasets/{dataset.ref}"
                    self.datasets.append(dataset_url)
                    print(f"✅ Found: {dataset.title} - {dataset_url}")
    
            except Exception as e:
                print(f"⚠️ Kaggle API error for '{query}': {e}")
    
        print("✅ Dataset Collection Complete!\n")

    # Agent 4: Generate Final Report



    def generate_final_report(self):
        print("📄 Generating Final Report in Excel Format...")
    
        # Prepare "Use Cases Feasibility Check" sheet
        use_cases_data = {
            "Use Cases": [],
            "Description": [],
            "Reference": []
        }
    
        for use_case in self.use_cases:
            use_cases_data["Use Cases"].append(use_case.split(":")[0])  # Extract title before ":"
            use_cases_data["Description"].append(use_case)  # Full description
            use_cases_data["Reference"].append(self.datasets.pop(0) if self.datasets else "")  # Kaggle dataset link
    
        use_cases_df = pd.DataFrame(use_cases_data)
    
        # Prepare "References of Articles_Resource" sheet (Industry Trends)
        industry_trends_df = pd.DataFrame(self.research_data["industry_trends"], columns=["Industry Trends Links"])
    
        # Prepare "Company Focus Areas" sheet
        company_focus_df = pd.DataFrame(self.research_data["company_focus"], columns=["Company Focus Area Links"])
    
        # Save to Excel file
        output_file_path = f"AI_Use_Case_Report_{self.company_name}.xlsx"
        with pd.ExcelWriter(output_file_path, engine="xlsxwriter") as writer:
            use_cases_df.to_excel(writer, sheet_name="Use Cases Feasibility Check", index=False)
            industry_trends_df.to_excel(writer, sheet_name="References of Articles_Resource", index=False)
            company_focus_df.to_excel(writer, sheet_name="Company Focus Areas", index=False)
    
        print(f"✅ Report saved as {output_file_path} 🎯\n")



# Run the system
if __name__ == "__main__":
    company_name = input("Enter the company name: ")
    industry_name = input("Enter the industry name: ")
    
    system = MultiAgentAIResearch(company_name, industry_name)
    system.research_industry_and_company()
    system.generate_use_cases()
    system.collect_datasets()
    system.generate_final_report()

    print("🎯 AI Research Process Complete!")
