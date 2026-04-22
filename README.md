#  Local Network Scanner with AI Assistance

An asynchronous local network scanner integrated with a built-in AI Assistant (Google Gemini) to help analyze discovered devices and maintain cybersecurity.

##  Key Features

* Asynchronous local network scanning
* Multiple information gathering (live hosts and their open ports, mac, vendor, banners of services grabbed, OS detection)
* High efficiency using connection-limiting optimizations and asyncio for efficiency
* Integrated Google ADK to assist in analyzing scan results and provide security advice
* User-friendly web app interface for clear and easy-to-read results

## 🛠️ Tech Stack

* **Backend:** Python (`asyncio`), FastAPI, WebSockets
* **Frontend:**  TailwindCSS, Vanilla JavaScript
* **AI Integration:** Google Generative AI (Gemini) via Google ADK
  
##  Screenshots

<table width="100%" align="center">
  <tr>
    <td align="center" width="50%" valign="top">
      <img src="https://github.com/user-attachments/assets/2fe626cd-6ba9-44a1-ab6a-7f780d9e5bc8" alt="Results of a scan" height="400px" style="object-fit: contain; border-radius: 12px; border: 2px solid #ddd; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
      <br>
      <em>Results of a scan</em>
    </td>
    <td align="center" width="50%" valign="top">
      <img src="https://github.com/user-attachments/assets/7cce1dd7-5a93-433e-a3c6-66cc67dff82c" alt="Chat with AI" height="400px" style="object-fit: contain; border-radius: 12px; border: 2px solid #ddd; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
      <br>
      <em>Chat with AI Assistant</em>
    </td>
  </tr>
</table>

##  Step-by-step Installation
- First, paste this in your shell:
 ```bash
git clone https://github.com/Szymon392/Local-Network-Scanner.git
cd Local-Network-Scanner
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
- Second, create file: /Local-Network-Scanner/.env
  - paste: ```GOOGLE_API_KEY="paste_your_google_ai_key_here"```
  - save the file
- Finally, start the app:
```bash
uvicorn main:app --reload
```
- The app is available on: http://127.0.0.1:8000
