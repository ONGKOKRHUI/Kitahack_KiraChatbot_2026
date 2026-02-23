Authentication - firebase authentication - user login allows multiple email options
Profile page: fill in company information
On login load user history information for rendering dashboard
Scan Tab: User upload invoice via: Camera OR PDF 
Camera: endpoint:  /camera/backend
Store in firebase storage and link in firebase datastore
Call Gemini function for doing OCR
Creates a JSON of the OCR results:
JSON key value:
Vendor name: 
…
JSON formatting and store at firebase
Docs: Invoice, receipt, bill (PDF)
Pdf reader python library
Pass Gemini function to produce JSON
JSON key value:
Vendor name: 
…
JSON formatting and store at firebase
A single cell for user to enter transport distance to facilitate scope 3 emission calculation - (will change to calling Google Maps API)
Home Dashboard:
On user login render by loading information from firebase (JSON from above)
Key metrics display
Filter by day, week, month, year
KIV: BigQuery cross user comparison display on dashboard
User upload receipt
Firebase Document Organization
Collection:
Users database
Company information
Admin and employee accounts
Emissions database
Scope 1, 2, 3 emissions
Generated reports url
Uploaded documents
Formula database
GITA database
Scope 1, 2, 3 factor data





Chatbot
Opening statement: Hi [User Name], I’m Kira! I can help you lower your carbon tax and find hidden tax savings. What would you like to do?
Tool 1: [ 🔎 Find a green supplier ]
Tool 2: [ Calculate ROI of using GITA alternatives ]
Tool 4: [ 📊 Compare me to my competitors ] (KIV)
Selection questions: 
Did I miss any GITA tax incentives in my receipts from last month?
Find me a GITA-compliant supplier for [LED lights/Solar/Packaging] in [Location].
Calculate if installing solar panels is worth it for my business.
How does my carbon footprint compare to other businesses in my industry? (KIV)
Specific invoice selection feature (KIV)
Allows users to select a document uploaded via a dropdown menu and ask questions about it - doc is attached to chat prompt
Sample Question: How to reduce carbon emission for this option?
Details about the specific invoice
allows the user to select a specific invoice they uploaded from a dropdown, and that invoice will be attached  to the chat. The user is then able to ask questions related to that invoice detail
Tool 1 : SEARCH_MYHIJAU_DIRECTORY
Purpose: Find compliant vendors- find alternatives for an invoice (KIV)
Logic: Takes product name and location, then searches the mock MyHijau directory (Vector Search) for GITA-eligible vendors.
Sample questions:  "I need to replace our warehouse lights. Who sells compliant LED lights in Selangor?" or "Find me a green packaging supplier."
Tool 2: TOOL_SIMULATE_INVESTMENT
Purpose: Calculates the estimated Return on Investment (ROI) for specific green upgrades by factoring in GITA tax incentives and energy savings.
Logic:
Input Analysis: Takes the user's query (e.g., "solar panels") and retrieves average market cost and energy saving parameters for Malaysia from the system knowledge base (or Gemini knowledge).
Incentive Retrieval: Checks the MyHijau Vector Store to confirm the asset's GITA eligibility (e.g., 100% Investment Tax Allowance).
Calculation: Uses a pre-set formula: (Initial Cost - Tax Rebate) / (Monthly Energy Savings) to determine the payback period.
Output: Returns a financial summary (e.g., "Break-even in 3.5 years with RM15,000 tax savings").
Tool 3: SIMULATE_TAX_IMPACT
Purpose: Provides a "Health Check" by estimating the user's potential Carbon Tax liability based on their current invoice data.
Logic:
Data Aggregation: Queries Firestore to sum up the total carbon footprint (kgCO2e) extracted from the user's uploaded utility and fuel invoices for the current financial year.
Rate Application: Applies the projected Malaysian Carbon Tax rate (e.g., RM value per tonne) to the total emissions.
Output: Displays the total estimated tax bill and a "risk level" (Low/Medium/High).

Tool 4: GET_INDUSTRY_BENCHMARK
Purpose: Benchmarks the user's carbon intensity against anonymized averages of other businesses in the same sector (e.g., Manufacturing, F&B).
Logic:
Sector Identification: Retrieves the user's industry tag from their profile in Firestore.
Comparison Query: Queries the backend analytics (e.g., BigQuery or aggregated Firestore stats) to find the "Average Carbon Emission per RM Revenue" for that specific industry.
Normalization: Divides the user's total emissions by their revenue (if available) to create a comparable metric.
Output: Returns a comparison statement (e.g., "You emit 15% less carbon than the average furniture manufacturer in Selangor").

