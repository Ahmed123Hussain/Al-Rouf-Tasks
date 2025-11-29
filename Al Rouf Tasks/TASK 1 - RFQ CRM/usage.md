💡 Overview of the Automation
This Zapier workflow automatically processes new RFQ emails, classifies their content, logs key data, stores attachments securely, and sends a quick acknowledgment response to the sender. This ensures no RFQ is missed and all relevant data is immediately captured.

🛠️ Zapier Workflow Steps
The automation follows a sequential process, triggered by a new email:

1. Trigger: New Email
Action: The Zap starts whenever a new email is received in the designated mailbox (e.g., a specific inbox or a filtered label).

2. Filter by Keyword (Classification)
Step 2: Analyzes the email body and/or subject line for keywords indicating a Price/Quotaton request.

Purpose: Only emails confirmed as RFQs proceed through the rest of the workflow.

3. Filter by Sender (Internal/External)
Step 3: Analyzes the sender's email address.

Purpose: Ensures the workflow only processes external RFQs from clients/partners and ignores internal communication.

4. Filter by Date/Time (Optional)
Step 4: This step likely ensures the email falls within a valid time frame or prevents processing overly old emails.

Purpose: Provides additional control based on time sensitivity (e.g., if you only want to process emails received in the last hour).

5. Google Sheets: Log RFQ Data
Action: If all filters pass, a new row is created in a specified Google Sheet (your RFQ CRM Log).

Data Logged: This step typically captures:

Sender's Name and Email.

Email Subject and Body Snippet.

Date and Time of Request.

A status (e.g., "Received - Automated").

6. Google Drive: Store Attachments
Action: Any attachments found in the RFQ email are uploaded and stored in a designated folder in Google Drive.

Purpose: Centralizes all documentation related to the RFQ for easy access by the sales team.

7. Gmail: Send Confirmation Email
Action: Sends an immediate, standardized acknowledgment email back to the sender.

Content: This email confirms that the request has been received, logged, and will be reviewed shortly by the sales team.

Purpose: Provides prompt recognition, enhancing customer experience and setting expectations.

🔗 Public Zap Link
To integrate this automation into your own Zapier account, you can use the provided public link:

Link Name: Zap Public Link.txt

Usage: Copy the link from the file and follow the Zapier prompts to create a copy of this Zap in your workspace. You will need to connect your own Gmail/Email, Google Sheets, and Google Drive accounts to the respective steps.
